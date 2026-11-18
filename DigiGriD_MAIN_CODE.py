'''
This is the main file for the DigiGriD application.
It incorporates all modules and defines the main workflow of the case management system.
'''
# Import streamlit for building the web application interface
import streamlit as st

# Import the datetime module for handling date and time operations
from datetime import datetime, timedelta

# Import the functions from digigrid_streamlit_config for configuration constants
from digigrid_streamlit_config import *

# Import the functions from the helper modules for various functionalities
from Helper_module_basics import get, put, clean, word_count, now, stamp, parse, show, later

from Helper_module_email import send_email, load_emails, authority_email, authority_name, email_cell_and_parties, valid_email, valid_contact

from Helper_module_file_handling import load_cases, save_cases, find_case, write_text, read_text, load_extra_users, check_login, create_respondent_account, safe_filename, save_evidence_file, read_file_bytes

from Helper_module_workflow import set_no_appeal, evaluate_appeal, apply_time_rules

from Helper_module_message_display import due_line, show_case_readonly, show_deadlines, show_decision, text_box_with_limit, can_answer_appeal, appeal_question

# =====================================================================
# DigiGriD - The whole working code (no longer a prototype)
# This code creates a fully functional portal-based system
# for SC/ST student grievance/disciplinary management in HEIs
# integrated with email notifications
# =====================================================================

# ============================ Case ID ============================
# Define a function to generate a new case ID based on the case type and the number of existing cases of that type

def new_case_id(cases, case_type):
    if case_type == "Discrimination": # Discrimination
        prefix = "DGDi"
    else:
        prefix = "DGAcM" # Academic Misconduct
    count = 0
    for case in cases:
        if get(case, "case_type") == case_type:
            count += 1 # Count the number of existing cases of the same type
    return prefix + str(count + 1).zfill(3) # zfill(3) pads the count with leading zeros to make it 3 digits long

# ============================ Login to DigiGriD =====================

# Define a function to display the login page for the DigiGriD application
# This page prompts users to enter their email ID and password to access the system
# If the credentials are incorrect, an error message is displayed
# Also, demo account information is provided for testing purposes
def login_page():
    st.title("DigiGriD") # st is the streamlit module used to create the web application interface
    st.subheader("An Institution-based Digital System for SC/ST Student Grievance and Disciplinary Management")
    st.write("Please log in to continue.")
    username = st.text_input("Email ID") # Call the text_input function from streamlit to create a text input field for the user to enter their email ID
    password = st.text_input("Password", type="password")

    if st.button("Log in"): # Call the button function from streamlit to create a button that triggers the login process when clicked
        user = check_login(username.strip(), password) # Call the check_login function from Helper_module_file_handling to verify the entered email ID and password against the stored user accounts
        if user is None:
            st.error("Incorrect username or password.") # Call the error function from streamlit to display an error message if the login credentials are incorrect
        else:
            st.session_state.user = user # Call the session_state object from streamlit to store the logged-in user's information for use in other pages of the application
            st.rerun() # Call the rerun function from streamlit to refresh the page and redirect the user to the appropriate page based on their role after successful login
    st.caption("Demo accounts - complainants: mewanzbwar@gmail.com / pass123, complainant2@xxxx.ac.in / pass456. "
               "Cell: dggrievance.cell@gmail.com / grv123. "
               "Committee: mewan.banshan@research.iiit.ac.in / disc123. "
               "Director: war.mewanb@gmail.com / dir123. "
               "Ombudsperson: ext_person@gmail.com / omb123. "
               "Respondents get their password by email when summoned "
               "(see 'Demo: email outbox' after logging in).") # Call the caption function from streamlit to display a caption with demo account information for testing purposes

# ============================ User 1: The Complainant ============================

