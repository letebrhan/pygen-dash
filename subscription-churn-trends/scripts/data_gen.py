import os
import numpy as np
import pandas as pd
from datetime import datetime

# --- Set seed for reproducibility ---
np.random.seed(42)

# --- Output folder ---
os.makedirs('data', exist_ok=True)

# --- Constants ---
regions = ['North America', 'EMEA', 'APAC']
plans = ['Basic', 'Pro', 'Enterprise']
reasons = ['Price', 'Features', 'Support', 'Competitor', 'Other']
months = pd.date_range(end=datetime.today(), periods=12, freq='M').strftime('%Y-%m')

# --- 1. subscriptions_by_region.csv ---
sub_rows = []
for month in months:
    for region in regions:
        active_users = np.random.randint(5000, 20000)
        sub_rows.append([region, month, active_users])

pd.DataFrame(
    sub_rows, columns=['Region', 'Month', 'ActiveUsers']
).to_csv('data/subscriptions_by_region.csv', index=False)

# --- 2. monthly_subscriptions.csv ---
sub_stats = []
for month in months:
    new = np.random.randint(2000, 8000)
    churn = np.random.randint(1000, 5000)
    net = new - churn
    sub_stats.append([month, new, churn, net])

pd.DataFrame(
    sub_stats, columns=['Month', 'NewSignups', 'Churned', 'NetGrowth']
).to_csv('data/monthly_subscriptions.csv', index=False)

# --- 3. churn_reasons.csv ---
reason_rows = []
for region in regions:
    for reason in reasons:
        count = np.random.randint(100, 800)
        reason_rows.append([reason, region, count])

pd.DataFrame(
    reason_rows, columns=['Reason', 'Region', 'Count']
).to_csv('data/churn_reasons.csv', index=False)

# --- 4. plan_churn_heatmap.csv ---
heat_rows = []
for plan in plans:
    for region in regions:
        for month in months:
            churn_rate = round(np.random.uniform(0.01, 0.15), 3)
            heat_rows.append([plan, region, month, churn_rate])

pd.DataFrame(
    heat_rows, columns=['Plan', 'Region', 'Month', 'ChurnRate']
).to_csv('data/plan_churn_heatmap.csv', index=False)

print("Synthetic data generated in /data")
