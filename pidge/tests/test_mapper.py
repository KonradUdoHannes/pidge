from contextlib import contextmanager

from pidge.ui.mapper import PidgeMapper


@contextmanager
def assert_value_changed_once(p, name):
    assertion_state = {"change_counter": 0}

    def inc(*args, **kwargs):
        assertion_state["change_counter"] += 1

    p.param.watch_values(inc, [name])

    yield
    assert_error = "Value did not change exactly once"

    assert assertion_state["change_counter"] == 1, assert_error


def test_mapper_initilization(mapper):
    assert hasattr(mapper, "mapped_data")
    assert "shop" in mapper.mapped_data
    assert hasattr(mapper, "gap_summary")
    assert "Edeka Bockenheim" in mapper.gap_summary.index
    assert hasattr(mapper, "target_summary")
    assert "EDEKA" not in mapper.target_summary.index
    assert "ALDI" in mapper.target_summary.index
    assert "REWE" in mapper.target_summary.index
    assert "pidge_version" in mapper.mapping_rule


def test_pidge_version_on_rule_reset(mapper):
    assert "pidge_version" in mapper.mapping_rule
    mapper.reset_rule()
    assert "pidge_version" in mapper.mapping_rule


def test_mapper_insert(mapper):
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"
    mapper.insert(mapper)
    assert "Edeka Bockenheim" not in mapper.gap_summary.index
    assert "EDEKA" in mapper.target_summary.index


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
    assert not empty_mapper.gap_summary.index.str.contains("Edeka", case=False).any()
    assert not empty_mapper.gap_summary.index.str.contains("Rewe", case=False).any()
    assert "Supermarket" in empty_mapper.target_summary.index


def test_insert_triggers_gap_updated(mapper):
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"

    with assert_value_changed_once(mapper, "gap_summary_updated"):
        mapper.insert(mapper)


def test_insert_triggers_target_updated(mapper):
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"

    with assert_value_changed_once(mapper, "target_summary_updated"):
        mapper.insert(mapper)


def test_insert_triggers_mapped_data_updated(mapper):
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"

    with assert_value_changed_once(mapper, "mapped_data_updated"):
        mapper.insert(mapper)


def test_insert_triggers_mapping_rule_updated(mapper):
    mapper.category = "EDEKA"
    mapper.pattern = "EDEKA"

    with assert_value_changed_once(mapper, "mapping_updated"):
        mapper.insert(mapper)