# Define a function to register a complaint in the DigiGriD application
def register_page(user):
    v = str(st.session_state.form_version) # Call the session_state object from streamlit to retrieve the current form version for the complaint registration form
    st.header("Register a complaint") # Call the header function from streamlit to display a header for the complaint registration page

    if st.session_state.last_case_id is not None: # Call the session_state object from streamlit to check if a new case ID has been generated after successful complaint registration
        st.success("Complaint registered. Your Case ID is "
                   + st.session_state.last_case_id + ". Keep it to track your case.") # st.success displays a success message 
        st.session_state.last_case_id = None
    st.info("The date and time of registration are recorded automatically.") # Call the info function from streamlit to display a message about the automatic recording of the registration date and time

    st.subheader("1. Case type") # Call the subheader function from streamlit to display a subheader for the case type selection
    case_type = st.selectbox("Type of case", CASE_TYPES, key="type" + v) # Call the selectbox function from streamlit to create a dropdown menu for selecting the type of case (Discrimination or Academic Misconduct)

    st.subheader("2. Your details (complainant)")
    name = st.text_input("Full name", key="name" + v)
    # Enter institute ID first, then email ID
    inst_id = st.text_input("Institute ID", key="inst" + v)
    email = user[0] # Retrieve the email ID of the logged-in user from the user tuple
    st.write("Email ID: **" + email + "**")
    contact = st.text_input("Contact number", key="contact" + v)

    st.subheader("3. Respondent (the person the complaint is about)")
    knows = st.radio("Can you identify the respondent?", ("Yes", "No"), # Call the radio function from streamlit to create a radio button selection for whether the complainant can identify the respondent
                     index=1, key="knows" + v)
    r_name = r_inst = r_email = r_contact = "" # Initialize variables for respondent details (name, institute ID, email, contact) to empty strings

    r_name = r_inst = r_email = r_contact = ""
    r_desc = "" # description of the respondent's appearance
    r_desc_ok = True

    if knows == "Yes":
        st.caption("Fill in at least the respondent's name and email ID.")
        r_name = st.text_input("Respondent's name", key="rname" + v)
        r_inst = st.text_input("Respondent's Institute ID", key="rinst" + v)
        r_email = st.text_input("Respondent's email ID", key="remail" + v)
        r_contact = st.text_input("Respondent's contact number", key="rcontact" + v)
    else:
        st.info("Since you do not know the respondent's details, please describe their "
                "physical appearance. The relevant authority will ask you to meet them to help identify the person.")
        r_desc, r_desc_ok = text_box_with_limit(
            "Physical appearance of the respondent", WORDS_SHORT, "rdesc" + v)

    st.subheader("4. Evidence")
    has_evidence = st.radio("Is evidence in support of your complaint available?",
                            ("Yes", "No"), index=1, key="hasev" + v)
    evidence = ""
    evidence_ok = True
    doc_files = [] # initialise, so the names exist even when "No" is chosen
    media_files = []
    if has_evidence == "Yes":
        evidence, evidence_ok = text_box_with_limit( # Call the text_box_with_limit function from Helper_module_message_display to create a text area for entering evidence with a word limit
            "Type in your evidence (optional if you upload a file)", WORDS_SHORT, "evidence" + v)
        doc_files = st.file_uploader("Document: PDF or TXT (up to 100 KB each)", # If evidence = documents (PDF/TXT)
                                     type=DOC_TYPES, accept_multiple_files=True,
                                     key="evdoc" + v)
        media_files = st.file_uploader("Photo / audio / video (up to 100 MB each)", # If evidence = multimedia (photos/audio/video)
                                       type=MEDIA_TYPES, accept_multiple_files=True,
                                       key="evmedia" + v)

    if st.button("Submit complaint"): # Call the button function from streamlit to create a button that triggers the complaint submission process when clicked
        errors = []

        if name.strip() == "": # Call the strip method to remove leading and trailing whitespace from the complainant's name and check if it is empty
            errors.append("Enter your name.")
        if not valid_email(email.strip()): # Call the valid_email function from Helper_module_email to validate the complainant's email ID and check if it is valid
            errors.append("Enter a valid email ID.")
        if inst_id.strip() == "":
            errors.append("Enter your Institute ID.")
        if not valid_contact(contact.strip()): # Valid contact number is 10 to 13 digits
            errors.append("Enter a valid contact number (10 to 13 digits).")
        if knows == "Yes":
            if (r_name.strip() == "" and r_inst.strip() == ""
                    and r_email.strip() == "" and r_contact.strip() == ""):
                errors.append("Enter at least one detail of the respondent, "
                              "or choose 'No'.")
            if r_email.strip() != "" and not valid_email(r_email.strip()):
                errors.append("The respondent's email ID is not valid.")
        if has_evidence == "Yes":
            if evidence.strip() == "" and len(doc_files) == 0 and len(media_files) == 0:
                errors.append("Type in your evidence or upload a file, or choose 'No'.")
            if not evidence_ok:
                errors.append("The typed evidence is longer than " + str(WORDS_SHORT) + " words.")
            for f in doc_files:
                if f.size > MAX_DOC_BYTES:
                    errors.append(f.name + " is larger than 100 KB.")
            for f in media_files:
                if f.size > MAX_MEDIA_BYTES:
                    errors.append(f.name + " is larger than 100 MB.")
        if knows == "No":
            if r_desc.strip() == "":
                errors.append("Describe the respondent's physical appearance.")
            elif not r_desc_ok:
                errors.append("The description is longer than " + str(WORDS_SHORT) + " words.")

        if len(errors) > 0:
            for message in errors:
                st.error(message)
        else:
            cases = load_cases() # Call the load_cases function from Helper_module_file_handling to load the list of cases from the cases file
            filed = now() # Call the now function from Helper_module_basics to get the current date and time for the complaint filing timestamp
            case_id = new_case_id(cases, case_type) # Call the new_case_id function to generate a new case ID based on the case type and the number of existing cases of that type
            case = [""] * len(FIELDS)
            put(case, "case_id", case_id)
            put(case, "case_type", case_type)
            put(case, "filed_at", stamp(filed))
            put(case, "name", clean(name))
            put(case, "email", clean(email))
            put(case, "institute_id", clean(inst_id))
            put(case, "contact", clean(contact))
            put(case, "respondent_known", knows)
            put(case, "r_name", clean(r_name))
            put(case, "r_institute_id", clean(r_inst))
            put(case, "r_email", clean(r_email))
            put(case, "r_contact", clean(r_contact))
            put(case, "evidence_available", has_evidence)
            put(case, "status", S_REG)
            due = stamp(filed + timedelta(hours=REVIEW_HOURS)) # Call the stamp function from Helper_module_basics to format the due date
            put(case, "review_due", due)
            stored = [] # names of the saved evidence files
            if has_evidence == "Yes":
                number = 1
                for f in doc_files + media_files:
                    stored.append(save_evidence_file(case_id, f, number))
                    number += 1
                if evidence.strip() != "":
                    write_text("evidence", case_id, evidence.strip())
            put(case, "evidence_files", ";".join(stored))
            if knows == "No":
                write_text("description", case_id, r_desc.strip()) # This creates description_DGDi001.txt and so on
            cases.append(case)
            save_cases(cases) # Call the save_cases function from Helper_module_file_handling to save the updated list of cases to the cases file

            # Email to the relevant cell / committee
            send_email(authority_email(case_type), # Call the authority_email function to get the email address of the relevant cell/committee based on the case type
                       "New case " + case_id + " - review within 24 hours",
                       "A new " + case_type + " case (" + case_id + ") was filed on "
                       + show(stamp(filed)) + ".\n"
                       "The case review must be done within " + str(REVIEW_HOURS)
                       + " hours of filing, i.e. by " + show(due) + ".\n"
                       "Please log in to the DigiGriD portal using your email ID "
                       "as username.")
            # Confirmation to the complainant
            send_email(clean(email), "Your complaint " + case_id + " is registered", # Call the clean function to ensure a cleaned complainant's email ID before sending the confirmation email
                       "Your complaint has been registered with Case ID " + case_id
                       + " on " + show(stamp(filed)) + ".")
                        # Summon the complainant to the relevant cell/committee if the respondent is unknown
            if knows == "No":
                meet_by = stamp(filed + timedelta(days=MEET_DAYS))
                send_email(clean(email), "Case " + case_id + ": please meet the "
                           + authority_name(case_type),
                           "You did not identify the respondent in case " + case_id + ".\n"
                           "Please meet the " + authority_name(case_type) + " in person "
                           "by " + show(meet_by) + " so that they can help identify the "
                           "respondent from your description.\n"
                           "Bring any further information or evidence you have.")
            st.session_state.last_case_id = case_id # Call the session_state object from streamlit to store the last registered case ID for display on the page
            st.session_state.form_version += 1 # Increment the form version in the session state to reset the form fields for a new complaint registration
            st.rerun() # Call the rerun function from streamlit to refresh the page and display the success message with the registered case ID after successful complaint registration

