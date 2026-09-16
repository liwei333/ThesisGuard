from __future__ import annotations

from datetime import timedelta

import pytest
from backend.evidence import services
from backend.evidence.errors import EvidenceIdempotencyConflict
from backend.evidence.models import EvidenceSeries
from tests.test_evidence_services import (
    r1c05a_historical_replay_fields,
    verified_evidence_fact,
)

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_evidence_services",)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("status_changed_at", lambda value: value + timedelta(seconds=1)),
        ("status_changed_by_actor", lambda value: "USER"),
        ("status_change_kind", lambda value: "REVIEW_DECISION"),
        ("status_reason", lambda value: f"{value} changed"),
    ],
)
async def test_same_key_changed_initial_verification_audit_tuple_conflicts(db, field, replacement):
    historical = await verified_evidence_fact(db, key_suffix=f"independent-{field}")
    series = await db.get(EvidenceSeries, historical.evidence_series_id)
    assert series is not None
    fields = r1c05a_historical_replay_fields(historical, series)
    key = f"evidence-verified-independent-{field}"
    await db.commit()

    fields[field] = replacement(fields[field])
    with pytest.raises(EvidenceIdempotencyConflict):
        await services.create_evidence_series_version(db, **fields, idempotency_key=key)
