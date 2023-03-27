import pandas as pd
import pytest


@pytest.fixture
def raw_shops():
    """Unlcean shop names containing distrcits."""
    return pd.DataFrame(
        {
            "shop_raw": [
                "REWE Nordend",
                "REWE Westend",
                "REWE Bornheim",
                "ALDI Bornheim",
                "Aldi Hausen",
                "Edeka Bockenheim",
                None,
            ]
        }
    )


@pytest.fixture
def cleaned_shops():
    """Unlcean shop names containing distrcits."""
    return pd.DataFrame(
        {
            "shop_raw": [
                "REWE Nordend",
                "REWE Westend",
                "REWE Bornheim",
                "ALDI Bornheim",
                "Aldi Hausen",
                "Edeka Bockenheim",
                None,
            ],
            "shop": ["REWE", "REWE", "REWE", "ALDI", "ALDI", None, None],
        }
    )
