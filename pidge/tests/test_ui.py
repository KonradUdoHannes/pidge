import copy

import panel as pn

from pidge.examples import SAMPLE_FOLDER
from pidge.ui import create_panel, create_web_ui, pidge_ui
from pidge.ui.ui import (
    create_gap_view,
    create_input_data_view,
    create_mapped_data_view,
    create_mapping_controls,
    create_rule_view,
    create_target_view,
    create_ui_config,
    insert_panel_in_template,
)


def test_create_panel_smoke(mapper):
    panel = create_panel(mapper)
    assert isinstance(panel, pn.Tabs)


def test_insert_panel_in_template_smoke():
    insert_panel_in_template(pn.Row())


def test_create_web_ui_smoke(mapper):
    create_web_ui(mapper)


def test_pidge_ui_smoke(raw_shops):
    pidge_ui(raw_shops)


def test_create_ui_config(mapper):
    config = create_ui_config(mapper)
    with open(SAMPLE_FOLDER / "fake_expenses.csv", "rb") as f:
        config[1].value = f.read()
    assert mapper.source_column == "date"


def test_create_mapping_controls(mapper):
    mapping_control = create_mapping_controls(mapper)

    mapping_parameters = mapping_control[0][0]
    mapping_parameter_headline = mapping_parameters[0]
    pattern_label = mapping_parameters[1]
    category_label = mapping_parameters[2]

    gap_headline = mapping_control[1][0]
    assert "shop_raw" in gap_headline.object

    target_headline = mapping_control[1][2]
    assert "shop" in target_headline.object

    mapper.source_column = "shop_type"
    assert "shop_type" in gap_headline.object
    assert "shop_type" in mapping_parameter_headline.value
    assert "shop_type" in pattern_label.name

    mapper.target_column = "new_target_column"
    assert "new_target_column" in target_headline.object
    assert "new_target_column" in mapping_parameter_headline.value
    assert "new_target_column" in category_label.name


def test_create_input_data(mapper):
    inp = create_input_data_view(mapper)
    assert isinstance(inp, pn.widgets.Tabulator)


def test_create_gap_view(mapper):
    gap_view = create_gap_view(mapper)
    assert gap_view.value.index.str.contains("EDEKA", case=False).any()

    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)

    assert not gap_view.value.index.str.contains("EDEKA", case=False).any()


def test_gap_view_row_selection(mapper):
    gap_view = create_gap_view(mapper)
    assert mapper.pattern == ""
    gap_view.selection = [0]
    assert mapper.pattern == mapper.gap_summary.index[0]


def test_create_target_view(mapper):
    target_view = create_target_view(mapper)
    assert not target_view.value.index.str.contains("EDEKA", case=False).any()

    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)

    assert target_view.value.index.str.contains("EDEKA", case=False).any()


def test_target_view_row_selection(mapper):
    target_view = create_target_view(mapper)
    assert mapper.category == ""
    target_view.selection = [0]
    assert mapper.category == mapper.target_summary.index[0]


def test_create_mapped_data(mapper):
    mapped_data = create_mapped_data_view(mapper)
    assert isinstance(mapped_data, pn.widgets.Tabulator)
    assert not any(mapped_data.value[mapper.target_column] == "EDEKA")

    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)

    assert any(mapped_data.value[mapper.target_column] == "EDEKA")


def test_create_rule_view(mapper):
    export = create_rule_view(mapper)
    assert isinstance(export, pn.widgets.JSONEditor)
    assert isinstance(export.value, dict)
    assert "EDEKA" not in export.value["rules"]

    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)

    assert "EDEKA" in export.value["rules"]

    assert "REWE" in export.value["rules"]
    assert "REWE" in mapper.mapping_rule["rules"]
    mapping_copy = copy.deepcopy(export.value)
    del mapping_copy["rules"]["REWE"]
    export.value = mapping_copy
    assert "REWE" not in mapper.mapping_rule["rules"]
