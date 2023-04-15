import json
from importlib.metadata import version

import pandas as pd
import param

from ..core import apply_pidge_mapping, summarize_rule_gaps, summarize_target


class PidgeMapper(param.Parameterized):
    mapping_rule_json = param.String()
    source_column = param.String()
    target_column = param.String()
    rule_name = param.String(default="pidge_mapping", readonly=True)
    category = param.String()
    pattern = param.String()
    insert = param.Action(lambda x: x.insert_rule(), label="Insert Rule")
    reset = param.Action(lambda x: x.reset_rule(), label="Reset Rules")
    gap_summary_updated = param.Event()
    target_summary_updated = param.Event()
    input_data_updated = param.Event()
    mapped_data_updated = param.Event()
    mapping_updated = param.Event()

    def __init__(self, input_data: pd.DataFrame, rule):
        super().__init__()

        self.input_data = input_data.copy()
        self.mapping_rule_json = json.dumps(rule)

        # copy initial values as the mapping_rule dict is subject
        # to param dependencies that trigger on assignments and as such
        # gets overwritten implicitly
        init_source, init_target = self.mapping_rule["source"], self.mapping_rule["target"]

        self.source_column = init_source
        self.target_column = init_target

    @param.depends("mapping_rule_json", watch=True)
    def _parse_mapping_rule(self):
        self.mapping_rule = json.loads(self.mapping_rule_json)
        if "pidge_version" not in self.mapping_rule:
            self.mapping_rule["pidge_version"] = version("pidge")
            with param.parameterized.discard_events(self):
                self.mapping_rule_json = json.dumps(self.mapping_rule)
        self.mapping_updated = True

    @param.depends("source_column", "target_column", watch=True)
    def _update_source_target(self):
        self.mapping_rule["source"] = self.source_column
        self.mapping_rule["target"] = self.target_column
        self._serialize_rule()

    def _serialize_rule(self):
        self.mapping_rule_json = json.dumps(self.mapping_rule)

    @param.depends("_parse_mapping_rule", "input_data_updated", watch=True)
    def calc_mapped_data(self):
        self.mapped_data = apply_pidge_mapping(self.input_data, self.mapping_rule)
        self.mapped_data_updated = True

    @param.depends("calc_mapped_data", watch=True)
    def calc_rule_gaps(self):
        summary = summarize_rule_gaps(self.mapped_data, self.mapping_rule)
        summary.name = "count"
        summary.index.name = self.source_column
        self.gap_summary = summary.to_frame()
        self.gap_summary_updated = True

    @param.depends("calc_mapped_data", watch=True)
    def calc_target_summary(self):
        summary = summarize_target(self.mapped_data, self.mapping_rule)
        summary.name = "count"
        summary.index.name = self.target_column
        self.target_summary = summary.to_frame()
        self.target_summary_updated = True

    def insert_rule(self):
        if (cat := self.category) != "" and (sub := self.pattern) != "":
            if cat in self.mapping_rule["rules"]:
                if sub not in self.mapping_rule["rules"][cat]:
                    self.mapping_rule["rules"][cat].append(sub)
            else:
                self.mapping_rule["rules"][cat] = [sub]
            self._serialize_rule()

    def reset_rule(self):
        self.mapping_rule["rules"] = {}
        self._serialize_rule()
