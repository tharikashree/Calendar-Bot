from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
import datetime
import dotenv
import pytz
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


# Basic email validation
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_time_slot_available(start_dt, end_dt):
    body = {
        "timeMin": start_dt.isoformat(),
        "timeMax": end_dt.isoformat(),
        "timeZone": "Asia/Kolkata",
        "items": [{"id": CALENDAR_ID}]
    }

    try:
        response = calendar_service.freebusy().query(body=body).execute()
        busy_times = response["calendars"][CALENDAR_ID]["busy"]
        return len(busy_times) == 0  # True = free
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def create_event(date, time, topic):
    try:
        # Parse and sanitize natural language input
        start_dt = parser.parse(f"{date} {time}", fuzzy=True)
        end_dt = start_dt + datetime.timedelta(hours=1)

        tz = pytz.timezone("Asia/Kolkata")
        start_dt = tz.localize(start_dt)
        end_dt = tz.localize(end_dt)

        # Check slot availability
        availability = is_time_slot_available(start_dt, end_dt)
        if isinstance(availability, dict) and availability.get("status") == "error":
            return availability  # propagate error

        if not availability:
            return {
                "status": "error",
                "message": "The selected time slot is not available. Please choose another time."
            }
        
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
