import json
import re
from typing import Optional, TypedDict

import pandas as pd


class PidgeMappingRule(TypedDict):
    source: str
    target: str
    rules: dict[str, list[str]]


def explode_rules(rules: dict[str, list[str]]):
    return {pattern: category for category, patterns in rules.items() for pattern in patterns}


def apply_rules(content: str, exploded_rules: dict[str, str]):
    # ToDo Currently stops after first successfull rule
    # There should not be more then one rule applying but there should be some
    # robustness/errors when it happens anyways
    for pattern, category in exploded_rules.items():
        if re.search(pattern, content, flags=re.IGNORECASE):
            return category
    return None


def apply_pidge_mapping(data: pd.DataFrame, rule: PidgeMappingRule) -> pd.DataFrame:
    data_with_mapping_result = data.copy()
    exploded_rules = explode_rules(rule["rules"])
    # TODO: Custom errors for invalid inputs
    # TODO: Distinguish missing sources and actual empty strings?
    data_with_mapping_result[rule["target"]] = (
        data_with_mapping_result[rule["source"]]
        .fillna("")
        .map(lambda x: apply_rules(x, exploded_rules))
    )
    return data_with_mapping_result


def pidge(
    data: pd.DataFrame, rule: Optional[PidgeMappingRule] = None, rule_file=None
) -> pd.DataFrame:
    if rule is None and rule_file is None:
        raise ValueError("Either  rule or rule_file need to be provided")
    if rule is None:
        with open(rule_file, "r") as f:
            rule = json.load(f)
    return apply_pidge_mapping(data, rule)


def summarize_rule_gaps(data: pd.DataFrame, rule: PidgeMappingRule) -> pd.Series:
    return (
        data.loc[data[rule["target"]].isna(), rule["source"]]
        .fillna("MISSING_SOURCE")
        .value_counts()
    )


def summarize_target(data: pd.DataFrame, rule: PidgeMappingRule) -> pd.Series:
    return data[rule["target"]].fillna("NO RULE").value_counts()
