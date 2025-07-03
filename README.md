# Conversational Google Calendar Booking Bot

This is an AI-powered calendar booking assistant using FastAPI, LangGraph, Streamlit, and Gemini API.

## Features
- Conversational chat interface via Streamlit
- Google Calendar integration using a service account
- Check free/busy slots and create bookings

## Setup

1. Create a service account in Google Cloud Console.
2. Share your Google Calendar with the service account.
3. Put the JSON file in `credentials/service_account.json`.
4. Add your `.env` file with GEMINI key and Calendar ID.

## Run Locally

```bash
cd backend
uvicorn main:app --reload
```

```bash
cd frontend
streamlit run app.py
```

## Example `.env`

```env
GEMINI_API_KEY=your_gemini_key_here
CALENDAR_ID=your_calendar_id@gmail.com
```
