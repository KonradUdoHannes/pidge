import json

from pidge.core import (
    apply_pidge_mapping,
    apply_rules,
    explode_rules,
    pidge,
    summarize_rule_gaps,
    summarize_target,
)


def test_explode_empty_rule(empty_rule):
    assert len(explode_rules(empty_rule["rules"])) == 0


def test_explode_empty_cat(empty_category_rule):
    assert len(explode_rules(empty_category_rule["rules"])) == 0


def test_explode_single_rule(single_rule):
    exploded_rules = explode_rules(single_rule["rules"])
    assert len(exploded_rules) == 1
    category = next(iter(single_rule["rules"].keys()))
    pattern = single_rule["rules"][category][0]
    assert pattern in exploded_rules
    assert exploded_rules[pattern] == category


def test_explode_multiple_rules(multiple_rules):
    rules = multiple_rules["rules"]
    exploded_rules = explode_rules(rules)
    assert sum(len(patterns) for patterns in rules.values()) == len(exploded_rules)


def test_explode_multiple_pattern_rule(multiple_pattern_rule):
    rules = multiple_pattern_rule["rules"]
    exploded_rules = explode_rules(rules)
    assert sum(len(patterns) for patterns in rules.values()) == len(exploded_rules)


def test_apply_rules_2_cat(exploded_rules_2_categories):
    assert apply_rules("REWE Nordend", exploded_rules_2_categories) == "REWE"
    assert apply_rules("aldi Westend", exploded_rules_2_categories) == "ALDI"
    assert apply_rules("Edeka Ostend", exploded_rules_2_categories) is None


def test_apply_rules_1_cat(exploded_rules_1_category):
    assert apply_rules("REWE Nordend", exploded_rules_1_category) == "Supermarket"
    assert apply_rules("aldi Westend", exploded_rules_1_category) == "Supermarket"
    assert apply_rules("Edeka Ostend", exploded_rules_1_category) is None


def test_apply_pidge_mapping(raw_shops, multiple_rules):
    raw_shops_backup = raw_shops.copy()
    cleaned_shops = apply_pidge_mapping(raw_shops, multiple_rules)
    assert raw_shops_backup.equals(raw_shops)
    assert multiple_rules["target"] in cleaned_shops
    assert "REWE" in cleaned_shops[multiple_rules["target"]].values
    assert "ALDI" in cleaned_shops[multiple_rules["target"]].values
    assert cleaned_shops[multiple_rules["target"]].isna().any()

    multiple_rules["target"] = "shops_2"
    cleaned_shops = apply_pidge_mapping(raw_shops, multiple_rules)
    assert "shops_2" in cleaned_shops


def test_pidge_with_dict(raw_shops, multiple_rules):
    cleaned_shops1 = apply_pidge_mapping(raw_shops, multiple_rules)
    cleaned_shops2 = pidge(raw_shops, rule=multiple_rules)
    assert cleaned_shops1.equals(cleaned_shops2)


def test_pidge_with_file(raw_shops, multiple_rules, tmp_path):
    rule_file = tmp_path / "rule.json"
    with open(rule_file, "w") as f:
        json.dump(multiple_rules, f)

    cleaned_shops1 = apply_pidge_mapping(raw_shops, multiple_rules)
    cleaned_shops2 = pidge(raw_shops, rule_file=rule_file)
    assert cleaned_shops1.equals(cleaned_shops2)


def test_summarize_rule_gaps(cleaned_shops, multiple_rules):
    summary = summarize_rule_gaps(cleaned_shops, multiple_rules)
    assert "MISSING_SOURCE" in summary
    assert "Edeka Bockenheim" in summary


def test_summarize_target(cleaned_shops, multiple_rules):
    summary = summarize_target(cleaned_shops, multiple_rules)
    assert "REWE" in summary
    assert "ALDI" in summary
