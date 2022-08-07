from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, make sure to delete the file token.json, because
# it will become invalid
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "credentials.json"


def log_in():
    credentials = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8001)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    return credentials


def read_guests():
    guests = []
    with open("guests.csv", "r") as guests_file:
        for line in guests_file:
            guests.append(line.strip())
    return guests


def main():
    guests = read_guests()
    with open("holiday-data.csv", "r") as events:
        for line in events:
            fields = line.strip().split(";")
            add_event(fields[0], fields[1], guests)


def add_event(title, date, guest_list):
    try:
        service = build("calendar", "v3", credentials=log_in())
        event = {
            "summary": title,
            "start": {"date": date, "timeZone": "America/Los_Angeles"},
            "end": {"date": date, "timeZone": "America/Los_Angeles"},
            "attendees": list(map(lambda guest: {"email": guest}, guest_list)),
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 1440}],
            },
        }

        event = service.events().insert(calendarId="primary", body=event).execute()
        print("Event created: %s" % (event.get("htmlLink")))
    except HttpError as error:
        print("An error occurred: %s" % error)


if __name__ == "__main__":
    main()
