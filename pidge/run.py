from pidge.dashboard import Cleaner, create_dashboard
from pidge.examples import get_fake_expenses

fake_expenses = get_fake_expenses()
rule = {"source": "recipient", "target": "shop", "rules": {}}
c = Cleaner(fake_expenses, rule)

dashboard = create_dashboard(c, 500)
dashboard.servable()