# Define a function to display the complainant's cases in the DigiGriD application
def complainant_cases_page(user):
    st.header("My complaints")
    cases = load_cases() # Call the load_cases function from Helper_module_file_handling to load the list of cases from the cases file
    # mine = [c for c in cases if get(c, "email") == user[0]]
    mine = [] # start with an empty list
    for c in cases:  # go through every case
        if get(c, "email") == user[0]: # keep it only if the complainant's email matches the logged-in user's email
            mine.append(c)  # add that case to the new list

    if len(mine) == 0:
        st.write("You have not registered any complaints yet.")
        return
    
    for case in mine:
        cid = get(case, "case_id") # Retrieve the case ID
        with st.expander(cid + " | " + get(case, "case_type") + " | " # Call the expander function from streamlit to create an expandable section for each case, displaying the case ID, type, and status
                         + get(case, "status")):
            show_case_readonly(case, show_complainant=False) # Leave out the complainant’s own name and contact details, since the logged-in person is the complainant and already knows them
            appeal_question(cases, case, "complainant")
            show_decision(case)

# ============================ User 2: The Respondent ============================

# Define a function to display notices for the respondent in the DigiGriD application
def respondent_page(user):
    st.header("Notices for me")
    cases = load_cases()
    mine = [c for c in cases if get(c, "r_email") == user[0]
            and get(c, "summoned_at") != ""]
    
    if len(mine) == 0:
        st.write("There are no cases against you.")
        return
    
    for case in mine:
        cid = get(case, "case_id")
        with st.expander(cid + " | " + get(case, "case_type") + " | "
                         + get(case, "status")):
            st.warning("A complaint (complaint ID: " + cid + ") has been filed against " # Call the warning function from streamlit to display a message to the respondent about the complaint filed against
                       "you. Please meet the relevant cell/committee WITHIN 5 DAYS. "
                       "Please be aware that you have the right to appeal in your "
                       "defence.")
            st.write("Filed on " + show(get(case, "filed_at")) + " | "
                     "Please meet the " + authority_name(get(case, "case_type"))
                     + " by " + show(get(case, "meet_by"))) # meet_by is the deadline for the respondent to meet the cell/committee
            statement = read_text("statement", cid) # Call the read_text function from Helper_module_file_handling to read the respondent's statement for the case from the corresponding text file
            if statement == "":
                text, ok = text_box_with_limit("Your statement (optional)",
                                               WORDS_SHORT, "stmt_" + cid)
                if st.button("Submit my statement", key="stmtbtn_" + cid):
                    if text.strip() == "" or not ok:
                        st.error("Enter a statement within the word limit.")
                    else:
                        write_text("statement", cid, text.strip())
                        put(case, "statement_at", stamp(now()))
                        save_cases(cases)
                        st.rerun()
            else:
                st.write("Your statement (submitted):")
                st.info(statement) # Call the info function from streamlit to display the respondent's submitted statement in an information box
            appeal_question(cases, case, "respondent")
            show_decision(case)

