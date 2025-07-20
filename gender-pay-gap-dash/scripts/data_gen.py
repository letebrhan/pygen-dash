import os
import pandas as pd
import numpy as np
import itertools

# Set seed for reproducibility
np.random.seed(42)

# Create data directory
os.makedirs("data", exist_ok=True)

# Ireland companies and years
companies = ["Ryanair", "New Look", "Odeon", "Northern Trust"]

# Constants
years = [2022, 2023]
metrics = ["Mean Hourly Pay", "Median Hourly Pay", "Mean Bonus Pay", "Median Bonus Pay"]
quartiles = ["Q4 - Lower", "Q3 - Lower Mid", "Q2 - Upper Mid", "Q1 - Upper"]

# Salary and bonus assumptions
quartile_salaries = {
    "Q4 - Lower": 25000,
    "Q3 - Lower Mid": 35000,
    "Q2 - Upper Mid": 45000,
    "Q1 - Upper": 60000
}
quartile_bonuses = {
    "Q4 - Lower": 500,
    "Q3 - Lower Mid": 800,
    "Q2 - Upper Mid": 1200,
    "Q1 - Upper": 2000
}

# Update the quartile percentages for Ryanair and Odeon according to the sample values for 2022 and 2023 
# Displayed on page https://genderpaygap.pythonanywhere.com/  (Ireland Gender Pay Gap Analysis)
ryanair_dist = {
    "Q4 - Lower": (89, 11),
    "Q3 - Lower Mid": (48, 52),
    "Q2 - Upper Mid": (60, 40),
    "Q1 - Upper": (70, 30)
}
odeon_dist = {
    "Q1 - Upper": (50, 50),
    "Q2 - Upper Mid": (62, 38),
    "Q3 - Lower Mid": (59, 41),
    "Q4 - Lower": (56, 44)
}

# Output data containers
quartile_data, summary_data, bonus_data, comparison_data = [], [], [], []
# Generate systhetic data for the following files:
for company, year in itertools.product(companies, years):
    male_dist, female_dist = [], []

    if company == "Ryanair":
        dist_map = ryanair_dist
    elif company == "Odeon":
        dist_map = odeon_dist
    else:
        dist_map = {q: (np.random.uniform(40, 60), 0) for q in quartiles}
        for q in quartiles:
            dist_map[q] = (dist_map[q][0], 100 - dist_map[q][0])

    for q in quartiles:
        male_pct, female_pct = dist_map[q]
        quartile_data.extend([
            {"Company": company, "Year": year, "Quartile": q, "Gender": "Male", "Percentage": round(male_pct, 1)},
            {"Company": company, "Year": year, "Quartile": q, "Gender": "Female", "Percentage": round(female_pct, 1)}
        ])
        male_dist.append((male_pct / 100) * quartile_salaries[q])
        female_dist.append((female_pct / 100) * quartile_salaries[q])

    mean_male_pay = sum(male_dist)
    mean_female_pay = sum(female_dist)
    mean_pay_gap = round((mean_male_pay - mean_female_pay) / mean_male_pay * 100, 1)

    median_male = quartile_salaries["Q2 - Upper Mid"]
    median_female = quartile_salaries["Q3 - Lower Mid"]
    median_pay_gap = round((median_male - median_female) / median_male * 100, 1)

    summary_data.extend([
        {"Company": company, "Year": year, "Metric": "Mean Hourly Pay", "Male": round(mean_male_pay, 1), "Female": round(mean_female_pay, 1)},
        {"Company": company, "Year": year, "Metric": "Median Hourly Pay", "Male": median_male, "Female": median_female}
    ])

    male_bonus_participation = np.random.uniform(60, 90)
    female_bonus_participation = np.random.uniform(40, 80)
    male_bonus_avg = sum((dist_map[q][0] / 100) * quartile_bonuses[q] for q in quartiles)
    female_bonus_avg = sum((dist_map[q][1] / 100) * quartile_bonuses[q] for q in quartiles)
    male_bonus = male_bonus_avg * (male_bonus_participation / 100)
    female_bonus = female_bonus_avg * (female_bonus_participation / 100)
    mean_bonus_gap = round((male_bonus - female_bonus) / male_bonus * 100, 1)

    summary_data.extend([
        {"Company": company, "Year": year, "Metric": "Mean Bonus Pay", "Male": round(male_bonus, 1), "Female": round(female_bonus, 1)},
        {"Company": company, "Year": year, "Metric": "Median Bonus Pay", "Male": 2000, "Female": 1000}
    ])

    bonus_data.extend([
        {"Company": company, "Year": year, "Gender": "Male", "Bonus Participation (%)": round(male_bonus_participation, 1)},
        {"Company": company, "Year": year, "Gender": "Female", "Bonus Participation (%)": round(female_bonus_participation, 1)}
    ])

    comparison_data.append({
        "Company": company,
        "Year": year,
        "Mean Hourly Gap (%)": mean_pay_gap,
        "Median Hourly Gap (%)": median_pay_gap,
        "Mean Bonus Gap (%)": mean_bonus_gap,
        "Median Bonus Gap (%)": 50.0
    })

# Sankey + Heatmap data
sankey_rows, heatmap_rows = [], []
targets = ["Bonus", "No Bonus", "Exit"]
for company, year in itertools.product(companies, years):
    for source in quartiles:
        weights = np.random.dirichlet(np.ones(len(targets))) * 100
        for tgt, w in zip(targets, weights):
            sankey_rows.append({
                "Company": company,
                "Year": year,
                "Source": source,
                "Target": tgt,
                "Value": round(w, 1)
            })

    for gender in ["Male", "Female"]:
        for quart in quartiles:
            base = np.random.uniform(60, 90)
            for month in range(1, 13):
                heatmap_rows.append({
                    "Company": company,
                    "Year": year,
                    "Gender": gender,
                    "Quartile": quart,
                    "Month": f"{year}-{str(month).zfill(2)}",
                    "Retention (%)": round(max(0, min(100, base + np.random.normal(0, 5))), 1)
                })

# Save to CSV
outputs = {
    "pay_quartiles.csv": quartile_data,
    "pay_gap_summary.csv": summary_data,
    "bonus_participation.csv": bonus_data,
    "pay_gap_comparison.csv": comparison_data,
    "sankey_flow.csv": sankey_rows,
    "retention_heatmap.csv": heatmap_rows,
}
for fname, rows in outputs.items():
    pd.DataFrame(rows).to_csv(f"data/{fname}", index=False)

print("List of Data files generated in `data/` directory!")
print(os.listdir("data"))