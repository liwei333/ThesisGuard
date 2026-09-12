"""Registry of all SQLAlchemy models.

Import this module to ensure all models are registered with Base metadata
before Alembic or create_all() is called.

As new domain modules are added, import their models here.
"""

from backend.instrument.models import (  # noqa: F401
    Instrument,
    InstrumentAlias,
    InstrumentRelation,
    InstrumentTag,
)
from backend.watchlist.models import WatchlistItem  # noqa: F401

# Future models will be imported here as they are added:
# from backend.research.models import ResearchPackage, ResearchModule
# ... etc.
