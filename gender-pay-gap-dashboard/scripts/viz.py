import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc
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

# Load CSV data
df_gap = load_data("data/pay_gap_summary.csv")
df_quart = load_data("data/pay_quartiles.csv")
df_bonus = load_data("data/bonus_participation.csv")
df_sankey = load_data("data/sankey_flow.csv")
df_comp = load_data("data/pay_gap_comparison.csv")
df_retention_heatmap = load_data("data/retention_heatmap.csv")


companies = df_gap["Company"].unique().tolist()
years = df_gap["Year"].unique().tolist()

# --- Commmon Style ---
FONT_FAMILY = "Segoe UI, Helvetica Neue, Arial, sans-serif"
# --- Legend Style ---
LEGEND = dict(
    font=dict(family=FONT_FAMILY, size=13, color="#333333"),
    orientation="h", y=-0.3, x=0.5, xanchor="center",
    bgcolor="white", bordercolor="#dddddd", borderwidth=1
)
COMMON_FONT = dict(family=FONT_FAMILY, size=13, color="#333333")
COMMON_TITLE_FONT = dict(family=FONT_FAMILY, size=18, color="#333333")
COMMON_AXIS_TITLE_FONT = dict(family=FONT_FAMILY, size=16, color="#333333")
COMMON_AXIS_TICK_FONT = dict(family=FONT_FAMILY, size=12, color="#333333")


def wrap_plotly(fig, include_plotlyjs=False):
    html_chart = to_html(fig, include_plotlyjs=include_plotlyjs, 
                         full_html=False, 
                         config={"responsive": True},
                         default_height="100%",
                         default_width="100%"
                    )
    html_content = f'<div class="plotly-inner" >{html_chart}</div>'
    
    return html_content
 
def build_kpi_block(year, company):
    # Filter by selected year and company
    summary = df_gap[(df_gap["Year"] == year) & (df_gap["Company"] == company)]
    
    card_html = '<div class="card-grid">'
    # Match metric name to readable title
    for metric, title in zip(
        ["Mean Hourly Pay", "Median Hourly Pay", "Mean Bonus Pay", "Median Bonus Pay"],
        ["Mean Pay Gap", "Median Pay Gap", "Mean Bonus Gap", "Median Bonus Gap"]
    ):
        row = summary[summary["Metric"] == metric]
        if row.empty:
            continue  # Skip if metric is missing
        male = row["Male"].values[0]
        female = row["Female"].values[0]
        gap = round(((male - female) / male) * 100, 1)
        card_html += f'''
            <div class="summary-card">
                <div class="summary-title">{title}</div>
                <div class="summary-value">{gap}%</div>
                <div class="summary-subtext">Higher for men</div>
            </div>
        '''
    card_html += '</div>'
    return card_html