# ============================ User 3: The Grievance Cell / Disciplinary Committee ============================

# Define a function to display cases for the authority (Grievance Cell or Disciplinary Committee) in the DigiGriD application
def authority_page(user):
    role = user[1] # Retrieve the role of the logged-in user from the user tuple
    if role == "Grievance Cell":
        ctype = "Discrimination"
    else:
        ctype = "Academic Misconduct"
    st.header(role + ": cases")
    st.caption("You can read cases but not edit them. The buttons below only "
               "record your actions in the workflow.")
    cases = load_cases()
    mine = [c for c in cases if get(c, "case_type") == ctype]
    if len(mine) == 0:
        st.write("No cases yet.")
        return
    ids = [get(c, "case_id") for c in mine]
    cid = st.selectbox("Select a case", ids, key="auth_case") # Call the selectbox function from streamlit to create a dropdown menu for selecting a case ID from the list of cases assigned to the authority
    case = find_case(cases, cid)
    status = get(case, "status")

    show_case_readonly(case)
    show_deadlines(case)
    statement = read_text("statement", cid)

    if statement != "": # Read the respondent's statement
        st.write("**Respondent's statement:**")
        st.info(statement)
    st.markdown("---") # Call the markdown function from streamlit to display a horizontal line separator in the case details section

    if status == S_REG: # If the case status is "ALLEGATION REGISTERED"
        if st.button("Mark case review as complete", key="rev_" + cid):
            put(case, "review_done_at", stamp(now())) # stamp the current time as the review completion timestamp
            put(case, "status", S_REVIEWED)
            save_cases(cases)
            st.rerun()

    elif status == S_REVIEWED: # If the case status is "REVIEWED BY CELL/COMMITTEE"
        st.subheader("Summon the respondent")
        r_email = st.text_input("Respondent's email ID", value=get(case, "r_email"),
                                key="sum_email_" + cid)
        r_name = st.text_input("Respondent's name", value=get(case, "r_name"),
                               key="sum_name_" + cid)
        if st.button("Send summons email", key="sum_" + cid):
            if not valid_email(r_email.strip()):
                st.error("Enter a valid email ID for the respondent.")
            else:
                email = clean(r_email)
                password = create_respondent_account(email, clean(r_name)) # Create a respondent account and generate a password
                summoned = now()
                meet_by = stamp(summoned + timedelta(days=MEET_DAYS)) # Calculate the deadline for the respondent to meet the cell/committee
                put(case, "r_email", email)
                put(case, "r_name", clean(r_name))
                put(case, "summoned_at", stamp(summoned))
                put(case, "meet_by", meet_by)
                put(case, "report_due", later(meet_by, days=REPORT_DAYS))
                put(case, "status", S_SUMMONED)
                save_cases(cases)
                send_email(email, "Complaint " + cid + " filed against you",
                           "A complaint (complaint ID: " + cid + ") has been filed "
                           "against you. Please meet the relevant cell/committee "
                           "WITHIN 5 DAYS (by " + show(meet_by) + "). Please be aware "
                           "that you have the right to appeal in your defence.\n\n"
                           "You can log in to the DigiGriD portal. Username: your email "
                           "ID (" + email + "). Password: " + password) # Send an email to the respondent with the summons and password
                st.rerun()

    elif status == S_SUMMONED: # If the case status is "RESPONDENT SUMMONED"
        meet_by = parse(get(case, "meet_by")) # Call the parse function from Helper_module_basics to convert the meet_by string to a datetime object for comparison with the current time
        if now() < meet_by: # If the current time is before the meet_by deadline, display a message to the authority about the respondent's meeting deadline and the report submission timeline
            st.info("The respondent has until " + show(get(case, "meet_by"))
                    + " to meet you. The report to the Director can be written "
                    "after this date.")
        else:
            st.subheader("Report to the Director")
            text, ok = text_box_with_limit("Write your report", WORDS_REPORT, # Call the text_box_with_limit function from Helper_module_message_display to create a text area for writing the report with a word limit
                                           "report_" + cid)
            if st.button("Send report to Director", key="repbtn_" + cid): # key="repbtn_" + cid is used to uniquely identify the button for each case, allowing the authority to send the report for the selected case
                if text.strip() == "" or not ok: # If the report text is empty or exceeds the word limit, display an error message to the authority
                    st.error("Enter a report within the word limit.")
                else:
                    sent = now()
                    write_text("report", cid, text.strip())
                    put(case, "report_sent_at", stamp(sent)) # Stamp the current time as the report sent timestamp
                    put(case, "director_due", stamp(sent + timedelta(days=DIRECTOR_READ_DAYS))) # Calculate the deadline for the director to read the report and update the "director_due" field of the case
                    put(case, "status", S_REPORT)
                    save_cases(cases)
                    send_email(DIRECTOR_EMAIL, "Report for case " + cid,
                               "The " + role + " has sent its report for case " + cid
                               + ". Please log in to the portal and read it within "
                               + str(DIRECTOR_READ_DAYS) + " days (by "
                               + show(get(case, "director_due")) + ").")
                    st.rerun()
    else:
        report = read_text("report", cid)
        if report != "":
            st.write("**Report sent to the Director:**")
            st.info(report)
        show_decision(case)

