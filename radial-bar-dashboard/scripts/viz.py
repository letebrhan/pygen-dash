# scripts/viz.py

import os
import html
import pandas as pd
import numpy as np
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
    
os.makedirs("outputs", exist_ok=True)

# Load data
df_categories = load_data("data/product_categories.csv")
df_product = load_data("data/product_items.csv")

# Clean and convert percentage strings to floats
for df in [df_categories, df_product]:
    for col in ["Fixed", "Repairable", "End of Life"]:
        df[col] = df[col].str.replace('%', '').astype(float)

# Sort and select Top 10 categories by Total
df_categories_top_10 = df_categories.sort_values(by="Total", ascending=True).head(10)
# Filter products by Top 20 Total values
df_product_top_20 = df_product.sort_values(by="Total", ascending=False).head(20)

# ----Standardize Constants ---
STATUSES = ["Fixed", "Repairable", "End of Life"]

# --- Commmon Style ---
FONT_FAMILY = "Segoe UI, Helvetica Neue, Arial, sans-serif"
FONT_COLOR = "#333333"
FONT_WEIGHT = "bold"
COMMON_TITLE_FONT = dict(family=FONT_FAMILY, size=18, color=FONT_COLOR)
COMMON_FONT = dict(family=FONT_FAMILY, size=14, color=FONT_COLOR)
COMMON_AXIS_TICK_FONT = dict(family=FONT_FAMILY, size=10, color=FONT_COLOR)

# Color palette
colors = {
    "Fixed": "#99d8a3", 
    "Repairable": "#85C1E9", 
    "End of Life": "#d3d3d3"  
}

LEGEND = dict(
        font=dict(family=FONT_FAMILY, size=12, color=FONT_COLOR),
        orientation="h",
        bgcolor="white",
        bordercolor="#dddddd",
        borderwidth=1,
        x=0.5, y=-0.25, xanchor="center"
    )

RADIALAXIS = dict(
            tickangle=0, # Horizontal labels
            tickvals=[0, 20, 40, 60, 80, 100],
            ticktext=["0%", "20%", "40%", "60%", "80%", "100%"],
            showticklabels=True,
            linecolor='black',
            linewidth=1,
            tickfont=COMMON_AXIS_TICK_FONT  # match black theme
        )

ANGULARAXIS = dict(
                visible=False,
                rotation=0,
                direction="counterclockwise",
                showline=True,
                gridcolor='white',
                linecolor='white',
                tickfont=dict(family=FONT_FAMILY, size=9, color=FONT_COLOR)
        )

# --- Data Preparation ---
# Creating KPI cards
def build_kpi_block_repairs():

    # Clean numeric columns
    df_product["Fixed Cnt"] = pd.to_numeric(df_product["Fixed Cnt"], errors="coerce")
    df_product["Repairable Cnt"] = pd.to_numeric(df_product["Repairable Cnt"], errors="coerce")
    df_product["End of Life Cnt"] = pd.to_numeric(df_product["End of Life Cnt"], errors="coerce")

    df = df_product.copy()
    # KPI calculations
    number_of_repairs = int(df["Fixed Cnt"].sum() + df["Repairable Cnt"].sum() + df["End of Life Cnt"].sum())
    total_fixed = df["Fixed Cnt"].sum()
    status_fixed_pct = round((total_fixed / number_of_repairs) * 100)
    n_categories = df["Category"].nunique()
    n_products = df["Product"].nunique() if "Product" in df.columns else df.shape[0]

    card_html = '<div class="card-grid">'

    # Build card components
    kpis = [
        ("Number of Repairs", f"{number_of_repairs:,}", ""),
        ("Status Fixed", f"{status_fixed_pct}%", ""),
        ("Categories", str(n_categories), ""),
        ("Products", str(n_products), "")
    ]

    for title, value, subtext in kpis:
        card_html += f'''
            <div class="summary-card">
                <div class="summary-title">{title}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-subtext">{subtext}</div>
            </div>
        '''

    card_html += '</div>'
    return card_html

