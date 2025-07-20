import os
import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Create output directory 'data'
os.makedirs("data", exist_ok=True)

regions = ["US", "UK", "EMEA"]
sub_categories = {
    "US": ["Real Estate", "Industrials", "Basic Materials", "Healthcare"],
    "UK": ["Accessories", "Consumer Cyclical", "Technology", "Financial Services", "Supplies"],
    "EMEA": ["Misc A", "Misc B", "Misc C", "Misc D"]
}

manufacturers = ["Group A", "Group B", "Group C", "Group D", "Group E"]
variants = ["Type 1", "Type 2", "Type 3"]

rows = []

# Ensure at least one of each manufacturer and variant is represented
for i in range(len(manufacturers)):
    rows.append({
        "Region": "US",
        "SubCategory": "Healthcare",
        "Manufacturer": manufacturers[i],
        "Variant": variants[i % len(variants)],
        "Value": np.random.randint(100, 500)
    })

# Additional randomly generated rows
for region in regions:
    for sub_cat in sub_categories[region]:
        num_mfg = np.random.randint(2, 4)
        mfgs = np.random.choice(manufacturers, size=num_mfg, replace=False)
        for mfg in mfgs:
            num_vars = np.random.randint(2, 4)
            vars_ = np.random.choice(variants, size=num_vars, replace=False)
            for var in vars_:
                value = int(np.random.normal(loc=300, scale=50))
                value = max(100, value)
                rows.append({
                    "Region": region,
                    "SubCategory": sub_cat,
                    "Manufacturer": mfg,
                    "Variant": var,
                    "Value": value
                })

df_icicle = pd.DataFrame(rows)
df_icicle.to_csv("data/icicle_data.csv", index=False)

print("List of Synthetic Data generated in `data/` directory!")
print(os.listdir("data"))