from datetime import timedelta

from digigrid_streamlit_config import (S_NO_APPEAL, S_APPEAL, S_HEAD_DONE, S_DECIDED,
                                       S_RESOLVED, NO_APPEAL_DECISION_DAYS,
                                       APPEAL_DECISION_DAYS, RESOLVE_HOURS,
                                       DIRECTOR_EMAIL, OMBUDS_EMAIL)
from Helper_module_basics import get, put, now, stamp, parse, show, later
from Helper_module_file_handling import load_cases, save_cases
from Helper_module_email import send_email, email_cell_and_parties

# ======================= Functions for Appeals/Decisions =========================

# Define a function to set the case status to "NO APPEAL" and update the relevant fields, including sending an email notification to the director
def set_no_appeal(case):
    put(case, "route", "NO APPEAL") # Call the put function from Helper_module_basics to update the "route" field of the case to "NO APPEAL"
    put(case, "status", S_NO_APPEAL)
    due = later(stamp(now()), days=NO_APPEAL_DECISION_DAYS) # Call the later function from Helper_module_basics to calculate the due date for the director's decision
    put(case, "decision_due", due)
    send_email(DIRECTOR_EMAIL, # Call the send_email function from Helper_module_email to send an email notification to the director
               "Case " + get(case, "case_id") + ": no appeal received", # Call the get function from Helper_module_basics to retrieve the case ID for the email subject
               "No appeal was received from the complainant or the respondent "
               "of case " + get(case, "case_id") + ".\n"
               "Please log in to the portal and enter your decision within "
               + str(NO_APPEAL_DECISION_DAYS) + " days (by " + show(due) + ").") # Call the show function from Helper_module_basics to format the due date for display in the email body

# Define a function for a case when there is an appeal and update the relevant fields, including sending an email notification to the ombudsperson
def evaluate_appeal(case):
    """Looks at the two answers and moves the case on if the outcome is clear."""
    c_ans = get(case, "complainant_appeal") # Call the get function from Helper_module_basics to retrieve the complainant's appeal answer from the case
    r_ans = get(case, "respondent_appeal") # Call the get function from Helper_module_basics to retrieve the respondent's appeal answer from the case
    who = []
    if c_ans == "YES":
        who.append("COMPLAINANT")
    if r_ans == "YES":
        who.append("RESPONDENT")
    if len(who) > 0:
        first_time = get(case, "route") != "APPEAL"
        put(case, "route", "APPEAL") # Call the put function from Helper_module_basics to update the "route" field of the case to "APPEAL"
        put(case, "status", S_APPEAL + " AND ".join(who))
        if first_time:
            due = later(get(case, "report_sent_at"), days=APPEAL_DECISION_DAYS) # Call the later function to calculate the due date for the appeal decision based on the report sent date
            put(case, "appeal_due", due)
            send_email(DIRECTOR_EMAIL,
                       "Case " + get(case, "case_id") + ": appeal requested",
                       "An appeal has been requested for case " + get(case, "case_id")
                       + ".\nPlease log in and forward the case to the ombudsperson ("
                       + OMBUDS_EMAIL + "). The appeal decision is due by "
                       + show(due) + " (" + str(APPEAL_DECISION_DAYS)
                       + " days from the date the report was sent).")
    elif c_ans == "NO" and r_ans == "NO":
        set_no_appeal(case)

# Define a function to check and apply time-based rules for cases:
# setting the status to "NO APPEAL" or "RESOLVED" based on deadlines and sending email notifications accordingly
def apply_time_rules():
    """Runs every time a page loads: handles rules that depend only on time."""
    cases = load_cases() # Call the load_cases function from Helper_module_file_handling to load the list of cases from the cases file
    changed = False
    t = now() # Call the now function from Helper_module_basics to get the current time, which may be shifted for testing purposes
    for case in cases:
        status = get(case, "status")

        if status == S_HEAD_DONE: # If the case status is "CASE REVIEWED BY HEAD of HEI"
            if t >= parse(get(case, "appeal_deadline")): # Call the parse function from Helper_module_basics to convert the appeal deadline string to a datetime object for comparison with the current time
                set_no_appeal(case) # Call the set_no_appeal function to update the case status and send an email notification to the director
                changed = True

        elif status == S_DECIDED: # If the case status is "DECISION RECORDED"
            if t >= parse(get(case, "decision_at")) + timedelta(hours=RESOLVE_HOURS):
                put(case, "status", S_RESOLVED)
                put(case, "resolved_at", stamp(t))
                email_cell_and_parties( # Call the email_cell_and_parties function from Helper_module_email to send an email notification to the complainant, respondent (if known), and the relevant cell/committee about the case resolution
                    case, "Case " + get(case, "case_id") + " resolved",
                    "Case " + get(case, "case_id") + " is now RESOLVED and closed.")
                changed = True
    if changed:
        save_cases(cases)