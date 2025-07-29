from typing import Optional
from pydantic import BaseModel, Field


class ReadDocumentInputSchema(BaseModel):
    url_source: Optional[str] = Field(
        None,
        description="Public URL of the file to extract text from (PDF, image, etc.).",
    )
    file_bytes: Optional[bytes] = Field(
        None,
        description="File contents as bytes; either url_source or file_bytes (not both) must be provided.",
    )


schema_mappings = {
    "read_document": {
        "description": "Extract all readable text content from a document using Azure's OCR. Returns concatenated content and confidence info. If 'return_raw' is True at toolkit init, adds the full raw analysis object.",
        "input_schema": ReadDocumentInputSchema,
    },
    # Add further entries for invoice/receipt/etc. as you extend
}
