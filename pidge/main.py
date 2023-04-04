import panel as pn

from pidge.examples import get_fake_expenses
from pidge.ui import PidgeMapper, create_web_ui

EXAMPLE_RULE = {
    "source": "recipient",
    "target": "expense_category",
    "rules": {"REWE": ["REWE"], "Fast Food": ["Burger King", "KFC"]},
}


def create_ui_with_sample_data():
    fake_expenses = get_fake_expenses()
    mapper = PidgeMapper(fake_expenses, EXAMPLE_RULE)

    return create_web_ui(mapper, 500)


def run():
    pn.serve(
        create_ui_with_sample_data,
        websocket_origin="*",
        port=5006,
        show=False,
    )
