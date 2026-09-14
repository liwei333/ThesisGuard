"""Registry of all SQLAlchemy models.

Import this module to ensure all models are registered with Base metadata
before Alembic or create_all() is called.

As new domain modules are added, import their models here.

此模块是模型注册中心：Alembic autogenerate 和 init_db 都依赖此处导入
来感知所有 ORM 模型。新增领域模块时必须在此补充 import，否则迁移
无法自动发现新表。
"""

from backend.instrument.models import (  # noqa: F401
    Instrument,
    InstrumentAlias,
    InstrumentRelation,
    InstrumentTag,
)
from backend.research.models import ResearchModule, ResearchPackage  # noqa: F401
from backend.watchlist.models import WatchlistItem  # noqa: F401

# Future models will be imported here as they are added:
# thesis/evidence/market 等模块的模型在实现后在此注册
# ... etc.
