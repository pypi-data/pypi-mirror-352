# Individual Consistency eXplorer (icx) Python Package

This package provides the functionality for an interactive Streamlit dashboard designed to support stakeholders in exploring individual fairness notions within algorithmic decision-making systems.

The dashboard allows users to:
* Explore and operate on a tabular dataset of individuals provided with their corresponding binary classifications;
* Define how similarity between individuals is measured, by configuring categorisation of attributes and how distances between attribute values are computed;
* Compute and visualise five individual fairness metrics that summarise the consistency of classifications across the dataset; and
* Inspect attributes of specific individuals and of those individuals most similar to them, to explore variations in attribute values and allow like-for-like comparisons of classifications.

This package implements the functionality described in a submission to ECAI Demo Track 2025, and further details and documentation will be provided upon publication.

To see an online version of the dashboard, see [Individual Consistency eXplorer Online](https://individual-consistency-explorer.streamlit.app).


## 📦 Installation

It is recommended to install icx in a virtual environment (e.g., conda).

```
pip install icx
```

## Basic Usage

```
from icx import dashboard
```

### Run the dashboard

```
dashboard.run()
```

In the dashboard there is the ability to upload your own datasets or use the demo datasets provided.
