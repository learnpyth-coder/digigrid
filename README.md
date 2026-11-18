# DigiGriD

DigiGriD: A Transparent Digital System for SC/ST Student Grievance and Disciplinary Management in Higher Education Institutions (HEIs)

HEIs lack a transparent, complaint-based tracking system that can record allegations, supporting materials, reviews, and decisions.
To address this problem, we propose DigiGriD.

DigiGriD is a Streamlit web portal for managing student grievances and academic
disciplinary cases. It supports complaint registration, evidence uploads,
case review, respondent notices, reports, appeals, decisions, and email
notifications.

## Features

- Complainant login and complaint registration
- Discrimination and Academic Misconduct workflows
- Evidence upload and case records
- Respondent accounts and notices
- Grievance Cell, Disciplinary Committee, Director, and Ombudsperson workflows
- SMTP email notifications
- Demo email outbox for successfully delivered messages

## Requirements

- Python 3.9 or newer
- SMTP credentials for email delivery

## Run locally

Open PowerShell in this project folder:

```powershell
cd "C:\path\to\digigrid"
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python -m streamlit run DigiGriD_MAIN_CODE.py
```

Open <http://localhost:8501> in a browser.



## Demo accounts

The login page displays the current demo accounts and passwords. These accounts
are defined in `digigrid_streamlit_config.py`. 

## Data storage

By default, case files, user records, uploaded evidence, and the email outbox
are stored in the project directory.
