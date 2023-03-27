import re
from typing import TypedDict

import pandas as pd


class ColCleanRule(TypedDict):
    source: str
    target: str
    rules: dict[str, list[str]]


def explode_rules(rules: dict[str, list[str]]):
    return {
        substring: category for category, substrings in rules.items() for substring in substrings
    }


def apply_rules(content: str, exploded_rules: dict[str, str]):
    # ToDo Currently stops after first successfull rule
    # There should not be more then one rule applying but there should be some
    # robustness/errors when it happens anyways
    for substring, category in exploded_rules.items():
        if re.search(substring, content, flags=re.IGNORECASE):
            return category
    return None


def apply_clean_rule(data: pd.DataFrame, rule: ColCleanRule) -> pd.DataFrame:
    cleaned_data = data.copy()
    exploded_rules = explode_rules(rule["rules"])
    # TODO: Custom errors for invalid inputs
    # TODO: Distinguish missing sources and actual empty strings?
    cleaned_data[rule["target"]] = (
        cleaned_data[rule["source"]].fillna("").map(lambda x: apply_rules(x, exploded_rules))
    )
    return cleaned_data


def summarize_rule_gaps(data: pd.DataFrame, rule: ColCleanRule) -> pd.Series:
    return (
        data.loc[data[rule["target"]].isna(), rule["source"]]
        .fillna("MISSING_SOURCE")
        .value_counts()
    )


def summarize_target(data: pd.DataFrame, rule: ColCleanRule) -> pd.Series:
    return data[rule["target"]].fillna("NO RULE").value_counts()
