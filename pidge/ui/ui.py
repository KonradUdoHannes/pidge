import json
from io import StringIO
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import panel as pn
import param
from jinja2 import Environment, FileSystemLoader

from .mapper import PidgeMapper

TEMPLATE_FOLDER = Path(__file__).parent
TEMPLATE_FILE = "web_ui_template.html"

PANEL_TABS: list[tuple[str, Callable]] = []


def register_panel_tab(tab_name: str) -> Callable:
    def register_creator_function(func):
        PANEL_TABS.append((tab_name, func))
        return func

    return register_creator_function


def create_panel(mapper):

    tabs = pn.Tabs(
        css_classes=["panel-ui-box"], sizing_mode="scale_width", min_width=300, width_policy="min"
    )

    for name, creation_function in PANEL_TABS:
        tabs.append((name, creation_function(mapper)))

    return tabs


def adjust_view_widths(tabulator_view, width) -> None:
    FIRST_COL_FRACTION = 0.8
    first_width = int(FIRST_COL_FRACTION * width)
    second_width = width - first_width
    cols = tabulator_view.value.columns
    tabulator_view.widths = {"index": first_width, cols[0]: second_width}


def create_gap_view(mapper):
    gap_view = pn.widgets.Tabulator(
        value=mapper.gap_summary,
        pagination="local",
        page_size=5,
        # width=400,
        height=210,
        widths={mapper.source_column: "80%", "count": "20%"},
        selectable=1,
    )

    @param.depends(mapper.param.gap_summary_updated, watch=True)
    def update_gap_view(gap_summary_udpated):
        gap_view.value = mapper.gap_summary

    def select_as_pattern(event):
        if len(event.new) == 1:
            mapper.pattern = event.obj.selected_dataframe.index[0]

    gap_view.param.watch(select_as_pattern, "selection")

    return gap_view


def create_target_view(mapper):
    target_view = pn.widgets.Tabulator(
        value=mapper.target_summary,
        pagination="local",
        page_size=5,
        height=210,
        widths={mapper.target_column: "80%", "count": "20%"},
        selectable=1,
    )

    @param.depends(mapper.param.target_summary_updated, watch=True)
    def update_target_view(target_summary_udated):
        target_view.value = mapper.target_summary

    def select_as_category(event):
        if len(event.new) == 1:
            mapper.category = event.obj.selected_dataframe.index[0]

    target_view.param.watch(select_as_category, "selection")

    return target_view


@register_panel_tab("Mapping Controll")
def create_mapping_controls(mapper):
    @param.depends(mapper.param.mapping_updated)
    def download(mapping_updated):
        sio = StringIO()
        sio.write(json.dumps(mapper.mapping_rule))
        sio.seek(0)
        return sio

    rule_export = pn.widgets.FileDownload(callback=download, filename=f"{mapper.rule_name}.json")

    m_params = ["pattern", "category", "insert", "reset"]
    mapping_params = pn.panel(
        mapper.param,
        parameters=m_params,
        width=265,
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

    gap_view = create_gap_view(mapper)
    target_view = create_target_view(mapper)

    mapping_control = pn.FlexBox(
        pn.Column(
            mapping_params,
            rule_export,
            width=285,
        ),
        pn.Column(
            gap_table_headline,
            gap_view,
            target_overview_headline,
            target_view,
            width=285,
        ),
    )
    return mapping_control


@register_panel_tab("Input Data")
def create_input_data_view(mapper):
    input_view = pn.widgets.Tabulator(
        mapper.input_data,
        pagination="local",
        page_size=10,
        show_index=False,
        sizing_mode="stretch_width",
    )

    @param.depends(mapper.param.input_data_updated, watch=True)
    def update_input_view(input_data_updated):
        input_view.value = mapper.input_data

    return input_view


@register_panel_tab("Mapped Data")
def create_mapped_data_view(mapper):
    mapped_data_view = pn.widgets.Tabulator(
        mapper.mapped_data,
        pagination="local",
        page_size=10,
        show_index=False,
        sizing_mode="stretch_width",
    )

    @param.depends(mapper.param.mapped_data_updated, watch=True)
    def update_input_view(mapped_data_updated):
        mapped_data_view.value = mapper.mapped_data

    return mapped_data_view


@register_panel_tab("Complete Mapping Rule")
def create_rule_view(mapper):
    json_editor = pn.widgets.JSONEditor(value=mapper.mapping_rule, sizing_mode="stretch_width")

    @param.depends(mapper.param.mapping_updated, watch=True)
    def update_input_view(mapping_updated):
        json_editor.value = mapper.mapping_rule

    def update_editor_changes(event):
        mapper.mapping_rule = event.new

    json_editor.param.watch(update_editor_changes, "value")

    return json_editor


@register_panel_tab("Config")
def create_ui_config(mapper):
    data_import = pn.widgets.FileInput(accept=".csv")

    def load_input_data(event):
        s = str(event.new, "utf-8")

        virtual_data_file = StringIO(s)

        data = pd.read_csv(virtual_data_file)
        mapper.input_data = data
        mapper.source_column = get_first_string_col(data)
        mapper.input_data_updated = True

    data_import.param.watch(load_input_data, "value")
    configs = pn.Column(
        pn.panel(
            mapper.param,
            parameters=["rule_name", "source_column", "target_column"],
            name="Rule Configuration",
        ),
        data_import,
    )
    return configs


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


def create_web_ui(mapper):
    panel = create_panel(mapper)
    return insert_panel_in_template(panel)