def generate_bonus_card(year, company):
    bonus = df_bonus[(df_bonus["Year"] == year) & (df_bonus["Company"] == company)]
    if bonus.empty:
        return "<p>No bonus data available</p>"

    rows_html = ""
    for _, row in bonus.iterrows():
        gender = row["Gender"]
        participation = row["Bonus Participation (%)"]
        rows_html += f"<tr><td>{gender}</td><td>{participation}%</td></tr>"

    return f"""
    <div class="bonus-table-wrapper">
        <h3 style="text-align: center;">Bonus Participation ({year}) – {company}</h3>
        <table class="bonus-table">
            <thead>
                <tr>
                    <th>Gender</th>
                    <th>Bonus Participation (%)</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

def render_quartiles(year, company):
    quart = df_quart[(df_quart["Year"] == year) & (df_quart["Company"] == company)]
    
    if quart.empty:
        return "<p>No quartile data available</p>"
    
    df_pivot = quart.pivot(index="Quartile", columns="Gender", values="Percentage").fillna(0)
    # Chose stacked horizontal bar to emphasize distribution order
    # Order matters: Q4 is lowest, Q1 is highest
    quartile_order = ["Q4 - Lower", "Q3 - Lower Mid", "Q2 - Upper Mid", "Q1 - Upper"]
    df_pivot = df_pivot.loc[quartile_order]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df_pivot.index, x=df_pivot["Male"], name="Male", orientation="h",
                         marker_color="teal", text=df_pivot["Male"], textposition="inside"))
    fig.add_trace(go.Bar(y=df_pivot.index, x=df_pivot["Female"], name="Female", orientation="h",
                         marker_color="tomato", text=df_pivot["Female"], textposition="inside"))
    chart_title = f"<b>Proportion of men and women in each pay quartile ({year}) – {company}</b>"
    fig.update_layout(
        barmode="stack",
        title=dict(text=chart_title, x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
        xaxis=dict(title='Percentage', ticksuffix='%',
                   tickfont=COMMON_AXIS_TICK_FONT),
        yaxis=dict(title='Quartile',  tickfont=COMMON_AXIS_TICK_FONT),
        font=COMMON_FONT, 
        xaxis_title="Percentage", yaxis_title="Quartile",
        legend=LEGEND,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return wrap_plotly(fig, include_plotlyjs='cdn')

def plot_sankey_flow(year, company):
    sankey_filtered = df_sankey[(df_sankey["Year"] == year) & (df_sankey["Company"] == company)].copy()
    if sankey_filtered.empty:
        return "<p>No sankey data available</p>"

    # Define professional color maps
    SOURCE_COLOR_MAP = {
        "Q1 - Upper": "#6BAED6",
        "Q2 - Upper Mid": "#9ECAE1",
        "Q3 - Lower Mid": "#C6DBEF",
        "Q4 - Lower": "#DEEBF7"
    }
    TARGET_COLOR_MAP = {
        "Bonus": "#4CAF50",
        "No Bonus": "#FFC107",
        "Exit": "#F44336"
    }

    # Build node list and index map
    unique_sources = sorted(sankey_filtered["Source"].unique().tolist())
    unique_targets = sorted(sankey_filtered["Target"].unique().tolist())
    nodes = unique_sources + unique_targets
    node_map = {label: i for i, label in enumerate(nodes)}

    # Sankey input values
    source = [node_map[s] for s in sankey_filtered["Source"]]
    target = [node_map[t] for t in sankey_filtered["Target"]]
    value = sankey_filtered["Value"]

    # Generate custom hover text: "Q1 - Upper → Bonus: 38.7%"
    customdata = sankey_filtered.apply(
        lambda row: f"{row['Source']} → {row['Target']}: {row['Value']:.1f}%", axis=1
    )

    # Node colors
    node_colors = [
        SOURCE_COLOR_MAP.get(n, TARGET_COLOR_MAP.get(n, "#B0BEC5")) for n in nodes
    ]

    # Link colors based on source
    def rgba(hex_color, opacity=0.4):
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r},{g},{b},{opacity})"

    link_colors = [rgba(node_colors[src], 0.5) for src in source]

    # Build Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="gray", width=0.5),
            label=nodes,
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            customdata=customdata,
            hovertemplate="%{customdata}<extra></extra>"
        )
    )])

    chart_title = f"<b>Pay Flow Sankey (Breakdown) ({year}) – {company}</b>"
    fig.update_layout(
        title=dict(text=chart_title, x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
        font=COMMON_FONT,
        margin=dict(t=80, l=40, r=40, b=40),
        autosize=True
    )

    return wrap_plotly(fig)

def plot_treemap_chart(year, company):
    df = df_sankey[(df_sankey["Year"] == year) & (df_sankey["Company"] == company)].copy()
    if df.empty:
        return "<p>No data for treemap</p>"

    fig = px.treemap(
        df,
        path=["Source", "Target"],  # 2-level hierarchy
        values="Value",
        color="Value",
        color_continuous_scale=["#DDEEFF", "#88B9E3", "#4B85C1", "#1F4E79"],
        hover_data={"Value": True}
    )

    fig.update_traces(
        texttemplate="%{label}<br>%{value:.1f}%",
        hovertemplate='<b>%{label}</b><br>Flow: %{value:.1f}%<extra></extra>'
    )

    chart_title = f"<b>Pay Flow Treemap ({year}) – {company}</b>"
    fig.update_layout(
        title=dict(text=chart_title, x=0.5, xanchor="center", font=COMMON_TITLE_FONT),
        margin=dict(t=60, l=10, r=10, b=10),
        autosize=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=COMMON_FONT
    )

    return wrap_plotly(fig)

def build_heatmap_chart(year, company):
    df = df_retention_heatmap[
        (df_retention_heatmap["Year"] == year) &
        (df_retention_heatmap["Company"] == company)
    ]
    if df.empty:
        return "<p>No heatmap data available</p>"

    df_avg = df.groupby(["Quartile", "Gender"])["Retention (%)"].mean().reset_index()
    df_pivot = df_avg.pivot(index="Quartile", columns="Gender", values="Retention (%)").fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.tolist(),
        y=df_pivot.index.tolist(),
        colorscale='Viridis',
        zmin=0, zmax=100,
        colorbar=dict(title="Retention (%)"),
        hovertemplate="Quartile: %{y}<br>Gender: %{x}<br>Retention: %{z:.1f}%<extra></extra>"
    ))

    chart_title = f"<b>Quartile Heatmap ({year}) – {company}</b>"
    fig.update_layout(
        title=dict(text=chart_title, x=0.5, xanchor='center', font=COMMON_TITLE_FONT),
        xaxis=dict(title='Gender', type='category', tickfont=COMMON_AXIS_TICK_FONT),
        yaxis=dict(title='Quartile', tickfont=COMMON_AXIS_TICK_FONT),
        autosize=True,
        margin=dict(t=40, l=30, r=30, b=30),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=COMMON_FONT
    )
    return wrap_plotly(fig)

def compare_gender_pay_gap():
    import html
    df_comp = pd.read_csv("data/pay_gap_comparison.csv")
    percent_cols = [col for col in df_comp.columns if "%" in col]

    headers = ''.join([f"<th>{html.escape(col)}</th>" for col in df_comp.columns])
    rows = ''
    for _, row in df_comp.iterrows():
        row_html = ''.join([
            f"<td>{row[col]}%</td>" if col in percent_cols else f"<td>{html.escape(str(row[col]))}</td>"
            for col in df_comp.columns
        ])
        rows += f"<tr>{row_html}</tr>"

    return f"""
    <h3 style='margin:10px; text-align: center;'>Comparison Table (Multi-company/year)</h3>
    <p style='text-align: left; font-size: 14px; color: gray;'>⬇️ Use buttons below to download, copy, or print this table</p>
    <table id="comparison-table" class="display" style="width:100%">
        <thead><tr>{headers}</tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """

year_default = 2023
company_default = "Ryanair"
# Build dashboard HTML with corrected class names and data attributes
cards_html = ""
for year in years:
    for company in companies:
       cards_html += f"""
            <div class="section">
                <div class="card card-summary" data-year="{year}" data-company="{company}">
                    {build_kpi_block(year, company)}
                </div>
                <div class="card card-bonus" data-year="{year}" data-company="{company}">
                    {generate_bonus_card(year, company)}
                </div>
                <div class="grid-2">
                    <div class="card" data-year="{year}" data-company="{company}">
                        {render_quartiles(year, company)}
                    </div>
                    <div class="card" data-year="{year}" data-company="{company}">
                        {plot_sankey_flow(year, company)}
                    </div>
                </div>

                <div class="grid-2">
                    <div class="card" data-year="{year}" data-company="{company}">
                        {plot_treemap_chart(year, company)}
                    </div>
                    <div class="card" data-year="{year}" data-company="{company}">
                        {build_heatmap_chart(year, company)}
                    </div>
                </div>
            </div>
        """


cards_html += f"""
    <div class="card static-card">
        {compare_gender_pay_gap()}
    </div>

