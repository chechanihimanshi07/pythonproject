"""Fill a DataStore with demo data:  python sample_data.py"""
import random
from datetime import date, timedelta
from storage import DataStore

NAMES = ["Asha Patel", "Ravi Shah", "Meera Joshi", "Karan Mehta", "Nisha Desai", "Vikram Rao", "Pooja Nair", "Imran Khan"]
ITEMS = ["Notebook", "Pen set", "Backpack", "Lamp", "Headphones", "Water bottle", "Desk mat"]


def seed(store, seed_value=1):
    rnd = random.Random(seed_value)
    for i, n in enumerate(NAMES):
        cid = store.add_customer(n, f"{n.split()[0].lower()}@example.com", f"98765{43210 + i}")
        for _ in range(rnd.randint(0, 9)):
            d = date.today() - timedelta(days=rnd.randint(1, 180))
            store.add_purchase(cid, d.isoformat(), rnd.choice(ITEMS), rnd.randint(150, 4000))


if __name__ == "__main__":
    s = DataStore()
    if s.customers.empty:
        seed(s)
        print("Sample data created in ./data")
    else:
        print("Data already exists; nothing changed.")
