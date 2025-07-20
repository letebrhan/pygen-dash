from dash import Dash, html, dcc
import plotly.graph_objects as go
import numpy as np

app = Dash(__name__)
app.title = "Finmark Style SaaS Dashboard"

# --- Metric Cards ---
def generate_metric_card(title, value, delta="+4.2%", delta_color="green"):
    return go.Figure(go.Indicator(
        mode="number+delta",
        value=float(value.strip('$').replace(',', '')),
        number={'prefix': '$', 'font': {'size': 24}},
        delta={'position': "right", 'reference': 0, 'valueformat': '.1f',
               'increasing': {'color': delta_color}, 'decreasing': {'color': 'red'}},
        title={"text": f"<b>{title}</b>"}
    )).update_layout(height=120, margin=dict(t=10, b=10, l=10, r=10))

# --- ARR Changes (Stacked Bar) ---
def stacked_bar_chart():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    upgrade = np.random.randint(5, 10, size=6)
    downgrade = np.random.randint(1, 3, size=6)
    churn = np.random.randint(2, 5, size=6)
    new = np.random.randint(3, 6, size=6)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=upgrade, name='Upgrade'))
    fig.add_trace(go.Bar(x=months, y=new, name='New'))
    fig.add_trace(go.Bar(x=months, y=downgrade, name='Downgrade'))
    fig.add_trace(go.Bar(x=months, y=churn, name='Churn'))
    fig.update_layout(barmode='stack', title='<b>ARR Changes</b>', height=300)
    return fig

# --- Employee Pie Chart ---
def employee_pie_chart():
    labels = ['Engineering', 'Sales', 'HR', 'Marketing', 'Support']
    values = [34, 10, 4, 6, 8]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
    fig.update_layout(title="<b>Employees by Department</b>", height=300)
    return fig

# --- Expenses Line Chart ---
def expenses_line_chart():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    categories = ['R&D', 'Marketing', 'Ops']
    fig = go.Figure()
    for c in categories:
        fig.add_trace(go.Scatter(x=months, y=np.random.uniform(1000, 6000, size=6),
                                 mode='lines+markers', name=c))
    fig.update_layout(title="<b>Expenses</b>", height=300)
    return fig

# --- Cohort Heatmap ---
def cohort_heatmap():
    months = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
    cohorts = ['Nov 21', 'Dec 21', 'Jan 22', 'Feb 22', 'Mar 22', 'Apr 22']
    z = np.random.choice([100, 97, 91, 86, 88, 84], size=(6, 6))

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=months,
        y=cohorts,
        colorscale='Blues',
        zmin=80,
        zmax=100,
        showscale=True,
        colorbar=dict(title="Retention")
    ))
    fig.update_layout(title="<b>Cohort Analysis</b>", height=300)
    return fig

# --- Layout ---
app.layout = html.Div(style={'fontFamily': 'Segoe UI, Arial', 'padding': '20px', 'backgroundColor': '#f5f7fa'}, children=[
    html.H1("SaaS Financial Dashboard", style={'textAlign': 'center'}),

    html.Div(style={'display': 'flex', 'gap': '20px', 'justifyContent': 'center'}, children=[
        dcc.Graph(figure=generate_metric_card("ARR", "$42964810"), config={'displayModeBar': False}),
        dcc.Graph(figure=generate_metric_card("Bookings", "$2019600"), config={'displayModeBar': False}),
        dcc.Graph(figure=generate_metric_card("Cash Balance", "$15150500"), config={'displayModeBar': False}),
        dcc.Graph(figure=generate_metric_card("Burn Rate", "$600000"), config={'displayModeBar': False}),
    ]),

    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginTop': '30px'}, children=[
        dcc.Graph(figure=stacked_bar_chart()),
        dcc.Graph(figure=cohort_heatmap()),
        dcc.Graph(figure=employee_pie_chart()),
        dcc.Graph(figure=expenses_line_chart())
    ])
])

if __name__ == "__main__":
    app.run(debug=True)