# ============================ User 4: The Director or the Head of HEI ============================

# Define a function to display cases for the Director in the DigiGriD application
def director_page(user):
    st.header("Director: cases")
    st.caption("You can read reports but not edit them.")
    cases = load_cases() # Call the load_cases function from Helper_module_file_handling to load the list of cases from the cases file
    mine = [c for c in cases if get(c, "report_sent_at") != ""] # Filter the cases to include only those that have a report sent to the Director
    if len(mine) == 0:
        st.write("No reports have been sent to you yet.")
        return
    ids = [get(c, "case_id") for c in mine] # Create a list of case IDs for the cases that have a report sent to the Director
    cid = st.selectbox("Select a case", ids, key="dir_case") # Call the selectbox function from streamlit to create a dropdown menu for selecting a case ID from the list of cases assigned to the Director
    case = find_case(cases, cid) # Call the find_case function from Helper_module_file_handling to retrieve the case details for the selected case ID

    # Opening the report moves the case to 'under review by head'
    if get(case, "status") == S_REPORT: # If the case status is "REPORT SENT TO DIRECTOR"
        put(case, "status", S_HEAD_READING) # Update the case status to "CASE UNDER REVIEW BY HEAD of HEI"
        put(case, "director_opened_at", stamp(now())) # Stamp the current time as the director opened timestamp
        save_cases(cases)

    status = get(case, "status")
    show_case_readonly(case) # Call the show_case_readonly function from Helper_module_message_display to display the case details in a read-only format for the Director
    show_deadlines(case) # Call the show_deadlines function from Helper_module_message_display to display the relevant deadlines for the case, such as appeal deadlines and decision deadlines
    st.write("**Report from the " + authority_name(get(case, "case_type")) + ":**")
    st.info(read_text("report", cid)) # Call the read_text function to read the report text for the selected case from the corresponding text file
    statement = read_text("statement", cid)

    if statement != "": # Read the respondent's statement for the selected case from the corresponding text file
        st.write("**Respondent's statement:**")
        st.info(statement)
    st.markdown("---")

    if status == S_HEAD_READING: # If the case status is "CASE UNDER REVIEW BY HEAD of HEI"
        if st.button("I have read the report - mark case as reviewed", key="dirrev_" + cid): # key="dirrev_" + cid is used to uniquely identify the button for each case, allowing the Director to mark the case as reviewed for the selected case
            reviewed = now()
            put(case, "director_reviewed_at", stamp(reviewed)) # Timestamp the current time as the director reviewed timestamp
            put(case, "appeal_deadline", stamp(reviewed + timedelta(days=APPEAL_WINDOW_DAYS)))
            put(case, "status", S_HEAD_DONE) # Update the case status to "CASE REVIEWED BY HEAD of HEI"
            save_cases(cases)
            email_cell_and_parties(
                case, "Case " + cid + ": reviewed by the Head of the Institute",
                "The Head of the Institute has reviewed case " + cid + ".\n"
                "The complainant and the respondent may log in to the portal and "
                "answer 'Do you want to appeal?' within " + str(APPEAL_WINDOW_DAYS)
                + " days (by " + show(get(case, "appeal_deadline")) + ").") # Send an email notification to the complainant and respondent about the appeal window and the deadline for submitting their appeals
            st.rerun()

    elif status == S_HEAD_DONE: # If the case status is "CASE REVIEWED BY HEAD of HEI"
        st.info("Waiting for the appeal answers (until "
                + show(get(case, "appeal_deadline")) + ").") # Display a message to the Director indicating that the system is waiting for the appeals from the complainant and respondent

    elif status.startswith(S_APPEAL): # If the case status starts with "APPEAL REQUESTED BY"
        # startswith() function to check whether string begins with a particular word or characters
        st.write("Appeal answers - complainant: " + (get(case, "complainant_appeal") or "-")
                 + " | respondent: " + (get(case, "respondent_appeal") or "-"))
        if st.button("Send the case to the ombudsperson (" + OMBUDS_EMAIL + ")",
                     key="fwd_" + cid): # key="fwd_" + cid is used to uniquely identify the button for each case, allowing the Director to forward the case to the ombudsperson for the selected case
            put(case, "referred_at", stamp(now()))
            put(case, "status", S_REFERRED)
            save_cases(cases)
            send_email(OMBUDS_EMAIL, "Appeal in case " + cid,
                       "An appeal has been requested in case " + cid + ". Please log "
                       "in to the portal (username: your email ID) to read the case "
                       "and the report, and enter your decision. The Director and "
                       "you must reach a decision by "
                       + show(get(case, "appeal_due")) + ".") # Send an email notification to the ombudsperson about the appeal and the deadline for reaching a decision
            st.rerun()

    elif status == S_NO_APPEAL: # If the case status is "NO APPEAL REQUESTED"
        st.subheader("Enter your decision")
        text, ok = text_box_with_limit("Decision", WORDS_DECISION, "dec_" + cid) # Call the text_box_with_limit function to create a text area for entering the decision within a word limit
        if st.button("Record decision",
                     key="decbtn_" + cid): # key="decbtn_" + cid is used to uniquely identify the button for each case, allowing the Director to record the decision for the selected case
            if text.strip() == "" or not ok: # If the decision text is empty or exceeds the word limit, display an error message to the Director
                st.error("Enter a decision within the word limit.")
            else:
                write_text("decision", cid, text.strip()) # Call the write_text function to save the decision for the selected case to the corresponding text file
                put(case, "decision_at", stamp(now()))
                put(case, "decision_by", "Director")
                put(case, "status", S_DECIDED)
                save_cases(cases)
                email_cell_and_parties(
                    case, "Decision in case " + cid,
                    "A decision has been recorded in case " + cid + ". Please log in "
                    "to the portal to read it. The case will be resolved in "
                    + str(RESOLVE_HOURS) + " hours.") # Send an email notification to the complainant, respondent (if known), and the relevant cell/committee about the recorded decision and the resolution timeline
                st.rerun()

    elif status == S_REFERRED: # If the case status is "REFERRED TO OMBUDSPERSON"
        st.info("Waiting for the ombudsperson's decision.")

    elif status == S_PROPOSED: # If the case status is "DECISION PROPOSED BY OMBUDSPERSON"
        st.write("**Decision proposed by the ombudsperson:**")
        st.success(read_text("decision", cid)) # Call the read_text function to read the proposed decision for the selected case from the corresponding text file and display it in a success message box
        if st.button("As recommended by the Ombudsperson",
                     key="conf_" + cid): # key="conf_" + cid is used to uniquely identify the button for each case, allowing the Director to confirm the proposed decision for the selected case
            put(case, "decision_at", stamp(now()))
            put(case, "decision_by", "Director and Ombudsperson")
            put(case, "status", S_DECIDED)
            save_cases(cases)
            email_cell_and_parties(
                case, "Decision in case " + cid,
                "A decision has been reached in case " + cid + ". Please "
                "log in to the portal to read it. The case will be resolved in "
                + str(RESOLVE_HOURS) + " hours.")
            st.rerun()
    else:
        show_decision(case)

