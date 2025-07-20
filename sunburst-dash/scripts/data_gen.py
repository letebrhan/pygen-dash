import os
import pandas as pd
import numpy as np

# Create output directory
os.makedirs("data", exist_ok=True)

np.random.seed(42)

# Hierarchical levels
years = ["CY 2011", "CY 2012", "CY 2013"]
genders = ["Male", "Female"]
categories = ["Road Bikes", "Mountain Bikes", "Touring Bikes"]

subcategory_map = {
    "Road Bikes": ["Road-150 Red", "Road-250", "Road-350-W", "Road-550-W"],
    "Mountain Bikes": ["Mountain-200 Black", "Mountain-200 Silver", "Mountain-300"],
    "Touring Bikes": ["Touring-1000", "Touring-2000"]
}

model_map = {
    "Road-150 Red": [f"Road-150 Red"] * 6,
    "Road-250": [f"Road-250"] * 4,
    "Road-350-W": [f"Road-350-W"] * 5,
    "Road-550-W": [f"Road-550-W"] * 5,
    "Mountain-200 Black": [f"Mountain-200 Black - {size}" for size in [38, 42, 46]],
    "Mountain-200 Silver": [f"Mountain-200 Silver - {size}" for size in [38, 42, 46]],
    "Mountain-300": ["Mountain-300"] * 3,
    "Touring-1000": ["Touring-1000"] * 8,
    "Touring-2000": ["Touring-2000"] * 4,
}

rows = []
for year in years:
    for gender in genders:
        for category in categories:
            for sub in subcategory_map[category]:
                models = model_map[sub]
                total_sub_sales = np.random.randint(500000, 2500000)
                for model in models:
                    model_sales = int(total_sub_sales / len(models))
                    rows.append([year, gender, category, sub, model, model_sales])

# Save generated data
df = pd.DataFrame(rows, columns=["Year", "Gender", "Category", "Subcategory", "Model", "Sales"])
df.to_csv("data/sunburst_bike_sales.csv", index=False)

print("Synthetic Data generated in `data/` directory!")
print(os.listdir("data"))