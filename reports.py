"""Matplotlib figures. Built with Figure (not pyplot) so they embed cleanly in Tkinter and test headless."""
from matplotlib.figure import Figure
from analytics import spending_tiers, monthly_spend


def _empty(fig, title):
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
    ax.set_title(title)
    ax.axis("off")
    return fig


def top_customers_chart(summary, n=10):
    fig, title = Figure(figsize=(7, 4.5)), "Top Customers by Total Spend"
    top = summary[summary["total_spent"] > 0].head(n)
    if top.empty:
        return _empty(fig, title)
    ax = fig.add_subplot(111)
    bars = ax.barh(top["name"][::-1], top["total_spent"][::-1], color="#3b7dd8")
    ax.bar_label(bars, fmt="%.0f", padding=3)
    ax.set(title=title, xlabel="Total spent")
    fig.tight_layout()
    return fig


def monthly_trend_chart(purchases):
    fig, title = Figure(figsize=(7, 4.5)), "Monthly Sales Trend"
    m = monthly_spend(purchases)
    if m.empty:
        return _empty(fig, title)
    ax = fig.add_subplot(111)
    ax.plot(m["month"], m["total"], marker="o", color="#2a9d8f", label="Revenue")
    ax.set(title=title, xlabel="Month", ylabel="Revenue")
    ax2 = ax.twinx()
    ax2.bar(m["month"], m["count"], alpha=0.25, color="gray", label="Purchases")
    ax2.set_ylabel("Purchases")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def spending_tier_chart(summary):
    fig, title = Figure(figsize=(7, 4.5)), "Revenue Share by Spending Tier"
    t = spending_tiers(summary)
    if t.empty:
        return _empty(fig, title)
    g = t.groupby("tier")["total_spent"].sum().reindex(["High", "Medium", "Low"]).dropna()
    counts = t.groupby("tier").size()
    ax = fig.add_subplot(111)
    ax.pie(g, labels=[f"{k} ({counts[k]} customers)" for k in g.index], autopct="%1.1f%%",
           colors=["#e76f51", "#f4a261", "#8ab17d"][:len(g)], startangle=90)
    ax.set_title(title)
    return fig


REPORTS = {
    "Top customers (bar)": lambda s, p: top_customers_chart(s),
    "Monthly sales trend (line)": lambda s, p: monthly_trend_chart(p),
    "Spending tiers (pie)": lambda s, p: spending_tier_chart(s),
}
