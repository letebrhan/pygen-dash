
import pandas as pd
import plotly.graph_objects as go
import os

# Load dataset
df = pd.read_csv("data/sunburst_bike_sales.csv")

# Add root node
df["Root"] = "Total"

# Prepare 6-level hierarchy: Total → Year → Gender → Category → Subcategory → Model
df["id"] = (
    df["Root"] + "/" + df["Year"] + "/" + df["Gender"] + "/" +
    df["Category"] + "/" + df["Subcategory"] + "/" + df["Model"]
)
df["parent"] = (
    df["Root"] + "/" + df["Year"] + "/" + df["Gender"] + "/" +
    df["Category"] + "/" + df["Subcategory"]
)

# Add intermediate levels
df["level_1"] = "Total"
df["level_2"] = df["level_1"] + "/" + df["Year"]
df["level_3"] = df["level_2"] + "/" + df["Gender"]
df["level_4"] = df["level_3"] + "/" + df["Category"]
df["level_5"] = df["level_4"] + "/" + df["Subcategory"]

# Build all unique ids/parents/labels/values
nodes = []

# Root
total_sales = df["Sales"].sum()
nodes.append(("Total", "", "", total_sales))

# Year
for year in df["Year"].unique():
    subset = df[df["Year"] == year]
    val = subset["Sales"].sum()
    nodes.append((f"Total/{year}", "Total", year, val))

# Gender
for (year, gender), sub in df.groupby(["Year", "Gender"]):
    val = sub["Sales"].sum()
    nodes.append((f"Total/{year}/{gender}", f"Total/{year}", gender, val))

# Category
for (year, gender, cat), sub in df.groupby(["Year", "Gender", "Category"]):
    val = sub["Sales"].sum()
    nodes.append((f"Total/{year}/{gender}/{cat}", f"Total/{year}/{gender}", cat, val))

# Subcategory
for (year, gender, cat, subcat), sub in df.groupby(["Year", "Gender", "Category", "Subcategory"]):
    val = sub["Sales"].sum()
    nodes.append((
        f"Total/{year}/{gender}/{cat}/{subcat}",
        f"Total/{year}/{gender}/{cat}",
        subcat,
        val
    ))

# Model (leaves)
for _, row in df.iterrows():
    nodes.append((
        row["id"],
        row["parent"],
        row["Model"],
        row["Sales"]
    ))

# Convert to DataFrame
sunburst_df = pd.DataFrame(nodes, columns=["id", "parent", "label", "value"])

# Create sunburst chart
fig = go.Figure(go.Sunburst(
    ids=sunburst_df["id"],
    labels=sunburst_df["label"],
    parents=sunburst_df["parent"],
    values=sunburst_df["value"],
    branchvalues="total",
    insidetextorientation="radial",
    root_color="white"
))

# Compute female stats for center
female_total = df[df["Gender"] == "Female"]["Sales"].sum()
female_pct = round(female_total / total_sales * 100)
center_label = f"<b>{female_pct}%</b><br>Female<br>${female_total:,.0f}".replace(",", ".")

# Add white circular center text via annotation
fig.update_layout(
    title_text="Sunburst Chart — 6-Level Hierarchy with Center Summary",
    margin=dict(t=50, l=0, r=0, b=0),
    paper_bgcolor="white",
    annotations=[dict(
        text=center_label,
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16),
        xanchor="center",
        yanchor="middle",
        bgcolor="white",
        borderpad=8
    )]
)

# Export to HTML
os.makedirs("outputs", exist_ok=True)
fig.write_html("outputs/dashboard_circle.html", include_plotlyjs="cdn", full_html=True)
