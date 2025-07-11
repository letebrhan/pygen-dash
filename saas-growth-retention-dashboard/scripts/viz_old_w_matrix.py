
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_html

# --- Load your real data ---
df_metrics = pd.read_csv("data/metrics_summary.csv")
df_arr = pd.read_csv("data/arr_changes.csv")
df_employees = pd.read_csv("data/employees_by_dept.csv")
df_expenses = pd.read_csv("data/expenses.csv")
df_cohort = pd.read_csv("data/cohort_retention.csv")

# --- Professional Color Palette ---
COLOR_PALETTE = {
    'Upgrade': '#5B8FF9',
    'New': '#5AD8A6',
    'Downgrade': '#F08BB4',
    'Churn': '#F6BD16',
    'NetGrowth': '#7262FD',
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

# --- Legend Style ---
LEGEND = dict(
    font=dict(family=FONT_FAMILY, size=13, color="#333333"),
    orientation="h", y=-0.3, x=0.5, xanchor="center",
    bgcolor="white", bordercolor="#dddddd", borderwidth=1
)

# --- Metric Cards ---
def generate_metric_card(title, value, delta="+4.2%", delta_color="green"):
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=float(value),
        number={'prefix': '$', 'font': {'size': 26}},
        delta={'position': "right", 'reference': 0, 'increasing': {'color': delta_color}},
        title={"text": f"<b>{title}</b>", "font": COMMON_TITLE_FONT}
    ))
    fig.update_layout(height=100, margin=dict(t=10, b=10, l=10, r=10), font=COMMON_FONT)
    return fig

fig_cards = [to_html(generate_metric_card(row['Metric'], row['Value']), full_html=False, include_plotlyjs=False) for _, row in df_metrics.iterrows()]

# --- ARR Stacked Bar Chart with optional Net Growth line ---
fig_arr = go.Figure()

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
df_arr['Month'] = pd.Categorical(df_arr['Month'], categories=months, ordered=True)
df_arr = df_arr.sort_values('Month')

for col in ['Upgrade', 'New', 'Downgrade', 'Churn']:
    fig_arr.add_trace(go.Bar(
        name=col,
        x=df_arr['Month'],
        y=df_arr[col],
        width=0.4,
        marker_color=COLOR_PALETTE[col]
    ))

fig_arr.add_trace(go.Scatter(
    name='NetGrowth',
    x=df_arr['Month'],
    y=df_arr['NetGrowth'],
    mode='lines+markers',
    line=dict(color='black', width=2),
    marker=dict(size=6, symbol='circle', color='black', line=dict(width=1, color='white')),
    yaxis='y2'
))

fig_arr.update_layout(
    barmode='stack',
    title='<b>ARR Changes with Net Growth</b>',
    xaxis=dict(title='Month', type='category', categoryorder='array', categoryarray=months),
    yaxis=dict(title='ARR ($)', tickprefix='$'),
    yaxis2=dict(title='Net Growth', overlaying='y', side='right', showgrid=False),
    height=400
)

# --- Export to HTML ---
os.makedirs("outputs", exist_ok=True)
with open("outputs/test_arr_chart.html", "w") as f:
    f.write(to_html(fig_arr, full_html=True, include_plotlyjs='cdn'))

print("✅ Chart exported to outputs/test_arr_chart.html")
fig_arr_html = to_html(fig_arr, include_plotlyjs=False, full_html=False)

# --- Employee Pie Chart ---
fig_emp = go.Figure(go.Pie(labels=df_employees['Department'], 
                           values=df_employees['Count'], 
                           hole=.4))
fig_emp.update_layout(title="<b>Employees by Department</b>", 
                      font=COMMON_FONT, 
                      title_font=COMMON_TITLE_FONT, 
                      height=400)
fig_emp_html = to_html(fig_emp, include_plotlyjs=False, full_html=False)

# --- Expenses Line Chart ---
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
categories = ['R&D', 'Marketing', 'Ops']
fig_exp = go.Figure()
for col in categories:
    fig_exp.add_trace(go.Scatter(x=df_expenses['Month'], 
                                 y=df_expenses[col], mode='lines+markers', 
                                 name=col))
fig_exp.update_layout(title="<b>Expenses</b>", 
                      font=COMMON_FONT, 
                      title_font=COMMON_TITLE_FONT, 
                      legend=LEGEND, 
                      height=400)
fig_exp_html = to_html(fig_exp, include_plotlyjs=False, full_html=False)

# --- Cohort Heatmap ---
fig_cohort = go.Figure(data=go.Heatmap(
    z=df_cohort.iloc[:, 1:].values,
    x=df_cohort.columns[1:], y=df_cohort['Cohort'],
    colorscale='Blues', zmin=50, zmax=100,
    colorbar=dict(title="Retention %")
))
fig_cohort.update_layout(title="<b>Cohort Analysis</b>", 
                         font=COMMON_FONT, 
                         title_font=COMMON_TITLE_FONT, 
                         height=300)
fig_cohort_html = to_html(fig_cohort, include_plotlyjs=False, full_html=False)

# --- Export HTML Layout ---
os.makedirs("outputs", exist_ok=True)
html_content = f"""
<html>
<head>
    <meta charset='UTF-8'>
    <title> SaaS Financial Dashboard </title>
    <script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
    <style>
        body {{
            font-family: {FONT_FAMILY};
            background-color: #f5f7fa;
            padding: 40px;
        }}
        h1 {{
            text-align: center;
            font-size: 28px;
            margin-bottom: 30px;
        }}
        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
    </style>
</head>
<body>
    <h1>Finmark-Style SaaS Dashboard</h1>
    <div class="grid-4">
        {''.join(f'<div class="card">{card}</div>' for card in fig_cards)}
    </div>
    <div class="grid-2">
        <div class="card">{fig_arr_html}</div>
        <div class="card">{fig_cohort_html}</div>
        <div class="card">{fig_emp_html}</div>
        <div class="card">{fig_exp_html}</div>
    </div>
</body>
</html>
"""

with open("outputs/golden_image.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Dashboard exported to outputs/golden_image.html")
