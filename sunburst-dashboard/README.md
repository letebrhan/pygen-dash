
# 🌞 Multi-Level Sunburst Chart — Product Sales Breakdown

This project visualizes hierarchical product sales data using an interactive 6-level **sunburst chart** built with **Plotly in Python**. The visualization displays a white central circle highlighting the percentage and sales value of **female customers**, and allows intuitive exploration of data from total sales down to individual models.

---

## 📊 Features

- ✅ 6-level hierarchy: `Total → Year → Gender → Category → Subcategory → Model`
- ✅ White circular center with female % and sales (formatted in European style)
- ✅ Hover tooltips showing full path and sales value
- ✅ Muted professional color palette (ColorBrewer-style)
- ✅ Responsive HTML export with styled layout
- ✅ Clean radial label orientation
- ✅ Python-only implementation using `pandas`, `plotly`, and `os`

---

## 📁 Project Structure

```
├── data/
│   └── sunburst_bike_sales.csv      # Input dataset (generated via script)
├── scripts/
│   ├── data_gen.py                  # Generates synthetic sales data
│   └── viz.py                       # Builds and exports sunburst chart
├── outputs/
│   └── sunburst_final_dashboard.html  # Final interactive HTML chart
├── README.md
```

---

## 🚀 How to Run

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/sunburst-chart.git
   cd sunburst-chart
   ```

2. (Optional) Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install pandas plotly
   ```

3. Generate sample data:
   ```bash
   python3 scripts/data_gen.py
   ```

4. Render the sunburst chart:
   ```bash
   python3 scripts/viz.py
   ```

5. Open `outputs/sunburst_final_dashboard.html` in your browser.

---

## 🧠 Prompt Behind the Chart

> *Create a 6-level sunburst chart to visualize hierarchical product sales data, starting from the total level and drilling down through year, gender, category, subcategory, and model. Display a white central circle showing the percentage and total sales value for females. Use a clean, professional color palette and radial text orientation.*

---

## 🖼 Screenshot

![Chart Preview](outputs/sunburst_final_dashboard.png)

---

## 📄 License

MIT License © 2025 Letebrhan Alemayoh

---

## 🙌 Acknowledgments

- [Plotly Python](https://plotly.com/python/sunburst-charts/)
- [ColorBrewer Palettes](https://colorbrewer2.org/)
- Inspired by dashboard styling best practices from Labelbox Visual Evaluation Guidelines
