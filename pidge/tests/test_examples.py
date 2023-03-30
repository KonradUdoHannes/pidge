import pandas as pd

from pidge.examples import get_fake_expenses


def test_get_fake_expenses_smoke():
    expenses = get_fake_expenses()
    assert isinstance(expenses, pd.DataFrame)
