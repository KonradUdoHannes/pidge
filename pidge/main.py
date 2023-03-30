import panel as pn

from pidge.examples import get_fake_expenses
from pidge.ui import PidgeMapper, create_web_ui

EXAMPLE_RULE = {
    "source": "recipient",
    "target": "shop",
    "rules": {"REWE": ["REWE"], "Fast Food": ["Burger King", "KFC"]},
}


def run():
    fake_expenses = get_fake_expenses()
    mapper = PidgeMapper(fake_expenses, EXAMPLE_RULE)

    ui = create_web_ui(mapper, 500)
    pn.serve(
        ui,
        websocket_origin="*",
        port=5006,
        show=False,
    )
