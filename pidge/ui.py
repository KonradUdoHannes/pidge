import json
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import panel as pn
import param
from jinja2 import Environment, FileSystemLoader

from .core import apply_pidge_mapping, summarize_rule_gaps, summarize_target

TEMPLATE_FOLDER = Path(__file__).parent
TEMPLATE_FILE = "web_ui_template.html"


class PidgeMapper(param.Parameterized):
    mapping_rule_json = param.String()
    source_column = param.String()
    target_column = param.String()
    data_update = param.Event()
    rule_name = param.String(default="pidge_mapping", readonly=True)
    category = param.String()
    pattern = param.String()
    insert = param.Action(lambda x: x.insert_rule(), label="Insert Rule")
    reset = param.Action(lambda x: x.reset_rule(), label="Reset Rules")

    def __init__(self, input_data: pd.DataFrame, rule):
        super().__init__()

        # TODO Make private
        self.gap_view = None
        self.target_view = None

        self._input_data = input_data.copy()
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

    @param.depends("source_column", "target_column", watch=True)
    def _update_source_target(self):
        self.mapping_rule["source"] = self.source_column
        self.mapping_rule["target"] = self.target_column
        self._serialize_rule()

    def _serialize_rule(self):
        self.mapping_rule_json = json.dumps(self.mapping_rule)

    @param.depends("_parse_mapping_rule", "data_update", watch=True)
    def calc_mapped_data(self):
        self._mapped_data = apply_pidge_mapping(self._input_data, self.mapping_rule)

    @param.depends("calc_mapped_data", watch=True)
    def calc_rule_gaps(self):
        summary = summarize_rule_gaps(self._mapped_data, self.mapping_rule)
        summary.name = "count"
        summary.index.name = self.source_column
        self._gap_summary = summary.to_frame()

    @param.depends("calc_mapped_data", watch=True)
    def calc_target_summary(self):
        summary = summarize_target(self._mapped_data, self.mapping_rule)
        summary.name = "count"
        summary.index.name = self.target_column
        self._target_summary = summary.to_frame()

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

    @property
    def view_gaps(self):
        if self.gap_view is None:
            self.gap_view = pn.widgets.Tabulator(
                value=self._gap_summary,
                pagination="local",
                page_size=5,
                width=400,
                height=210,
                widths={self.source_column: "80%", "count": "20%"},
            )
        return self.gap_view

    @param.depends("calc_rule_gaps", watch=True)
    def view_update_gap(self):
        if self.gap_view is not None:
            self.gap_view.value = self._gap_summary

    @property
    def view_targets(self):
        if self.target_view is None:
            self.target_view = pn.widgets.Tabulator(
                value=self._target_summary,
                pagination="local",
                page_size=5,
                width=400,
                height=210,
                widths={self.target_column: "80%", "count": "20%"},
            )
        return self.target_view

    @param.depends("calc_target_summary", watch=True)
    def view_update_target(self):
        if self.target_view is not None:
            self.target_view.value = self._target_summary

    @param.depends("_parse_mapping_rule")
    def view_rule(self):
        return pn.pane.JSON(self.mapping_rule_json)

    @param.depends("calc_mapped_data")
    def mapped_data(self):
        return pn.widgets.Tabulator(
            self._mapped_data, pagination="local", page_size=10, show_index=False
        )

    @param.depends("data_update")
    def input_data(self):
        return pn.widgets.Tabulator(
            self._input_data, pagination="local", page_size=10, show_index=False
        )


def create_panel(mapper, width=None):
    FIRST_COL_FRACTION = 0.8

    if width is not None:
        first_width = int(FIRST_COL_FRACTION * width)
        second_width = width - first_width
        gap_cols = list(mapper.view_gaps.value.columns)
        mapper.view_gaps.widths = {"index": first_width, gap_cols[0]: second_width}

        tsum_cols = list(mapper.view_targets.value.columns)
        mapper.view_targets.widths = {"index": first_width, tsum_cols[0]: second_width}

    @param.depends(mapper.param.mapping_rule_json)
    def download(mapping_rule_json):
        sio = StringIO()
        sio.write(mapping_rule_json)
        sio.seek(0)
        return sio

    rule_export = pn.widgets.FileDownload(callback=download, filename=f"{mapper.rule_name}.json")
    data_import = pn.widgets.FileInput(accept=".csv")

    def load_input_data(event):
        s = str(event.new, "utf-8")

        virtual_data_file = StringIO(s)

        data = pd.read_csv(virtual_data_file)
        # TODO: Should not call a private attribute here.
        mapper._input_data = data
        mapper.source_column = get_first_string_col(data)
        mapper.data_update = True

    data_import.param.watch(load_input_data, "value")

    tabs = pn.Tabs()

    m_params = ["pattern", "category", "insert", "reset"]
    mapping_params = pn.panel(
        mapper.param,
        parameters=m_params,
        width=275,
        sort=lambda x: (["name"] + m_params).index(x[0]),
        name="",
    )

    mapping_params[0].style = {"font-size": "16px"}

    gap_table_headline = pn.pane.HTML()
    target_overview_headline = pn.pane.HTML()

    def insert_target_col(event):
        mapping_params[2].name = f"Target category in {event.new} col"
        target_overview_headline.object = f"<p><strong>{event.new}</strong> (target) overview</p>"
        mapping_params[0].value = f"Mapping from {event.obj.source_column} to {event.new}"

    mapper.param.watch(insert_target_col, "target_column")

    def insert_source_col(event):
        mapping_params[1].name = f"Pattern for {event.new} col"
        gap_table_headline.object = (
            f"<p><strong>{event.new} </strong> (source) values without mapping</p>"
        )
        mapping_params[0].value = f"Mapping from {event.new} to {event.obj.target_column}"

    mapper.param.watch(insert_source_col, "source_column")

    mapper.param.trigger("source_column", "target_column")

    mapping_control = pn.FlexBox(
        pn.Column(
            mapping_params,
            rule_export,
            width=300,
        ),
        pn.Column(
            gap_table_headline,
            mapper.view_gaps,
            target_overview_headline,
            mapper.view_targets,
            width=300,
        ),
    )
    mapping_view = pn.panel(mapper.view_rule)

    tabs.append(("Mapping Controll", mapping_control))

    tabs.append(("Input Data", pn.panel(mapper.input_data)))
    mapped_data = pn.panel(mapper.mapped_data)
    tabs.append(("Mapped Data", mapped_data))
    tabs.append(("Export Preview", mapping_view))
    configs = pn.Column(
        pn.panel(
            mapper.param,
            parameters=["rule_name", "source_column", "target_column"],
            name="Rule Configuration",
        ),
        data_import,
    )
    tabs.append(("Config", configs))

    return tabs


def get_first_string_col(data: pd.DataFrame) -> str:
    for col in data.columns:
        if pd.api.types.infer_dtype(data[col]) == "string":
            return col
            break
    else:
        raise ValueError("DataFrame needs a string column")


def pidge_ui(data: pd.DataFrame, source: Optional[str] = None, target: Optional[str] = None):
    empty_rule = {
        "source": source or get_first_string_col(data),
        "target": target or "target",
        "rules": {},
    }
    mapper = PidgeMapper(data, empty_rule)
    return create_panel(mapper)


def insert_panel_in_template(panel):
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
    web_ui_template = env.get_template(TEMPLATE_FILE)

    tmpl = pn.Template(web_ui_template)
    tmpl.add_panel("DASHBOARD", panel)
    return tmpl


def create_web_ui(mapper, width=None):
    panel = create_panel(mapper, width=None)
    return insert_panel_in_template(panel)
