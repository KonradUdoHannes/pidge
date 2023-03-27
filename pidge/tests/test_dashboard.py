import panel as pn
import pytest

from pidge.dashboard import Cleaner


@pytest.fixture
def cleaner(raw_shops, multiple_rules):
    return Cleaner(raw_shops, multiple_rules)


def test_cleaner_initilization(cleaner):
    # assert cleaner.cleaning_rule_json
    assert hasattr(cleaner, "_cleaned_data")
    assert "shop" in cleaner._cleaned_data
    assert hasattr(cleaner, "_gap_summary")
    assert "Edeka Bockenheim" in cleaner._gap_summary
    assert hasattr(cleaner, "_target_summary")
    assert "EDEKA" not in cleaner._target_summary
    assert "ALDI" in cleaner._target_summary
    assert "REWE" in cleaner._target_summary
    assert cleaner.gap_view is None
    assert cleaner.target_view is None


def test_cleaner_insert(cleaner):
    cleaner.category = "EDEKA"
    cleaner.substring = "EDEKA"
    cleaner.insert(cleaner)
    assert "Edeka Bockenheim" not in cleaner._gap_summary
    assert "EDEKA" in cleaner._target_summary


def test_views(cleaner):
    assert isinstance(cleaner.view_gaps, pn.widgets.Tabulator)
    assert isinstance(cleaner.gap_view, pn.widgets.Tabulator)
    assert isinstance(cleaner.view_targets, pn.widgets.Tabulator)
    assert isinstance(cleaner.target_view, pn.widgets.Tabulator)
    json_widget = cleaner.view_rule()
    assert isinstance(json_widget, pn.pane.JSON)
    assert json_widget.object == cleaner.cleaning_rule_json

    assert cleaner.view_gaps.value.equals(cleaner._gap_summary.to_frame())
    assert cleaner.view_targets.value.equals(cleaner._target_summary.to_frame())
    cleaner.category = "EDEKA"
    cleaner.substring = "EDEKA"
    cleaner.insert(cleaner)

    assert cleaner.view_gaps.value.equals(cleaner._gap_summary.to_frame())
    assert cleaner.view_targets.value.equals(cleaner._target_summary.to_frame())
