module_columns = {
    "m1": [
        "Person ID",
        "Surname Forename",
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
            

print(modules.keys())
print(module_columns.keys())
