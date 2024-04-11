import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np

import urllib
import urllib3
import json
import requests


"""
TODO
Do calculations for last day of return rather than 'today'
NUmber marks on plots
years plans started buckets
note to save pdf using ctrl + p
explanation for box plot
data analysis warnings
pie chart sub plots

headline stats

length to durations

For timeframes, ensure that the same child doesn't have huge timeframes when they appear multiple times - should be fine because of requests record ID
Find out what H means - this could be inflating numbers
open timeframes seem long as this is data from 2 years ago!
volummes of things happening by category by period eg closure reason by year
conversion rates from place to place DONE
children appearing multiple times per list as a measure - done
EHCP closure reason this year DONE
EHCP closed per year DONE
EHCPs issued this year DONE
Assessments completed this year (plus outcome breakdown) DONE
Assessments open now (plus assessment duration) DONE
Requests (plus request outcome)

How long plans have been open buckets

conversion rates -> req ass plan using parallel_categories

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


# Utilities
def age_buckets(age):
    if age < 1:
        return "Under 1"
    elif age <= 4:
        return "1-4 years"
    elif age <= 9:
        return "5-9 years"
    elif age <= 15:
        return "10-15 years"
    else:
        return "16 & over"


def timeliness_buckets(time_delta):
    if time_delta <= pd.Timedelta(45, "d"):
        return "45 days or less"
    elif time_delta <= pd.Timedelta(90, "d"):
        return "46-90 days"
    elif time_delta <= pd.Timedelta(150, "d"):
        return "91-150 days"
    elif time_delta <= pd.Timedelta(365, "d"):
        return "151-365 days"
    elif time_delta <= pd.Timedelta(720, "d"):
        return "1-2 years"
    elif time_delta <= pd.Timedelta(1085, "d"):
        return "2-3 years"
    elif time_delta <= pd.Timedelta(1450, "d"):
        return "3-4 years"
    else:
        return "over 4 years"


def add_identifiers(identifiers, m2, m3, m4, m5):
    identifiers["Gender"] = identifiers["Gender"].map(
        {1: "Male", 2: "Female", 0: "Not Stated", 9: "Neither"}
    )
    identifiers["Age"] = pd.to_datetime("today") - pd.to_datetime(
        identifiers["Dob (ccyy-mm-dd)"], format="%d/%m/%Y", errors="coerce"
    )
    identifiers["Age"] = round((identifiers["Age"] / np.timedelta64(1, "Y")))
    identifiers["Age Group"] = identifiers["Age"].apply(age_buckets)

    st.write(identifiers)
    m2 = pd.merge(m2, identifiers, on="Person ID", how="left")
    m3 = pd.merge(m3, identifiers, on="Person ID", how="left")
    m4 = pd.merge(m4, identifiers, on="Person ID", how="left")
    m5 = pd.merge(m5, identifiers, on="Person ID", how="left")
    return m2, m3, m4, m5


# Plotting functions
def hist_for_categories(df):
    hist_gender = px.histogram(df, x="Gender")
    hist_ethnicity = px.histogram(df, x="Ethnicity")
    hist_age = px.histogram(df, x="Age Group", color="Gender", marginal="violin")

    return hist_gender, hist_ethnicity, hist_age


def box_for_categories(df, y):
    box_gender = px.box(df, x="Gender", y=y)
    box_ethnicity = px.box(df, x="Ethnicity", y=y)
    box_age = px.box(df, x="Age Group", color="Gender", y=y)

    return box_gender, box_ethnicity, box_age


# Calculation functions
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

    fig_count_ceased = go.Figure(go.Indicator(value=count_ehc_ceased))
    fig_count_ceased.update_layout(
        title={
            "text": "EHC ceased in the last year",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )
    gender_hist, ethnicity_hist, age_hist = hist_for_categories(ehc_ceased_in_year)

    gender_hist.update_layout(title="EHC ceased this year by gender")
    ethnicity_hist.update_layout(title="EHC ceased this year by ethnicity")
    age_hist.update_layout(title="EHC ceased this year by age and gender")

    reason_ceased_pie = px.pie(
        reason_ech_ceased,
        values="count",
        names="Reason EHC Plan Ceased",
        title="Reason EHC ceased",
    )

    return fig_count_ceased, gender_hist, ethnicity_hist, age_hist, reason_ceased_pie


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
    fig_count_started = go.Figure(go.Indicator(value=count_ehc_started))
    fig_count_started.update_layout(
        title={
            "text": "EHC started in the last year",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    gender_hist, ethnicity_hist, age_hist = hist_for_categories(ehc_started_in_year)

    gender_hist.update_layout(title="EHC started this year by gender")
    ethnicity_hist.update_layout(title="EHC started this year by ethnicity")
    age_hist.update_layout(title="EHC started this year by age and gender")

    return fig_count_started, gender_hist, ethnicity_hist, age_hist


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
    ass_outcomes_pie = px.pie(
        ass_year_outcomes,
        values="count",
        names="Assessment Outcome To Issue EHCP",
        title="Outcomes of assessments closed this year",
    )

    assessments_completed_this_year = len(ass_this_year)
    fig_count_completed = go.Figure(go.Indicator(value=assessments_completed_this_year))
    fig_count_completed.update_layout(
        title={
            "text": "Assessments completed in the last year",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    gender_hist, ethnicity_hist, age_hist = hist_for_categories(ass_this_year)

    gender_hist.update_layout(title="Assessments completed this year by gender")
    ethnicity_hist.update_layout(title="Assessments completed this year by ethnicity")
    age_hist.update_layout(title="Assessments completed this year by age and gender")

    return fig_count_completed, gender_hist, ethnicity_hist, age_hist, ass_outcomes_pie


def closed_ass_timeframes(df1, df2):
    """
    Time between request being recieved in module 2, and now, (filtering closed assessments from module 3).

    df1 = module 2
    df2 = module 3
    """

    df = pd.merge(
        df1,
        df2,
        on=[
            "Person ID",
            "Requests Record ID",
            "Gender",
            "Ethnicity",
            "Age",
            "Age Group",
        ],
        how="inner",
    )

    df["Date Request Was Received"] = pd.to_datetime(
        df["Date Request Was Received"], format="%d/%m/%Y", errors="coerce"
    )
    df["Assessment Outcome Date"] = pd.to_datetime(
        df["Assessment Outcome Date"], format="%d/%m/%Y", errors="coerce"
    )
    df = df[
        (df["Assessment Outcome Date"].notna())
        & (
            (pd.to_datetime("today") - df["Assessment Outcome Date"])
            <= pd.Timedelta(timeframe, "d")
        )
    ]

    closed_assessment_requests = len(
        df[
            df["Assessment Outcome Date"].notna()
            & df["Date Request Was Received"].notna()
        ]
    )
    closed_requests = go.Figure(go.Indicator(value=closed_assessment_requests))
    closed_requests.update_layout(
        title={
            "text": "Closed assessment requests in the past year",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    st.plotly_chart(closed_requests)

    df["closed_ass_timeliness"] = (
        df["Assessment Outcome Date"] - df["Date Request Was Received"]
    ) / pd.Timedelta(1, "day")
    df["closed_ass_timeliness"] = df["closed_ass_timeliness"].round()

    gender_box, ethnicity_box, age_box = box_for_categories(df, "closed_ass_timeliness")
    gender_box.update_layout(
        title="Distribution of wait times for closed assessments by gender"
    )
    ethnicity_box.update_layout(
        title="Distribution of wait times for closed assessments by ethnicity"
    )
    age_box.update_layout(
        title="Distribution of wait times for closed assessments by age"
    )

    return gender_box, ethnicity_box, age_box


def open_ass_timeframes(df1, df2):
    """
    Time between request being recieved in module 2, and now, (filtering closed assessments from module 3).

    df1 = module 2
    df2 = module 3
    """
    df = pd.merge(
        df1,
        df2,
        on=[
            "Person ID",
            "Requests Record ID",
            "Gender",
            "Ethnicity",
            "Age",
            "Age Group",
        ],
        how="inner",
    )
    df = df[df["Date Request Was Received"].notna()]

    uncompleted_assessment_requests = len(df[df["Assessment Outcome Date"].isna()])
    uncompleted_requests = go.Figure(
        go.Indicator(value=uncompleted_assessment_requests)
    )
    uncompleted_requests.update_layout(
        title={
            "text": "Uncompleted assessment requests",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    df = df[df["Assessment Outcome Date"].isna()]
    df["Date Request Was Received"] = pd.to_datetime(
        df["Date Request Was Received"], format="%d/%m/%Y", errors="coerce"
    )
    df["open_ass_timeliness"] = (
        np.datetime64("today") - df["Date Request Was Received"]
    ) / pd.Timedelta(1, "day")
    df["open_ass_timeliness"] = df["open_ass_timeliness"].round()

    gender_box, ethnicity_box, age_box = box_for_categories(df, "open_ass_timeliness")
    gender_box.update_layout(
        title="Distribution of wait times for currently open assessments by gender"
    )
    ethnicity_box.update_layout(
        title="Distribution of wait times for currently open assessments by ethnicity"
    )
    age_box.update_layout(
        title="Distribution of wait times for currently open assessments by age"
    )

    return uncompleted_requests, gender_box, ethnicity_box, age_box


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
    fig_count_req = go.Figure(go.Indicator(value=count_requests_this_year))
    fig_count_req.update_layout(
        title={
            "text": "Requests this year",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    request_outcomes = (
        df.groupby("Request Outcome")["Request Outcome"]
        .count()
        .reset_index(name="count")
    )
    requests_pie = px.pie(request_outcomes, values="count", names="Request Outcome")

    gender_hist, ethnicity_hist, age_hist = hist_for_categories(df)
    gender_hist.update_layout(title="Distribution of gender for requests this year")
    ethnicity_hist.update_layout(
        title="Distribution of ethnicity for requests this year"
    )
    age_hist.update_layout(title="Distribution of age for requests this year")

    return fig_count_req, gender_hist, ethnicity_hist, age_hist, requests_pie


def multiple_appearances(m2, m3):
    m2 = m2.groupby("Person ID")["Person ID"].count().reset_index(name="count")
    m2 = m2[m2["count"] > 1]
    multiple_m2 = go.Figure(go.Indicator(value=len(m2)))
    multiple_m2.update_layout(
        title={
            "text": "Children appearing in the requests list multiple times",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    m3 = m3.groupby("Person ID")["Person ID"].count().reset_index(name="count")
    m3 = m3[m3["count"] > 1]
    multiple_m3 = go.Figure(go.Indicator(value=len(m2)))
    multiple_m3.update_layout(
        title={
            "text": "Children appearing in the assessments list multiple times",
            "y": 0.6,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    return multiple_m2, multiple_m3


def journeys(m2, m3):
    m2 = m2[m2["Date Request Was Received"].notna()]
    m2["Request"] = "Request Made"

    m3["Assessment Complete"] = m3["Assessment Outcome Date"].apply(
        lambda x: (
            "Assessment Completed" if pd.notna(x) else "Assessment not yet completed"
        )
    )

    df = pd.merge(
        m2,
        m3[
            [
                "Requests Record ID",
                "Person ID",
                "Assessment Outcome To Issue EHCP",
                "Assessment Complete",
            ]
        ],
        on=["Person ID", "Requests Record ID"],
        how="left",
    )

    df["Assessment Complete"] = df["Assessment Complete"].fillna(
        "Assessment uncompleted"
    )
    df["Assessment Outcome To Issue EHCP"] = df[
        "Assessment Outcome To Issue EHCP"
    ].fillna("No assessment outcome")

    fig = px.parallel_categories(
        df,
        dimensions=[
            "Request",
            "Request Outcome",
            "Assessment Complete",
            "Assessment Outcome To Issue EHCP",
        ],
    )
    fig.update_layout(margin=dict(l=50, r=50, t=50, b=50))
    st.plotly_chart(fig)


def plan_length_plots(m4):
    m4["EHC Plan Start Date"] = pd.to_datetime(
        m4["EHC Plan Start Date"], format="%d/%m/%Y"
    )
    m4["Date EHC Plan Ceased"] = pd.to_datetime(
        m4["Date EHC Plan Ceased"], format="%d/%m/%Y"
    )

    df_open = m4[m4["Date EHC Plan Ceased"].isna() & m4["EHC Plan Start Date"].notna()]
    df_open["Plan length"] = pd.to_datetime("today") - df_open["EHC Plan Start Date"]
    df_open["Plan length"] = df_open["Plan length"].apply(timeliness_buckets)
    open_gender_hist = px.histogram(
        df_open,
        x="Plan length",
        color="Gender",
        title="Currently open plan lengths by gender",
        category_orders={
            "Plan length": [
                "45 days or less",
                "46-90 days",
                "91-150 days",
                "151-365 days",
                "1-2 years",
                "2-3 years",
                "3-4 years",
                "over 4 years",
            ]
        },
    )
    open_ethnicity_hist = px.histogram(
        df_open,
        x="Plan length",
        color="Ethnicity",
        title="Currently open plan lengths by ethnicity",
        category_orders={
            "Plan length": [
                "45 days or less",
                "46-90 days",
                "91-150 days",
                "151-365 days",
                "1-2 years",
                "2-3 years",
                "3-4 years",
                "over 4 years",
            ]
        },
    )
    open_age_hist = px.histogram(
        df_open,
        x="Plan length",
        color="Age Group",
        title="Currently open plan lengths by age",
        category_orders={
            "Plan length": [
                "45 days or less",
                "46-90 days",
                "91-150 days",
                "151-365 days",
                "1-2 years",
                "2-3 years",
                "3-4 years",
                "over 4 years",
            ]
        },
    )

    df_closed = m4[
        m4["Date EHC Plan Ceased"].notna() & m4["EHC Plan Start Date"].notna()
    ]
    df_closed["Plan length"] = (
        df_closed["Date EHC Plan Ceased"] - df_closed["EHC Plan Start Date"]
    )
    df_closed["Plan length"] = df_closed["Plan length"].apply(timeliness_buckets)
    closed_gender_hist = px.histogram(
        df_closed,
        x="Plan length",
        color="Gender",
        title="Closed plan lengths by gender",
        category_orders={
            "Plan length": [
                "45 days or less",
                "46-90 days",
                "91-150 days",
                "151-365 days",
                "1-2 years",
                "2-3 years",
                "3-4 years",
                "over 4 years",
            ]
        },
    )
    closed_ethnicity_hist = px.histogram(
        df_closed,
        x="Plan length",
        color="Ethnicity",
        title="Closed plan lengths by ethnicity",
        category_orders={
            "Plan length": [
                "45 days or less",
                "46-90 days",
                "91-150 days",
                "151-365 days",
                "1-2 years",
                "2-3 years",
                "3-4 years",
                "over 4 years",
            ]
        },
    )
    closed_age_hist = px.histogram(
        df_closed,
        x="Plan length",
        color="Age Group",
        title="Closed plan lengths by age",
        category_orders={
            "Plan length": [
                "45 days or less",
                "46-90 days",
                "91-150 days",
                "151-365 days",
                "1-2 years",
                "2-3 years",
                "3-4 years",
                "over 4 years",
            ]
        },
    )

    return (
        open_gender_hist,
        open_ethnicity_hist,
        open_age_hist,
        closed_gender_hist,
        closed_ethnicity_hist,
        closed_age_hist,
    )


# Main script
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

    modules["m2"], modules["m3"], modules["m4"], modules["m5"] = add_identifiers(
        modules["m1"], modules["m2"], modules["m3"], modules["m4"], modules["m5"]
    )

    st.title("EHC ceased this year")
    (
        ceased,
        ceased_gender_hist,
        ceased_ethnicity_hist,
        ceased_age_hist,
        reason_ceased_pie,
    ) = ehc_ceased_year(modules["m4"])

    st.plotly_chart(ceased)
    st.plotly_chart(ceased_gender_hist)
    st.plotly_chart(ceased_ethnicity_hist)
    st.plotly_chart(ceased_age_hist)
    st.plotly_chart(reason_ceased_pie)

    st.title("EHC Starting this year")

    started, started_gender_hist, started_ethnicity_hist, started_age_hist = (
        ehc_starting_year(modules["m4"])
    )
    st.plotly_chart(started)
    st.plotly_chart(started_gender_hist)
    st.plotly_chart(started_ethnicity_hist)
    st.plotly_chart(started_age_hist)

    st.title("Assessments completed this year")
    (
        completed,
        completed_gender_hist,
        completed_ethnicity_hist,
        completed_age_hist,
        ass_outcome_pie,
    ) = ass_completed_year(modules["m3"])

    st.plotly_chart(completed)
    st.plotly_chart(completed_gender_hist)
    st.plotly_chart(completed_ethnicity_hist)
    st.plotly_chart(completed_age_hist)
    st.plotly_chart(ass_outcome_pie)

    st.title("Open assessment timeframes")
    open, open_gender_box, open_ethnicity_box, open_age_box = open_ass_timeframes(
        modules["m2"], modules["m3"]
    )

    st.plotly_chart(open)
    st.plotly_chart(open_gender_box)
    st.plotly_chart(open_ethnicity_box)
    st.plotly_chart(open_age_box)

    st.title("Closed assessment timeframes (last year)")
    closed_ass_gender_box, closed_ass_ethnicity_box, closed_ass_age_box = (
        closed_ass_timeframes(modules["m2"], modules["m3"])
    )

    st.plotly_chart(closed_ass_gender_box)
    st.plotly_chart(closed_ass_ethnicity_box)
    st.plotly_chart(closed_ass_age_box)

    st.title("Requests this year")
    req_fig, req_gender_box, req_ethnicity_box, req_age_box, req_pie = requests_fn(
        modules["m2"]
    )

    st.plotly_chart(req_fig)
    st.plotly_chart(req_gender_box)
    st.plotly_chart(req_ethnicity_box)
    st.plotly_chart(req_age_box)
    st.plotly_chart(req_pie)

    st.title("Multiple appearances")
    multiple_m2, multiple_m3 = multiple_appearances(modules["m2"], modules["m3"])
    st.plotly_chart(multiple_m2)
    st.plotly_chart(multiple_m3)

    fig = journeys(modules["m2"], modules["m3"])
    st.plotly_chart(fig)

    st.title("Currently open and currently closed plan lengths")
    (
        open_gender_hist,
        open_ethnicity_hist,
        open_age_hist,
        closed_gender_hist,
        closed_ethnicity_hist,
        closed_age_hist,
    ) = plan_length_plots(modules["m4"])
    st.plotly_chart(open_gender_hist)
    st.plotly_chart(open_ethnicity_hist)
    st.plotly_chart(open_age_hist)
    st.plotly_chart(closed_gender_hist)
    st.plotly_chart(closed_ethnicity_hist)
    st.plotly_chart(closed_age_hist)
