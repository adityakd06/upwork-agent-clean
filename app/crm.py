import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1K6mEHsKbHuTnde0d-r3CMLf3IoefKTWz5yYqIap2tm0"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


HEADERS = [
    "Date", "Job Title", "Job Link", "Budget/Rate",
    "Duration", "Connects", "Proposal", "Status", "Notes",
    "Viewed", "Replied", "Converted to Client"
]

# Columns (1-indexed) that should have Yes/No dropdown validation
DROPDOWN_COLS = {
    10: "Viewed",
    11: "Replied",
    12: "Converted to Client",
}


@st.cache_resource
def get_sheet():
    """Connect to Google Sheets using service account from Streamlit secrets."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    sheet = spreadsheet.sheet1

    # Add headers and dropdowns if sheet is empty
    if not sheet.get_all_values():
        sheet.append_row(HEADERS)
        _add_dropdowns(spreadsheet, sheet)

    return sheet


def _add_dropdowns(spreadsheet, sheet):
    """Add Yes/No dropdown validation to Viewed, Replied, Converted columns."""
    sheet_id = sheet._properties["sheetId"]
    requests = []
    for col_index in DROPDOWN_COLS:
        requests.append({
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,      # skip header row
                    "endRowIndex": 1000,
                    "startColumnIndex": col_index - 1,
                    "endColumnIndex": col_index,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [
                            {"userEnteredValue": "Yes"},
                            {"userEnteredValue": "No"},
                        ],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        })
    spreadsheet.batch_update({"requests": requests})


def log_to_crm(date, job_title, job_link, budget, duration, connects, proposal):
    """Append a new row to the CRM sheet."""
    try:
        sheet = get_sheet()
        sheet.append_row([
            date, job_title, job_link, budget,
            duration, connects, proposal, "Sent", "",
            "", "", ""   # Viewed, Replied, Converted to Client — filled manually
        ])
        return True
    except Exception as e:
        return str(e)