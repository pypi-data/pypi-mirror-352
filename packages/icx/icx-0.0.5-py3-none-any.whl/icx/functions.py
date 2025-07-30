import pandas as pd
import numpy as np
from gower import gower_matrix
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from sklearn.neighbors import NearestNeighbors

import os

def similarity(df, user_inputs, categorical_columns):
    binned_df = df.copy()
    for col in df.columns:
        if not (user_inputs[col] == ""):
            binned_df = bin_column(binned_df, col, user_inputs[col])
            categorical_columns.append(col)
    return binned_df, categorical_columns


def bin_column(df, col_name, bins_str):
    """
    Bins a column into specified bins with range labels and replaces the original column.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the column to bin.
        col_name (str): The column name to bin.
        bins_str (str): A comma-separated string of bin edges (e.g., "10,20,30").

    Returns:
        pd.DataFrame: The DataFrame with the original column replaced by binned values.
    """
    # Convert the comma-separated string into a list of numbers
    bins = [float(x) for x in bins_str.split(",")] + [float('inf')]  # Add infinity as the last bin

    # Generate labels in the format "start-end"
    labels = [f"{int(bins[i])}-{int(bins[i+1])-1 if bins[i+1] != float('inf') else 'inf'}" for i in range(len(bins)-1)]

    # Replace the original column with binned values
    df[col_name] = pd.cut(df[col_name], bins=bins, labels=labels, right=False)

    return df


# get the k nearest neighbours for all individuals in the test data, and their corresponding distances
# created by me to be able to edit the distance metric used
def get_knn(X, k, categorical_columns):
    # Create a boolean array where True indicates a categorical column
    is_categorical = np.array(X.columns.isin(categorical_columns))

    X_gower = gower_matrix(X.values, cat_features=is_categorical)

    # Create a KNN model and fit it
    k = k + 1
    nbrs = NearestNeighbors(n_neighbors=k, metric='precomputed')
    nbrs.fit(X_gower)

    # Find the k nearest neighbors for all examples
    distances, indices = nbrs.kneighbors(X_gower)
    return distances, indices


def find_similar_inds(df, k, categorical_columns):
    """ Compute the consistency score.

        Individual fairness metric from [#zemel13]_ that measures how similar the
        labels are for similar instances.

        Args:
            X (array-like): Sample features.
            y (array-like): Sample targets.
            k (int): Number of neighbors for the knn
                computation.

        References:
            .. [#zemel13] `R. Zemel, Y. Wu, K. Swersky, T. Pitassi, and C. Dwork,
               "Learning Fair Representations," International Conference on Machine
               Learning, 2013. <http://proceedings.mlr.press/v28/zemel13.html>`_
        """
    X = df.drop(columns=["y"])
    y = df["y"]

    # learn a KNN on the features
    distances, indices = get_knn(X, k, categorical_columns)

    # ADDED code, remove the index (individual) itself
    similar_inds = {}
    sim_ind_distances = {}
    for i in range(len(indices)):
        if i in indices[i]:
            similar_inds[i] = np.delete(indices[i], np.where(indices[i] == i))
            sim_ind_distances[i] = np.delete(distances[i], np.where(indices[i] == i))
        else:
            similar_inds[i] = indices[i][:-1]
            sim_ind_distances[i] = distances[i][:-1]
    return similar_inds, sim_ind_distances

def get_ind_cons(df, sim_inds):
    y = df["y"]
    ind_cons = []
    for key in sim_inds:
        ind_con = (1 - abs(y[key] - y[sim_inds[key]].mean()))
        ind_cons.append(round(ind_con,2))
    return ind_cons

def get_overall_consistency(ind_cons):
    return round(sum(ind_cons)/len(ind_cons),3)


def get_licc_score(ind_cons, delta):
    return sum(1 for x in ind_cons if x <= delta)


def get_pcc_score(ind_cons, delta):
    count = 0
    for c in ind_cons:
        if round(c,2) >= delta:
            count = count + 1

    pcc = (count/len(ind_cons))
    return round(pcc, 3)


def get_bcc_score(ind_cons, delta=0.5):
    count = 0
    for c in ind_cons:
        if round(c,2) >= delta:
            count = count + c

    bcc = (count/len(ind_cons))
    return round(bcc,3)


