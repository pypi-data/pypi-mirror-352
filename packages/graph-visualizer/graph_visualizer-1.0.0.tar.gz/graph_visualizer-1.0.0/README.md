# 📊 GraphVisualizer

**GraphVisualizer** is a beginner-friendly Python library for interactive and guided exploratory data analysis (EDA). It supports multiple backends like Seaborn, Matplotlib, and Plotly.

## ✨ Features

- Univariate, Bivariate, Multivariate, and Datetime visualizations
- Supports Seaborn, Matplotlib, and Plotly
- Guided menus for user-friendly graph selection
- Save plots and build dashboards
- Great for students and educators

## 🚀 Quick Start

```python
from graph_visualizer import GraphVisualizer
import seaborn as sns

df = sns.load_dataset("taxis")  # or your own DataFrame
gv = GraphVisualizer(df)
gv.run()
```

## 🔧 Installation

```bash
git clone https://github.com/yourusername/graph-visualizer.git
cd graph-visualizer
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License.