"""

dropdown_html = f"""
    <div class="filter-bar">
        <label for='yearToggle'>Select Year:</label>
        <select id='yearToggle' onchange='updateCards()'>
            {''.join([f"<option value='{year}' {'selected' if year == year_default else ''}>{year}</option>" for year in years])}
        </select>

        <label for='companyToggle'>Select Company:</label>
        <select id='companyToggle' onchange='updateCards()'>
            {''.join([f"<option value='{company}' {'selected' if company == company_default else ''}>{company}</option>" for company in companies])}
        </select>
    </div>

"""
dropdown_script = f"""
<script>
    function updateCards() {{
        const year = document.getElementById("yearToggle").value;
        const company = document.getElementById("companyToggle").value;

        const selectors = ['.card:not(.static-card)', '.card-summary', '.card-bonus'];

        // Hide all elements first
        selectors.forEach(function(selector) {{
            document.querySelectorAll(selector).forEach(function(el) {{
                el.style.display = 'none';
            }});
        }});

        // Show only matching year and company
        selectors.forEach(function(selector) {{
            const toShow = document.querySelectorAll(`${{selector}}[data-year="${{year}}"][data-company="${{company}}"]`);
            toShow.forEach(function(el) {{
                el.style.display = 'block';
            }});
        }});

        setTimeout(resizeAllPlotlyCharts, 100);
    }}

    function resizeAllPlotlyCharts() {{
        if (window.Plotly) {{
            document.querySelectorAll(".plotly").forEach(function(el) {{
                Plotly.Plots.resize(el);
            }});
        }}
    }}

    window.addEventListener('load', function() {{
        updateCards();
        setTimeout(resizeAllPlotlyCharts, 300);
    }});

    window.addEventListener('resize', resizeAllPlotlyCharts);

    if (window.ResizeObserver) {{
        const ro = new ResizeObserver(resizeAllPlotlyCharts);
        document.querySelectorAll(".plotly").forEach(function(el) {{
            ro.observe(el);
        }});
    }}
