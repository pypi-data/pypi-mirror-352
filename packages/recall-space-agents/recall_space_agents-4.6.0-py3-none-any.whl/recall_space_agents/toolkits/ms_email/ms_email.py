"""
This module provides a toolkit for interacting with Microsoft Graph API to manage emails.
It includes functionalities to retrieve and send emails using asynchronous methods.

Classes:
    MSEmailToolKit: A toolkit class for managing emails using Microsoft Graph API.
"""

import base64
import pytz
import io
from PyPDF2 import PdfReader
from agent_builder.builders.tool_builder import ToolBuilder
from bs4 import BeautifulSoup
from msgraph import GraphServiceClient
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.users.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

from recall_space_agents.toolkits.ms_email.schema_mappings import schema_mappings
from msgraph.generated.models.file_attachment import FileAttachment
import base64

class MSEmailToolKit:
    """
    A toolkit class for managing emails using Microsoft Graph API.

    Methods:
        aget_emails: Asynchronously retrieve a list of emails based on specified filters.
        asend_email: Asynchronously send an email with the specified subject, body, and recipients.
        get_tools: Retrieve a list of tools mapped to the methods in the toolkit. Use it to bind
        tools to agents.
    """

    def __init__(self, credentials, as_application = False):
        """
        Initialize the MSEmailToolKit with Microsoft Graph API client.

        Args:
            credentials: The credentials required to authenticate with the Microsoft Graph API.
        """
        self.as_application =as_application
        if self.as_application is True:
            self.required_scopes_as_user = [".default"]
        else:
            self.required_scopes_as_user = [
                "Mail.Read",
                "Mail.ReadWrite",
                "Mail.Send",
                "People.Read",
                "Contacts.Read",
                "Contacts.ReadWrite",
            ]
        self.ms_graph_client = GraphServiceClient(
            credentials=credentials, scopes=self.required_scopes_as_user
        )
        self.schema_mappings = schema_mappings

    async def aget_emails(
        self,
        limit=5,
        skip=0,
        filter="parentFolderId eq 'inbox'",
        return_attachments=False,
    ):
        """
        Asynchronously retrieve a list of emails based on specified filters.
        When `return_attachments` is True, return only attachment details (bytes, name, size).
        Otherwise, return the email metadata without processing attachments.
        """
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=["subject", "from", "receivedDateTime", "body"],
            top=limit,
            skip=skip,
            filter=filter,
            expand=(
                ["attachments"] if return_attachments else None
            ),  # Expand attachments only if needed
        )
        request_config = (
            MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
        )

        # Fetch messages asynchronously
        messages = await self.ms_graph_client.me.messages.get(
            request_configuration=request_config
        )

        full_emails = list(messages.value)
        berlin_timezone = pytz.timezone("Europe/Berlin")

        filtered_emails = []

        for each in full_emails:
            # If `return_attachments` is True, process and return only attachment details
            email_data = {
                "from": f"{each.from_.email_address.address} - {each.from_.email_address.name}",
                "subject": each.subject or "",
                "body": BeautifulSoup(each.body.content, "html.parser").get_text(),
                "received_date_time": each.received_date_time.astimezone(
                    berlin_timezone
                ).strftime("%Y-%m-%d %H:%M:%S %Z%z"),
            }
            if return_attachments:
                attachments = []
                if hasattr(each, "attachments") and each.attachments:
                    for attachment in each.attachments:
                        attachment_info = {
                            "name": attachment.name,
                            "size": attachment.size,
                        }

                        # Download the attachment content
                        attachment_content = await self.download_attachment(
                            attachment.id, each.id
                        )
                        attachment_info["file_bytes"] = attachment_content
                        attachments.append(attachment_info)

                email_data["attachments"] = attachments

            filtered_emails.append(email_data)

        return filtered_emails

    async def asend_email(
        self,
        subject: str,
        body_html: str,
        to_recipient: str,
        senders_email=None,
        attachments: list = None,   # New parameter, accepts a list of dicts {name, content_type, file_bytes}
    ) -> dict:
        """
        Asynchronously send an email with the specified subject, body, recipients, and attachments.

        Args:
            subject (str): Subject of the email.
            body_html (str): HTML content of the email body.
            to_recipient (str): Recipient email address.
            attachments (list): List of dicts with 'name', 'content_type', and 'file_bytes' as bytes.

        Returns:
            dict: A dictionary with the status of the email sent operation.
        """
        to_recipients_list_object = []
        recipient = Recipient()
        recipient.email_address = EmailAddress(address=to_recipient)
        to_recipients_list_object.append(recipient)

        # Attachments
        attachments_list = []
        if attachments:
            for att in attachments:
                # att should be dict: {'name':.., 'content_type':.., 'file_bytes':..}
                print(f"name: {att["name"]}")
                print(f"content_type: {att["content_type"]}")
                print(f"content_bytes: {type(att["file_bytes"])}")
                file_attachment = FileAttachment(
                    odata_type="#microsoft.graph.fileAttachment",
                    name=att["name"],
                    content_type=att["content_type"],
                    content_bytes=att["file_bytes"],
                )
                attachments_list.append(file_attachment)

        email_message = Message(
            subject=subject,
            body=ItemBody(content=body_html, content_type=BodyType("html")),
            to_recipients=to_recipients_list_object,
            attachments=attachments_list if attachments_list else None,
        )
        request_body = SendMailPostRequestBody(
            message=email_message,
            )
        #request_body.message = email_message

        if senders_email is not None and self.as_application is True:
            await self.ms_graph_client.users.by_user_id(senders_email).send_mail.post(request_body)
        else:
            await self.ms_graph_client.me.send_mail.post(request_body)
        return {"status": "Email sent successfully."}

    async def asend_email_by_name(
        self, subject: str, body_html: str, to_recipient_by_name: str
    ) -> dict:
        """
        Asynchronously send an email with the specified subject, body,
        and recipient specified by their name by searching in the user's contacts
        and then in people if not found.

        Args:
            subject (str): Subject of the email.
            body_html (str): HTML content of the email body.
            to_recipient_by_name (str): Recipient name to look up.

        Returns:
            dict: A dictionary with the status of the email sent operation.
        """
        to_recipient_email_address = ""

        name = to_recipient_by_name.strip()

        # First, search in contacts
        from msgraph.generated.users.item.contacts.contacts_request_builder import (
            ContactsRequestBuilder,
        )

        # Construct query parameters for the contacts search
        query_params = ContactsRequestBuilder.ContactsRequestBuilderGetQueryParameters(
            filter=f"contains(displayName,'{name}') or contains(givenName,'{name}') or contains(surname,'{name}')",
            select=["emailAddresses", "displayName"],
        )

        # Set the request configuration with query parameters
        request_configuration = RequestConfiguration(
            query_parameters=query_params,
        )

        # Search contacts
        contacts = await self.ms_graph_client.me.contacts.get(
            request_configuration=request_configuration
        )

        # Check if any contact was found
        if contacts and contacts.value and len(contacts.value) > 0:
            contact = contacts.value[0]
            # Get the email address
            if contact.email_addresses and len(contact.email_addresses) > 0:
                email_address = contact.email_addresses[0].address
                to_recipient_email_address = email_address
            else:
                print(
                    f"this is just a print. No email address found for '{name}' in contacts."
                )
        else:
            print(
                f"this is just a print. No contact found for name '{name}' in contacts."
            )

        # If no email address found in contacts, search in 'people'
        if not to_recipient_email_address:
            # Import the necessary classes for people
            from msgraph.generated.users.item.people.people_request_builder import (
                PeopleRequestBuilder,
            )

            # Construct query parameters for the people search
            query_params = PeopleRequestBuilder.PeopleRequestBuilderGetQueryParameters(
                search=f'"{name}"',
            )

            request_configuration = RequestConfiguration(
                query_parameters=query_params,
            )

            # Search people (contacts, organization, etc.)
            people = await self.ms_graph_client.me.people.get(
                request_configuration=request_configuration
            )

            # Check if any person was found
            if people and people.value and len(people.value) > 0:
                person = people.value[0]
                # Get the email address
                if (
                    person.scored_email_addresses
                    and len(person.scored_email_addresses) > 0
                ):
                    email_address = person.scored_email_addresses[0].address
                    to_recipient_email_address = email_address
                else:
                    print(f"No email address found for '{name}' in people.")
            else:
                print(f"No person found for name '{name}' in people.")

        if not to_recipient_email_address:
            return {
                "status": f"No email address found for the name '{name}' in contacts or people."
            }

        # Send the email using the asend_email method
        return await self.asend_email(subject, body_html, to_recipient_email_address)

    async def download_attachment(self, attachment_id, message_id):
        """
        Download the attachment content (PDF binary) from Microsoft Graph API.
        """
        # Use ms_graph_client to fetch the attachment content (binary)
        attachment = (
            await self.ms_graph_client.me.messages.by_message_id(message_id=message_id)
            .attachments.by_attachment_id(attachment_id=attachment_id)
            .get()
        )
        return attachment.content_bytes

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list: A list of ToolBuilder objects, each representing a method in the toolkit.
        """
        tools = []
        for each_method_key, each_method_value in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=each_method_key)
            tool_builder.set_function(eval(f"self.{each_method_key}"))
            tool_builder.set_coroutine(eval(f"self.{each_method_key}"))
            tool_builder.set_description(description=each_method_value["description"])
            tool_builder.set_schema(schema=each_method_value["input_schema"])
            tool_builder = tool_builder.build()
            tools.append(tool_builder)
        return tools
