import os
import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_html

# --- Load Data ---
subs_region = pd.read_csv("data/subscriptions_by_region.csv")
monthly = pd.read_csv("data/monthly_subscriptions.csv")
churn_reasons = pd.read_csv("data/churn_reasons.csv")
heatmap = pd.read_csv("data/plan_churn_heatmap.csv")

# --- Color Palette ---
COLOR_PALETTE = {
    'North America': '#5B8FF9',
    'EMEA': '#61DDAA',
    'APAC': '#65789B',
    'New Signups': '#5AD8A6',
    'Churned': '#F6BD16',
    'Net Growth': '#7262FD',
    'Price': '#F08BB4',
    'Features': '#5D7092',
    'Support': '#6DC8EC',
    'Competitor': '#FF9D4D',
    'Other': '#C2C8D5'
}

# --- Font Styles ---
FONT_FAMILY = "Segoe UI, Arial, sans-serif"
COMMON_FONT = dict(family=FONT_FAMILY, size=14, color="#333333")
COMMON_TITLE_FONT = dict(family=FONT_FAMILY, size=18, color="#333333")
COMMON_AXIS_TITLE_FONT = dict(family=FONT_FAMILY, size=16, color="#333333")
COMMON_AXIS_TICK_FONT = dict(family=FONT_FAMILY, size=13, color="#333333")

# --- Legend Styles---
LEGEND=dict(
    font=dict(
        family=FONT_FAMILY,  # Clean and modern
        size=13,                               # Slightly larger for readability
        color="#333333"                        # Dark grey = softer than black, still readable
    ),
    orientation="h",                          # Horizontal layout is clean and modern
    y=-0.3,
    x=0.5,
    xanchor="center",
    bgcolor="white",
    bordercolor="#dddddd",
    borderwidth=1
)

# --- Chart 1: KPI Bar + Line Chart ---
monthly['Month'] = pd.to_datetime(monthly['Month']).dt.strftime('%b %Y')
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=monthly['Month'], y=monthly['NewSignups'],
    name='New Signups', marker_color=COLOR_PALETTE['New Signups']
))
fig1.add_trace(go.Bar(
    x=monthly['Month'], y=monthly['Churned'],
    name='Churned', marker_color=COLOR_PALETTE['Churned']
))
fig1.add_trace(go.Scatter(
    x=monthly['Month'], y=monthly['NetGrowth'],
    name='Net Growth', mode='lines+markers',
    line=dict(color=COLOR_PALETTE['Net Growth'], width=2),
    marker=dict(size=8, line=dict(width=1, color='white'))
))
fig1.update_layout(
    title=dict(text="<b>Monthly Subscription KPIs Over Time</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    xaxis=dict(title=dict(text="Month", font=COMMON_AXIS_TITLE_FONT), tickfont=COMMON_AXIS_TICK_FONT, 
               tickmode="array", tickvals=monthly['Month'].unique()),
    yaxis=dict(title=dict(text="Subscribers", font=COMMON_AXIS_TITLE_FONT), tickfont=COMMON_AXIS_TICK_FONT),
    barmode='group', template="plotly_white",
    legend=LEGEND
)

# --- Chart 2: Active Users by Region ---
subs_region['Month'] = pd.to_datetime(subs_region['Month']).dt.strftime('%b %Y')
fig2 = go.Figure()
for region in subs_region['Region'].unique():
    df = subs_region[subs_region['Region'] == region]
    fig2.add_trace(go.Scatter(
        x=df['Month'], y=df['ActiveUsers'],
        mode='lines+markers', name=region,
        line=dict(color=COLOR_PALETTE.get(region, '#ccc'))
    ))
fig2.update_layout(
    title=dict(text="<b> Active Users by Region</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    xaxis=dict(title=dict(text="Month", font=COMMON_AXIS_TITLE_FONT), tickfont=COMMON_AXIS_TICK_FONT,
               tickmode="array", tickvals=subs_region['Month'].unique()),
    yaxis=dict(title=dict(text="Active Users", font=COMMON_AXIS_TITLE_FONT), tickfont=COMMON_AXIS_TICK_FONT),
    template="plotly_white",
    legend=LEGEND
)

# --- Chart 3: Churn Reasons Pie Chart ---
agg = churn_reasons.groupby("Reason")["Count"].sum().reset_index()
fig3 = go.Figure()
fig3.add_trace(go.Pie(
    labels=agg["Reason"], values=agg["Count"], hole=0.4,
    marker=dict(colors=[COLOR_PALETTE.get(reason, '#888888') for reason in agg['Reason']]),
    textinfo='percent+label'
))
fig3.update_layout(
    title=dict(text="<b> Churn Reasons Breakdown</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    height=500,
    template="plotly_white", 
    font=dict(family=FONT_FAMILY),
    legend=LEGEND

)

# --- Chart 4: Churn Heatmap ---
heatmap['Month'] = pd.to_datetime(heatmap['Month']).dt.strftime('%b %Y')
heatmap['Row'] = heatmap['Plan'] + " - " + heatmap['Region']
pivot = heatmap.pivot(index='Row', columns='Month', values='ChurnRate').sort_index()
fig4 = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale=[[0, '#E6F7FF'], [1, '#0050B3']],
    colorbar=dict(title="Churn Rate")
))
fig4.update_layout(
    title=dict(text="<b> Churn Rate Heatmap by Plan & Region</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    xaxis=dict(title=dict(text="Month", font=COMMON_AXIS_TITLE_FONT), tickfont=COMMON_AXIS_TICK_FONT,
               tickmode="array", tickvals=heatmap['Month'].unique()),
    yaxis=dict(title=dict(text="Plan - Region", font=COMMON_AXIS_TITLE_FONT), tickfont=COMMON_AXIS_TICK_FONT),
    template="plotly_white"
)

fig1.update_layout(margin=dict(b=80, t=80))
fig2.update_layout(margin=dict(b=80, t=80))
fig3.update_layout(margin=dict(b=50, t=80))
fig4.update_layout(margin=dict(b=50, t=80))

# Generate HTML strings from plots
fig1_html = to_html(fig1, include_plotlyjs='cdn', full_html=False)
fig2_html = to_html(fig2, include_plotlyjs=False, full_html=False)
fig3_html = to_html(fig3, include_plotlyjs=False, full_html=False)
fig4_html = to_html(fig4, include_plotlyjs=False, full_html=False)

# --- Export HTML Layout ---
os.makedirs("outputs", exist_ok=True)
html_content = f"""
<html>
<head>
    <meta charset="UTF-8">
    <title>SaaS Dashboard</title>
    <style>
        body {{
            font-family: {FONT_FAMILY};
            background-color: #f5f7fa;
            margin: 0;
            padding: 40px;
        }}
        .dashboard-title {{
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 40px;
        }}
        .card {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 30px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-title">SaaS Subscription & Churn Dashboard</div>
    <div class="grid-2">
        <div class="card">{fig1_html}</div>
        <div class="card">{fig2_html}</div>
    </div>
    <div class="grid-2">
        <div class="card">{fig3_html}</div>
        <div class="card">{fig4_html}</div>
    </div>
</body>
<footer>
    <div style="text-align:center; margin-top:20px; font-size:12px; color:gray;">
    © 2025 SaaS Analytics Dashboard. Powered by Plotly.
</div>
</footer>
</html>
"""
# Save to outputs/golden_image.html
with open("outputs/golden_image.html", "w") as f:
    f.write(html_content)

print("Dashboard exported to outputs/golden_image.html")