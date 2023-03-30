import panel as pn
import pytest

from pidge.ui import PidgeMapper, create_panel, create_web_ui, insert_panel_in_template


@pytest.fixture
def mapper(raw_shops, multiple_rules):
    return PidgeMapper(raw_shops, multiple_rules)


@pytest.fixture
def empty_mapper(raw_shops, multiple_rules):
    empty_expense_rule = {"source": "shop_raw", "target": "expense_type", "rules": {}}
    return PidgeMapper(raw_shops, empty_expense_rule)


def test_mapper_initilization(mapper):
    assert hasattr(mapper, "_mapped_data")
    assert "shop" in mapper._mapped_data
    assert hasattr(mapper, "_gap_summary")
    assert "Edeka Bockenheim" in mapper._gap_summary
    assert hasattr(mapper, "_target_summary")
    assert "EDEKA" not in mapper._target_summary
    assert "ALDI" in mapper._target_summary
    assert "REWE" in mapper._target_summary
    assert mapper.gap_view is None
    assert mapper.target_view is None


def test_mapper_insert(mapper):
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)
    assert "Edeka Bockenheim" not in mapper._gap_summary
    assert "EDEKA" in mapper._target_summary


def test_multi_insert(empty_mapper):
    empty_mapper.category = "Supermarket"
    empty_mapper.pattern = "EDEKA"
    PidgeMapper.insert(empty_mapper)

    assert len(empty_mapper.mapping_rule["rules"]["Supermarket"]) == 1

    # prevent duplcate inserts
    PidgeMapper.insert(empty_mapper)
    assert len(empty_mapper.mapping_rule["rules"]["Supermarket"]) == 1

    # allow multiple inserts
    empty_mapper.category = "Supermarket"
    empty_mapper.pattern = "REWE"
    PidgeMapper.insert(empty_mapper)

    assert len(empty_mapper.mapping_rule["rules"]["Supermarket"]) == 2
    assert not empty_mapper._gap_summary.index.str.contains("Edeka", case=False).any()
    assert not empty_mapper._gap_summary.index.str.contains("Rewe", case=False).any()
    assert "Supermarket" in empty_mapper._target_summary


def test_views(mapper):
    assert isinstance(mapper.view_gaps, pn.widgets.Tabulator)
    assert isinstance(mapper.gap_view, pn.widgets.Tabulator)
    assert isinstance(mapper.view_targets, pn.widgets.Tabulator)
    assert isinstance(mapper.target_view, pn.widgets.Tabulator)
    json_widget = mapper.view_rule()
    assert isinstance(json_widget, pn.pane.JSON)
    assert json_widget.object == mapper.mapping_rule_json

    assert mapper.view_gaps.value.equals(mapper._gap_summary.to_frame())
    assert mapper.view_targets.value.equals(mapper._target_summary.to_frame())
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)

    assert mapper.view_gaps.value.equals(mapper._gap_summary.to_frame())
    assert mapper.view_targets.value.equals(mapper._target_summary.to_frame())


def test_create_panel_smoke(mapper):
    panel = create_panel(mapper)
    assert isinstance(panel, pn.Tabs)

    create_panel(mapper, width=500)


def test_insert_panel_in_template_smoke():
    insert_panel_in_template(pn.Row())


def test_create_web_ui_smoke(mapper):
    create_web_ui(mapper)
