from pathlib import Path

import panel as pn

from pidge.examples import get_fake_expenses
from pidge.ui import PidgeMapper, create_web_ui

EXAMPLE_RULE = {
    "source": "recipient",
    "target": "expense_category",
    "rules": {"REWE": ["REWE"], "Fast Food": ["Burger King", "KFC"]},
}

CSS_DIR = Path(__file__).parent / "ui" / "css"
ASSETS_DIR = Path(__file__).parent / "ui" / "assets"


def create_ui_with_sample_data():
    fake_expenses = get_fake_expenses()
    mapper = PidgeMapper(fake_expenses, EXAMPLE_RULE)

    return create_web_ui(mapper)


def run():
    pn.serve(
        create_ui_with_sample_data,
        websocket_origin="*",
        port=5006,
        show=False,
        static_dirs={"css": str(CSS_DIR.resolve()), "assets": str(ASSETS_DIR.resolve())},
    )
