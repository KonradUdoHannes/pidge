from pidge.ui.mapper import PidgeMapper


def test_mapper_initilization(mapper):
    assert hasattr(mapper, "mapped_data")
    assert "shop" in mapper.mapped_data
    assert hasattr(mapper, "gap_summary")
    assert "Edeka Bockenheim" in mapper.gap_summary.index
    assert hasattr(mapper, "target_summary")
    assert "EDEKA" not in mapper.target_summary.index
    assert "ALDI" in mapper.target_summary.index
    assert "REWE" in mapper.target_summary.index


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
