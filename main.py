"""Entry point:  python main.py   (add --sample to load demo data first)"""
import sys
from storage import DataStore


def main():
    store = DataStore("data")
    if "--sample" in sys.argv and store.customers.empty:
        from sample_data import seed
        seed(store)
    from gui import App
    App(store).mainloop()


if __name__ == "__main__":
    main()