def get_bcc_penalty_score(ind_cons, delta, penalty=-1):
    count = 0
    for c in ind_cons:
        if round(c,2) >= delta:
            count = count + c
        else:
            count = count + penalty

    bcc = (count/len(ind_cons))
    return round(bcc, 3)



# Function to highlight rows based on consistencies
def highlight_rows():
    return JsCode("""
                function(params) {
                    if (params.data.c <= params.data.delta) {
                        return {
                            'color': 'black',
                            'backgroundColor': 'lightyellow'
                        }
                    }
                };
                """)


def highlight_first_row():
    return JsCode("""function(params) {
        if (params.node.rowIndex === 0) {
            return { 'background-color': 'lightyellow', 'font-weight': 'bold' };
        }
    }""")


def get_ordered(df, col, sorted_attributes):
    # Create a mapping dictionary {value: order_index}
    order_mapping = {val: idx for idx, val in enumerate(sorted_attributes)}

    # Replace values in df['Category'] with their order
    df[col] = df[col].map(order_mapping)
    return df


def get_value_order(df, col, sorted_attributes):
    # Create a mapping dictionary {value: order_index}
    order_mapping = {val: f"{idx} ({val})" for idx, val in enumerate(sorted_attributes)}
    # Replace values in df['Category'] with their order
    df[col] = df[col].map(order_mapping)
    return df


def replace_data(binned_df, df_display):
    # Find columns where the data types are different
    differing_cols = [col for col in binned_df.columns if binned_df[col].dtype != df_display[col].dtype and df_display[col].dtype != 'int64']

    # Replace those columns in binned_df with df_display
    binned_df[differing_cols] = df_display[differing_cols]
    return binned_df


def get_draggable_style():
    return """
.sortable-component {
    background-color:rgb(0, 225, 255);
    font-size: 16px;
    counter-reset: item;
}
.sortable-item {
    background-color: gray;
    color: white;
}
"""


def display_scores(individual_consistencies, delta):
    # Assuming `f` and `individual_consistencies` are defined
    consistency_score = get_overall_consistency(individual_consistencies)
    licc_score = get_licc_score(individual_consistencies, delta)
    pcc_score = get_pcc_score(individual_consistencies, delta)
    bcc_score = get_bcc_score(individual_consistencies, delta)
    bcc_pen_score = get_bcc_penalty_score(individual_consistencies, delta)

    st.markdown("## 📊 Dataset Metrics")

    # Arrange scores in a clean layout
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Consistency Score", value=f"{consistency_score:.3f}", help="Measures the overall level of disparity in a dataset in the classification of individuals with respect to their most similar individuals. Calculated as the average individual consistency score) ")
    with col2:
        st.metric(label="LICC Score", value=f"{licc_score}", help="Absolute measure of the total number of individuals in a dataset with decisions deemed unacceptable. Calculated as the count of individuals for which their individual consistency score is less than threshold $\\delta$.")
        st.metric(label="PCS Score", value=f"{pcc_score:.3f}", help="Proportion of individuals in the datasets whose decisions are deemed acceptable. Calculated as the proportion of individuals with an individual consistency score greater than or equal to $\\delta$")
    with col3:
        st.metric(label="BCC Score", value=f"{bcc_score:.3f}", help="Average individual consistency score above a level that is deemed acceptable. Calculated as the sum of the individual consistency scores above or equal some threshold $\\delta$ divided by the total number of individuals.")
        st.metric(label="BCC with Penalty Score", value=f"{bcc_pen_score:.3f}", help="As BCC, but penalises for unacceptable decisions, and hence it is more sensitive to those decisions. Calculated as a modification of BCC score which counts an individual as -1 for each individual consistency score below $\\delta$.")

def format_distances(distances, df):
    # Get number of columns in the DataFrame
    num_columns = df.shape[1] - 1

    # Multiply each distance by the number of columns and format to 3 decimal places
    return [f"{(dist * num_columns):.3f}" for dist in distances]


