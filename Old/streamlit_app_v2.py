import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import markdown as md

# Display Title and Description
st.set_page_config(page_title="Sample of Dismissal Entries", layout="wide")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
df = conn.read(worksheet="first500_1May2025", usecols=list(range(17)), ttl=60)
df = df.dropna(how="all")
columns_to_convert = ['entrynumber']
df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce')
columns_to_convert = ['id','entrynumber','unique_caseheader_id','fullcase_id']
df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce', downcast='integer')

# Step through empty rows updating as we go
while df['dismissal_entry_type'].isna().sum() > 0:
    # Display the next empty row
    next_empty_row = df.loc[df['dismissal_entry_type'].isna()].iloc[0]
    display_text = next_empty_row['entrytext']
    display_case_id = next_empty_row['unique_caseheader_id']

    md_string = f'''# Let's code the following entry from Unique Case Header ID {display_case_id}:
    
    ### {display_text} 
    '''
    st.markdown(md_string)

    # Dropdown for user input
    dismissal_entry_type = st.selectbox(
        "Does the entry contain a motion to dismiss, an order of dismissal, or neither?",
        [
            "Motion to Dismiss",
            "Order of Dismissal",
            "Neither",
        ],
    )

    if dismissal_entry_type == "Order of Dismissal":
        st.markdown("Please select the type of Order of Dismissal.")
        order_type_voluntary = st.selectbox(
            "Is the dismissal voluntary or involuntary?",
            [
                "Voluntary Dismissal",
                "Involuntary Dismissal",
                "Unknown",
            ],
        )
        order_type_prejudice = st.selectbox(
            "Is the dismissal with or without prejudice?",
            [
                "With prejudice",
                "Without prejudice",
                "Unknown",
            ],
        )
        order_type_partial = st.selectbox(
            "Is the action dismissed in full or in part",
            [
                "Full Dismissal",
                "Partial Dismissal",
                "Unknown",
            ],
        )

        st.markdown("**required*")
        submit_button = st.button(label="Submit docket entry details")

        if submit_button:
            # Check if all mandatory fields are filled
            if not dismissal_entry_type or not order_type_voluntary or not order_type_prejudice or not order_type_partial:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                # Update the DataFrame and Google Sheets with the new entry
                df.loc[next_empty_row.name, 'dismissal_entry_type'] = dismissal_entry_type
                df.loc[next_empty_row.name, 'order_type_voluntary'] = order_type_voluntary
                df.loc[next_empty_row.name, 'order_type_prejudice'] = order_type_prejudice
                df.loc[next_empty_row.name, 'order_type_partial'] = order_type_partial
                conn.update(worksheet="first500_1May2025", data=df)
                st.success("Entry details successfully submitted!")

    elif dismissal_entry_type != "Order of Dismissal":
        st.markdown("**required*")
        submit_button = st.button(label="Submit docket entry details")

        if submit_button:
            # Check if all mandatory fields are filled
            if not dismissal_entry_type:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                # Update the DataFrame and Google Sheets with the new entry
                df.loc[next_empty_row.name, 'dismissal_entry_type'] = dismissal_entry_type
                conn.update(worksheet="first500_1May2025", data=df)
                st.success("Entry details successfully submitted!")
                
# Check if there are any rows left to process
if df['dismissal_entry_type'].isna().sum() == 0:
    st.success("All entries have been filled!")
    st.stop()


# if action == "Onboard New Vendor":
#     st.markdown("Enter the details of the new vendor below.")
#     with st.form(key="vendor_form"):
#         company_name = st.text_input(label="Company Name*")
#         business_type = st.selectbox(
#             "Business Type*", options=BUSINESS_TYPES, index=None
#         )
#         products = st.multiselect("Products Offered", options=PRODUCTS)
#         years_in_business = st.slider("Years in Business", 0, 50, 5)
#         onboarding_date = st.date_input(label="Onboarding Date")
#         additional_info = st.text_area(label="Additional Notes")

#         st.markdown("**required*")
#         submit_button = st.form_submit_button(label="Submit Vendor Details")

#         if submit_button:
#             if not company_name or not business_type:
#                 st.warning("Ensure all mandatory fields are filled.")
#             elif df["CompanyName"].str.contains(company_name).any():
#                 st.warning("A vendor with this company name already exists.")
#             else:
#                 vendor_data = pd.DataFrame(
#                     [
#                         {
#                             "CompanyName": company_name,
#                             "BusinessType": business_type,
#                             "Products": ", ".join(products),
#                             "YearsInBusiness": years_in_business,
#                             "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
#                             "AdditionalInfo": additional_info,
#                         }
#                     ]
#                 )
#                 updated_df = pd.concat([df, vendor_data], ignore_index=True)
#                 conn.update(worksheet="Vendors", data=updated_df)
#                 st.success("Vendor details successfully submitted!")

# elif action == "Update Existing Vendor":
#     st.markdown("Select a vendor and update their details.")

#     vendor_to_update = st.selectbox(
#         "Select a Vendor to Update", options=df["CompanyName"].tolist()
#     )
#     vendor_data = df[df["CompanyName"] == vendor_to_update].iloc[
#         0
#     ]

#     with st.form(key="update_form"):
#         company_name = st.text_input(
#             label="Company Name*", value=vendor_data["CompanyName"]
#         )
#         business_type = st.selectbox(
#             "Business Type*",
#             options=BUSINESS_TYPES,
#             index=BUSINESS_TYPES.index(vendor_data["BusinessType"]),
#         )
#         products = st.multiselect(
#             "Products Offered",
#             options=PRODUCTS,
#             default=vendor_data["Products"].split(", "),
#         )
#         years_in_business = st.slider(
#             "Years in Business", 0, 50, int(vendor_data["YearsInBusiness"])
#         )
#         onboarding_date = st.date_input(
#             label="Onboarding Date", value=pd.to_datetime(vendor_data["OnboardingDate"])
#         )
#         additional_info = st.text_area(
#             label="Additional Notes", value=vendor_data["AdditionalInfo"]
#         )

#         st.markdown("**required*")
#         update_button = st.form_submit_button(label="Update Vendor Details")

#         if update_button:
#             if not company_name or not business_type:
#                 st.warning("Ensure all mandatory fields are filled.")
#             else:
#                 # Removing old entry
#                 df.drop(
#                     df[
#                         df["CompanyName"] == vendor_to_update
#                     ].index,
#                     inplace=True,
#                 )
#                 # Creating updated data entry
#                 updated_vendor_data = pd.DataFrame(
#                     [
#                         {
#                             "CompanyName": company_name,
#                             "BusinessType": business_type,
#                             "Products": ", ".join(products),
#                             "YearsInBusiness": years_in_business,
#                             "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
#                             "AdditionalInfo": additional_info,
#                         }
#                     ]
#                 )
#                 # Adding updated data to the dataframe
#                 updated_df = pd.concat(
#                     [df, updated_vendor_data], ignore_index=True
#                 )
#                 conn.update(worksheet="Vendors", data=updated_df)
#                 st.success("Vendor details successfully updated!")

# # View All Vendors
# elif action == "View All Vendors":
#     st.dataframe(df)

# # Delete Vendor
# elif action == "Delete Vendor":
#     vendor_to_delete = st.selectbox(
#         "Select a Vendor to Delete", options=df["CompanyName"].tolist()
#     )

#     if st.button("Delete"):
#         df.drop(
#             df[df["CompanyName"] == vendor_to_delete].index,
#             inplace=True,
#         )
#         conn.update(worksheet="Vendors", data=df)
#         st.success("Vendor successfully deleted!")
    
