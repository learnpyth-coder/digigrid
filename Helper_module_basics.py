'''
This module contains basic helper functions for the DigiGriD application
These functions are used to access case data, format timestamps, and perform other utility tasks
'''
# Import relevant modules
from datetime import datetime, timedelta
import streamlit as st

from digigrid_streamlit_config import FIELDS, SEP, SHOW_FMT, TIME_FMT, TIME_FMT

# Define a function to get the value of a field from a case
def get(case, name):
    return case[FIELDS.index(name)]

# Define a function to set the value of a field in a case
def put(case, name, value):
    case[FIELDS.index(name)] = value

# Define a function to clean text by replacing separators and newlines, and stripping whitespace
def clean(text):
    return text.replace(SEP, "/").replace("\n", " ").strip()

# Define a function to count the number of words in a given text
def word_count(text):
    return len(text.split())

# Define a function to get the current date and time
def now():
    """Current time."""
    shift = timedelta(days=st.session_state.shift_days,
                      hours=st.session_state.shift_hours)
    return datetime.now() + shift

# Define a function to format a timestamp as a string
def stamp(moment):
    return moment.strftime(TIME_FMT)

# Define a function to parse a timestamp string into a datetime object
def parse(text):
    if text == "":
        return None
    return datetime.strptime(text, TIME_FMT)

# Define a function to format a timestamp for display
def show(text):
    moment = parse(text)
    if moment is None:
        return "-"
    return moment.strftime(SHOW_FMT)

# Define a function to calculate a future timestamp by adding a specified duration to a given timestamp
def later(moment_text, **kwargs):
    """Time stamp text + days/hours, as text."""
    return stamp(parse(moment_text) + timedelta(**kwargs))