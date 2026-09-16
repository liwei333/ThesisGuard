"""Verifier-owned production-wiring probes; no candidate edits or fake DB behavior."""

from __future__ import annotations

import pytest
from backend.evidence import services
from sqlalchemy.ext.asyncio import AsyncSession
from tests.test_evidence_services import (
    QIANGRUI_INSTRUMENT_ID,
    db,
    dt,
    evidence_fact,
    pg_sessionmaker,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("operation", ["create", "same_series_revision", "replacement"])
async def test_public_derived_write_validates_its_new_exact_target(
    db: AsyncSession, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    support = await evidence_fact(db, key_suffix=f"wiring-{operation}")
    exact_targets: list[str | None] = []
    traversed_targets: list[str] = []
    real_validate = services._validate_derivation_links
    real_reach = services._support_graph_reaches_exact_version

    async def observe_validation(*args, **kwargs):
        if kwargs.get("provenance_kind") == "DERIVED":
            exact_targets.append(kwargs.get("proposed_derived_evidence_version_id"))
        return await real_validate(*args, **kwargs)

    async def observe_reachability(*args, **kwargs):
        traversed_targets.append(kwargs["target_evidence_version_id"])
        return await real_reach(*args, **kwargs)

    monkeypatch.setattr(services, "_validate_derivation_links", observe_validation)
    monkeypatch.setattr(services, "_support_graph_reaches_exact_version", observe_reachability)

    created = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key=f"wiring-{operation}",
        provenance_kind="DERIVED",
        display_title="Production wiring probe",
        display_text="Production wiring probe",
        as_of=dt(),
        derivation_links=[services.DerivationLinkInput(support.id, "INPUT_FACT")],
        instrument_links=[
            services.InstrumentLinkInput(QIANGRUI_INSTRUMENT_ID, "PRIMARY_SCOPE")
        ],
        idempotency_key=f"wiring-create-{operation}",
    )

    if operation == "create":
        result = created
    else:
        exact_targets.clear()
        traversed_targets.clear()
        overrides = {}
        if operation == "replacement":
            overrides["derivation_links"] = [
                services.DerivationLinkInput(support.id, "INPUT_FACT"),
                services.DerivationLinkInput(created.id, "SUPPORTS_INFERENCE"),
            ]
        result = await services.revise_correct_evidence(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=1,
            display_text="Revised production wiring probe",
            status_changed_at=dt(day=13),
            status_changed_by_actor="IMPORTER",
            status_reason="production wiring probe",
            idempotency_key=f"wiring-revise-{operation}",
            **overrides,
        )

    assert result.id in exact_targets, (
        f"{operation}: new exact target {result.id} never supplied to production validator; "
        f"observed targets={exact_targets}, graph traversal targets={traversed_targets}"
    )
    assert result.id in traversed_targets, (
        f"{operation}: production graph traversal never checked new exact target {result.id}"
    )
