import pandas as pd
import plotly.graph_objects as go

# Load data
df = pd.read_csv("data/sunburst_bike_sales.csv")

# Ensure consistent column names (e.g., strip whitespace)
df.columns = [col.strip() for col in df.columns]

# Identify hierarchical columns (excluding Sales and Gender)
hierarchy_cols = [col for col in df.columns if col not in ['Sales', 'Gender']]
if 'Year' in hierarchy_cols:
    # Ensure 'Year' is the first hierarchy level if present
    hierarchy_cols.remove('Year')
    hierarchy_cols.insert(0, 'Year')

# Prepare lists for sunburst components
ids = []
labels = []
parents = []
values = []

# Dummy root node "Total" at center
total_value = df['Sales'].sum()
ids.append("Total")
labels.append("")           # no text label (we'll use custom center text)
parents.append("")          # root has no parent
values.append(total_value)

# Build hierarchy (levels beyond Gender)
if len(hierarchy_cols) >= 1:
    # Level 1 (e.g., Year)
    lvl1 = hierarchy_cols[0]
    lvl1_groups = df.groupby(lvl1)['Sales'].sum().reset_index()
    for _, row in lvl1_groups.iterrows():
        lvl1_val = row[lvl1]
        lvl1_id = f"{lvl1}-{lvl1_val}"
        ids.append(lvl1_id)
        labels.append(str(lvl1_val))
        parents.append("Total")
        values.append(row['Sales'])
    if len(hierarchy_cols) >= 2:
        # Level 2 (e.g., Category)
        lvl2 = hierarchy_cols[1]
        lvl2_groups = df.groupby([lvl1, lvl2])['Sales'].sum().reset_index()
        for _, row in lvl2_groups.iterrows():
            lvl1_val = row[lvl1]; lvl2_val = row[lvl2]
            lvl1_id = f"{lvl1}-{lvl1_val}"
            lvl2_id = f"{lvl1_val}-{lvl2_val}"
            ids.append(lvl2_id)
            labels.append(str(lvl2_val))
            parents.append(lvl1_id)
            values.append(row['Sales'])
        # Extend similarly if more hierarchy levels exist (not expected in this dataset)

# Add Gender level as leaves
if 'Gender' in df.columns:
    group_keys = hierarchy_cols.copy()
    group_keys.append('Gender')
    gender_groups = df.groupby(group_keys)['Sales'].sum().reset_index()
    for _, row in gender_groups.iterrows():
        gender = row['Gender']
        # Determine parent id based on hierarchy above
        if len(hierarchy_cols) == 0:
            parent_id = "Total"
        elif len(hierarchy_cols) == 1:
            parent_val = row[hierarchy_cols[0]]
            parent_id = f"{hierarchy_cols[0]}-{parent_val}"
        else:
            parent_val1 = row[hierarchy_cols[0]]
            parent_val2 = row[hierarchy_cols[1]]
            parent_id = f"{parent_val1}-{parent_val2}"
        # Create unique id for gender leaf
        leaf_id = f"{parent_id}-{gender}"
        ids.append(leaf_id)
        labels.append(str(gender))
        parents.append(parent_id)
        values.append(row['Sales'])

# Create sunburst figure
sunburst_trace = go.Sunburst(ids=ids, labels=labels, parents=parents, values=values, branchvalues='total')
fig = go.Figure(sunburst_trace)

# Set the root node color to white
fig.update_traces(root_color="white")

# Compute female percentage for each relevant segment (for center text display)
female_percent = {}
if 'Gender' in df.columns:
    total_female = df[df['Gender'] == 'Female']['Sales'].sum()
    total_male = df[df['Gender'] == 'Male']['Sales'].sum()
    female_percent['Total'] = total_female / (total_female + total_male) if (total_female + total_male) > 0 else 0
    if len(hierarchy_cols) >= 1:
        lvl1 = hierarchy_cols[0]
        lvl1_gender = df.groupby([lvl1, 'Gender'])['Sales'].sum().reset_index()
        for _, row in lvl1_groups.iterrows():
            lvl1_val = row[lvl1]
            total = row['Sales']
            female_val = lvl1_gender[(lvl1_gender[lvl1] == lvl1_val) & (lvl1_gender['Gender'] == 'Female')]['Sales'].sum()
            female_percent[f"{lvl1}-{lvl1_val}"] = (female_val / total) if total > 0 else 0
    if len(hierarchy_cols) >= 2:
        lvl1 = hierarchy_cols[0]; lvl2 = hierarchy_cols[1]
        lvl2_gender = df.groupby([lvl1, lvl2, 'Gender'])['Sales'].sum().reset_index()
        for _, row in lvl2_groups.iterrows():
            lvl1_val = row[lvl1]; lvl2_val = row[lvl2]
            total = row['Sales']
            female_val = lvl2_gender[(lvl2_gender[lvl1] == lvl1_val) & 
                                     (lvl2_gender[lvl2] == lvl2_val) & 
                                     (lvl2_gender['Gender'] == 'Female')]['Sales'].sum()
            female_percent[f"{lvl1_val}-{lvl2_val}"] = (female_val / total) if total > 0 else 0

# Default center text: Female % and total sales
if 'Total' in female_percent:
    default_text = f"Female {female_percent['Total']*100:.1f}%<br>$ {total_value:,.0f}"
else:
    default_text = f"$ {total_value:,.0f}"

# Add annotation for center text
fig.update_layout(
    annotations=[dict(text=default_text,
                      x=0.5, y=0.5, xanchor='center', yanchor='middle',
                      showarrow=False, font=dict(size=20, color="black"))]
)
# Set radial text orientation for better readability
fig.update_traces(insidetextorientation='radial')

# Define callback to update center text on hover or click
def update_center_text(trace, points, state):
    if points.point_inds:
        i = points.point_inds[0]
        seg_id = trace.ids[i]
        seg_value = trace.values[i]
        # Determine female% for this segment's context
        if seg_id in female_percent:
            fp = female_percent[seg_id]
        else:
            parent_id = trace.parents[i]
            fp = female_percent.get(parent_id, None)
        # Format new center text
        if fp is not None:
            new_text = f"Female {fp*100:.1f}%<br>$ {seg_value:,.0f}"
        else:
            new_text = f"$ {seg_value:,.0f}"
        fig.layout.annotations[0].text = new_text
    else:
        # Reset to default when not hovering
        fig.layout.annotations[0].text = default_text

fig.write_html("outputs/dashboard.html", include_plotlyjs="cdn", full_html=True)


