import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendarIntegration:
    """Handles Google Calendar API integration"""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/google/callback")

        self.scopes = [
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/calendar.readonly'
        ]

    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )

        return authorization_url

    def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }

    def _get_credentials(self, token_data: Dict[str, Any]) -> Credentials:
        """Create credentials from stored token data"""
        return Credentials(
            token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def create_event(
        self,
        token_data: Dict[str, Any],
        title: str,
        description: str = "",
        start_date: str = None,
        end_date: str = None,
        all_day: bool = True,
        reminder_minutes: int = 1440  # 24 hours default
    ) -> Dict[str, Any]:
        """Create a calendar event"""
        credentials = self._get_credentials(token_data)
        service = build('calendar', 'v3', credentials=credentials)

        # Default to today if no date provided
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')

        if not end_date:
            end_date = start_date

        if all_day:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'date': start_date,
                },
                'end': {
                    'date': end_date,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': reminder_minutes},
                    ],
                },
            }
        else:
            # For timed events, assume full day if times not provided
            start_datetime = f"{start_date}T09:00:00"
            end_datetime = f"{end_date}T10:00:00"

            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': reminder_minutes},
                    ],
                },
            }

        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
            return {
                "id": event.get('id'),
                "html_link": event.get('htmlLink'),
                "summary": event.get('summary'),
                "start": event.get('start'),
                "end": event.get('end')
            }
        except HttpError as error:
            raise Exception(f"Failed to create event: {error}")

    def create_expiration_reminder(
        self,
        token_data: Dict[str, Any],
        item_name: str,
        expiration_date: str,
        days_before: int = 1
    ) -> Dict[str, Any]:
        """Create a reminder for item expiration"""
        # Parse the expiration date
        exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
        reminder_date = exp_date - timedelta(days=days_before)

        title = f"Reminder: {item_name} expires soon!"
        description = f"{item_name} will expire on {expiration_date}. Consider using it before then!"

        return self.create_event(
            token_data=token_data,
            title=title,
            description=description,
            start_date=reminder_date.strftime('%Y-%m-%d'),
            end_date=reminder_date.strftime('%Y-%m-%d'),
            all_day=True,
            reminder_minutes=540  # 9 AM reminder
        )

    def list_upcoming_events(
        self,
        token_data: Dict[str, Any],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """List upcoming calendar events"""
        credentials = self._get_credentials(token_data)
        service = build('calendar', 'v3', credentials=credentials)

        now = datetime.utcnow().isoformat() + 'Z'

        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return [
                {
                    "id": event.get('id'),
                    "summary": event.get('summary'),
                    "start": event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                    "end": event.get('end', {}).get('dateTime', event.get('end', {}).get('date')),
                    "html_link": event.get('htmlLink')
                }
                for event in events
            ]
        except HttpError as error:
            raise Exception(f"Failed to list events: {error}")


# Global instance
google_calendar = GoogleCalendarIntegration()
