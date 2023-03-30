import pytest

from pidge.core import PidgeMappingRule


@pytest.fixture
def empty_rule() -> PidgeMappingRule:
    return {"source": "shop_raw", "target": "shop", "rules": {}}


@pytest.fixture
def empty_category_rule() -> PidgeMappingRule:
    return {"source": "shop_raw", "target": "shop", "rules": {"REWE": []}}


@pytest.fixture
def single_rule() -> PidgeMappingRule:
    return {"source": "shop_raw", "target": "shop", "rules": {"Shopping": ["REWE"]}}


@pytest.fixture
def multiple_pattern_rule() -> PidgeMappingRule:
    return {
        "source": "shop_raw",
        "target": "shop",
        "rules": {
            "Supermarket": ["REWE", "ALDI"],
        },
    }


@pytest.fixture
def multiple_rules() -> PidgeMappingRule:
    return {"source": "shop_raw", "target": "shop", "rules": {"REWE": ["REWE"], "ALDI": ["ALDI"]}}


@pytest.fixture
def exploded_rules_2_categories() -> dict[str, str]:
    return {"REWE": "REWE", "ALDI": "ALDI"}


@pytest.fixture
def exploded_rules_1_category() -> dict[str, str]:
    return {"REWE": "Supermarket", "ALDI": "Supermarket"}
