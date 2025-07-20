# Repair Outcomes — Radial Breakdown Dashboard

This project generates a radial bar chart dashboard visualizing repair outcomes for product categories and individual products. It uses synthetic data generated in CSV format and rendered with Plotly in Python.

## 📁 Folder Structure

```
├── data/
│   ├── product_categories.csv
│   └── product_items.csv
├── scripts/
│   ├── data_gen.py
│   └── viz.py
├── outputs/
│   └── dashboard.html
└── README_radial_dashboard.md
```

## 🔧 Setup Instructions

1. Create a virtual environment (optional but recommended):
   ```bash
   python3.8 -m venv myenv
   source myenv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install pandas numpy plotly
   ```

3. Generate data:
   ```bash
   python3.8 scripts/data_gen.py
   ```

4. Visualize and export the dashboard:
   ```bash
   python3.8 scripts/viz.py
   ```

5. Open the dashboard:
   Open `outputs/dashboard.html` in any modern browser.

## 📊 Dashboard Features

- **Left Chart**: Radial stacked bar of top 10 product categories (0°–90° sector).
- **Right Chart**: Full circle breakdown of top 20 most frequent products.
- **Labels**: Placed along outer arcs with guiding lines and proper text alignment.
- **Legend**: Custom horizontal legend with title.
- **Style**: Clean layout with responsive styling and proper typography.

## 🎨 Customization Tips

- Update the color palette in `viz.py` under the `colors` dictionary.
- Modify chart size or label placement using parameters like `r_multiplier`, `angle_range`, or font size.
- For publishing, set `include_plotlyjs='cdn'` to reduce HTML size.

## 📦 Dependencies

- Python 3.8+
- pandas
- numpy
- plotly

## 📝 License

MIT License (You may adapt or reuse for personal or professional projects)
