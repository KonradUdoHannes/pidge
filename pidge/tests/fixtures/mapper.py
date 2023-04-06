import pytest

from pidge.ui.mapper import PidgeMapper


@pytest.fixture
def mapper(raw_shops, multiple_rules):
    return PidgeMapper(raw_shops, multiple_rules)


@pytest.fixture
def empty_mapper(raw_shops, multiple_rules):
    empty_expense_rule = {"source": "shop_raw", "target": "expense_type", "rules": {}}
    return PidgeMapper(raw_shops, empty_expense_rule)
