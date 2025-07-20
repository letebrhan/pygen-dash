# scripts/viz.py

import os
import pandas as pd
import plotly.express as px
from plotly.io import to_html

# Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

# 1. Load data
df_icicle = pd.read_csv("data/icicle_data.csv")
df_icicle['Region'] = pd.Categorical(df_icicle['Region'], categories=['US', 'UK', 'EMEA'], ordered=True)
df_icicle = df_icicle.sort_values(['Region', 'SubCategory', 'Manufacturer', 'Variant'])

# 2. Fonts and styling
FONT_FAMILY = "Segoe UI, Helvetica Neue, Arial, sans-serif"
FONT_COLOR = "#333333"
COMMON_FONT = dict(family=FONT_FAMILY, size=14, color=FONT_COLOR)
COMMON_TITLE_FONT = dict(family=FONT_FAMILY, size=22, color=FONT_COLOR)

# 3. Create the icicle chart
fig = px.icicle(
    df_icicle,
    path=['Region', 'SubCategory', 'Manufacturer', 'Variant'],
    values='Value',
    color='Region',
    color_discrete_map={
        'US': '#ff796d',
        'UK': '#1ad4d9',
        'EMEA': '#d4b1f0'
    }
)

fig.update_traces(
    tiling=dict(orientation='v'),
    textfont=dict(family=FONT_FAMILY, size=13, color=FONT_COLOR)
)

fig.update_layout(
    title=None,
    font=COMMON_FONT,
    height=600,
    paper_bgcolor='white',
    plot_bgcolor='white',
    margin=dict(l=120, r=20, t=20, b=20)
)

# 4. Left-aligned axis labels (annotations)
levels = ["Category", "SubCategory", "Manufacturer", "Variant"]
y_positions = [0.7, 0.5, 0.3, 0.1]

for label, y in zip(levels, y_positions):
    fig.add_annotation(
        text=f"<b>{label}</b>",
        x=-0.01,
        y=y,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=13, color="black"),
        xanchor="right",
        yanchor="middle"
    )

# 5. Generate HTML body
fig_html = to_html(fig, include_plotlyjs='cdn', full_html=False)

html_template = f"""
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Icicle Chart - Category Breakdown</title>
    <style>
        body {{
            background-color: #f4f6f8;
            font-family: {FONT_FAMILY};
            margin: 0;
            padding: 40px 20px;
        }}
        .dashboard-title {{
            background-color: #264653;
            color: white;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
            padding: 14px 0;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .card {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            padding: 20px;
            max-width: 1100px;
            margin: auto;
        }}
        .legend-note {{
            text-align: center;
            font-size: 13px;
            color: #666;
            margin-top: 18px;
        }}
        footer {{
            text-align: center;
            font-size: 12px;
            color: #aaa;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-title">Icicle Chart — Category Breakdown</div>
    <div class="card">{fig_html}</div>
    <div class="legend-note">* Color indicates Region (US, UK, EMEA). Each level breaks down from region to variant.</div>
    <footer>© 2025 Icicle Chart — Category Breakdown. Powered by Plotly.</footer>
</body>
</html>
"""

# Save file
with open("outputs/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Updated dashboard exported to outputs/dashboard.html")