def display_dataset_stats(df):
    # Dataset shape
    st.markdown("---")
    st.header("🧭 Dataset Explorer")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])

    if "y" in df.columns:
        # Compute proportion of y == 1
        positive_ratio = (df["y"] == 1).mean() * 100
        col3.metric("Proportion of positive labels", value=f"{positive_ratio:.1f}%")
    else:
        st.warning("⚠️ Column `y` not found in dataset — skipping target distribution.")

    with st.expander("See column data types"):
        st.dataframe(df.dtypes.astype(str).reset_index().rename(columns={"index": "Column", 0: "Type"}))

    '''
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        st.success("No missing values found!")
    else:
        st.warning("Columns with missing values:")
        st.dataframe(missing.reset_index().rename(columns={"index": "Column", 0: "Missing Count"}))
    '''


def welcome_message():
    st.markdown("""
    Welcome to the **Individual Consistency Explorer Dashboard**!

    This dashboard can be used to **explore the individual fairness** of a dataset.
    It allows for **three demo datasets**, which you can use to try out the functionality quickly.

    ---

    We recommend using this dashboard locally with any sensitive data.
    Please use the Python package as detailed [here](https://pypi.org/project/icx/) to upload and analyse your own data.

    ---
    ## 📂 Select a Demo Dataset or Upload Your Own Dataset
    Choose from one of the following preloaded datasets:
    """)

    # Dataset names for dropdown
    dataset_labels = {
        "Adult Census": "adult",
        "German Credit": "german",
        "COMPAS": "compas",
        "Upload Own Dataset": "own_data"
    }

    # Dropdown selection
    selected_label = st.selectbox("Choose a dataset:", options=list(dataset_labels.keys()))
    selected_dataset = dataset_labels[selected_label]

    # Show link to dataset
    dataset_links = {
        "adult": "https://archive.ics.uci.edu/ml/datasets/adult",
        "german": "https://archive.ics.uci.edu/ml/datasets/statlog+(german+credit+data)",
        "compas": "https://www.kaggle.com/datasets/danofer/compass",
        "own_data": None
    }

    if dataset_links[selected_dataset] is not None:
        st.markdown(f"🔗 [View dataset source for **{selected_label}**]({dataset_links[selected_dataset]})")
    return selected_dataset


def load_dataset():
    # Step 1: Upload CSV
    uploaded_file = st.file_uploader("Choose a CSV file:", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("CSV loaded successfully!")

        st.write("### Preview of Data")
        st.dataframe(df.head())

        st.write("Ensure the correct class column is selected, and specify the positive class:")

        # Step 2: Select target column (y)
        columns = df.columns.tolist()
        default_index = columns.index("y") if "y" in columns else 0
        y_col = st.selectbox("Select the class (y) column", options=df.columns, index=default_index)

        # Step 3: Select positive label
        if y_col:
            unique_labels = df[y_col].dropna().unique().tolist()
            positive_label = st.selectbox("Select the positive class value", options=unique_labels)

            # Step 4: Button to convert and rename
            if st.button("🔄 Convert Target Column and Upload Data"):
                try:
                    # Convert the selected column to binary
                    df[y_col] = df[y_col].apply(lambda x: 1 if x == positive_label else 0)

                    # Rename the column to 'y'
                    df.rename(columns={y_col: "y"}, inplace=True)

                    st.success(f"Converted column `{y_col}`: `{positive_label}` → 1, others → 0 and renamed it to `y`.")

                    return df
                except Exception as e:
                    st.error(f"Error transforming column: {e}")
    return get_dataset("adult")


def get_dataset(selected_dataset):
    # Base directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the Datasets folder
    dataset_dir = os.path.join(base_dir, 'Datasets')

    if selected_dataset == "compas":
        file_path = os.path.join(dataset_dir, "compas.csv")
        df = pd.read_csv(file_path)
        df["y"] = (df["y"] == "Survived").astype(int)
    elif selected_dataset == "german":
        file_path = os.path.join(dataset_dir, "german.csv")
        df = pd.read_csv(file_path)
        df["y"] = (df["y"] == "good").astype(int)
    else:
        file_path = os.path.join(dataset_dir, "adult.csv")
        df = pd.read_csv(file_path).head(1000)
        df["y"] = (df["y"] == ">50K").astype(int)

    return df
