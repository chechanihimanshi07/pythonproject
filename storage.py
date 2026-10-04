"""Persistent storage: customers and purchases live in two CSV files, held as pandas DataFrames."""
import os
import pandas as pd
from validation import (validate_name, validate_email, validate_phone, validate_date,
                        validate_item, validate_amount, ValidationError)

CUSTOMER_COLS = ["customer_id", "name", "email", "phone"]
PURCHASE_COLS = ["purchase_id", "customer_id", "date", "item", "amount"]


class DataStore:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.cust_path = os.path.join(data_dir, "customers.csv")
        self.purch_path = os.path.join(data_dir, "purchases.csv")
        self.customers = self._load(self.cust_path, CUSTOMER_COLS)
        self.purchases = self._load(self.purch_path, PURCHASE_COLS)
        self.purchases["amount"] = pd.to_numeric(self.purchases["amount"], errors="coerce").fillna(0.0)

    @staticmethod
    def _load(path, cols):
        """Read a CSV; return an empty frame if missing or unreadable (corrupt file is backed up)."""
        if not os.path.exists(path):
            return pd.DataFrame(columns=cols)
        try:
            df = pd.read_csv(path, dtype=str).fillna("")
            if list(df.columns) != cols:
                raise ValueError("unexpected columns")
            return df
        except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError):
            os.replace(path, path + ".bak")
            return pd.DataFrame(columns=cols)

    def save(self):
        try:
            self.customers.to_csv(self.cust_path, index=False)
            self.purchases.to_csv(self.purch_path, index=False)
        except OSError as exc:
            raise IOError(f"Could not save data: {exc}")

    @staticmethod
    def _next_id(series, prefix, width):
        nums = [int(s[1:]) for s in series if s[1:].isdigit()]
        return f"{prefix}{(max(nums) if nums else 0) + 1:0{width}d}"

    def add_customer(self, name, email, phone):
        name, email, phone = validate_name(name), validate_email(email), validate_phone(phone)
        if (self.customers["email"] == email).any():
            raise ValidationError("A customer with this email already exists.")
        cid = self._next_id(self.customers["customer_id"], "C", 3)
        self.customers.loc[len(self.customers)] = [cid, name, email, phone]
        self.save()
        return cid

    def add_purchase(self, customer_id, date, item, amount):
        if customer_id not in set(self.customers["customer_id"]):
            raise ValidationError("Select an existing customer.")
        row = [validate_date(date), validate_item(item), validate_amount(amount)]
        pid = self._next_id(self.purchases["purchase_id"], "P", 4)
        self.purchases.loc[len(self.purchases)] = [pid, customer_id] + row
        self.purchases["amount"] = self.purchases["amount"].astype(float)
        self.save()
        return pid

    def delete_customer(self, customer_id):
        """Deletes the customer and their purchases."""
        if customer_id not in set(self.customers["customer_id"]):
            raise ValidationError("Customer not found.")
        self.customers = self.customers[self.customers["customer_id"] != customer_id].reset_index(drop=True)
        self.purchases = self.purchases[self.purchases["customer_id"] != customer_id].reset_index(drop=True)
        self.save()

    def delete_purchase(self, purchase_id):
        if purchase_id not in set(self.purchases["purchase_id"]):
            raise ValidationError("Purchase not found.")
        self.purchases = self.purchases[self.purchases["purchase_id"] != purchase_id].reset_index(drop=True)
        self.save()
