import json

import pandas as pd
import panel as pn
import param

from .core import apply_clean_rule, summarize_rule_gaps, summarize_target


class Cleaner(param.Parameterized):
    cleaning_rule_json = param.String()
    category = param.String()
    substring = param.String()
    insert = param.Action(lambda x: x.insert_rule(), label="Insert Rule")

    def __init__(self, raw_data: pd.DataFrame, rule):
        super().__init__()

        # TODO Make private
        self.gap_view = None
        self.target_view = None

        self._raw_data = raw_data.copy()
        self.cleaning_rule_json = json.dumps(rule)

    @param.depends("cleaning_rule_json", watch=True)
    def _parse_cleaning_rule(self):
        self.cleaning_rule = json.loads(self.cleaning_rule_json)

    def _serialize_rule(self):
        self.cleaning_rule_json = json.dumps(self.cleaning_rule)

    @param.depends("_parse_cleaning_rule", watch=True)
    def calc_cleaned_data(self):
        self._cleaned_data = apply_clean_rule(self._raw_data, self.cleaning_rule)

    @param.depends("calc_cleaned_data", watch=True)
    def calc_rule_gaps(self):
        self._gap_summary = summarize_rule_gaps(self._cleaned_data, self.cleaning_rule)

    @param.depends("calc_cleaned_data", watch=True)
    def calc_target_summary(self):
        self._target_summary = summarize_target(self._cleaned_data, self.cleaning_rule)

    def insert_rule(self):
        if (cat := self.category) != "" and (sub := self.substring) != "":
            if cat in self.cleaning_rule["rules"]:
                if sub not in self.cleaning_rule["rules"][cat]:
                    self.cleaning_rule["rules"][cat].append(sub)
            else:
                self.cleaning_rule["rules"][cat] = [sub]
            self._serialize_rule()

    @property
    def view_gaps(self):
        if self.gap_view is None:
            self.gap_view = pn.widgets.Tabulator(
                value=self._gap_summary.to_frame(), pagination="local", page_size=5
            )
        return self.gap_view

    @param.depends("calc_rule_gaps", watch=True)
    def view_update_gap(self):
        if self.gap_view is not None:
            self.gap_view.value = self._gap_summary.to_frame()

    @property
    def view_targets(self):
        if self.target_view is None:
            self.target_view = pn.widgets.Tabulator(
                value=self._target_summary.to_frame(), pagination="local", page_size=5
            )
        return self.target_view

    @param.depends("calc_target_summary", watch=True)
    def view_update_target(self):
        if self.target_view is not None:
            self.target_view.value = self._target_summary.to_frame()

    @param.depends("_parse_cleaning_rule")
    def view_rule(self):
        return pn.pane.JSON(self.cleaning_rule_json)


def create_dashboard(cleaner, width=None):
    FIRST_COL_FRACTION = 0.8

    if width is not None:
        first_width = int(FIRST_COL_FRACTION * width)
        second_width = width - first_width
        gap_cols = list(cleaner.view_gaps.value.columns)
        cleaner.view_gaps.widths = {"index": first_width, gap_cols[0]: second_width}

        tsum_cols = list(cleaner.view_targets.value.columns)
        cleaner.view_targets.widths = {"index": first_width, tsum_cols[0]: second_width}
    return pn.Row(
        pn.Column(cleaner.view_gaps, cleaner.view_targets),
        pn.Column(
            pn.panel(cleaner.param, parameters=["category", "substring", "insert"]),
            cleaner.view_rule,
        ),
        height=500,
    )
