
import pandas as pd
import plotly.graph_objects as go
import os

# Load dataset
df = pd.read_csv("data/sunburst_bike_sales.csv")
df["Root"] = "Total"

# 6-level hierarchy: Total → Year → Gender → Category → Subcategory → Model
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

# Gather unique nodes
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

# Leaves: Model
for _, row in df.iterrows():
    nodes.append((row["id"], row["parent"], row["Model"], row["Sales"]))

sunburst_df = pd.DataFrame(nodes, columns=["id", "parent", "label", "value"])

# Female stats
female_total = df[df["Gender"] == "Female"]["Sales"].sum()
total_sales = df["Sales"].sum()
female_pct = round(female_total / total_sales * 100)

def euro_format(value):
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

formatted_sales = euro_format(female_total)
center_label = f"<b>{female_pct}%</b><br>Female<br>{formatted_sales}"

# Professional color palette
colors = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692",
    "#B6E880", "#FF97FF", "#FECB52"
]

# Render sunburst
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

# Layout with center annotation
fig.update_layout(
    title="<b>Sunburst Chart — 6-Level Hierarchy with Center Summary</b>",
    margin=dict(t=50, l=0, r=0, b=0),
    paper_bgcolor="white",
    annotations=[dict(
        text=center_label,
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=20, family="Arial", color="black"),
        xanchor="center",
        yanchor="middle",
        bgcolor="white",
        borderpad=10
    )]
)

# Save HTML
os.makedirs("outputs", exist_ok=True)
fig.write_html("outputs/dashboard.html", include_plotlyjs="cdn", full_html=True)