# ============================ User 5: The Ombudsperson ============================

# Define a function to display cases for the Ombudsperson in the DigiGriD application
def ombudsperson_page(user):
    st.header("Ombudsperson: appeals")
    cases = load_cases()
    mine = [c for c in cases if get(c, "referred_at") != ""] # Filter the cases to include only those that have been referred to the Ombudsperson for appeal review
    if len(mine) == 0:
        st.write("No appeals have been referred to you yet.")
        return
    ids = [get(c, "case_id") for c in mine] # Create a list of case IDs for the cases that have been referred to the Ombudsperson for appeal review
    cid = st.selectbox("Select a case", ids, key="omb_case") # Call the selectbox function to create a dropdown menu for selecting a case ID from the list of cases assigned to the Ombudsperson
    case = find_case(cases, cid)
    show_case_readonly(case)
    show_deadlines(case)
    st.write("**Report from the " + authority_name(get(case, "case_type")) + ":**")
    st.info(read_text("report", cid))
    statement = read_text("statement", cid)

    if statement != "": # Read the respondent's statement for the selected case from the corresponding text file
        st.write("**Respondent's statement:**")
        st.info(statement)
    st.markdown("---")
    status = get(case, "status")

    if status == S_REFERRED: # If the case status is "REFERRED TO OMBUDSPERSON"
        st.subheader("Enter your decision")
        st.caption("The Director must confirm it for it to be recorded.")
        text, ok = text_box_with_limit("Decision", WORDS_DECISION, # Call the text_box_with_limit function to create a text area for entering the decision within a word limit
                                        "omb_dec_" + cid) # key="omb_dec_" + cid is used to uniquely identify the text area for entering the decision for the selected case
        if st.button("Submit decision to the Director",
                     key="ombbtn_" + cid): # key="ombbtn_" + cid is used to uniquely identify the button for each case, allowing the Ombudsperson to submit the decision for the selected case to the Director
            if text.strip() == "" or not ok: # If the decision text is empty or exceeds the word limit, display an error message to the Ombudsperson
                st.error("Enter a decision within the word limit.")
            else:
                write_text("decision", cid, text.strip())
                put(case, "status", S_PROPOSED) # Update the case status to "DECISION PROPOSED BY OMBUDSPERSON"
                save_cases(cases)
                send_email(DIRECTOR_EMAIL, "Ombudsperson's decision in case " + cid,
                           "The ombudsperson has entered a decision in case " + cid
                           + ". Please log in to confirm it.") # Send an email notification to the Director about the proposed decision by the Ombudsperson for the selected case
                st.rerun()
    else:
        show_decision(case)

