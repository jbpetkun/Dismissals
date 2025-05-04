import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np

# Display Title and Description
st.set_page_config(page_title="Sample of Dismissal Entries", layout="wide")
st.title("Sample of Dismissal Entries")

# Establishing a Google Sheets connection and placing data frame in session state
conn = st.connection("gsheets", type=GSheetsConnection)
if "df" not in st.session_state:
    st.session_state.df = conn.read(worksheet="first500_1May2025", usecols=list(range(17)), ttl=60)
    df = st.session_state.df
else:
    df = st.session_state.df
if "current_index" not in st.session_state:
    # Find index of first row in df where dismissal_entry_type is NaN
    st.session_state.current_index = np.where(df['dismissal_entry_type'].isnull())[0][0]
df = df.dropna(how="all")
columns_to_convert = ['entrynumber']
df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce')
columns_to_convert = ['id','entrynumber','unique_caseheader_id','fullcase_id']
df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce', downcast='integer')

# Check if there are any rows left to process
if df['dismissal_entry_type'].isna().sum() == 0:
    st.success("All entries have been filled!")
    st.stop()

# Get the current row to display
current_row = df.iloc[st.session_state.current_index]
st.markdown(f"### Docket Entry {current_row['unique_caseheader_id']}")
st.markdown(f"**Entry Text:** {current_row['entrytext']}")

# Input fields for the current docket entry
dismissal_entry_type = st.selectbox(
    "Dismissal Entry Type:",
    ["","Motion to Dismiss", "Order of Dismissal", "Neither"],
    key="dismissal_type_selection"
)
if dismissal_entry_type == "Order of Dismissal":
    st.markdown("Please select the type of Order of Dismissal.")
    # Additional fields for Order of Dismissal
    order_type_voluntary = st.selectbox(
        "Order Type Voluntary:",
        ["","Unknown", "Voluntary", "Involuntary"],
        key="vol_type_selection"
    )
    order_type_prejudice = st.selectbox(
        "Order Type Prejudice:",
        ["","Unknown", "With Prejudice", "Without Prejudice"],
        key="prej_type_selection"
    )
    order_type_partial = st.selectbox(
        "Order Type Partial:",
        ["","Unknown", "Full", "Partial"],
        key="part_type_selection"
    )
else:
    order_type_voluntary = "Unknown"
    order_type_prejudice = "Unknown"
    order_type_partial = "Unknown"

submit_button = st.button(label="Submit docket entry details")

if submit_button:
    # Check if all mandatory fields are filled
    if not dismissal_entry_type or not order_type_voluntary or not order_type_prejudice or not order_type_partial:
        st.warning("Ensure all mandatory fields are filled.")
    else:
        # Update the original DataFrame with the user's input
        original_index = current_row.name  # Get the index of the current row in the original DataFrame
        st.session_state.df.loc[original_index, 'dismissal_entry_type'] = dismissal_entry_type
        df.loc[original_index, 'dismissal_entry_type'] = dismissal_entry_type
        st.session_state.df.loc[original_index, 'order_type_voluntary'] = order_type_voluntary
        st.session_state.df.loc[original_index, 'order_type_prejudice'] = order_type_prejudice
        st.session_state.df.loc[original_index, 'order_type_partial'] = order_type_partial

        # Update Google Sheets
        conn.update(worksheet="first500_1May2025", data=st.session_state.df)
        # Move to the next relevant docket entry
        st.session_state.current_index = np.where(df['dismissal_entry_type'].isnull())[0][0] if df['dismissal_entry_type'].isnull().any() else None

        # Reset buttons and rerun the app to display the next entry
        del st.session_state.dismissal_type_selection
        st.rerun()