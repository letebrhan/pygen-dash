import os
import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Create output directory
os.makedirs("data", exist_ok=True)

# Define 39 specific product categories
category_names = [
    "Vacuum", "Coffee maker", "Hi-Fi separates", "Lamp", "Power tool", "Small kitchen item",
    "Watch/clock", "AC adapter", "Food processor", "Sewing machine", "Tablet", "Smartphone",
    "Camera", "Printer", "Router", "Speaker", "Laptop", "Electric Kettle", "Washing Machine",
    "Refrigerator", "Microwave", "Toaster", "Grill", "Heater", "Fan", "Iron", "Ceiling Light",
    "Projector", "TV", " Computer", "Smartwatch", "Gaming Console", "Camcorder",
    "Alarm Clock", "Wall Clock", "Thermostat", "Smart Lock", "Smoke Detector", "Electric Scooter"
]

# Generate a random number of products per category
product_categories = [(name, np.random.randint(1, 217)) for name in category_names]

# Initialize lists to collect sub-product data
products = []
totals = []
fixed_percents = []
repairable_percents = []
end_of_life_percents = []
fixed_counts = []
repairable_counts = []
end_of_life_counts = []
category_labels = []
n_product_counts = []
category_summary = []

# Generate sub-products per category
for cat_name, n_sub in product_categories:
    total_cat = np.random.randint(3000, 12000)  # Total for the whole category

    # Distribute total randomly across sub-products
    weights = np.random.dirichlet(np.ones(n_sub))
    sub_totals = np.round(weights * total_cat).astype(int)

    total_fixed_cnt = 0
    total_repairable_cnt = 0
    total_eol_cnt = 0

    for i in range(n_sub):
        sub_name = f"{cat_name} - Model {i+1}"
        total = sub_totals[i]

        fixed = np.random.uniform(40, 80)
        repairable = np.random.uniform(5, 30)
        end_of_life = 100 - fixed - repairable
        if end_of_life < 0:
            excess = -end_of_life
            fixed -= excess / 2
            repairable -= excess / 2
            end_of_life = 0

        fixed_cnt = int(round(total * fixed / 100))
        repairable_cnt = int(round(total * repairable / 100))
        end_of_life_cnt = total - fixed_cnt - repairable_cnt

        products.append(sub_name)
        totals.append(total)
        fixed_percents.append(f"{fixed:.1f}%")
        repairable_percents.append(f"{repairable:.1f}%")
        end_of_life_percents.append(f"{end_of_life:.1f}%")
        fixed_counts.append(fixed_cnt)
        repairable_counts.append(repairable_cnt)
        end_of_life_counts.append(end_of_life_cnt)
        category_labels.append(cat_name)
        n_product_counts.append(n_sub)

        total_fixed_cnt += fixed_cnt
        total_repairable_cnt += repairable_cnt
        total_eol_cnt += end_of_life_cnt

    category_summary.append({
        "Category": cat_name,
        "Total": total_cat,
        "N_products": n_sub,
        "Fixed": f"{100 * total_fixed_cnt / total_cat:.1f}%",
        "Repairable": f"{100 * total_repairable_cnt / total_cat:.1f}%",
        "End of Life": f"{100 * total_eol_cnt / total_cat:.1f}%",
        "Fixed Cnt": total_fixed_cnt,
        "Repairable Cnt": total_repairable_cnt,
        "End of Life Cnt": total_eol_cnt
    })

# Compute percentage share per product
grand_total = sum(totals)
percentage_share = [f"{100 * t / grand_total:.1f}%" for t in totals]

# Build sub-product DataFrame
df_product = pd.DataFrame({
    "Product": products,
    "Category": category_labels,
    "N_products": n_product_counts,
    "Total": totals,
    "Percentage": percentage_share,
    "Fixed": fixed_percents,
    "Repairable": repairable_percents,
    "End of Life": end_of_life_percents,
    "Fixed Cnt": fixed_counts,
    "Repairable Cnt": repairable_counts,
    "End of Life Cnt": end_of_life_counts
})

# Save sub-product data
df_product.to_csv("data/product_items.csv", index=False)

# Save generated category data
df_categories = pd.DataFrame(category_summary)
df_categories.to_csv("data/product_categories.csv", index=False)

print("List of Synthetic Data generated in `data/` directory!")
print(os.listdir("data"))