# ============================ For demonstration: Email outbox ============================

# Define a function to display the email outbox in the DigiGriD application
def outbox_page():
    st.header("Demo: email outbox")
    st.caption("Successfully delivered emails are recorded here, newest first.")
    mails = load_emails() # Call the load_emails function from Helper_module_email to load the list of emails from the email outbox file
    if len(mails) == 0:
        st.write("No emails yet.")
        return
    # For loop to iterate through the list of emails in reverse order (newest first) and display each email in an expandable section using the expander function from streamlit
    for mail in reversed(mails):
        with st.expander(show(mail[0]) + "  |  To: " + mail[1] + "  |  " + mail[2]): # with() statement to create an expandable section for each email
            # Displaying the (0) timestamp, (1) recipient, and (2) subject of the email
            st.text(mail[3].replace(NEWLINE_CODE, "\n")) # Displays the (3) email body, replacing the newline code with actual newline characters for proper formatting

# ============================ The Main Function ============================

# The main function of the DigiGriD application
# It initializes session state variables, handles user login, and routes users to the appropriate pages based on their roles

if "user" not in st.session_state: # Check if the "user" key is present in the session state
    st.session_state.user = None # None means nobody is logged in yet
if "form_version" not in st.session_state: # Check if the "form_version" key is present in the session state
    st.session_state.form_version = 0 # 0 means the complaint registration form is at its initial version
