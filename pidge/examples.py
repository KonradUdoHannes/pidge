from pathlib import Path

import pandas as pd

SAMPLE_FOLDER = Path(__file__).parent / "sample_data"


def get_fake_expenses():
    return pd.read_csv(SAMPLE_FOLDER / "fake_expenses.csv")
