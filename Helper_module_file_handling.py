'''
This module contains functions for handling file operations in the DigiGriD application
These functions are used to load and save case data, find specific cases, read and write text files, and manage user accounts.
'''
# Import relevant modules
from Helper_module_basics import get, now
from digigrid_streamlit_config import CASES_FILE, FIELDS, SEP, USERS, USERS_FILE

# Define a function to load cases from the cases file
def load_cases():
    cases = []
    try:
        f = open(CASES_FILE, "r")
        for line in f:
            parts = line.rstrip("\n").split(SEP)
            if len(parts) == len(FIELDS):
                cases.append(parts)
        f.close()
    except FileNotFoundError:
        pass
    return cases

# Define a function to save the list of cases to the cases file
def save_cases(cases):
    f = open(CASES_FILE, "w")
    for case in cases:
        f.write(SEP.join(case) + "\n")
    f.close()

# Define a function to find a specific case by its case ID from the list of cases
def find_case(cases, case_id):
    for case in cases:
        if get(case, "case_id") == case_id:
            return case
    return None

# Define a function to write text to a file with a specific kind and case ID
def write_text(kind, case_id, text):
    f = open(kind + "_" + case_id + ".txt", "w")
    f.write(text)
    f.close()

# Define a function to read text from a file with a specific kind and case ID
def read_text(kind, case_id):
    try:
        f = open(kind + "_" + case_id + ".txt", "r")
        text = f.read()
        f.close()
        return text
    except FileNotFoundError:
        return ""

# Define a function to load extra users from the users file
def load_extra_users():
    users = []
    try:
        f = open(USERS_FILE, "r")
        for line in f:
            parts = line.rstrip("\n").split(SEP)
            if len(parts) == 4:
                users.append(parts)
        f.close()
    except FileNotFoundError:
        pass
    return users

# Define a function to check the login credentials of a user
def check_login(username, password):
    """Returns (username, role, display name) or None."""
    for u in USERS:
        if u[0] == username and u[1] == password:
            return (u[0], u[2], u[3])
    for u in load_extra_users():
        if u[0] == username and u[1] == password:
            return (u[0], u[2], u[3])
    return None

# Define a function to create a respondent account with a unique password
def create_respondent_account(email, name):
    """Returns the password. If the respondent already has an account,
    the old password is returned (no duplicate)."""
    for u in load_extra_users():
        if u[0] == email:
            return u[1]
    password = "DG" + now().strftime("%H%M%S%f")[-6:]
    f = open(USERS_FILE, "a")
    f.write(SEP.join((email, password, "Respondent", name or "Respondent")) + "\n")
    f.close()
    return password

# Replace any unsafe character in a file name with "_" (so it cannot break paths or the cases file)
def safe_filename(name):
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    result = ""
    for ch in name:
        if ch in allowed:
            result += ch
        else:
            result += "_"
    return result

# Save the uploaded evidence file to project folder and return the name it was saved under
def save_evidence_file(case_id, uploaded, number):
    stored = "evidence_" + case_id + "_" + str(number) + "_" + safe_filename(uploaded.name)
    f = open(stored, "wb") # "wb" = write binary (PDFs, photos, video because they are not plain text, they're raw bytes, so they must be written in binary mode)
    f.write(uploaded.getbuffer()) # Write the uploaded contents into the file. uploaded.getbuffer() gives the raw bytes of what the user uploaded
    # f.write(...) puts them into the new file in the project folder
    f.close()
    return stored

# Read a saved file back as bytes (empty if it is missing)
# Use try-except
def read_file_bytes(stored):
    try:
        f = open(stored, "rb") # "rb" = read binary
        data = f.read()
        f.close()
        return data
    except FileNotFoundError:
        return b""