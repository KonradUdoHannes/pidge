import panel as pn

from pidge.examples import get_fake_expenses
from pidge.ui import PidgeMapper, create_web_ui

EXAMPLE_RULE = {
    "source": "recipient",
    "target": "shop",
    "rules": {"REWE": ["REWE"], "Fast Food": ["Burger King", "KFC"]},
}


def create_ui_with_sample_data():
    fake_expenses = get_fake_expenses()
    mapper = PidgeMapper(fake_expenses, EXAMPLE_RULE)

    return create_web_ui(mapper, 500)


def run():
    ui = create_ui_with_sample_data()
    pn.serve(
        ui,
        websocket_origin="*",
        port=5006,
        show=False,
    )
