import pandas as pd
import js
from js import files
import pyodide_js
import json
import io
import plotly as px

dfs = {}
for i, v in enumerate(files):
    dfs[i] = pd.read_csv(io.StringIO(files[i]))

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

fig = fig.to_html(
    include_plotlyjs=False,
    full_html=False,
    default_height='350px'
)

js.document.fig = fig

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

modules = {}

for key, df in dfs.items():
    for module_name, column_list in module_columns.items():
        if list(df.columns) == column_list:
            modules[module_name] = df


if len(modules.keys()) != 5:
    js.alert(f'Modules found {modules.keys()}, please check column names.')

modules['m1']["Dob (ccyy-mm-dd)"] = pd.to_datetime(modules['m1']["Dob (ccyy-mm-dd)"])


