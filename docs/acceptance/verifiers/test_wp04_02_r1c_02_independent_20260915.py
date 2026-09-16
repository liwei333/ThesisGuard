"""Independent frozen lifecycle oracle, real PostgreSQL audit and rollback checks."""
import pytest
import os
from sqlalchemy import select
from backend.evidence import services
from backend.evidence.errors import EvidenceDomainError
from backend.evidence.models import EvidenceAuditEvent
from tests.test_evidence_services import (
    db, pg_sessionmaker, dt, evidence_fact,
    evidence_with_lifecycle_status, evidence_table_counts,
)

pytestmark = pytest.mark.asyncio

STATES = ["UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "DISPUTED",
          "REJECTED", "INVALIDATED", "RETRACTED"]
COMMANDS = ["review", "verify", "reject", "dispute", "invalidate", "retract"]
LEGAL = {
    ("UNREVIEWED", "review"): ("PENDING_REVIEW", "REVIEW_REQUEST"),
    ("UNREVIEWED", "reject"): ("REJECTED", "REVIEW_DECISION"),
    ("PENDING_REVIEW", "verify"): ("VERIFIED", "REVIEW_DECISION"),
    ("PENDING_REVIEW", "reject"): ("REJECTED", "REVIEW_DECISION"),
    ("VERIFIED", "dispute"): ("DISPUTED", "DISPUTE"),
    ("VERIFIED", "invalidate"): ("INVALIDATED", "INVALIDATION"),
    ("VERIFIED", "retract"): ("RETRACTED", "RETRACTION"),
    ("DISPUTED", "verify"): ("VERIFIED", "DISPUTE"),
    ("DISPUTED", "reject"): ("REJECTED", "DISPUTE"),
    ("DISPUTED", "retract"): ("RETRACTED", "RETRACTION"),
}


@pytest.fixture(autouse=True)
def diagnostic_prior_status_behavior(monkeypatch):
    """Reconstruct only R1C-02's prior semantics, never files or DB fixture route."""
    if os.getenv("TG_R1C02_REPLAY_PRIOR") != "1":
        return
    original = services._status_command

    async def prior(*args, **kwargs):
        kwargs.pop("status_change_kind_by_from", None)
        scope = kwargs["idempotency_scope"]
        if scope == "verify_or_reject":
            kwargs["allowed_from"] = {"PENDING_REVIEW", "DISPUTED"}
        elif scope == "mark_disputed":
            kwargs["allowed_from"] = {"VERIFIED", "REJECTED", "PENDING_REVIEW"}
        elif scope == "retract_or_invalidate":
            kwargs["allowed_from"] = {"UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "REJECTED", "DISPUTED"}
        return await original(*args, **kwargs)

    monkeypatch.setattr(services, "_status_command", prior)


async def run(session, series_id, version, command, key):
    kwargs = dict(db=session, evidence_series_id=series_id,
                  expected_version=version, reason="Independent matrix reason",
                  actor="USER", idempotency_key=key, as_of=dt(day=20))
    if command == "review":
        return await services.request_review(**kwargs)
    if command in {"verify", "reject"}:
        return await services.verify_or_reject(
            **kwargs, decision="VERIFIED" if command == "verify" else "REJECTED")
    if command == "dispute":
        return await services.mark_disputed(**kwargs)
    return await services.retract_or_invalidate(
        **kwargs, target_status="INVALIDATED" if command == "invalidate" else "RETRACTED")


@pytest.mark.parametrize("state,command", [(s,c) for s in STATES for c in COMMANDS])
async def test_independent_matrix_persists_exact_audit_and_replay_once(
    db, pg_sessionmaker, state, command,
):
    prior = await evidence_with_lifecycle_status(
        db, status=state, key_suffix=f"independent02-{state}-{command}")
    series_id, prior_id, version = prior.evidence_series_id, prior.id, prior.version
    key = f"independent02-{state}-{command}-command"
    before = await evidence_table_counts(db)
    expected = LEGAL.get((state, command))
    if expected is None:
        with pytest.raises(EvidenceDomainError) as error:
            await run(db, series_id, version, command, key)
        assert error.value.code == "EVIDENCE_INVALID_STATE_TRANSITION"
        await db.commit()
        async with pg_sessionmaker() as reader:
            assert await evidence_table_counts(reader) == before
            assert (await services.get_current_evidence(reader, series_id)).id == prior_id
        return
    result = await run(db, series_id, version, command, key)
    result_id = result.id
    await db.commit()
    async with pg_sessionmaker() as reader:
        persisted = await services.get_exact_evidence_version(reader, result_id)
        original = await services.get_exact_evidence_version(reader, prior_id)
        assert persisted.version == version + 1
        assert persisted.verification_status == expected[0]
        assert persisted.status_change_kind == expected[1]
        assert persisted.status_changed_at == dt(day=20)
        assert persisted.status_changed_by_actor == "USER"
        assert persisted.status_reason == "Independent matrix reason"
        assert persisted.supersedes_evidence_version_id == prior_id
        assert original.verification_status == state
        assert persisted.raw_value == original.raw_value
        assert [x.raw_locator for x in persisted.source_locators] == [x.raw_locator for x in original.source_locators]
        assert set(x.id for x in persisted.source_locators).isdisjoint(x.id for x in original.source_locators)
        assert [x.instrument_id for x in persisted.instrument_links] == [x.instrument_id for x in original.instrument_links]
        events = list((await reader.scalars(select(EvidenceAuditEvent).where(
            EvidenceAuditEvent.aggregate_id == result_id))).all())
        assert len(events) == 1
        assert events[0].event_type == f"EVIDENCE_{expected[1]}"
        assert events[0].actor == "USER"
        assert events[0].occurred_at == dt(day=20)
        assert events[0].payload["reason"] == "Independent matrix reason"
        after = await evidence_table_counts(reader)
        replay = await run(reader, series_id, version, command, key)
        assert replay.id == result_id
        await reader.commit()
    async with pg_sessionmaker() as observer:
        assert await evidence_table_counts(observer) == after


async def test_caller_rollback_removes_entire_status_append(db, pg_sessionmaker):
    prior = await evidence_fact(db, key_suffix="independent02-rollback")
    series_id, prior_id = prior.evidence_series_id, prior.id
    await db.commit()
    before = await evidence_table_counts(db)
    result = await run(db, series_id, 1, "review", "independent02-rollback-review")
    result_id = result.id
    await db.rollback()
    async with pg_sessionmaker() as observer:
        assert await evidence_table_counts(observer) == before
        assert await services.get_exact_evidence_version(observer, result_id) is None
        assert (await services.get_current_evidence(observer, series_id)).id == prior_id
