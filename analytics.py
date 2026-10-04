"""Customer-level calculations using pandas for tables and NumPy for statistics."""
import numpy as np
import pandas as pd


def search_customers(customers, text):
    """Case-insensitive match on id, name, email or phone."""
    text = (text or "").strip().lower()
    if not text:
        return customers
    mask = customers.apply(lambda r: text in " ".join(r.astype(str)).lower(), axis=1)
    return customers[mask]


def filter_purchases(purchases, customer_id=None, start=None, end=None, min_amount=None, max_amount=None):
    df = purchases
    if customer_id:
        df = df[df["customer_id"] == customer_id]
    if start:
        df = df[df["date"] >= start]
    if end:
        df = df[df["date"] <= end]
    if min_amount is not None:
        df = df[df["amount"] >= min_amount]
    if max_amount is not None:
        df = df[df["amount"] <= max_amount]
    return df


def customer_summary(customers, purchases):
    """One row per customer: purchase count, total, average, last purchase (zeros if none)."""
    agg = purchases.groupby("customer_id").agg(
        purchase_count=("amount", "size"), total_spent=("amount", "sum"),
        avg_purchase=("amount", "mean"), last_purchase=("date", "max")).reset_index()
    out = customers[["customer_id", "name"]].merge(agg, on="customer_id", how="left")
    out["purchase_count"] = out["purchase_count"].fillna(0).astype(int)
    out[["total_spent", "avg_purchase"]] = out[["total_spent", "avg_purchase"]].fillna(0.0)
    out["last_purchase"] = out["last_purchase"].fillna("-")
    return out.round(2).sort_values(["total_spent", "name"], ascending=[False, True]).reset_index(drop=True)


def frequent_customers(summary, min_purchases=None):
    """Customers at/above a purchase-count threshold (default: 75th percentile, minimum 2)."""
    buyers = summary[summary["purchase_count"] > 0]
    if buyers.empty:
        return buyers
    if min_purchases is None:
        min_purchases = max(2, int(np.ceil(np.percentile(buyers["purchase_count"].to_numpy(), 75))))
    return buyers[buyers["purchase_count"] >= min_purchases]


def spending_tiers(summary):
    """Compare spending: Low/Medium/High tiers by tertiles, plus each customer's share of revenue."""
    buyers = summary[summary["total_spent"] > 0].copy()
    if buyers.empty:
        return buyers.assign(tier=pd.Series(dtype=str), revenue_share_pct=pd.Series(dtype=float))
    lo, hi = np.percentile(buyers["total_spent"].to_numpy(), [100 / 3, 200 / 3])
    buyers["tier"] = np.select([buyers["total_spent"] <= lo, buyers["total_spent"] <= hi],
                               ["Low", "Medium"], default="High")
    buyers["revenue_share_pct"] = (buyers["total_spent"] / buyers["total_spent"].sum() * 100).round(1)
    return buyers


def monthly_spend(purchases):
    """Total spend and purchase count per month (YYYY-MM)."""
    if purchases.empty:
        return pd.DataFrame(columns=["month", "total", "count"])
    m = purchases.assign(month=purchases["date"].str[:7])
    return m.groupby("month")["amount"].agg(total="sum", count="size").reset_index().sort_values("month")
