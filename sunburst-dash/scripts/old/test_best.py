# Finalized viz.py logic to match reference image exactly with a circular white center

import pandas as pd
import plotly.express as px
import os

# Load enhanced sunburst data
df = pd.read_csv("data/sunburst_bike_sales.csv")

# Add dummy root column "Total" to shift actual data one ring outward
df["Root"] = "Total"

# Compute female share
total_sales = df["Sales"].sum()
female_sales = df[df["Gender"] == "Female"]["Sales"].sum()
female_pct = round(female_sales / total_sales * 100)
female_sales_str = f"{female_sales:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

center_text = f"<b>{female_pct}%</b><br>Female<br>${female_sales_str}"

# Color map (optional refinement)
color_map = {
    "Road Bikes": "#FFD700",
    "Mountain Bikes": "#F4A460",
    "Touring Bikes": "#7CFC00"
}

# Create 6-level sunburst with white root node
fig = px.sunburst(
    df,
    path=["Root", "Year", "Gender", "Category", "Subcategory", "Model"],
    values="Sales",
    color="Category",
    color_discrete_map=color_map
)

# Layout with central white hole + circle-shaped annotation
fig.update_layout(
    title_text="Sunburst Chart — Category Breakdown",
    margin=dict(t=60, l=0, r=0, b=0),
    paper_bgcolor="white",
    uniformtext=dict(minsize=10, mode='hide'),
    sunburstcolorway=list(color_map.values()),
    extendsunburstcolors=True,
    annotations=[dict(
        text=center_text,
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="black"),
        xanchor="center", yanchor="middle",
        bgcolor="white",
        borderpad=10,
        bordercolor="white"
    )]
)

# Save output
os.makedirs("outputs", exist_ok=True)
fig.write_html("outputs/dashboard.html", include_plotlyjs="cdn", full_html=True)

