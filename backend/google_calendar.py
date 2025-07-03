from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
import datetime
import dotenv
import os
import re

dotenv.load_dotenv()

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv("CALENDAR_ID")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
calendar_service = build('calendar', 'v3', credentials=credentials)

def ensure_gmail_has_access():
    acl = calendar_service.acl().list(calendarId=CALENDAR_ID).execute()
    has_access = any(
        rule["scope"].get("value") == "tharikashreer88@gmail.com"
        for rule in acl.get("items", [])
    )

    if not has_access:
        calendar_service.acl().insert(calendarId=CALENDAR_ID, body={
            "role": "writer",  # Gives you permission to manage events
            "scope": {
                "type": "user",
                "value": "tharikashreer88@gmail.com"
            }
        }).execute()
        print("✅ Access granted to tharikashreer88@gmail.com")
    else:
        print("ℹ️ Gmail already has access")

# Call this once to set permissions
ensure_gmail_has_access()

print("Calendar ACL updated successfully.")

# Basic email validation
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def create_event(date, time, topic):
    try:
        # Parse and sanitize natural language input
        start_dt = parser.parse(f"{date} {time}", fuzzy=True)
        end_dt = start_dt + datetime.timedelta(hours=1)
        event = {
            "summary": topic,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"}
        }

        result = calendar_service.events().insert(
            calendarId=CALENDAR_ID, body=event
        ).execute()

        return {
            "status": "success",
            "eventLink": result.get("htmlLink"),
            "eventId": result.get("id"),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