# Function for radial stacks
def make_radial_traces(df_percent, label_col, angle_range):
    n = len(df_percent)

    bar_width = (angle_range[1] - angle_range[0]) / n * 0.8
    theta_values = np.linspace(angle_range[0], angle_range[1], n, endpoint=False) + bar_width / 2

    customdata = np.stack([
        df_percent[label_col],  # Category or Product
        df_percent["Fixed"],
        df_percent["Repairable"],
        df_percent["End of Life"]
    ], axis=-1)

    traces = []
    for status in STATUSES:
        if status == "Fixed":
            base = 0
        else:
            base = df_percent[STATUSES].loc[:, :status].drop(columns=[status]).sum(axis=1)

        traces.append(go.Barpolar(
            r=df_percent[status],
            base=base,
            theta=theta_values,
            width=[bar_width] * n,
            marker_color=colors[status],
            name=status,
            showlegend=True,
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "Fixed: %{customdata[1]:.1f}%<br>" +
                "Repairable: %{customdata[2]:.1f}%<br>" +
                "End of Life: %{customdata[3]:.1f}%<br>" 
            ),
        ))

    return traces

def outer_arc_text_layer(df_top_records, label_col, angle_range, r_multiplier=1.25):

    if label_col == 'Product':
        df_top_records["Product"] = df_top_records["Product"].str.replace(" - ", "<br>")

    n = len(df_top_records)
    bar_width = (angle_range[1] - angle_range[0]) / n * 0.8
    theta_values = np.linspace(angle_range[0], angle_range[1], n, endpoint=False) + bar_width / 2

    max_r = df_top_records[STATUSES].sum(axis=1).max()
    r_values = [max_r * r_multiplier] * n

    labels = [
        f"{df_top_records[label_col].iloc[i]}<br>{int(df_top_records['Total'].iloc[i]):,}"
        for i in range(n)
    ]

    # Flip text angles if upside-down (for readability)
    angles = []
    for t in theta_values:
        t_mod = t % 360
        if 90 < t_mod < 270:
            angles.append((t + 180) % 360)  # Flip angle for readability
        else:
            angles.append(t)

    # Add text trace
    text_trace = go.Scatterpolar(
        r=r_values,
        theta=theta_values,
        mode="text",
        text=labels,
        textfont=dict(size=10, family=FONT_FAMILY, color="#333333"),
        hoverinfo="skip",
        showlegend=False,
        cliponaxis=False
    )

    # Add radial leader lines
    line_trace = go.Scatterpolar(
        r=np.tile([0, max_r * r_multiplier * 0.94], n),
        theta=np.repeat(theta_values, 2),
        mode="lines",
        line=dict(color="#BBBBBB", width=0.6),
        hoverinfo="skip",
        showlegend=False
    )

    return [text_trace, line_trace]

# Add left chart (0°–90°)
fig_first_quadrant = go.Figure()
for trace in make_radial_traces(df_categories_top_10, "Category", (0, 90)):
    fig_first_quadrant.add_trace(trace)

# 90°: no rotation
for trace in outer_arc_text_layer(df_categories_top_10, "Category", (0, 90)):
    fig_first_quadrant.add_trace(trace)

