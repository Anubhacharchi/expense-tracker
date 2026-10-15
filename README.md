# Personal Expense Tracker

A simple web app to record daily expenses and see where your money goes.
Built with Python, SQLite and Streamlit.

## Features
- Add an expense with date, category, amount and an optional note
- Data is saved in an SQLite database, so it stays after you close the app
- Filter by month and category
- See total spent, number of expenses and budget left for the month
- Warning when you go over your monthly budget
- Bar chart of spending by category and line chart of spending per month
- Delete an expense by its ID
- Download the filtered expenses as a CSV file

## Tech used
Python, SQL (SQLite), Pandas, Streamlit

## How to run
1. Install Python 3.9 or newer.
2. Open a terminal in this folder and install the packages:
   `pip install -r requirements.txt`
3. Start the app:
   `streamlit run app.py`
4. Open the link shown in the terminal (usually http://localhost:8501).

## How it works
- `app.py` creates an `expenses` table in `expenses.db` the first time it runs.
- Adding an expense runs an SQL `INSERT`. Deleting runs an SQL `DELETE`.
- Pandas reads the table into a DataFrame, which is filtered and grouped
  for the summary numbers and charts.

## Ideas for the future
- User login so each person sees only their own expenses
- Edit an existing expense
- Recurring expenses (rent, subscriptions)
- Deploy online with Streamlit Community Cloud
