"""Verifier-owned R1B counterexamples for TASK-WP04-02-R1B-REBASELINE-REVERIFY-R1.

This file is intentionally outside the candidate worktree. It imports the
candidate's real PostgreSQL fixtures and public service API, then exercises
contract edges not covered by merely rerunning the candidate's four R1B tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from backend.evidence import services
from backend.evidence.errors import EvidenceDomainError
from backend.evidence.models import EvidenceDerivationLink, EvidenceSeries
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.test_evidence_services import (
    QIANGRUI_INSTRUMENT_ID,
    SHENLING_INSTRUMENT_ID,
    db,
    dt,
    evidence_fact,
    evidence_table_counts,
    expected_cross_scope,
    pg_sessionmaker,
)

pytestmark = pytest.mark.asyncio


async def test_replacement_can_support_prior_exact_version_without_exact_cycle(
    db: AsyncSession,
) -> None:
    """Exact-version graph rule allows V2 -> V1 when V1 has no path to V2.

    The frozen contract forbids self-links and cycles between exact
    EvidenceVersion rows. It does not declare that every support from a previous
    version in the same EvidenceSeries is a cycle. A changed support set should
    route to replacement v1 with the prior exact version as predecessor.
    """
    support = await evidence_fact(db, key_suffix="rv-prior-support")
    derived = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="rv-prior-derived",
        provenance_kind="DERIVED",
        display_title="Initial derived evidence",
        display_text="Initial derived evidence",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support.id,
                role="INPUT_FACT",
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="rv-prior-derived",
    )
    await db.commit()
    before = await evidence_table_counts(db)

    replacement = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived.evidence_series_id,
        expected_version=1,
        display_text="Refined derived evidence using the prior exact inference",
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_reason="refined support set",
        idempotency_key="rv-prior-replacement",
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=derived.id,
                role="SUPPORTS_INFERENCE",
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support.id,
                role="INPUT_FACT",
            ),
        ],
    )
    await db.commit()

    assert replacement.version == 1
    assert replacement.evidence_series_id != derived.evidence_series_id
    assert replacement.supersedes_evidence_version_id == derived.id
    assert {
        link.supporting_evidence_version_id for link in replacement.derived_links
    } == {derived.id, support.id}
    after = await evidence_table_counts(db)
    assert after["series"] == before["series"] + 1
    assert after["version"] == before["version"] + 1
    assert after["derivation_link"] == before["derivation_link"] + 2


async def test_cross_instrument_invalid_replacement_leaves_no_residue(
    db: AsyncSession,
) -> None:
    """A failed member-set replacement must leave no partial rows."""
    scope_key = expected_cross_scope(QIANGRUI_INSTRUMENT_ID, SHENLING_INSTRUMENT_ID)
    created = await services.create_evidence_series_version(
        db,
        scope_type="CROSS_INSTRUMENT",
        scope_key=scope_key,
        information_type="ESTIMATE",
        claim_key="rv-cross-no-residue",
        provenance_kind="MANUAL",
        display_title="Cross estimate",
        display_text="Cross estimate",
        as_of=dt(),
        manual_entry_reason="manual",
        manual_observed_at=dt(),
        created_by_actor="USER",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
            ),
            services.InstrumentLinkInput(
                instrument_id=SHENLING_INSTRUMENT_ID,
                role="PEER",
            ),
        ],
        idempotency_key="rv-cross-no-residue",
    )
    await db.commit()
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError):
        await services.revise_correct_evidence(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=1,
            status_changed_at=dt(day=13),
            status_changed_by_actor="USER",
            status_reason="invalid member",
            idempotency_key="rv-cross-invalid-member",
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id="99999999-9999-4999-8999-999999999999",
                    role="PRIMARY_SCOPE",
                )
            ],
        )

    assert await evidence_table_counts(db) == before


async def test_manual_matching_caller_origin_does_not_override_canonical_identity(
    db: AsyncSession,
) -> None:
    """Supplying the exact canonical origin is tolerated but does not select another lineage."""
    origin = "manual:USER:rv-manual-origin"
    created = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="ESTIMATE",
        claim_key=" rv-manual-origin ",
        provenance_kind="MANUAL",
        origin_key=origin,
        display_title="Manual estimate",
        display_text="Manual estimate",
        normalized_value=Decimal("1"),
        as_of=dt(),
        manual_entry_reason="manual",
        manual_observed_at=dt(),
        created_by_actor="USER",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
            )
        ],
        idempotency_key="rv-manual-origin",
    )
    await db.commit()

    series = await db.get(EvidenceSeries, created.evidence_series_id)
    assert series is not None
    assert series.origin_key == origin


async def test_derivation_failure_does_not_write_link_rows(db: AsyncSession) -> None:
    """Invalid DERIVED commands must not leave a partial derivation child."""
    support = await evidence_fact(db, key_suffix="rv-derivation-no-residue")
    await db.commit()
    before = await evidence_table_counts(db)
    link_count_before = int(
        await db.scalar(select(func.count()).select_from(EvidenceDerivationLink)) or 0
    )

    with pytest.raises(EvidenceDomainError):
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="THESIS_INFERENCE",
            claim_key="rv-duplicate-derivation",
            provenance_kind="DERIVED",
            display_title="Duplicate derivation",
            display_text="Duplicate derivation",
            as_of=dt(),
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support.id,
                    role="INPUT_FACT",
                ),
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support.id,
                    role="INPUT_FACT",
                ),
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                )
            ],
            idempotency_key="rv-duplicate-derivation",
        )

    assert await evidence_table_counts(db) == before
    link_count_after = int(
        await db.scalar(select(func.count()).select_from(EvidenceDerivationLink)) or 0
    )
    assert link_count_after == link_count_before
