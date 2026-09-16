"""Verifier-owned real PostgreSQL checks; candidate and old verifiers unchanged."""
from __future__ import annotations

import pytest
import os
from backend.evidence import services
from tests.test_evidence_services import (
    db,
    pg_sessionmaker,
    verified_evidence_fact,
    dt,
    evidence_table_counts,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def replay_exact_one_line_baseline_when_requested(monkeypatch):
    """Opt-in diagnostic reconstruction of the sole committed service difference."""
    if os.getenv("TG_R1C_REPLAY_BASELINE") == "1":
        monkeypatch.setattr(services, "ELIGIBLE_CURRENT_STATUSES", {
            "UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "DISPUTED",
        })


async def correction(session, base, key):
    return await services.revise_correct_evidence(
        session,
        evidence_series_id=base.evidence_series_id,
        expected_version=base.version,
        display_text="Independent ordinary correction",
        status_changed_at=dt(day=1),
        status_changed_by_actor="IMPORTER",
        status_reason="Independent correction requires new review",
        idempotency_key=key,
    )


@pytest.mark.parametrize("status", [
    "UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "REJECTED",
    "DISPUTED", "INVALIDATED", "RETRACTED",
])
async def test_latest_version_number_wins_and_reads_do_not_write(
    db, pg_sessionmaker, status,
):
    base = await verified_evidence_fact(db, key_suffix=f"independent-{status}")
    if status in {"UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "REJECTED"}:
        latest = await correction(db, base, f"independent-{status}-correct")
        if status != "UNREVIEWED":
            latest = await services.request_review(
                db, evidence_series_id=base.evidence_series_id,
                expected_version=latest.version, reason="Independent review",
                actor="USER", idempotency_key=f"independent-{status}-review",
                as_of=dt(day=2),
            )
        if status in {"VERIFIED", "REJECTED"}:
            latest = await services.verify_or_reject(
                db, evidence_series_id=base.evidence_series_id,
                expected_version=latest.version, decision=status,
                reason="Independent review decision", actor="USER",
                idempotency_key=f"independent-{status}-decision", as_of=dt(day=3),
            )
    elif status == "DISPUTED":
        latest = await services.mark_disputed(
            db, evidence_series_id=base.evidence_series_id, expected_version=1,
            reason="Independent dispute", actor="USER",
            idempotency_key="independent-dispute", as_of=dt(day=1),
        )
    else:
        latest = await services.retract_or_invalidate(
            db, evidence_series_id=base.evidence_series_id, expected_version=1,
            target_status=status, reason="Independent withdrawal", actor="IMPORTER",
            idempotency_key=f"independent-{status}-withdraw", as_of=dt(day=1),
        )
    await db.commit()
    assert latest.version > base.version
    assert latest.created_at < base.created_at
    async with pg_sessionmaker() as reader:
        before = await evidence_table_counts(reader)
        current = await services.get_current_evidence(reader, base.evidence_series_id)
        valid = await services.get_current_valid_evidence(reader, base.evidence_series_id)
        history = await services.list_evidence_history(reader, base.evidence_series_id)
        exact = await services.get_exact_evidence_version(reader, base.id)
        after = await evidence_table_counts(reader)
        assert before == after
        assert current.id == latest.id
        assert current.verification_status == status
        if status == "VERIFIED":
            assert valid.id == latest.id
            assert valid.id != base.id
        else:
            assert valid is None
        assert exact.verification_status == "VERIFIED"
        assert len(exact.source_locators) == 1
        assert len(exact.instrument_links) == 1
        assert [item.version for item in history] == list(range(1, latest.version + 1))
        assert history[0].id == base.id
        assert history[-1].id == latest.id


async def test_baseline_status_set_reproduces_bug_without_file_or_git_changes(
    db, monkeypatch,
):
    """Diagnostic old constant reproduces the defect; not a production mock path."""
    base = await verified_evidence_fact(db, key_suffix="independent-red-control")
    latest = await correction(db, base, "independent-red-control-correction")
    await db.commit()
    assert latest.verification_status == "UNREVIEWED"
    with monkeypatch.context() as patch:
        patch.setattr(services, "ELIGIBLE_CURRENT_STATUSES", {
            "UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "DISPUTED",
        })
        old_result = await services.get_current_valid_evidence(db, base.evidence_series_id)
        assert old_result is not None and old_result.id == latest.id
    assert await services.get_current_valid_evidence(db, base.evidence_series_id) is None
