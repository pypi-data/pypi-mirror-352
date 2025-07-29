"""
This module defines the schema mappings for Google Calendar functionality,
including event creation, updates, deletion, and listing.

Each schema ensures clear input validation and consistency for API calls
to the memory engine's Google Calendar toolset.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- SCHEMA MAPPINGS ---
class CreateCalendarInputSchema(BaseModel):
    summary: str = Field(..., description="The summary (name) for the new calendar.")
    time_zone: Optional[str] = Field(
        default="UTC", description="Time zone of the calendar."
    )


class DeleteCalendarInputSchema(BaseModel):
    calendar_id: str = Field(..., description="The ID of the calendar to delete.")


class UpdateCalendarInputSchema(BaseModel):
    calendar_id: str = Field(..., description="The ID of the calendar to update.")
    summary: Optional[str] = Field(
        default=None, description="The new summary for the calendar."
    )
    time_zone: Optional[str] = Field(default=None, description="The new time zone.")


class ListCalendarsInputSchema(BaseModel):
    pass  # No input required


class CreateEventInputSchema(BaseModel):
    calendar_id: str = Field(
        ..., description="The ID of the calendar where the event is created."
    )
    event_data: Dict[str, Any] = Field(
        ...,
        description="The event body, must include at least 'summary', 'start', and 'end' fields following Google Calendar event format.",
    )


class DeleteEventInputSchema(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID containing the event.")
    event_id: str = Field(..., description="The ID of the event to delete.")


class UpdateEventInputSchema(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID containing the event.")
    event_id: str = Field(..., description="The event ID to update.")
    update_fields: Dict[str, Any] = Field(
        ..., description="Fields to update in the event."
    )


class ListEventsInputSchema(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID for listing events.")
    time_min: Optional[str] = Field(
        default=None,
        description="RFC3339 timestamp (inclusive) for the earliest event to return (e.g., '2025-04-17T00:00:00Z'). Defaults to now.",
    )
    time_max: Optional[str] = Field(
        default=None,
        description="RFC3339 timestamp (exclusive) for the latest event to return. Defaults to 30 days ahead.",
    )


class SearchEventByDescriptionInputSchema(BaseModel):
    calendar_id: str = Field(..., description="Calendar ID to search events in.")
    search_text: str = Field(
        ..., description="Substring to search in event descriptions."
    )


# Describe schema mappings
schema_mappings = {
    "acreate_calendar": {
        "description": "Create a new Google Calendar.",
        "input_schema": CreateCalendarInputSchema,
    },
    "adelete_calendar": {
        "description": "Delete an existing Google Calendar by ID.",
        "input_schema": DeleteCalendarInputSchema,
    },
    "aupdate_calendar": {
        "description": "Update a calendar's summary or time zone by ID.",
        "input_schema": UpdateCalendarInputSchema,
    },
    "alist_calendars": {
        "description": "List all calendars accessible by the service account.",
        "input_schema": ListCalendarsInputSchema,
    },
    "acreate_event": {
        "description": "Create an event in a specific Google Calendar.",
        "input_schema": CreateEventInputSchema,
    },
    "adelete_event": {
        "description": "Delete an event from a calendar by event ID.",
        "input_schema": DeleteEventInputSchema,
    },
    "aupdate_event": {
        "description": "Update an event in a calendar by event ID with provided fields.",
        "input_schema": UpdateEventInputSchema,
    },
    "alist_events": {
        "description": "List events from a Google Calendar within a specified time window.",
        "input_schema": ListEventsInputSchema,
    },
    "asearch_event_by_description": {
        "description": "Search for events by description substring in a specific calendar.",
        "input_schema": SearchEventByDescriptionInputSchema,
    },
}
