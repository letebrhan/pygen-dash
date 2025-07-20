
import pandas as pd
import plotly.graph_objects as go
import os

# Load sales data
df = pd.read_csv("data/sunburst_bike_sales.csv")
df["Root"] = "Total"

# Build 6-level hierarchy: Total → Year → Gender → Category → Subcategory → Model
df["id"] = (
    df["Root"] + "/" + df["Year"] + "/" + df["Gender"] + "/" +
    df["Category"] + "/" + df["Subcategory"] + "/" + df["Model"]
)
df["parent"] = (
    df["Root"] + "/" + df["Year"] + "/" + df["Gender"] + "/" +
    df["Category"] + "/" + df["Subcategory"]
)

# Add intermediate levels (not required for Plotly, just organizational)
nodes = [("Total", "", "", df["Sales"].sum())]

for year in df["Year"].unique():
    nodes.append((f"Total/{year}", "Total", year, df[df["Year"] == year]["Sales"].sum()))

for (year, gender), sub in df.groupby(["Year", "Gender"]):
    nodes.append((f"Total/{year}/{gender}", f"Total/{year}", gender, sub["Sales"].sum()))

for (year, gender, cat), sub in df.groupby(["Year", "Gender", "Category"]):
    nodes.append((f"Total/{year}/{gender}/{cat}", f"Total/{year}/{gender}", cat, sub["Sales"].sum()))

for (year, gender, cat, subcat), sub in df.groupby(["Year", "Gender", "Category", "Subcategory"]):
    nodes.append((
        f"Total/{year}/{gender}/{cat}/{subcat}",
        f"Total/{year}/{gender}/{cat}",
        subcat,
        sub["Sales"].sum()
    ))

# Model level (leaf)
for _, row in df.iterrows():
    nodes.append((row["id"], row["parent"], row["Model"], row["Sales"]))

sunburst_df = pd.DataFrame(nodes, columns=["id", "parent", "label", "value"])

# Female stats for center display
female_total = df[df["Gender"] == "Female"]["Sales"].sum()
total_sales = df["Sales"].sum()
female_pct = round(female_total / total_sales * 100)

def euro_format(value):
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

formatted_sales = euro_format(female_total)
center_label = f"<b>{female_pct}%</b><br>Female<br>{formatted_sales}"

# Muted professional palette
colors = [
    "#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C",
    "#FB9A99", "#E31A1C", "#FDBF6F", "#FF7F00",
    "#CAB2D6", "#6A3D9A"
]

# Build sunburst chart
fig = go.Figure(go.Sunburst(
    ids=sunburst_df["id"],
    labels=sunburst_df["label"],
    parents=sunburst_df["parent"],
    values=sunburst_df["value"],
    branchvalues="total",
    insidetextorientation="radial",
    marker=dict(colors=colors * (len(sunburst_df) // len(colors) + 1), line=dict(color='white', width=1)),
    root_color="white"
))

# Layout
fig.update_layout(
    title="<b>Sales Distribution by Year, Gender, and Product Hierarchy</b>",
    margin=dict(t=50, l=0, r=0, b=0),
    paper_bgcolor="white",
    annotations=[dict(
        text=center_label,
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=18, family="Arial", color="black"),
        xanchor="center",
        yanchor="middle",
        bgcolor="white",
        borderpad=8
    )]
)

# Save final HTML
os.makedirs("outputs", exist_ok=True)
fig.write_html("outputs/sunburst_final_dashboard.html", include_plotlyjs="cdn", full_html=True)
