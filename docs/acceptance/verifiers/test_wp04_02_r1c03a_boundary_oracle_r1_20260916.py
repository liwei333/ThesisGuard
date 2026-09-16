"""TASK-WP04-02-R1C-03A-ORACLE-R1: independently owned 58-case oracle.

Shares only disposable fixtures and the disclosed constraint-legal legacy seed.
VF-01 uses public correction/review/verification setup, committed before baseline.
VF-02 uses the repair contract's exact route taxonomy and command ownership.
No production monkeypatch, diagnostic replay or positive trusted rule injection.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pytest
from backend.evidence import services
from backend.evidence.errors import EvidenceValidationError
from backend.evidence.models import (
    EvidenceAuditEvent,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceInstrumentLink,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    SourceDocument,
    SourceDocumentVersion,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.test_evidence_services import db as db
from tests.test_evidence_services import pg_sessionmaker as pg_sessionmaker
from tests.test_evidence_services import r1c03a_legacy_prior

pytestmark = pytest.mark.asyncio
ROUTES = ["same", "automatic", "direct", "initial", "underlying-replacement"]
MODELS = [
    EvidenceSeries,
    EvidenceVersion,
    EvidenceSourceLocator,
    EvidenceInstrumentLink,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceAuditEvent,
    SourceDocument,
    SourceDocumentVersion,
]
STATUS_AT = datetime(2026, 9, 16, tzinfo=UTC)
CREATE_AT = datetime(2026, 9, 17, tzinfo=UTC)
STATUS_ACTOR = "USER"
REASON = "Verifier-owned boundary correction"
TEXT = "Verifier-owned corrected text"
AUDIT_MAP = {
    "same": ("EVIDENCE_CORRECTION", "USER", STATUS_AT),
    "automatic": ("EVIDENCE_VERSION_CREATED", "IMPORTER", STATUS_AT),
    "direct": ("EVIDENCE_VERSION_CREATED", "SYSTEM", STATUS_AT),
    "underlying-replacement": ("EVIDENCE_VERSION_CREATED", "ADMIN_SCRIPT", CREATE_AT),
    "initial": ("EVIDENCE_VERSION_CREATED", "ADMIN_SCRIPT", CREATE_AT),
}


@dataclass(frozen=True)
class Setup:
    prior: EvidenceVersion
    support_ids: tuple[str, ...] = ()


def columns(row: Any) -> dict[str, Any]:
    return {col.name: getattr(row, col.name) for col in row.__table__.columns}


def exact_snapshot(row: EvidenceVersion) -> dict[str, Any]:
    return {
        "version": columns(row),
        **{
            rel: sorted([columns(c) for c in getattr(row, rel)], key=lambda x: x["id"])
            for rel in ["source_locators", "instrument_links", "derived_links"]
        },
    }


async def durable_rows(session: AsyncSession) -> dict[str, list[dict[str, Any]]]:
    """All columns of all rows in the nine original persistence tables."""
    result = {}
    for model in MODELS:
        rows = (await session.execute(select(model.__table__))).mappings().all()
        result[model.__tablename__] = sorted([dict(r) for r in rows], key=repr)
    return result


def snapshot_hash(rows: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()


def emit(stage: str, **values: Any) -> None:
    print(json.dumps({"stage": stage, **values}, sort_keys=True, default=str))


def origin_for(support_id: str) -> str:
    """Frozen DERIVED identity from exact support set; no production hash helper."""
    return (
        "derived:"
        + hashlib.sha256(json.dumps([support_id], separators=(",", ":")).encode()).hexdigest()
    )


async def assert_acyclic(session: AsyncSession) -> None:
    links = list(await session.scalars(select(EvidenceDerivationLink)))
    edges: dict[str, set[str]] = {}
    for link in links:
        assert link.derived_evidence_version_id != link.supporting_evidence_version_id
        edges.setdefault(link.derived_evidence_version_id, set()).add(
            link.supporting_evidence_version_id
        )
    visited: set[str] = set()
    active: set[str] = set()

    def visit(exact_id: str) -> None:
        assert exact_id not in active, "Exact derivation cycle"
        if exact_id in visited:
            return
        active.add(exact_id)
        for support_id in edges.get(exact_id, set()):
            visit(support_id)
        active.remove(exact_id)
        visited.add(exact_id)

    for exact_id in edges:
        visit(exact_id)


async def prepare(session: AsyncSession, route: str) -> Setup:
    prior = await r1c03a_legacy_prior(session, derived=route == "automatic")
    assert prior.created_by_actor == "IMPORTER"
    assert prior.verification_status == "VERIFIED"
    assert prior.trusted_correction_rule == "legacy-historical-rule"
    support_ids: tuple[str, ...] = ()
    if route == "automatic":
        initial = await services.get_exact_evidence_version(
            session, prior.derived_links[0].supporting_evidence_version_id
        )
        assert initial is not None
        assert initial.version == 1 and initial.supersedes_evidence_version_id is None
        assert initial.information_type == "FACT" and initial.verification_status == "VERIFIED"
        initial_snapshot = exact_snapshot(initial)
        corrected = await services.revise_correct_evidence(
            session,
            evidence_series_id=initial.evidence_series_id,
            expected_version=initial.version,
            display_text="Lawful alternate support correction",
            status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            status_changed_by_actor="USER",
            status_reason="Oracle support setup correction",
            idempotency_key="oracle-r1-support-correct",
        )
        assert corrected.verification_status == "UNREVIEWED"
        assert corrected.trusted_correction_rule is None
        pending = await services.request_review(
            session,
            evidence_series_id=initial.evidence_series_id,
            expected_version=corrected.version,
            reason="Oracle support setup review",
            actor="USER",
            idempotency_key="oracle-r1-support-review",
            as_of=datetime(2026, 9, 14, tzinfo=UTC),
        )
        assert pending.verification_status == "PENDING_REVIEW"
        verified = await services.verify_or_reject(
            session,
            evidence_series_id=initial.evidence_series_id,
            expected_version=pending.version,
            decision="VERIFIED",
            reason="Oracle support setup accepted",
            actor="USER",
            idempotency_key="oracle-r1-support-verify",
            as_of=datetime(2026, 9, 15, tzinfo=UTC),
        )
        support_ids = (initial.id, corrected.id, pending.id, verified.id)
        assert len(set(support_ids)) == 4
        assert [initial.version, corrected.version, pending.version, verified.version] == [
            1,
            2,
            3,
            4,
        ]
        assert corrected.supersedes_evidence_version_id == initial.id
        assert pending.supersedes_evidence_version_id == corrected.id
        assert verified.supersedes_evidence_version_id == pending.id
        assert (
            verified.verification_status == "VERIFIED" and verified.trusted_correction_rule is None
        )
        eligible = await services.get_current_valid_evidence(session, initial.evidence_series_id)
        assert eligible is not None and eligible.id == verified.id
        assert initial.id != verified.id and verified.id != prior.id
        # The proposed support is a source-backed leaf, so cannot lead back to prior.
        assert verified.provenance_kind == "SOURCE_BACKED" and not verified.derived_links
        assert (
            exact_snapshot(await services.get_exact_evidence_version(session, initial.id))
            == initial_snapshot
        )
        assert [c.supporting_evidence_version_id for c in prior.derived_links] == [initial.id]
        series = await session.get(EvidenceSeries, prior.evidence_series_id)
        assert series is not None and series.origin_key == origin_for(initial.id)
        assert series.origin_key != origin_for(verified.id)
    await assert_acyclic(session)
    await session.commit()
    assert not session.in_transaction(), "Setup must finish before rejection baseline"
    emit("setup_committed", route=route, prior_exact_id=prior.id, support_exact_ids=support_ids)
    return Setup(prior, support_ids)


async def command(
    session: AsyncSession, setup: Setup, route: str, rule_kwargs: dict[str, Any], key: str
) -> EvidenceVersion:
    prior = setup.prior
    audit = {
        "status_changed_at": STATUS_AT,
        "status_changed_by_actor": STATUS_ACTOR,
        "status_reason": REASON,
        "idempotency_key": key,
    }
    if route in {"same", "automatic"}:
        changed = {}
        if route == "automatic":
            assert len(set(setup.support_ids)) == 4
            changed["derivation_links"] = [
                services.DerivationLinkInput(
                    supporting_evidence_version_id=setup.support_ids[-1],
                    role="INPUT_FACT",
                    support_order=1,
                )
            ]
        emit(
            "production_call",
            route=route,
            prior_exact_id=prior.id,
            rule_type=type(rule_kwargs.get("trusted_correction_rule")).__name__,
        )
        return await services.revise_correct_evidence(
            session,
            evidence_series_id=prior.evidence_series_id,
            expected_version=prior.version,
            display_text=TEXT,
            **changed,
            **audit,
            **rule_kwargs,
        )
    series = await session.get(EvidenceSeries, prior.evidence_series_id)
    assert series is not None
    fields = {
        "scope_type": series.scope_type,
        "scope_key": series.scope_key,
        "information_type": prior.information_type,
        "claim_key": prior.claim_key,
        "metric_key": "verifier-owned-new-metric",
        "period_start": prior.period_start,
        "period_end": prior.period_end,
        "provenance_kind": prior.provenance_kind,
        "primary_source_document_id": series.primary_source_document_id,
        "source_document_version_id": prior.source_document_version_id,
        "display_title": prior.display_title,
        "display_text": TEXT,
        "raw_value": prior.raw_value,
        "raw_unit": prior.raw_unit,
        "normalized_value": prior.normalized_value,
        "normalized_unit": prior.normalized_unit,
        "as_of": prior.as_of,
        "extractor_name": prior.extractor_name,
        "extractor_version": prior.extractor_version,
        "locators": [
            services.SourceLocatorInput(
                locator_type=c.locator_type,
                raw_locator=c.raw_locator,
                short_citation=c.short_citation,
                locator_payload=dict(c.locator_payload),
                quote_hash=c.quote_hash,
            )
            for c in prior.source_locators
        ],
        "instrument_links": [
            services.InstrumentLinkInput(
                instrument_id=c.instrument_id,
                role=c.role,
                link_order=c.link_order,
                link_metadata=dict(c.link_metadata or {}),
            )
            for c in prior.instrument_links
        ],
        "created_by_actor": "SYSTEM" if route == "direct" else "ADMIN_SCRIPT",
    }
    emit(
        "production_call",
        route=route,
        prior_exact_id=prior.id,
        rule_type=type(rule_kwargs.get("trusted_correction_rule")).__name__,
    )
    if route == "direct":
        return await services.create_replacement_evidence_series(
            session, prior_evidence_version_id=prior.id, **fields, **audit, **rule_kwargs
        )
    if route == "initial":
        return await services.create_evidence_series_version(
            session, **fields, created_at=CREATE_AT, idempotency_key=key, **rule_kwargs
        )
    assert route == "underlying-replacement"
    return await services.create_evidence_series_version(
        session,
        **fields,
        created_at=CREATE_AT,
        supersedes_evidence_version_id=prior.id,
        verification_status="VERIFIED",
        status_change_kind="CORRECTION",
        **audit,
        **rule_kwargs,
    )


def assert_old_rows_preserved(
    before: dict[str, list[dict[str, Any]]], after: dict[str, list[dict[str, Any]]]
) -> None:
    for model in MODELS:
        primary_keys = [col.name for col in model.__table__.primary_key.columns]
        index = {tuple(row[k] for k in primary_keys): row for row in after[model.__tablename__]}
        for row in before[model.__tablename__]:
            assert index[tuple(row[k] for k in primary_keys)] == row


async def assert_audit(
    session: AsyncSession,
    result: EvidenceVersion,
    setup: Setup,
    route: str,
    rule_kwargs: dict[str, Any],
) -> None:
    events = list(
        await session.scalars(
            select(EvidenceAuditEvent).where(EvidenceAuditEvent.aggregate_id == result.id)
        )
    )
    assert len(events) == 1
    event = events[0]
    expected_type, expected_actor, expected_at = AUDIT_MAP[route]
    assert event.aggregate_type == "EvidenceVersion"
    assert event.aggregate_id == result.id
    assert event.event_type == expected_type
    assert event.actor == expected_actor
    assert event.occurred_at == expected_at
    assert result.created_by_actor == expected_actor and result.created_at == expected_at
    payload = event.payload
    assert isinstance(payload, dict)
    prior = setup.prior
    if route == "same":
        assert result.status_changed_by_actor == "USER" and result.status_changed_at == STATUS_AT
        assert payload["evidence_series_id"] == prior.evidence_series_id
        assert payload["expected_version"] == prior.version
        assert payload["status_changed_at"] == "2026-09-16T00:00:00Z"
        assert payload["status_changed_by_actor"] == "USER"
        assert payload["status_reason"] == REASON
        assert payload["overrides"] == {"display_text": TEXT, **rule_kwargs}
    else:
        series = await session.get(EvidenceSeries, result.evidence_series_id)
        assert series is not None and payload["series_hash"] == series.series_identity_hash
        assert payload["display_title"] == prior.display_title
        assert payload["display_text"] == TEXT
        assert payload["source_document_version_id"] == prior.source_document_version_id
        assert payload["verification_status"] == (
            "VERIFIED" if route == "underlying-replacement" else "UNREVIEWED"
        )
        assert payload["as_of"] == prior.as_of.astimezone(UTC).isoformat().replace("+00:00", "Z")
        assert isinstance(payload["locators"], list) and len(payload["locators"]) == len(
            prior.source_locators
        )
        assert isinstance(payload["instrument_links"], list) and len(
            payload["instrument_links"]
        ) == len(prior.instrument_links)
        assert (
            payload["instrument_links"][0]["instrument_id"]
            == "11111111-1111-4111-8111-111111111111"
        )
        assert payload["instrument_links"][0]["role"] == "PRIMARY_SCOPE"
        if route == "automatic":
            assert (
                payload["derivation_links"][0]["supporting_evidence_version_id"]
                == setup.support_ids[-1]
            )
            assert len(payload["derivation_links"]) == 1
        else:
            assert payload["derivation_links"] == []
            assert payload["locators"][0]["raw_locator"] == "p.12"
            assert payload["normalized_value"] == "32.5"
    emit(
        "exact_audit_checked",
        route=route,
        exact_id=result.id,
        event_id=event.id,
        event_type=event.event_type,
        actor=event.actor,
        occurred_at=event.occurred_at,
        payload=payload,
    )


async def test_empty_production_approval_and_normal_environment() -> None:
    assert frozenset() == services._APPROVED_TRUSTED_CORRECTION_RULES
    for name in ["TG_TEST_ADMIN_DATABASE_URL", "TG_R1C_REPLAY_BASELINE", "TG_R1C02_REPLAY_PRIOR"]:
        assert name not in os.environ


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize(
    "rule",
    [
        "",
        " \t\n",
        "unknown-rule",
        "same-source-parser-v1",
        "SAME-SOURCE-PARSER-V1",
        False,
        1,
        {},
        [],
    ],
    ids=[
        "empty",
        "whitespace",
        "unknown",
        "legacy-fixture",
        "case",
        "bool",
        "int",
        "mapping",
        "list",
    ],
)
async def test_rejected_trusted_commit_preserves_every_durable_row(
    db: AsyncSession, pg_sessionmaker: async_sessionmaker[AsyncSession], route: str, rule: Any
) -> None:
    setup = await prepare(db, route)
    before = await durable_rows(db)
    old = exact_snapshot(setup.prior)
    emit(
        "no_residue_baseline",
        route=route,
        rule_type=type(rule).__name__,
        snapshot_sha256=snapshot_hash(before),
    )
    with pytest.raises(EvidenceValidationError) as error:
        await command(db, setup, route, {"trusted_correction_rule": rule}, "owned-denied")
    assert error.value.code == "EVIDENCE_VALIDATION_ERROR"
    assert error.value.details["validation_path"] == "trusted_correction_rule"
    assert error.value.details["trusted_correction_rule"] == rule
    assert error.value.details["rule_type"] == type(rule).__name__
    assert error.value.details["reason"] == (
        "unapproved_rule" if isinstance(rule, str) else "invalid_rule_type"
    )
    assert not db.new and not db.dirty
    await db.commit()
    async with pg_sessionmaker() as fresh:
        assert fresh is not db
        after = await durable_rows(fresh)
        assert after == before
        original = await services.get_exact_evidence_version(fresh, setup.prior.id)
        assert original is not None and exact_snapshot(original) == old
        assert original.trusted_correction_rule == "legacy-historical-rule"
        current = await services.get_current_evidence(fresh, original.evidence_series_id)
        assert current is not None and current.id == original.id
        emit(
            "domain_rejected_commit_fresh_no_residue",
            route=route,
            rule_type=type(rule).__name__,
            code=error.value.code,
            before_sha256=snapshot_hash(before),
            fresh_sha256=snapshot_hash(after),
            prior_exact_id=original.id,
        )


@pytest.mark.parametrize("route", [r for r in ROUTES if r != "initial"])
@pytest.mark.parametrize(
    "rule_kwargs", [{}, {"trusted_correction_rule": None}], ids=["omitted", "none"]
)
async def test_ordinary_never_inherits_and_retains_correction_routing(
    db: AsyncSession,
    pg_sessionmaker: async_sessionmaker[AsyncSession],
    route: str,
    rule_kwargs: dict[str, Any],
) -> None:
    setup = await prepare(db, route)
    prior = setup.prior
    old = exact_snapshot(prior)
    before = await durable_rows(db)
    corrected = await command(db, setup, route, rule_kwargs, "owned-ordinary")
    result_id = corrected.id
    await db.commit()
    async with pg_sessionmaker() as fresh:
        assert fresh is not db
        original = await services.get_exact_evidence_version(fresh, prior.id)
        result = await services.get_exact_evidence_version(fresh, result_id)
        assert original is not None and result is not None
        assert exact_snapshot(original) == old
        assert original.trusted_correction_rule == "legacy-historical-rule"
        assert_old_rows_preserved(before, await durable_rows(fresh))
        assert result.verification_status == "UNREVIEWED" and result.trusted_correction_rule is None
        assert result.supersedes_evidence_version_id == prior.id
        assert (
            result.status_changed_at,
            result.status_changed_by_actor,
            result.status_change_kind,
            result.status_reason,
        ) == (STATUS_AT, STATUS_ACTOR, "CORRECTION", REASON)
        assert result.display_text == TEXT
        assert await services.get_current_valid_evidence(fresh, result.evidence_series_id) is None
        if route == "same":
            assert result.evidence_series_id == prior.evidence_series_id
            assert result.version == prior.version + 1
        else:
            assert result.evidence_series_id != prior.evidence_series_id and result.version == 1
            assert (
                await services.get_current_evidence(fresh, prior.evidence_series_id)
            ).id == prior.id
            old_series = await fresh.get(EvidenceSeries, prior.evidence_series_id)
            new_series = await fresh.get(EvidenceSeries, result.evidence_series_id)
            assert old_series is not None and new_series is not None
            assert new_series.series_identity_hash != old_series.series_identity_hash
            if route == "automatic":
                assert new_series.origin_key == origin_for(setup.support_ids[-1])
                assert old_series.origin_key == origin_for(setup.support_ids[0])
                assert result.id not in setup.support_ids
                assert [c.supporting_evidence_version_id for c in result.derived_links] == [
                    setup.support_ids[-1]
                ]
        for rel in ["source_locators", "instrument_links", "derived_links"]:
            a, b = getattr(original, rel), getattr(result, rel)
            assert len(a) == len(b)
            assert {c.id for c in a}.isdisjoint(c.id for c in b)
        await assert_acyclic(fresh)
        await assert_audit(fresh, result, setup, route, rule_kwargs)
        emit(
            "ordinary_commit_fresh_history_preserved",
            route=route,
            rule_input="none" if rule_kwargs else "omitted",
            prior_exact_id=prior.id,
            result_exact_id=result.id,
            result_series_id=result.evidence_series_id,
            verification_status=result.verification_status,
            trusted_correction_rule=result.trusted_correction_rule,
        )


@pytest.mark.parametrize("route", ["direct", "initial"])
@pytest.mark.parametrize("trusted", [False, True], ids=["same-request", "new-trusted-request"])
async def test_replay_is_read_only_and_never_absorbs_new_trust(
    db: AsyncSession, pg_sessionmaker: async_sessionmaker[AsyncSession], route: str, trusted: bool
) -> None:
    setup = await prepare(db, route)
    result = await command(db, setup, route, {}, "owned-replay")
    result_id = result.id
    await db.commit()
    before = await durable_rows(db)
    async with pg_sessionmaker() as caller:
        assert caller is not db
        original = await services.get_exact_evidence_version(caller, setup.prior.id)
        assert original is not None
        replay_setup = Setup(original, setup.support_ids)
        if trusted:
            with pytest.raises(EvidenceValidationError) as error:
                await command(
                    caller,
                    replay_setup,
                    route,
                    {"trusted_correction_rule": "unknown-rule"},
                    "owned-replay",
                )
            assert error.value.code == "EVIDENCE_VALIDATION_ERROR"
            assert error.value.details["validation_path"] == "trusted_correction_rule"
            assert error.value.details["trusted_correction_rule"] == "unknown-rule"
            assert error.value.details["rule_type"] == "str"
            assert error.value.details["reason"] == "unapproved_rule"
        else:
            replayed = await command(caller, replay_setup, route, {}, "owned-replay")
            assert replayed.id == result_id
        await caller.commit()
    async with pg_sessionmaker() as fresh:
        after = await durable_rows(fresh)
        assert after == before
        persisted = await services.get_exact_evidence_version(fresh, result_id)
        assert persisted is not None
        assert (
            persisted.trusted_correction_rule is None
            and persisted.verification_status == "UNREVIEWED"
        )
        await assert_audit(fresh, persisted, setup, route, {})
        emit(
            "replay_commit_fresh_no_residue",
            route=route,
            trusted_request=trusted,
            exact_id=result_id,
            before_sha256=snapshot_hash(before),
            fresh_sha256=snapshot_hash(after),
        )
