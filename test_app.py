import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import analytics as an
import reports
from storage import DataStore
from validation import ValidationError, validate_amount, validate_date, validate_email, validate_phone


class ValidationTests(unittest.TestCase):
    def test_bad_inputs(self):
        for fn, bad in [(validate_email, "nope"), (validate_phone, "12ab"), (validate_date, "2020/01/01"),
                        (validate_date, "2999-01-01"), (validate_amount, "-5"), (validate_amount, "abc")]:
            with self.assertRaises(ValidationError):
                fn(bad)

    def test_good_inputs(self):
        self.assertEqual(validate_amount("12.345"), 12.35 if False else round(12.345, 2))
        self.assertEqual(validate_email(" A@B.com "), "a@b.com")


class DataTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.s = DataStore(self.tmp.name)
        self.a = self.s.add_customer("Asha Patel", "asha@x.com", "9876543210")
        self.b = self.s.add_customer("Ravi Shah", "ravi@x.com", "9876543211")
        self.c = self.s.add_customer("Zed Idle", "zed@x.com", "9876543212")
        for amt in (100, 200, 300):
            self.s.add_purchase(self.a, "2025-01-10", "Pen", amt)
        self.s.add_purchase(self.b, "2025-02-10", "Lamp", 50)

    def tearDown(self):
        self.tmp.cleanup()

    def test_persistence(self):
        s2 = DataStore(self.tmp.name)
        self.assertEqual(len(s2.customers), 3)
        self.assertEqual(s2.purchases["amount"].sum(), 650)

    def test_duplicate_email_and_unknown_customer(self):
        with self.assertRaises(ValidationError):
            self.s.add_customer("Other", "asha@x.com", "9876543299")
        with self.assertRaises(ValidationError):
            self.s.add_purchase("C999", "2025-01-01", "x", 5)

    def test_summary_counts_totals(self):
        sm = an.customer_summary(self.s.customers, self.s.purchases).set_index("customer_id")
        self.assertEqual(sm.loc[self.a, "purchase_count"], 3)
        self.assertEqual(sm.loc[self.a, "total_spent"], 600)
        self.assertEqual(sm.loc[self.c, "purchase_count"], 0)

    def test_frequent_and_tiers(self):
        sm = an.customer_summary(self.s.customers, self.s.purchases)
        self.assertEqual(list(an.frequent_customers(sm)["customer_id"]), [self.a])
        t = an.spending_tiers(sm)
        self.assertAlmostEqual(t["revenue_share_pct"].sum(), 100, delta=0.2)

    def test_search_and_filter(self):
        self.assertEqual(len(an.search_customers(self.s.customers, "ravi")), 1)
        f = an.filter_purchases(self.s.purchases, customer_id=self.a, min_amount=150)
        self.assertEqual(len(f), 2)

    def test_delete_customer_cascades(self):
        self.s.delete_customer(self.a)
        self.assertNotIn(self.a, set(self.s.purchases["customer_id"]))

    def test_corrupt_file_recovered(self):
        with open(self.s.cust_path, "w") as f:
            f.write("garbage,only\n1,2\n")
        self.assertTrue(DataStore(self.tmp.name).customers.empty)

    def test_reports_build(self):
        sm = an.customer_summary(self.s.customers, self.s.purchases)
        for build in reports.REPORTS.values():
            self.assertTrue(build(sm, self.s.purchases).axes)
        empty = DataStore(tempfile.mkdtemp())
        esm = an.customer_summary(empty.customers, empty.purchases)
        for build in reports.REPORTS.values():
            build(esm, empty.purchases)


if __name__ == "__main__":
    unittest.main()
