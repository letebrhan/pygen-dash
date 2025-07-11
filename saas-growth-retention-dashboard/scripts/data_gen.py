import os
import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Create output folder
os.makedirs("data", exist_ok=True)

# --- Metric Summary ---
metrics = {
    "ARR": 42964810,
    "Bookings": 2019600,
    "Cash Balance": 15150500,
    "Burn Rate": 600000
}
df_metrics = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
df_metrics.to_csv("data/metrics_summary.csv", index=False)

# --- ARR Changes ---
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
arr_changes = {
    "Month": months,
    "Upgrade": np.random.randint(3_000_000, 4_000_000, size=6),
    "New": np.random.randint(2_000_000, 3_000_000, size=6),
    "Downgrade": np.random.randint(1_000_000, 2_000_000, size=6),
    "Churn": np.random.randint(1_000_000, 2_500_000, size=6),
}
df_arr = pd.DataFrame(arr_changes)
# --- Net Growth Calculation ---
df_arr['NetGrowth'] = df_arr['Upgrade'] + df_arr['New'] - df_arr['Downgrade'] - df_arr['Churn']
df_arr.to_csv("data/arr_changes.csv", index=False)

# --- Employees by Department ---
departments = [
    ("Software Engineering", 44),
    ("Sales", 20),
    ("HR", 8),
    ("Marketing", 10),
    ("Customer Support", 12),
    ("Administration", 5),
    ("Finance", 8),
    ("Product Management", 6),
    ("Legal", 4),

]
df_employees = pd.DataFrame(departments, columns=["Department", "Count"])
df_employees.to_csv("data/employees_by_dept.csv", index=False)

# --- Expenses ---
expense_months = months
expense_categories = ["R&D", "Marketing", "Ops"]
data = {
    "Month": expense_months
}
for cat in expense_categories:
    data[cat] = np.random.uniform(100_000, 6_000_000, size=6)
df_expenses = pd.DataFrame(data)
df_expenses.to_csv("data/expenses.csv", index=False)

# --- Cohort Retention ---
cohorts = ['Nov 21', 'Dec 21', 'Jan 22', 'Feb 22', 'Mar 22', 'Apr 22']
retention_data = []
for cohort in cohorts:
    base = 100
    row = [base]
    for i in range(1, 6):
        decay = np.random.randint(80, 100)
        row.append(min(decay, row[-1]))  # ensure monotonic drop
    retention_data.append([cohort] + row)

df_cohort = pd.DataFrame(retention_data, columns=['Cohort', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'])
df_cohort.to_csv("data/cohort_retention.csv", index=False)

print("All synthetic CSVs generated in /data/")
