import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np

import urllib
import urllib3
import json
import requests


"""
conversion rates from place to place
volummes of things happening by category by period eg closure reason by year

EHCP closure reason this year DONE
EHCP closed per year DONE
EHCPs issued this year DONE
Assessments completed this year (plus outcome breakdown) DONE
Assessments open now (plus assessment duration) DONE
Requests (plus request outcome)

age
gender
ethnic background
by location

EHCP issue but each broken down by gender, ethnic groups (individual), location (first bit of pstcode?)

(age AND gender splits)

by age/gender compared to population
by ethnicity compared to population
by location if possible
by duration since plan started
And then similar sets for:

treat like an updateable written report 
click through drilldowns would be cool
Same chart appearing next to each chart per cohort (so structure by stage or by cohort)
"""

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


timeframe = 730


def ehc_ceased_year(df):
    """
    df = module 4
    """
    df = df[df["Date EHC Plan Ceased"].notna()]
    df["Date EHC Plan Ceased"] = pd.to_datetime(
        df["Date EHC Plan Ceased"], dayfirst=True
    )  # format="%d/%m/%Y", errors="corece")
    df["Time Since EHC Ceased"] = np.datetime64("today") - df["Date EHC Plan Ceased"]
    ehc_ceased_in_year = df[df["Time Since EHC Ceased"] <= pd.Timedelta(timeframe, "d")]
    count_ehc_ceased = len(ehc_ceased_in_year)
    reason_ech_ceased = (
        ehc_ceased_in_year.groupby("Reason EHC Plan Ceased")["Reason EHC Plan Ceased"]
        .count()
        .reset_index(name="count")
    )
    return count_ehc_ceased


def ehc_starting_year(df):
    """
    df = module 4
    """
    df = df[df["EHC Plan Start Date"].notna()]
    df["EHC Plan Start Date"] = pd.to_datetime(
        df["EHC Plan Start Date"], format="%d/%m/%Y", errors="coerce"
    )
    df["Time since EHC Started"] = np.datetime64("today") - df["EHC Plan Start Date"]
    ehc_started_in_year = df[
        df["Time since EHC Started"] <= pd.Timedelta(timeframe, "d")
    ]
    count_ehc_started = len(ehc_started_in_year)
    return count_ehc_started


def ass_completed_year(df):
    """
    df = module 3
    """
    df_completed = df[df["Assessment Outcome Date"].notna()]
    df_completed["Time Since Ass Completion"] = np.datetime64("today") - pd.to_datetime(
        df_completed["Assessment Outcome Date"], format="%d/%m/%Y", errors="coerce"
    )
    ass_this_year = df_completed[
        df_completed["Time Since Ass Completion"] <= pd.Timedelta(timeframe, "d")
    ]

    ass_year_outcomes = (
        ass_this_year.groupby("Assessment Outcome To Issue EHCP")[
            "Assessment Outcome To Issue EHCP"
        ]
        .count()
        .reset_index(name="count")
    )

    assessments_completed_this_year = len(ass_this_year)

    return assessments_completed_this_year, ass_year_outcomes


def open_ass_timeframes(df1, df2):
    """
    Time between request being recieved in module 2, and now, (filtering closed assessments from module 3).

    df1 = module 2
    df2 = module 3
    """
    uncompleted_assessment_requests = len(df2[df2["Assessment Outcome Date"].isna()])

    df = pd.merge(df1, df2, on="Requests Record ID", how="inner")
    df = df[df["Assessment Outcome Date"].isna()]
    df["Date Request Was Received"] = pd.to_datetime(
        df["Date Request Was Received"], format="%d/%m/%Y", errors="coerce"
    )
    df["open_ass_timeliness"] = (
        np.datetime64("today") - df["Date Request Was Received"]
    ) / pd.Timedelta(1, "day")
    df["open_ass_timeliness"] = df["open_ass_timeliness"].round()

    return uncompleted_assessment_requests, df


def requests_fn(df):
    df = df[df["Date Request Was Received"].notna()]
    df["Date Request Was Received"] = pd.to_datetime(
        df["Date Request Was Received"], format="%d/%m/%Y", errors="coerce"
    )
    df["Request Outcome Date"] = pd.to_datetime(
        df["Request Outcome Date"], format="%d/%m/%y", errors="coerce"
    )

    req_timeliness_df = df[df["Request Outcome Date"].notna()]
    req_timeliness_df["Request Delta"] = (
        req_timeliness_df["Request Outcome Date"]
        - req_timeliness_df["Date Request Was Received"]
    ) / pd.Timedelta(1, "days")
    req_timeliness_df["Request Delta"] = req_timeliness_df["Request Delta"].round()

    df["Request Timeframe"] = np.datetime64("today") - df["Date Request Was Received"]
    requests_this_year = df[df["Request Timeframe"] <= pd.Timedelta(timeframe, "d")]
    count_requests_this_year = len(requests_this_year)

    request_outcomes = (
        df.groupby("Request Outcome")["Request Outcome"]
        .count()
        .reset_index(name="count")
    )

    return count_requests_this_year, request_outcomes


def add_identifiers(identifiers, m2, m3, m4, m5):
    m2 = pd.merge(m2, identifiers, on="Person ID", how="left")
    m3 = pd.merge(m3, identifiers, on="Person ID", how="left")
    m4 = pd.merge(m4, identifiers, on="Person ID", how="left")
    m5 = pd.merge(m5, identifiers, on="Person ID", how="left")
    return m2, m3, m4, m5


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
    # ass_outcomes = (
    #     modules["m3"]
    #     .groupby(["Assessment Outcome To Issue EHCP"])[
    #         "Assessment Outcome To Issue EHCP"
    #     ]
    #     .count()
    #     .reset_index(name="count")
    # )
    # assessment_outcome_plot = px.pie(
    #     ass_outcomes, values="count", names="Assessment Outcome To Issue EHCP"
    # )
    # st.plotly_chart(assessment_outcome_plot)

    # Request to outcome timeliness
    # requests = modules["m2"][modules["m2"].notna()]

    # requests["Request Timeliness"] = pd.to_datetime(
    #     requests["Request Outcome Date"], format="%d/%m/%Y"
    # ) - pd.to_datetime(requests["Date Request Was Received"], format="%d/%m/%Y")

    # requests["Request Timeliness"] = (
    #     (requests["Request Timeliness"] / np.timedelta64(1, "D"))
    #     .round()
    #     .astype("int", errors="ignore")
    # )

    # request_timeliness_plot = px.histogram(requests, x="Request Timeliness")
    # st.plotly_chart(request_timeliness_plot)

    # postcode_count = (
    #     modules["m1"].groupby("Postcode")["Postcode"].count().reset_index(name="count")
    # )

    modules["m2"], modules["m3"], modules["m4"], modules["m5"] = add_identifiers(
        modules["m1"], modules["m2"], modules["m3"], modules["m4"], modules["m5"]
    )

    ehc_ceased_year(modules["m4"])

    ehc_starting_year(modules["m4"])

    ass_completed_year(modules["m3"])

    open_ass_timeframes(modules["m2"], modules["m3"])

    requests_fn(modules["m2"])