if "last_case_id" not in st.session_state: # Check if the "last_case_id" key is present in the session state
    st.session_state.last_case_id = None # None means no case has been registered yet
if "shift_days" not in st.session_state: # Check if the "shift_days" key is present in the session state
    st.session_state.shift_days = 0 # 0 means no shift in days for deadlines
    # This variable stores the number of days by which a deadline should be shifted
if "shift_hours" not in st.session_state: # Check if the "shift_hours" key is present in the session state; if not, initialize it to 0
    st.session_state.shift_hours = 0 # This variable stores the hours by which a deadline should be shifted

if st.session_state.user is None: # Nobody is logged in yet, so display the login page
    login_page()
else:
    apply_time_rules() # If someone is logged in, call the apply_time_rules function to apply any time-based rules such as shifting deadlines based on the current date and time
    user = st.session_state.user # Retrieve the logged-in user's information from the session state
    role = user[1] # Retrieve the role of the logged-in user from the user tuple
    st.sidebar.write("Logged in as **" + user[2] + "**") # Display the logged-in user's name in the sidebar (whether complainant, respondent, or authority)
    st.sidebar.write("Role: " + role) # Display the logged-in user's role in the sidebar (whether complainant, respondent, or authority)

    if role == "Complainant":
        pages = ("Register a complaint", "My complaints")
    elif role == "Respondent":
        pages = ("Notices for me",)
    else:
        pages = ("Cases",)
    page = st.sidebar.radio("Menu", pages + ("Demo: email outbox",))
    if st.sidebar.button("Log out"):
        st.session_state.user = None
        st.rerun()

# Calling all the above defined functions
    if page == "Register a complaint":
        register_page(user) # Call the register_page function to display the complaint registration form for the complainant
    elif page == "My complaints":
        complainant_cases_page(user) # Call the complainant_cases_page function to display the list of complaints filed by the complainant
    elif page == "Notices for me":
        respondent_page(user) # Call the respondent_page function to display the notices for the respondent
    elif page == "Demo: email outbox":
        outbox_page() # Call the outbox_page function to display the email outbox for demonstration purposes
    elif role in ("Grievance Cell", "Disciplinary Committee"):
        authority_page(user) # Call the authority_page function to display the cases assigned to the authority (Grievance Cell or Disciplinary Committee)
    elif role == "Director":
        director_page(user) # Call the director_page function to display the cases assigned to the Director
    elif role == "Ombudsperson":
        ombudsperson_page(user) # Call the ombudsperson_page function to display the appeals assigned to the Ombudsperson
