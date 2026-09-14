"""Registry of all SQLAlchemy models.

Import this module to ensure all models are registered with Base metadata
before Alembic or create_all() is called.

As new domain modules are added, import their models here.
"""

from backend.evidence.models import (  # noqa: F401
    EvidenceAuditEvent,
    EvidenceCorroborationLink,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceInstrumentLink,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    SourceDocument,
    SourceDocumentVersion,
)
from backend.instrument.models import (  # noqa: F401
    Instrument,
    InstrumentAlias,
    InstrumentRelation,
    InstrumentTag,
)
from backend.research.models import ResearchModule, ResearchPackage  # noqa: F401
from backend.watchlist.models import WatchlistItem  # noqa: F401
