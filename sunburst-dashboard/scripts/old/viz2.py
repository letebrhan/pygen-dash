import pandas as pd
import plotly.express as px
import os

# Load data
df = pd.read_csv("data/sunburst_bike_sales.csv")

# Compute center content
total_sales = df["Sales"].sum()
female_sales = df[df["Gender"] == "Female"]["Sales"].sum()
female_pct = round(female_sales / total_sales * 100)
female_sales_str = f"{female_sales:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

center_text = f"<b>{female_pct}%</b><br>Female<br>${female_sales_str}"

# Optional color map
color_map = {
    "Road Bikes": "#FFD700",
    "Mountain Bikes": "#F4A460",
    "Touring Bikes": "#7CFC00"
}

# Create 5-level sunburst
fig = px.sunburst(
    df,
    path=["Year", "Gender", "Category", "Subcategory", "Model"],
    values="Sales",
    color="Category",
    color_discrete_map=color_map
)

# Center layout
fig.update_layout(
    title_text="Sunburst Chart — Category Breakdown",
    margin=dict(t=60, l=0, r=0, b=0),
    paper_bgcolor="white",
    annotations=[dict(
        text=center_text,
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16),
        xanchor="center", yanchor="middle",
        bgcolor="white"
    )]
)

# Save to HTML
os.makedirs("outputs", exist_ok=True)
fig.write_html("outputs/dashboard.html", include_plotlyjs="cdn", full_html=True)

