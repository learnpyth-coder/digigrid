'''
This is a helper module for the case management system.
It contains functions for displaying case information.
'''
# Import relevant modules
import streamlit as st
from digigrid_streamlit_config import S_APPEAL, S_HEAD_DONE
from Helper_module_workflow import evaluate_appeal
from Helper_module_basics import get, now, parse, put, show, word_count
from Helper_module_file_handling import read_text, save_cases, read_file_bytes

# Define a function to display a line indicating when something is due and whether it was completed on time
def due_line(label, due_text, done_text=""):
    """One line saying when something is due and whether it was on time."""
    if due_text == "":
        return
    due = parse(due_text)
    if done_text != "":
        if parse(done_text) <= due:
            st.write("- " + label + ": done on time (due " + show(due_text) + ")")
        else:
            st.write("- " + label + ": done LATE (due " + show(due_text)
                     + ", done " + show(done_text) + ")")
    elif now() > due:
        st.write("- " + label + ": **OVERDUE** (was due " + show(due_text) + ")")
    else:
        st.write("- " + label + ": due by " + show(due_text))

# Define a function to display case information in read-only mode, including complainant and respondent details, and evidence if available
def show_case_readonly(case, show_complainant=True, show_respondent=True,
                       show_evidence=True):
    cid = get(case, "case_id")
    st.write("**Case ID:** " + cid + "  |  **Type:** " + get(case, "case_type"))
    st.write("**Filed:** " + show(get(case, "filed_at")))
    st.write("**Status:** " + get(case, "status"))
    if show_complainant:
        st.write("**Complainant:** " + get(case, "name") + " | "
                 + get(case, "institute_id") + " | " + get(case, "email")
                 + " | " + get(case, "contact"))
    if show_respondent:
        if get(case, "respondent_known") == "Yes" or get(case, "r_email") != "":
            st.write("**Respondent:** " + get(case, "r_name") + " | "
                     + get(case, "r_institute_id") + " | " + get(case, "r_email")
                     + " | " + get(case, "r_contact"))
        else:
            st.write("**Respondent:** not identified by the complainant")
    # if show_evidence:
    #     if get(case, "evidence_available") == "Yes":
    #         st.write("**Evidence submitted:**")
    #         st.info(read_text("evidence", cid))
    #     else:
    #         st.write("**Evidence:** none submitted")
    if show_evidence:
        if get(case, "evidence_available") == "Yes":
            st.write("**Evidence submitted:**")
            text = read_text("evidence", cid)
            if text != "":
                st.info(text)
            files = get(case, "evidence_files")
            if files != "":
                for stored in files.split(";"):
                    st.download_button("Download " + stored, data=read_file_bytes(stored), # draw a button on the page. When someone clicks it, they can download it.
                                       file_name=stored, key="dl_" + cid + "_" + stored) # key gives a unique ID for the button (including case ID and file name)
        else:
            st.write("**Evidence:** none submitted")

# Define a function to display the deadlines associated with a case, including review, meeting, reporting, and decision deadlines
def show_deadlines(case):
    st.write("**Deadlines**")
    due_line("Review by cell/committee", get(case, "review_due"),
             get(case, "review_done_at"))
    due_line("Respondent to meet the cell/committee", get(case, "meet_by"))
    due_line("Report to Director", get(case, "report_due"),
             get(case, "report_sent_at"))
    due_line("Director's review of the report", get(case, "director_due"),
             get(case, "director_reviewed_at"))
    if get(case, "route") == "APPEAL":
        due_line("Appeal decision", get(case, "appeal_due"), get(case, "decision_at"))
    if get(case, "route") == "NO APPEAL":
        due_line("Director's decision", get(case, "decision_due"),
                 get(case, "decision_at"))

# Define a function to display the decision made on a case, including who recorded it and when
def show_decision(case):
    if get(case, "decision_at") != "":
        st.write("**Decision** (read only) - recorded by " + get(case, "decision_by")
                 + " on " + show(get(case, "decision_at")))
        st.success(read_text("decision", get(case, "case_id")))

# Define a function to create a text box with a word limit, displaying an error if the limit is exceeded and showing the current word count
def text_box_with_limit(label, limit, key):
    text = st.text_area(label + " (up to " + str(limit) + " words)", key=key)
    count = word_count(text)
    if count > limit:
        st.error("Too long: " + str(count) + " words (limit " + str(limit) + ").")
    else:
        st.caption(str(count) + " / " + str(limit) + " words")
    return text, count <= limit

# Define a function to determine if a party (complainant or respondent) can answer an appeal based on the case status and appeal deadline
def can_answer_appeal(case, who):
    status = get(case, "status")
    if get(case, who + "_appeal") != "":
        return False
    if status != S_HEAD_DONE and not status.startswith(S_APPEAL):
        return False
    return now() < parse(get(case, "appeal_deadline"))

# Define a function to handle the appeal question for a party (complainant or respondent), allowing them to submit their answer and updating the case accordingly
def appeal_question(cases, case, who):
    """who is 'complainant' or 'respondent'."""
    cid = get(case, "case_id")
    answer = get(case, who + "_appeal")
    if answer != "":
        st.write("Your answer to 'Do you want to appeal?': **" + answer + "**")
    elif can_answer_appeal(case, who):
        st.warning("The Head of the Institute has reviewed this case. "
                   "You may decide on an appeal until "
                   + show(get(case, "appeal_deadline")) + ".")
        choice = st.radio("Do you want to appeal?", ("Yes", "No"), index=None,
                          key="ap_" + cid + "_" + who)
        if st.button("Submit answer", key="apbtn_" + cid + "_" + who):
            if choice is None:
                st.error("Please choose Yes or No.")
            else:
                put(case, who + "_appeal", choice.upper())
                evaluate_appeal(case)
                save_cases(cases)
                st.rerun()