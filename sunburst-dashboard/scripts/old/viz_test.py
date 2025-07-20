import pandas as pd
import plotly.graph_objects as go

# Load the updated dataset
df = pd.read_csv("data/sunburst_bike_data.csv")

# Create the sunburst chart
fig = go.Figure(go.Sunburst(
    labels=df["id"],
    parents=df["parent"],
    values=df["value"],
    branchvalues="total",
    hovertemplate="<b>%{label}</b><br>Sales: %{value:$,.2f}<extra></extra>",
    customdata=df["id"]
))

# Update chart layout for clarity and polish
fig.update_layout(
    title_text="Bike Sales Breakdown (5-Level Sunburst)",
    title_font=dict(size=24, family="Arial Black"),
    margin=dict(t=50, l=0, r=0, b=10),
    uniformtext=dict(minsize=10, mode="hide"),
    width=1000,
    height=800
)

# Export as interactive HTML
fig.write_html("outputs/sunburst_bike_chart.html", full_html=True, include_plotlyjs="cdn")

