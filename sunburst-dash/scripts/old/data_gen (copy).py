import pandas as pd
import random

# Config
categories = ["Road Bikes", "Mountain Bikes", "Touring Bikes"]
genders = ["Female", "Male"]
years = ["2011", "2012", "2013"]

# Generate product-level data
records = []
for year in years:
    for gender in genders:
        for category in categories:
            cat_node = f"{category} {gender} {year}"
            for i in range(1, 11):  # 10 sub-products
                product = f"{category.split()[0]}-{i:03d} {gender[0]}{year[-2:]}"
                value = random.randint(100_000, 500_000)
                records.append((product, cat_node, value))

df = pd.DataFrame(records, columns=["id", "parent", "value"])

# Roll-up structure
rollups = []
for year in years:
    for gender in genders:
        for category in categories:
            cat_id = f"{category} {gender} {year}"
            gender_id = f"{gender} {year}"
            rollups.append((cat_id, gender_id))
        rollups.append((gender_id, f"CY {year}"))
    rollups.append((f"CY {year}", "Total"))

# Add root
rollups.append(("Total", ""))

# Roll-up aggregation
for node, parent in rollups:
    val = df[df["parent"] == node]["value"].sum()
    df = pd.concat([df, pd.DataFrame([{"id": node, "parent": parent, "value": val}])], ignore_index=True)

# Normalize Gender IDs in both 'id' and 'parent' columns
for gender in genders:
    for year in years:
        year_tag = f"{gender} {year}"
        df["id"] = df["id"].replace(year_tag, gender)
        df["parent"] = df["parent"].replace(year_tag, gender)

# Save final CSV
df.to_csv("data/sunburst_bike_data_sampled.csv", index=False)

