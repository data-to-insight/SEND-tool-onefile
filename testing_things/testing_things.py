import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np


module_columns = {
    "m1": [
        "Person ID",
        "Surname",
        "Forename",
        "Dob (ccyy-mm-dd)",
        "Gender",
        "Ethnicity",
        "Postcode",
        "UPN - Unique Pupil Number",
        "ULN - Young Persons Unique Learner Number",
        "UPN and ULN unavailable reason",
    ],
    "m2": [
        "Person ID",
        "Requests Record ID",
        "Date Request Was Received",
        "Initial Request Whilst In RYA",
        "Request Outcome Date",
        "Request Outcome",
        "Request Mediation",
        "Request Tribunal",
        "Exported - Child Or Young Person Moves Out Of LA Before Assessment Is Completed",
        "New start date",
    ],
    "m3": [
        "Person ID",
        "Requests Record ID",
        "Assessment Outcome To Issue EHCP",
        "Assessment Outcome Date",
        "Assessment Mediation",
        "Assessment Tribunal",
        "Other Mediation",
        "Other Tribunal",
        "Twenty Weeks Time Limit Exceptions Apply",
    ],
    "m4": [
        "Person ID",
        "Request Records ID",
        "EHC Plan Start Date",
        "Residential Settings",
        "Worked based learning activity",
        "Personal budget taken up",
        "Personal budget - organised arrangements",
        "Personal budget - direct payments",
        "Date EHC Plan Ceased",
        "Reason EHC Plan Ceased",
    ],
    "m5": [
        "Person ID",
        "Request Records ID",
        "EHC Plan (Transfer)",
        "Residential Settings",
        "Worked based learning activity",
        "EHCP review decisions date",
    ],
}

uploaded_files = st.file_uploader("pls", accept_multiple_files=True)


if uploaded_files:

    dfs = {
        uploaded_file.name: pd.read_csv(uploaded_file)
        for uploaded_file in uploaded_files
    }

    modules = {}
    for key, df in dfs.items():
        for module_name, column_list in module_columns.items():
            if list(df.columns) == column_list:
                modules[module_name] = df

    # st.write(loaded_files.keys())

    # Assessments pie chart
    ass_outcomes = (
        modules["m3"]
        .groupby(["Assessment Outcome To Issue EHCP"])[
            "Assessment Outcome To Issue EHCP"
        ]
        .count()
        .reset_index(name="count")
    )
    assessment_outcome_plot = px.pie(
        ass_outcomes, values="count", names="Assessment Outcome To Issue EHCP"
    )
    st.plotly_chart(assessment_outcome_plot)

    # Request to outcome timeliness
    requests = modules["m2"][modules["m2"].notna()]

    requests["Request Timeliness"] = pd.to_datetime(
        requests["Request Outcome Date"], format="%d/%m/%Y"
    ) - pd.to_datetime(requests["Date Request Was Received"], format="%d/%m/%Y")

    requests["Request Timeliness"] = (
        (requests["Request Timeliness"] / np.timedelta64(1, "D"))
        .round()
        .astype("int", errors="ignore")
    )

    request_timeliness_plot = px.histogram(requests, x="Request Timeliness")
    st.plotly_chart(request_timeliness_plot)

#     # postcode_count = modules["m1"].groupby('Postcode')['Postcode'].count().reset_index(name="count")
