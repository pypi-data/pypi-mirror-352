"""
Google Calendar Toolkit
========================

This toolkit provides asynchronous methods for interacting with Google Calendar using a service account.
It supports creating, listing, updating, and deleting both calendars and events. It is designed to be
used as part of a memory/agent framework (like LangGraph or LangChain).

Setup Instructions for Google Calendar API Integration:
-------------------------------------------------------
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or use an existing one.
3. Enable the Google Calendar API for the project.
4. Go to "APIs & Services > Credentials" and create a service account.
5. Download the service account key (JSON file).
6. Share the target calendar with the service account email (ending in `@<project>.iam.gserviceaccount.com`).
7. Use the service account JSON and calendar ID to authenticate and perform operations.

Dependencies:
-------------
- google-api-python-client
- google-auth
- google-auth-httplib2
- google-auth-oauthlib

Install via pip:
```
pip install --upgrade google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```
"""

import datetime
from typing import Optional, List, Union
from google.oauth2 import service_account
from googleapiclient.discovery import build
from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.toolkits.google_calendar.schema_mappings import (
    schema_mappings,
)


class GoogleCalendarToolkit:

    def __init__(
        self,
        service_account_info: Union[str, dict],
        scopes: List[str] = ["https://www.googleapis.com/auth/calendar"],
    ):
        if isinstance(service_account_info, str):
            self.creds = service_account.Credentials.from_service_account_file(
                service_account_info, scopes=scopes
            )
        elif isinstance(service_account_info, dict):
            self.creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=scopes
            )
        else:
            raise ValueError(
                "`service_account_info` must be a file path (str) or dict."
            )
        self.service = build("calendar", "v3", credentials=self.creds)
        self.schema_mappings = schema_mappings

    # ------------ CALENDAR OPERATIONS ------------

    async def acreate_calendar(self, summary: str, time_zone: str = "UTC"):
        calendar = {"summary": summary, "timeZone": time_zone}
        created = self.service.calendars().insert(body=calendar).execute()
        return created

    async def adelete_calendar(self, calendar_id: str):
        self.service.calendars().delete(calendarId=calendar_id).execute()
        return {"status": "deleted", "calendar_id": calendar_id}

    async def aupdate_calendar(
        self,
        calendar_id: str,
        summary: Optional[str] = None,
        time_zone: Optional[str] = None,
    ):
        calendar = self.service.calendars().get(calendarId=calendar_id).execute()
        if summary:
            calendar["summary"] = summary
        if time_zone:
            calendar["timeZone"] = time_zone
        updated = (
            self.service.calendars()
            .update(calendarId=calendar_id, body=calendar)
            .execute()
        )
        return updated

    async def alist_calendars(self):
        calendars = self.service.calendarList().list().execute()
        return calendars.get("items", [])

    # ------------ EVENT OPERATIONS ------------

    async def acreate_event(self, calendar_id: str, event_data: dict):
        event = (
            self.service.events()
            .insert(calendarId=calendar_id, body=event_data)
            .execute()
        )
        return event

    async def adelete_event(self, calendar_id: str, event_id: str):
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return {"status": "deleted", "event_id": event_id}

    async def aupdate_event(self, calendar_id: str, event_id: str, update_fields: dict):
        event = (
            self.service.events()
            .get(calendarId=calendar_id, eventId=event_id)
            .execute()
        )
        event.update(update_fields)
        updated = (
            self.service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )
        return updated

    async def alist_events(
        self,
        calendar_id: str,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
    ):
        if not time_min:
            time_min = datetime.datetime.utcnow().isoformat() + "Z"
        if not time_max:
            time_max = (
                datetime.datetime.utcnow() + datetime.timedelta(days=30)
            ).isoformat() + "Z"
        events = (
            self.service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events.get("items", [])

    async def asearch_event_by_description(self, calendar_id: str, search_text: str):
        all_events = await self.alist_events(calendar_id)
        matched = [
            event
            for event in all_events
            if search_text.lower() in (event.get("description", "") or "").lower()
        ]
        return matched



    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list of ToolBuilder objects, each representing a method in the toolkit.
        """
        tools = []
        for method_name, method_info in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=method_name)
            tool_builder.set_function(getattr(self, method_name))
            tool_builder.set_coroutine(getattr(self, method_name))
            tool_builder.set_description(description=method_info["description"])
            tool_builder.set_schema(schema=method_info["input_schema"])
            tool = tool_builder.build()
            tools.append(tool)
        return tools

    # async def close(self):
    #     """Closes the aiohttp session."""
    #     await self.session.close()