</script>
"""

dropdown_html += dropdown_script
dropdown_html += """
<script>
    document.addEventListener("DOMContentLoaded", function () {
        const year = document.getElementById("yearToggle").value;
        const company = document.getElementById("companyToggle").value;

        const selectors = ['.card:not(.static-card)', '.card-summary', '.card-bonus'];
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                el.style.display = 'none';
                if (el.dataset.year === year && el.dataset.company === company) {
                    el.style.display = 'block';
                }
            });
        });
    });
</script>
"""

card_styles = """
    <style>
        /* Sticky Filter Dropdown */
        .filter-bar {
            display: flex;
            align-items: center;
            gap: 20px;
            margin: 20px 0 30px 20px;
            font-size: 16px;
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }
        /* Block for - Filter by Company or/and year */
        .filter-bar label {
            font-weight: 600;
            color: #333;
        }

        .filter-bar select {
            padding: 6px 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 18px;
            font-family: inherit;
            background-color: #fff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: border 0.2s ease-in-out;
        }

        .filter-bar select:focus {
            border-color: #4e73df;
            outline: none;
        }

        .card:not(.static-card),
        .card-summary,
        .card-bonus,
        .chart-card {
            display: none;
        }

        /* All Cards */
        .card {
            padding: 20px;
            background-color: white;
            border-radius: 12px;  /* slightly tighter radius */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        .card-bonus {
            background-color: white;
            border-top: 6px solid #4e73df;
            border-radius: 12px;  /* slightly tighter radius */
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            padding: 20px;
            width: 100%;
            box-sizing: border-box;
        }

        .card-grid {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin: 20px;
        }

        /* To adjust image with is container */
        .plotly-inner {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }

        /* Define two charts within one row */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }

            .card {
                width: 100%;
            }
        }

        /* Summary KPI cards */

        /* Style for Pay Gap Summary */
        .summary-card {
            background-color: #ffffff;
            border-left: 6px solid #4e73df;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            padding: 16px 20px;
            width: 20%;
            min-width: 220px;
            margin: 10px 0;
        }

        @media (max-width: 768px) {
            .summary-card {
                width: 100%;
            }
        }

        .summary-title {
            font-size: 14px;
            font-weight: 600;
            color: #4e73df;
            margin-bottom: 5px;
        }
        .summary-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .summary-subtext {
            font-size: 12px;
            color: #999;
        }

        /* Static card for Comparison Table */
        .card.static-card {
            display: block;
            margin-top: 10px;
            margin-bottom: 20px;
            padding: 20px;
            background-color: #ffffff;
            border-left: 6px solid #4e73df;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        }

        #comparison-table {
            width: 100%;
            font-family: "Segoe UI, Helvetica Neue, Arial, sans-serif";
            font-size: 14px;
            border-collapse: collapse;
            margin-top: 0;
        }

        #comparison-table thead th {
            background-color: #4e73df;
            color: white;
            font-weight: 600;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #ddd;
            position: sticky;
            top: 0;
            z-index: 2;
        }

        #comparison-table tbody td {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }

        #comparison-table tbody tr:hover {
            background-color: #f1f5fb;
        }

        /* Button to download table file as CSV, EXCEL or to print or copy Table values*/
        .dt-button {
            background-color: #4e73df;
            color: white;
            border: none;
            padding: 6px 12px;
            margin: 4px 4px 8px 0;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
        }

        .dt-button:hover {
            background-color: #3b5ec2;
        }

        /* Making dashboard responsive for different device */
        @media (max-width: 480px) {
            body {
                padding: 20px;
            }

            .dashboard-title {
                font-size: 20px;
            }

            .card {
                padding: 15px;
            }

            .card, .card-bonus, .summary-card, .static-card {
                padding: 10px;
                font-size: 14px;
            }
        }

        .card {
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* TABLE CUSTOM STYLES */
        .bonus-table-wrapper {
            width: 100%;
            padding: 10px;
            box-sizing: border-box;
        }

        .bonus-table {
            width: 100%;
            border-collapse: collapse;
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            font-size: 15px;
            margin-top: 10px;
        }

        .bonus-table th {
            background-color: #4e73df;
            color: white;
            text-align: center;
            padding: 12px;
            font-weight: 600;
            border-bottom: 2px solid #ccc;
        }

        .bonus-table td {
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }

        .bonus-table tbody tr:hover {
            background-color: #f8f9fc;
        }

    </style>
"""

# Final HTML export
html_content = f"""
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> Ireland Gender Pay Gap Dashboard</title>
    <!-- DataTables core CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
    <!-- Buttons extension CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css">

    <!-- jQuery (required) -->
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <!-- DataTables core JS -->
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <!-- Buttons extension JS -->
    <script src="https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.html5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.print.min.js"></script>

    <style>
        body {{
            font-family: {FONT_FAMILY};
            background-color: #f5f7fa;
            padding: 40px;
        }}
        .dashboard-title {{
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            background-color: #5A5A5A;
            color: white;
            padding: 10px; 
            border-radius: 4px; 
        }}
    </style>
    {card_styles}
</head>
<body class="bg-light p-4">
    <div class="dashboard-title">Ireland Gender Pay Gap Dashboard </div>
    {dropdown_html}
    {cards_html}
</body>
    
    <footer>
        <div style="text-align:center; margin-top:20px; font-size:12px; color:gray;">
        © 2025 Ireland Gender Pay Gap Analysis. Powered by Plotly.
        </div>
    </footer>

    <script>
        $(document).ready(function() {{
            $('#comparison-table').DataTable({{
                paging: true,
                searching: true,
                info: false,
                pageLength: 10,
                dom: 'Bfrtip',
                buttons: ['csv', 'excel', 'copy', 'print']
            }});
        }});

    </script>
</html>
"""

# Save output
with open("outputs/dashboard.html", "w") as f:
    f.write(html_content)

print(" Dashboard saved to outputs/dashboard.html")