## python-data-generation-plotly
This repository contains Python scripts for generating realistic synthetic datasets and creating professional, interactive dashboards using Plotly. It serves as a versatile foundation for data visualization projects, making it easy to simulate and showcase metrics across multiple domains.

✨ Projects Included
📊 Gender Pay Gap Dashboard
Generate pay gap summaries, quartile distributions, and bonus participation data. Visualize them with stacked bar charts, Sankey diagrams, and KPI cards.

📈 SaaS Metrics Dashboard
Simulate ARR changes, cohort retention, employee breakdowns, and expense trends. Render the results using Plotly for modern, responsive dashboard layouts.

# Financial Performance Dashboard
Create data for bookings, cash balances, burn rate, and regional churn insights. Includes heatmaps, pie charts, and summary cards.

# Structure
bash
Copy
Edit
data/       # Generated CSV/NPY files
outputs/    # Interactive HTML dashboards
scripts/    # Data generation and visualization scripts
# 📊 Tools & Libraries
pandas, numpy – data manipulation and generation

plotly, kaleido – interactive charts and image exports

dash (optional) – for advanced UI interactivity

# Repository Structure
data/       # Generated CSV/NPY files
outputs/    # Exported interactive HTML dashboards
scripts/    # Python scripts for data generation & visualization


# ⚙️ Setup Instructions

1. Clone the repository:

git clone https://github.com/letebrhan/python-data-generation-plotly.git
cd python-data-generation-plotly

2. Create a virtual environment (optional but recommended):

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install required dependencies:

pip install -r requirements.txt


##🚀 How to Use 
1. Generate Data
Run the following script to create the necessary .csv and .npy files inside the data/ folder:

python scripts/data_gen.py

2. Create Dashboards
Render and export the interactive dashboard as an HTML file.

python scripts/viz.py

## Dependencies
pandas

numpy

plotly

kaleido (for static image export)

dash (optional for advanced interactivit

