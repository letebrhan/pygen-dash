
import pandas as pd
import plotly.graph_objects as go
import os

# Load data
df = pd.read_csv("data/sunburst_bike_sales.csv")

# Compute total and female sales
total_sales = df["Sales"].sum()
female_sales = df[df["Gender"] == "Female"]["Sales"].sum()
female_pct = round(female_sales / total_sales * 100)

# Format currency for European style
def euro_format(value):
    return f"${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

formatted_sales = euro_format(female_sales)
initial_center_label = f"<b>{female_pct}%</b><br>Female<br>{formatted_sales}"

# Create hierarchy
df["Total"] = "Total"
hierarchy = ["Total", "Year", "Gender", "Category", "Subcategory", "Model"]

# Labels and parents
labels = df[hierarchy].apply(lambda row: row[-1], axis=1)
parents = df[hierarchy].apply(lambda row: row[-2], axis=1)
values = df["Sales"]

# Build figure with custom hovertemplate to update center
fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    hovertemplate="<b>%{label}</b><br>Sales: %{value:,}<extra></extra>",
    insidetextorientation="radial",
    root_color="white",
    marker=dict(line=dict(width=1, color="white"))
))

# Add static initial annotation
fig.update_layout(
    margin=dict(t=40, l=0, r=0, b=0),
    title="<b>Sunburst Chart — Category Breakdown</b>",
    annotations=[dict(
        text=initial_center_label,
        x=0.5, y=0.5,
        font=dict(size=20, color="black"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
        align='center',
        bgcolor='white',
        bordercolor='white',
        borderwidth=2,
        opacity=1,
        name="center_text"
    )]
)

# Inject JavaScript for dynamic hover
fig.update_layout(
    updatemenus=[{
        "buttons": [],
        "type": "buttons",
        "direction": "left"
    }],
    hovermode="closest"
)

# Add custom JavaScript to override the center dynamically
custom_script = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    const plot = document.querySelector('.js-plotly-plot');
    const center = document.querySelector('.svg-container .infolayer .annotation');

    plot.on('plotly_hover', function(event) {
        const point = event.points[0];
        if (!point) return;
        const value = point.value.toLocaleString('de-DE');
        const label = point.label;
        if (center) {
            center.innerHTML = `<tspan style='font-weight:bold'>${label}</tspan><tspan x='0' dy='1.2em'>Sales</tspan><tspan x='0' dy='1.2em'>$ ${value}</tspan>`;
        }
    });

    plot.on('plotly_unhover', function() {
        if (center) {
            center.innerHTML = `<tspan style='font-weight:bold'>{female_pct}%</tspan><tspan x='0' dy='1.2em'>Female</tspan><tspan x='0' dy='1.2em'>{formatted_sales}</tspan>`;
        }
    });
});
</script>
""".replace("{female_pct}", str(female_pct)).replace("{formatted_sales}", formatted_sales)

# Save as HTML with embedded script
os.makedirs("outputs", exist_ok=True)
html_path = "outputs/dashboard_dynamic.html"
fig.write_html(html_path, include_plotlyjs="cdn", full_html=True, post_script=custom_script)
