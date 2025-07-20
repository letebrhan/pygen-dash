
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_html

import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Helper function for loading CSV files safely
def load_data(path):
    try:
        df = pd.read_csv(path)
        logging.info(f"Successfully loaded {path}")
        return df
    except Exception as e:
        logging.error(f"Failed to load {path}: {e}")
        return pd.DataFrame()

# Load sales data
df = load_data("data/sunburst_bike_sales.csv")
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

def dollars_format(value):
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

formatted_sales = dollars_format(female_total)
center_label = f"<b>{female_pct}%</b><br>Female<br>{formatted_sales}"

# Fonts and styling
FONT_FAMILY = "Segoe UI, Helvetica Neue, Arial, sans-serif"
FONT_COLOR = "#333333"
COMMON_FONT = dict(family=FONT_FAMILY, size=14, color=FONT_COLOR)
COMMON_TITLE_FONT = dict(family=FONT_FAMILY, size=22, color=FONT_COLOR)

# Muted professional color palette
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
    marker=dict(
        colors=(["white"] + colors * ((len(sunburst_df) - 1) // len(colors) + 1))[:len(sunburst_df)],
        line=dict(color='white', width=1)
    ),
    hovertemplate='<b>%{label}</b><br><b>Path:</b> %{id}<br><b>Sales:</b> %{value:,}<extra></extra>',
   
    root={"color": "white"} 
))

# Add a white circular shape to simulate the center
fig.add_shape(
    type="circle",
    xref="paper", yref="paper",
    x0=0.37, y0=0.37,  # Adjust the size and position
    x1=0.63, y1=0.63,
    fillcolor="white",
    line_color="white",
    layer="below"
)

# Layout
fig.update_layout(
    title=dict(
        text="<b>Sales Distribution by Year, Gender, and Product Hierarchy</b>", 
        x=0.5, xanchor="center", font=COMMON_TITLE_FONT
    ),
    margin=dict(t=60, l=0, r=0, b=20),
    paper_bgcolor="white",
    font= COMMON_FONT,
    annotations=[dict(
        text=center_label,
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, family=FONT_FAMILY, color=FONT_COLOR),
        xanchor="center",
        yanchor="middle"
    )]
)

os.makedirs("outputs", exist_ok=True)

# Save final HTML
fig_html = to_html(fig, include_plotlyjs='cdn', full_html=False)

html_template = f"""
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sunburst Chart - Product Sales Breakdown</title>
    <style>
        body {{
            background-color: #f4f6f8;
            font-family: {FONT_FAMILY};
            margin: 0;
            padding: 40px 20px;
        }}
        .card {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            padding: 20px;
            max-width: 1200px;
            margin: auto;
            border: 1px solid #e0e0e0;
        }}
        .legend-note {{
            text-align: center;
            font-size: 13px;
            color: #666;
            margin-top: 18px;
        }}
        footer {{
            text-align: center;
            font-size: 11px;
            color: #bbb;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="card">{fig_html}</div>
    <div class="legend-note">* 6-level hierarchy: Total → Year → Gender → Category → Subcategory → Model.</div>
    <footer>© 2025 Multi-Level Product Sales Breakdown with Gender Highlights. Powered by Plotly.</footer>
</body>
</html>
"""

# Save file
with open("outputs/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Updated dashboard exported to outputs/dashboard.html")
