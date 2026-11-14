'''
This is a helper module for the case management system.
It contains functions for sending and loading emails.
And for determining the appropriate authority to contact based on the case type.
And also for validating email addresses and contact numbers.
'''

import smtplib
from email.message import EmailMessage

from Helper_module_basics import clean, get, now, stamp
from digigrid_streamlit_config import (
    DISCIPLINE_EMAIL,
    GRIEVANCE_EMAIL,
    MAIL_FILE,
    NEWLINE_CODE,
    SEP,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_TIMEOUT,
    SMTP_USE_SSL,
    SMTP_USERNAME,
)


class EmailDeliveryError(RuntimeError):
    """Raised when an email cannot be delivered through the configured SMTP server."""


# Deliver the message and retain a copy in the application outbox.
def send_email(to, subject, body):
    if not all((SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM)):
        raise EmailDeliveryError(
            "Email delivery is not configured. Set DIGIGRID_SMTP_HOST, "
            "DIGIGRID_SMTP_USERNAME, DIGIGRID_SMTP_PASSWORD, and "
            "DIGIGRID_SMTP_FROM on the server."
        )

    message = EmailMessage()
    message["From"] = SMTP_FROM
    message["To"] = to
    message["Subject"] = clean(subject)
    message.set_content(body)

    try:
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(
                SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT
            ) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError(
            "Email could not be sent through the configured SMTP server."
        ) from exc

    with open(MAIL_FILE, "a", encoding="utf-8") as file:
        line = SEP.join(
            (
                stamp(now()),
                to,
                clean(subject),
                body.replace("\n", NEWLINE_CODE).replace(SEP, "/"),
            )
        )
        file.write(line + "\n")

# Define a function to load emails from the mail file
def load_emails():
    mails = []
    try:
        f = open(MAIL_FILE, "r")
        for line in f:
            parts = line.rstrip("\n").split(SEP)
            if len(parts) == 4:
                mails.append(parts)
        f.close()
    except FileNotFoundError:
        pass
    return mails

# Define a function to determine the appropriate authority email based on the case type
def authority_email(case_type):
    if case_type == "Discrimination":
        return GRIEVANCE_EMAIL
    return DISCIPLINE_EMAIL

# Define a function to determine the appropriate authority name based on the case type
def authority_name(case_type):
    if case_type == "Discrimination":
        return "Grievance Cell"
    return "Disciplinary Committee"

# Define a function to send the same email to the complainant, respondent (if known), and the appropriate cell/committee
def email_cell_and_parties(case, subject, body):
    """Same message to complainant, respondent (if known) and cell/committee."""
    send_email(get(case, "email"), subject, body)
    if get(case, "r_email") != "":
        send_email(get(case, "r_email"), subject, body)
    send_email(authority_email(get(case, "case_type")), subject, body)

# Define a function to validate an entered email address
def valid_email(email):
    return "@" in email and "." in email.split("@")[-1] and " " not in email

# Define a function to validate an entered contact number
def valid_contact(number):
    digits = number.replace("+", "").replace(" ", "").replace("-", "")
    return digits.isdigit() and 10 <= len(digits) <= 13