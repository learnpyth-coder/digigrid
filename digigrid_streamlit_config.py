'''
This module contains constants and configuration settings for the DigiGriD application
'''

import os
from pathlib import Path

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def _setting(name, default=""):
    value = os.getenv(name)
    if value is not None:
        return value

    try:
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default


# Define constants for file names, separators, time formats, email addresses, time limits, word limits, case types, user accounts, case statuses, and case fields
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(_setting("DIGIGRID_DATA_DIR", str(BASE_DIR)))
DATA_DIR.mkdir(parents=True, exist_ok=True)

CASES_FILE = str(DATA_DIR / "digigrid_cases.txt")
USERS_FILE = str(DATA_DIR / "users_db.txt")
MAIL_FILE = str(DATA_DIR / "emails_outbox.txt")
SEP = " | "
NEWLINE_CODE = "~~"
TIME_FMT = "%Y-%m-%d %H:%M:%S"
SHOW_FMT = "%d-%m-%Y %H:%M"

# SMTP settings. Keep credentials in the server environment, never in source code.
SMTP_HOST = _setting("DIGIGRID_SMTP_HOST")
SMTP_PORT = int(_setting("DIGIGRID_SMTP_PORT", "587"))
SMTP_USERNAME = _setting("DIGIGRID_SMTP_USERNAME")
SMTP_PASSWORD = _setting("DIGIGRID_SMTP_PASSWORD")
SMTP_FROM = _setting("DIGIGRID_SMTP_FROM", SMTP_USERNAME)
SMTP_USE_SSL = _setting("DIGIGRID_SMTP_USE_SSL", "false").lower() == "true"
SMTP_TIMEOUT = int(_setting("DIGIGRID_SMTP_TIMEOUT", "30"))

# Institute email IDs (from the workflow)
GRIEVANCE_EMAIL = _setting("DIGIGRID_GRIEVANCE_EMAIL", "grievance_cell@xxxx.ac.in")
DISCIPLINE_EMAIL = _setting("DIGIGRID_DISCIPLINE_EMAIL", "discipline_comm@xxxx.ac.in")
DIRECTOR_EMAIL = _setting("DIGIGRID_DIRECTOR_EMAIL", "director@xxxx.ac.in")
OMBUDS_EMAIL = _setting("DIGIGRID_OMBUDS_EMAIL", "ext_person@gmail.com")

# Time limits for various stages of the case workflow (in minutes for demonstration purposes)
# for the sake of demonstration, kept all as "x" minute using fractions
REVIEW_HOURS = 1 / 60          # 1 minute (orig = 24) limit for cell/committee review after filing
MEET_DAYS = 2 / 1440           # 2 minutes (orig = 5) for respondent to meet the cell/committee
REPORT_DAYS = 3 / 1440         # 3 minutes (orig = 15) for report to director
DIRECTOR_READ_DAYS = 4 / 1440  # 4 minutes (orig = 5) for director to read the report
APPEAL_WINDOW_DAYS = 5 / 1440  # 5 minutes (orig = 5) for complainant/respondent to decide on appeal
APPEAL_DECISION_DAYS = 6 / 1440 # 6 minutes (orig = 30) for appeal decision
NO_APPEAL_DECISION_DAYS = 6 / 1440 # 6 minutes (orig = 7) for no appeal decision
RESOLVE_HOURS = 1 / 60         # 1 minute (orig = 24) decision visibility before resolving
WORDS_SHORT = 100          
WORDS_REPORT = 300
WORDS_DECISION = 200

# Constants for uploading multimedia for evidence
MAX_DOC_BYTES = 100 * 1024            # 100 KB for PDF/TXT
MAX_MEDIA_BYTES = 100 * 1024 * 1024   # 100 MB for photo/audio/video
DOC_TYPES = ["pdf", "txt"]
MEDIA_TYPES = ["jpg", "jpeg", "png", "mp3", "mp4"]

CASE_TYPES = ("Discrimination", "Academic Misconduct")

# Accounts: (email ID, password, role, display name)
# Everyone logs in using their email ID
USERS = (
    ("mewanzbwar@gmail.com", "pass123", "Complainant", "Demo Student One"),
    ("complainant2@xxxx.ac.in", "pass456", "Complainant", "Demo Student Two"),
    (GRIEVANCE_EMAIL, "grv123", "Grievance Cell", "Grievance Cell"),
    (DISCIPLINE_EMAIL, "disc123", "Disciplinary Committee", "Disciplinary Committee"),
    (DIRECTOR_EMAIL, "dir123", "Director", "Director of the Institute"),
    (OMBUDS_EMAIL, "omb123", "Ombudsperson", "Ombudsperson"),
)

# Case statuses
S_REG = "ALLEGATION REGISTERED"
S_REVIEWED = "REVIEWED BY CELL/COMMITTEE"
S_SUMMONED = "RESPONDENT SUMMONED"
S_REPORT = "REPORT SENT TO DIRECTOR"
S_HEAD_READING = "CASE UNDER REVIEW BY HEAD of HEI"
S_HEAD_DONE = "CASE REVIEWED BY HEAD of HEI"
S_APPEAL = "APPEAL REQUESTED BY "
S_NO_APPEAL = "NO APPEAL RECEIVED - AWAITING DIRECTOR'S DECISION"
S_REFERRED = "APPEAL REFERRED TO OMBUDSPERSON"
S_PROPOSED = "DECISION PROPOSED BY OMBUDSPERSON - AWAITING DIRECTOR'S CONFIRMATION"
S_DECIDED = "DECISION RECORDED"
S_RESOLVED = "CASE RESOLVED"

# The fields of one case
FIELDS = (
    "case_id", "case_type", "filed_at",
    "name", "email", "institute_id", "contact",
    "respondent_known", "r_name", "r_institute_id", "r_email", "r_contact",
    "evidence_available", "evidence_files", "status",
    "review_due", "review_done_at",
    "summoned_at", "meet_by", "report_due", "statement_at",
    "report_sent_at", "director_due", "director_opened_at", "director_reviewed_at",
    "appeal_deadline", "complainant_appeal", "respondent_appeal", "route",
    "appeal_due", "referred_at", "decision_due", "decision_at", "decision_by",
    "resolved_at",
)