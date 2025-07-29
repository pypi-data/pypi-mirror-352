# Individual Consistency eXplorer (icx) Python Package

This package provides the functionality for an interactive Streamlit dashboard designed to support stakeholders in exploring individual fairness notions within algorithmic decision-making systems.

The dashboard allows users to:
* Explore and operate on a tabular dataset of individuals provided with their corresponding binary classifications;
* Define how similarity between individuals is measured, by configuring categorisation of attributes and how distances between attribute values are computed;
* Compute and visualise five individual fairness metrics that summarise the consistency of classifications across the dataset; and
* Inspect attributes of specific individuals and of those individuals most similar to them, to explore variations in attribute values and allow like-for-like comparisons of classifications.

This package implements the functionality described in a submission to ECAI Demo Track 2025, and further details and documentation will be provided upon publication.


## 📦 Installation

```
pip install icx
```

## Basic Usage

```
from icx import dashboard
```

### Run with default settings
Uses first 1000 individuals from pre-loaded ['adult.csv'](https://doi.org/10.24432/C5XW20) dataset from UCI Machine Learning repository.

```
dashboard.run()
```

## 🗂️ Use Your Own Dataset

You can provide your own dataset, as long as it meets the following requirements:

- The **first row** contains **column headers** (attribute names).  
- Each attribute is either **numeric** (`int`, `float`) or **categorical** (`string`).  
- Each instance must be assigned a **binary class**: either *positive* or *negative*. You can specify the value representing the positive class — all other values will be treated as negative.  
- The **class** column must be named `"y"` or explicitly defined in the parameters.

### Example

```
dashboard.run(
    filepath="path/to/your/data.csv",   # Path to your CSV file
    y="class_column_name",             # Name of the class column (default: "y")
    positive="positive_label"           # Label for the positive class (default: 1)
)
```
