import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1K6mEHsKbHuTnde0d-r3CMLf3IoefKTWz5yYqIap2tm0"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


@st.cache_resource
def get_sheet():
    """Connect to Google Sheets using service account from Streamlit secrets."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    
    # Add headers if sheet is empty
    if not sheet.get_all_values():
        sheet.append_row([
            "Date", "Job Title", "Job Link", "Budget/Rate",
            "Duration", "Connects", "Proposal", "Status", "Notes"
        ])
    return sheet


def log_to_crm(date, job_title, job_link, budget, duration, connects, proposal):
    """Append a new row to the CRM sheet."""
    try:
        sheet = get_sheet()
        sheet.append_row([
            date, job_title, job_link, budget,
            duration, connects, proposal, "Sent", ""
        ])
        return True
    except Exception as e:
        return str(e)
