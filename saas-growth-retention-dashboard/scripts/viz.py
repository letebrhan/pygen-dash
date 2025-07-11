
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
    title=dict(text="<b>ARR Changes with Net Growth</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    xaxis=dict(title='Month', type='category', categoryorder='array', tickfont=COMMON_AXIS_TICK_FONT),
    yaxis=dict(title='ARR ($)', tickprefix='$', tickfont=COMMON_AXIS_TICK_FONT),
    yaxis2=dict(title='Net Growth', tickprefix='$', overlaying='y', side='right', showgrid=False, tickfont=COMMON_AXIS_TICK_FONT),
    height=350,
    font=COMMON_FONT,
    legend=LEGEND, 
    plot_bgcolor='white',
    paper_bgcolor='white',

)

# --- Cohort Heatmap ---
fig_cohort = go.Figure(data=go.Heatmap(
    z=df_cohort.iloc[:, 1:].values,
    x=df_cohort.columns[1:], y=df_cohort['Cohort'],
    colorscale='Blues', zmin=50, zmax=100,
    colorbar=dict(title="Retention %")
))
fig_cohort.update_layout(title=dict(text="<b>Cohort Analysis</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
                         font=COMMON_FONT, 
                         xaxis=dict(title='Month', type='category', categoryorder='array', tickfont=COMMON_AXIS_TICK_FONT),
                         height=350)

# --- Employee Pie Chart ---
COLOR_PALETTE_EMPLOYEES = {
    "Sales": "#FDB45C",
    "Software Engineering": "#A3CDFD",
    "Customer Support": "#FECBA3",
    "Product Management": "#6FA8DC",
    "Marketing": "#F9B4A2",
    "Administration": "#FEC165",
    "Finance": "#B576C8",
    "HR": "#C6A3D8",
    "Legal": "#F3C1E0"
}
labels = df_employees['Department']
values = df_employees['Count']
fig_emp = go.Figure(go.Pie(
    labels=labels,
    values=values,
    hole=0.4,
    marker=dict(colors=[COLOR_PALETTE_EMPLOYEES.get(dept, "#CCCCCC") for dept in labels])
))
total_employees = values.sum()
fig_emp.update_layout(
    annotations=[dict(text=str(total_employees), x=0.75, y=0.5, font_size=24, showarrow=False)],
    title=dict(text="<b>Employees by Department</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    height=350,
    font=COMMON_FONT,
    legend=LEGEND.update(orientation="v"),
)

# --- Expenses Line Chart ---
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
categories = ['R&D', 'Marketing', 'Ops']
fig_exp = go.Figure()
for col in categories:
    fig_exp.add_trace(go.Scatter(x=df_expenses['Month'], 
                                 y=df_expenses[col], mode='lines+markers', 
                                 name=col))
fig_exp.update_layout(title=dict(text="<b>Expenses</b>", x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
                      font=COMMON_FONT, 
                      xaxis=dict(title='Month', type='category', categoryorder='array', tickfont=COMMON_AXIS_TICK_FONT),
                      yaxis=dict(title='Exp ($)', tickprefix='$', tickfont=COMMON_AXIS_TICK_FONT),
                      legend=LEGEND.update(orientation="h"),
                      height=350,
                      plot_bgcolor='white',
		            paper_bgcolor='white',
		)



fig_arr.update_layout(margin=dict(b=80, t=80))
fig_exp.update_layout(margin=dict(b=80, t=80))
fig_emp.update_layout(margin=dict(b=50, t=80))
fig_cohort.update_layout(margin=dict(b=50, t=80))

# Generate HTML strings from plots
fig1_html = to_html(fig_arr, include_plotlyjs='cdn', full_html=False)
fig2_html = to_html(fig_cohort, include_plotlyjs=False, full_html=False)
fig3_html = to_html(fig_emp, include_plotlyjs=False, full_html=False)
fig4_html = to_html(fig_exp, include_plotlyjs=False, full_html=False)


# --- Export HTML Layout ---
os.makedirs("outputs", exist_ok=True)

html_content = f"""
<html>
<head>
    <meta charset="UTF-8">
    <title>SaaS Growth, Expense & Retention Dashboard</title>
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
    <div class="dashboard-title">SaaS Growth, Expense & Retention Dashboard</div>
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
with open("outputs/dashboard.html", "w") as f:
    f.write(html_content)

print("Dashboard exported to outputs/dashboard.html")

