"""WP-02 Instrument and Watchlist behavior tests.

验证标的搜索和自选池分类的核心业务逻辑：
1. 内置目录搜索支持代码和中文名
2. 301128（强瑞技术）分类为 INSTITUTIONAL_TREND，关注订单和利润验证
3. 000722（湖南发展）分类为 HOT_MONEY，关注梯队和情绪周期
"""

from backend.instrument.services import search_catalog
from backend.watchlist.services import classify_instrument


def test_catalog_search_finds_qiangrui_by_symbol() -> None:
    """User can search the WP-02 acceptance stock by code."""
    results = search_catalog("301128")

    assert results
    assert results[0].symbol == "301128"
    assert results[0].name == "强瑞技术"


def test_catalog_search_finds_qiangrui_by_name() -> None:
    """User can search the WP-02 acceptance stock by Chinese name."""
    results = search_catalog("强瑞")

    assert results
    assert results[0].symbol == "301128"


def test_watchlist_classifies_qiangrui_as_institutional_trend() -> None:
    """301128 should get an explainable institutional-trend classification."""
    instrument = search_catalog("301128")[0]

    result = classify_instrument(instrument)

    assert result.classification == "INSTITUTIONAL_TREND"
    assert result.confidence == 82
    assert "订单" in result.reason
    assert "利润" in result.reason


def test_watchlist_classifies_hot_money_example() -> None:
    """Hot-money examples should not be forced into a PE-driven model."""
    instrument = search_catalog("湖南发展")[0]

    result = classify_instrument(instrument)

    assert result.classification == "HOT_MONEY"
    assert "梯队" in result.reason
