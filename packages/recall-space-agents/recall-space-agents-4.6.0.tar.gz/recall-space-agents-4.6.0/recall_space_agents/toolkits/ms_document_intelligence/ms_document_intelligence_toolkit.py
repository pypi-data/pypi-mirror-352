import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.toolkits.ms_document_intelligence.schema_mappings import (
    schema_mappings,
)


class AzureDocumentIntelligenceToolkit:
    """
    Toolkit for Azure Document Intelligence (Read model, extensible).
    Returns either processed content or raw Azure response as needed.
    Methods are mapped for agent-style tool invocation.
    """

    def __init__(self, endpoint: str, key: str, return_raw: bool = False):
        self.endpoint = endpoint
        self.key = key
        self.return_raw = return_raw
        self.client = DocumentIntelligenceClient(
            self.endpoint, AzureKeyCredential(self.key)
        )
        self.schema_mappings = schema_mappings

    async def read_document(self, url_source: str = None, file_bytes: bytes = None):
        """
        Extract text content from a document (OCR) using the prebuilt 'read' model.
        Returns {'content': ..., 'confidence_min': ..., 'confidence_max': ...}
        If initialized with 'return_raw=True', also adds 'raw_response'.
        """
        if not (url_source or file_bytes):
            raise ValueError("Either url_source or file_bytes must be provided.")

        async with self.client:
            if url_source:
                poller = await self.client.begin_analyze_document(
                    "prebuilt-read", AnalyzeDocumentRequest(url_source=url_source)
                )
            else:
                poller = await self.client.begin_analyze_document(
                    "prebuilt-read", AnalyzeDocumentRequest(bytes_source=file_bytes)
                )

            result = await poller.result()

        content = getattr(result, "content", "")
        confidences = [
            word.confidence
            for page in getattr(result, "pages", [])
            for word in getattr(page, "words", [])
            if word.confidence is not None
        ]
        min_conf = min(confidences) if confidences else None
        max_conf = max(confidences) if confidences else None

        response = {
            "content": content,
            "confidence_min": min_conf,
            "confidence_max": max_conf,
        }
        if self.return_raw:
            response["raw_response"] = result  # This is the raw Azure SDK output
        return response

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in this toolkit
        for agent-style orchestration.
        """
        tools = []
        for method_name, method_config in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            # Use getattr for method safety
            method = getattr(self, method_name)
            tool_builder.set_name(name=method_name)
            tool_builder.set_function(method)
            tool_builder.set_coroutine(method)
            tool_builder.set_description(description=method_config["description"])
            tool_builder.set_schema(schema=method_config["input_schema"])
            tool = tool_builder.build()
            tools.append(tool)
        return tools
