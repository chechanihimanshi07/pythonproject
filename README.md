# Customer Purchase Analytics

A desktop app for a small store to record customers and purchases and see who buys most, how often, and how much.

## Features
- Add/delete customers and purchases (saved automatically to CSV in `data/`)
- Search customers; filter purchases by customer, date range, and amount range
- Per-customer purchase count, total, average, last purchase date
- **Frequent customers**: purchase count in the top quartile (minimum 2)
- **Spending comparison**: Low / Medium / High tiers and each customer's revenue share
- Three charts (save as PNG): top customers (bar), monthly trend (line + bars), tier share (pie)

## Project layout
| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `gui.py` | Tkinter interface |
| `storage.py` | CSV file handling and record management (pandas) |
| `analytics.py` | Counts, totals, filters, frequent customers, tiers (pandas + NumPy) |
| `reports.py` | Matplotlib figures |
| `validation.py` | Input validation and `ValidationError` |
| `sample_data.py` | Demo data generator |
| `tests/test_app.py` | Unit tests |

## Install and run
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py --sample          # first run with demo data
python main.py                   # normal use
```
Tkinter ships with Python on Windows/macOS. On Debian/Ubuntu: `sudo apt install python3-tk`.

## How to use
1. **Customers tab** - enter name, email, phone, click Add. Type in Search to filter. Select a row and Delete to remove (also removes their purchases).
2. **Purchases tab** - pick a customer, enter date (`YYYY-MM-DD`), item, amount, click Add. Use the filter bar and Apply/Clear.
3. **Summary tab** - choose All customers, Frequent customers, or Spending comparison.
4. **Reports tab** - pick a chart; Save as PNG to export.

Invalid input (bad email, future date, negative amount, duplicate email...) shows a warning and nothing is saved.

## Tests
```bash
python -m unittest discover -s tests
```

## Publish on GitHub
1. Create an empty repository on github.com (no README), e.g. `customer-analytics`.
2. In the project folder:
```bash
git init
git add .
git commit -m "Initial commit: customer purchase analytics app"
git branch -M main
git remote add origin https://github.com/<your-username>/customer-analytics.git
git push -u origin main
```
3. Take screenshots of the app and put them in a `screenshots/` folder, then reference them in this README.
4. Optional: add a license (GitHub > Add file > Create new file > `LICENSE`), and repository topics such as `python`, `tkinter`, `pandas`.
