"""Personal Expense Tracker - a simple Streamlit app backed by SQLite."""
import sqlite3
from contextlib import closing
from datetime import date

import pandas as pd
import streamlit as st

DB_FILE = "expenses.db"
CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Health", "Education", "Other"]


# ---------- Database functions (plain SQL) ----------
def run_query(sql, params=()):
    """Open the database, run one SQL statement, save the change, close."""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.execute(sql, params)
        conn.commit()


def init_db():
    run_query(
        """CREATE TABLE IF NOT EXISTS expenses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               spent_on TEXT NOT NULL,
               category TEXT NOT NULL,
               amount REAL NOT NULL CHECK (amount > 0),
               note TEXT
           )"""
    )


def add_expense(spent_on, category, amount, note):
    run_query(
        "INSERT INTO expenses (spent_on, category, amount, note) VALUES (?, ?, ?, ?)",
        (str(spent_on), category, amount, note),
    )


def delete_expense(expense_id):
    run_query("DELETE FROM expenses WHERE id = ?", (expense_id,))


def load_expenses():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        return pd.read_sql_query(
            "SELECT id, spent_on, category, amount, note FROM expenses "
            "ORDER BY spent_on DESC, id DESC",
            conn,
        )


# ---------- Page setup ----------
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")
init_db()
st.title("Personal Expense Tracker")
st.caption("Add your daily expenses, then see where your money goes.")

# ---------- Sidebar: add expense and set budget ----------
with st.sidebar:
    st.header("Add an expense")
    with st.form("add_form", clear_on_submit=True):
        spent_on = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", CATEGORIES)
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add expense")

    if submitted:
        if amount <= 0:
            st.error("Amount must be more than 0.")
        else:
            add_expense(spent_on, category, amount, note)
            st.success("Expense added!")

    st.divider()
    budget = st.number_input("Monthly budget (₹)", min_value=0.0, value=10000.0, step=500.0)

# ---------- Load data ----------
df = load_expenses()
if df.empty:
    st.info("No expenses yet. Add your first one from the sidebar.")
    st.stop()

df["spent_on"] = pd.to_datetime(df["spent_on"])
df["month"] = df["spent_on"].dt.strftime("%Y-%m")

# ---------- Filters ----------
col_a, col_b = st.columns(2)
month = col_a.selectbox("Month", sorted(df["month"].unique(), reverse=True))
chosen = col_b.multiselect("Categories", CATEGORIES, default=CATEGORIES)

month_total = df[df["month"] == month]["amount"].sum()
view = df[(df["month"] == month) & (df["category"].isin(chosen))]

# ---------- Summary numbers ----------
m1, m2, m3 = st.columns(3)
m1.metric("Spent (selected)", f"₹{view['amount'].sum():,.0f}")
m2.metric("Number of expenses", len(view))
m3.metric("Budget left this month", f"₹{budget - month_total:,.0f}")
if budget and month_total > budget:
    st.warning(f"You are over your budget by ₹{month_total - budget:,.0f} this month.")

# ---------- Charts ----------
left, right = st.columns(2)
with left:
    st.subheader("Spending by category")
    st.bar_chart(view.groupby("category")["amount"].sum())
with right:
    st.subheader("Total spending per month")
    st.line_chart(df.groupby("month")["amount"].sum())

# ---------- Table, delete and download ----------
st.subheader("All expenses")
table = view[["id", "spent_on", "category", "amount", "note"]].copy()
table["spent_on"] = table["spent_on"].dt.date
st.dataframe(table, width="stretch", hide_index=True)

d1, d2 = st.columns(2)
with d1:
    delete_id = st.number_input("Expense ID to delete", min_value=0, step=1)
    if st.button("Delete expense"):
        delete_expense(int(delete_id))
        st.rerun()
with d2:
    st.download_button("Download as CSV", table.to_csv(index=False), "expenses.csv", "text/csv")