# Layout settings
fig_first_quadrant.update_layout(title=dict(text="<b>Top 10 Product Categorie</b>", 
                                            x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    font=COMMON_FONT,
    height=550,
    polar=dict(
        sector=[0, 90],  # Limit only the first polar (Top 10 Categories)
        angularaxis=ANGULARAXIS,
        bgcolor="#f0f4f8" ,
        radialaxis=RADIALAXIS
    ),
    legend=LEGEND,
    margin=dict(t=100, b=60, l=100, r=40),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Add right chart (0°–360°)
fig_full_circle = go.Figure()
for trace in make_radial_traces(df_product_top_20, "Product", (0, 360)):
    fig_full_circle.add_trace(trace)

# 360°: rotate labels
for trace in outer_arc_text_layer(df_product_top_20, "Product", (0, 360), r_multiplier=1.4):
    fig_full_circle.add_trace(trace)

# Layout settings
fig_full_circle.update_layout(title=dict(text="<b>Top 20 Most Presented Products</b>", 
                                         x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
    font=COMMON_FONT,
    height=550,
    polar=dict(  # Full circle for second plot
        angularaxis=ANGULARAXIS,
        bgcolor="#f0f4f8",
        radialaxis=RADIALAXIS
    ),
    margin=dict(t=100, b=60, l=100, r=40),
    legend=LEGEND,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

def make_datatable_html(df, table_id, title):

    headers = ''.join([f"<th>{html.escape(col)}</th>" for col in df.columns])
    rows = ''
    for _, row in df.iterrows():
        row_html = ''
        for col in df.columns:
            value = str(row[col])
            if 'Fixed' in col and '%' in value:
                row_html += f'<td style="color:green;"><strong>{html.escape(value)}</strong></td>'
            else:
                row_html += f'<td>{html.escape(value)}</td>'
        rows += f"<tr>{row_html}</tr>"

    return f"""
    <div id="{table_id}" class="data-table">
        <h3 style='margin-bottom:10px; text-align:center'>{title}</h3>
        <p style='text-align: left; font-size: 14px; color: gray;'>⬇️ Use buttons below to download or Copy table data</p>
        <table id="{table_id}-table" class="display nowrap" style="width:100%">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows}</tbody>
        </table>
        <div style="margin-top:10px;">
            <button onclick="resetFilters('{table_id}-table')" class="toggle-button">Reset All Filters</button>
            <button onclick="closeTable('{table_id}')" class="toggle-button">Close Table</button>
        </div>
    </div>
    """

# Generate the HTML block for the current KPI values
kpi_html_block = build_kpi_block_repairs()

# Generate HTML strings from plots
fig2_html = to_html(fig_first_quadrant, include_plotlyjs='cdn', full_html=False)
fig3_html = to_html(fig_full_circle, include_plotlyjs=False, full_html=False)

# Generate both tables
category_table_html = make_datatable_html(df_categories, "category", "Product Categories")
product_table_html = make_datatable_html(df_product, "product", "Product Items")

card_styles = """
    <style>
        .card-grid {
            display: grid;
            gap: 20px;
            justify-content: center;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            flex-wrap: wrap;
             width: 100%;
            margin-bottom: 30px;
        }
        .summary-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            padding: 20px;
            width: 100%;
            box-sizing: border-box;
            text-align: center;
            border-left: 6px solid #2c5282;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .summary-title {
            font-size: 22px;
            font-family: {FONT_FAMILY};
            font-weight: bold;
            color: #2c5282;
            margin-bottom: 5px;
        }
        .summary-value {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .summary-subtext {
            font-size: 12px;
            color: #999;
        }

    </style>
"""
chart_styles = """"
    <style>
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
        }

        .card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 20px;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            overflow: visible;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .grid-2  {
                flex-direction: column;
                align-items: center;
            }
            .card {
                width: 100%;
            }
        }
    </style>
"""

table_style = """
<style>
    /* Button styles */
    .toggle-button {
        background: linear-gradient(to bottom, #4a90e2, #2c5282);
        border: 1px solid #1a365d;
        border-radius: 6px;
        color: #fff;
        font-weight: bold;
        font-size: 14px;
        padding: 8px 16px;
        margin-right: 10px;
        cursor: pointer;
        box-shadow: inset 0 -1px 0 rgba(0,0,0,0.2);
        transition: background 0.2s ease;
    }

    .data-toggle-buttons {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 10px;
        margin-bottom: 20px;
    }

    /* Datatable layout */
    .data-table {
        display: none;
        margin-top: 10px;
    }
    .data-table.active {
        display: block;
    }

    table.dataTable {
        width: 100% !important;
    }

    .dataTables_wrapper {
        overflow-x: auto;
    }

    /* Add outer border and spacing */
    table.display {
        border: 1px solid #cccccc;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
        background-color: white;
        margin-top: 10px;
    }

    /* Target all DataTables-initialized header cells */
    table.display thead th {
        background-color: #396e99;
        color: white;
        font-weight: bold;
        font-size: 15px;
        padding: 12px 8px;
        text-align: center;
        white-space: nowrap;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }

    table.display th, table.display td {
        border-bottom: 1px solid #e0e0e0;
    }

    /* Table body cells */
    table.display tbody td {
        font-size: 13px;
        padding: 10px 8px;
        color: #222;
        text-align: center;
        white-space: nowrap;
    }

    th.dt-center, td.dt-center {
        text-align: center;
        white-space: nowrap;
    }

    @media (max-width: 768px) {
        .data-table {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
    }

</style>

"""
table_script = """
<script>

    function showTable(tableId) {{
        $('.data-table').removeClass('active');
        const target = $('#' + tableId);
        target.addClass('active');

        const table = $('#' + tableId + '-table').DataTable();
        setTimeout(() => {{
            table.columns.adjust().draw(false);
        }}, 10);  // short delay ensures layout is stable
    }}

    function closeTable(tableId) {{
        $('#' + tableId).removeClass('active');
    }}

    function resetFilters(tableId) {{
        let table = $('#' + tableId).DataTable();
        table.search('').columns().search('').draw();
    }}

    $(document).ready(function() {
        $('table.display').DataTable({
            dom: 'Bfrtip',
            buttons: [
                'copyHtml5',
                'excelHtml5',
                'csvHtml5'
            ],
            scrollX: true,
            responsive: true,
            autoWidth: false,
            pageLength: 20,
            columnDefs: [
                { targets: "_all", className: "dt-center" }
            ]
        });
    });


    window.addEventListener('resize', () => {{
        document.querySelectorAll('.js-plotly-plot').forEach(el => Plotly.Plots.resize(el));
    }});

</script>
"""

# --- Export HTML Layout ---
html_content = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repair Cafe Dashboard </title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/responsive/2.4.1/css/responsive.dataTables.min.css">

    <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/responsive/2.4.1/js/dataTables.responsive.min.js"></script>

    <title> Repair Outcomes — Radial Breakdown</title>
    <style>
        body {{
            font-family: {FONT_FAMILY};
            background-color: #f5f7fa;
            margin: 0;
            padding: 40px;
        }}
        .dashboard-title {{
            background-color: #4678a0;
            color: white;
            text-align: center;
            font-size: 30px;
            font-weight: bold;
            padding: 12px 0;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
    </style>
    {card_styles}
    {chart_styles}
    {table_style}
</head>
<body>
    <div class="dashboard-title"> Repair Cafe Dashboard</div>
        {kpi_html_block}
    <div class="grid-2">
        <div class="card">{fig2_html}</div>
        <div class="card">{fig3_html}</div>
    </div>
    <div class="data-toggle-buttons">
        <strong>Open Table:</strong>
        <button class="toggle-button" onclick="showTable('category')">Categories</button>
        <button class="toggle-button" onclick="showTable('product')">Products</button>
    </div>
    {category_table_html}
    {product_table_html}
    {table_script}
</body>
<footer>
    <div style="text-align:center; margin-top:20px; font-size:12px; color:gray;">
    © 2025 Repair Cafe Dashboard. Powered by Plotly.
</div>
</footer>
</html>
"""
# Save to outputs/golden_image.html
with open("outputs/dashboard.html", "w") as f:
    f.write(html_content)

print("Dashboard exported to outputs/dashboard.html")
