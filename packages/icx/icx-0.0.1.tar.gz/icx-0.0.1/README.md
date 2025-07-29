**Individual Consistency Explorer** is a Python package that launches an interactive Streamlit dashboard for exploring the individual fairness for individual classifications.

This package implements the functionality described in a submission to ECAI Demo Track 2025.

# 📦 Installation

pip install ice_py_dash

# Basic Usage

from ice_py_dash import dashboard

## Run with default settings (uses built-in 'adult.csv' dataset)
dashboard.run()

## Or provide custom parameters
dashboard.run(
    filepath="path/to/your/data.csv",  # Path to your CSV file
    y="target_column_name",            # Name of the target column (default: "y")
    positive="positive_label"          # Value considered the 'positive' class (default: 1)
)
