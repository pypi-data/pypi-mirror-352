"""
This module defines the schema mappings for the Azure AI Search functionality,
including the input schemas for creating/updating the index, managing documents,
and performing searches.

Updates:
1. Make 'embedding' optional in CreateOrUpdateDocumentInputSchema.
2. Rename the "recall" schema to "vector_search" so it accepts plain text
   instead of an embedding vector.
3. Rename the "search" schema to "text_search" for clarity in text-based searches.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class DeleteIndexInputSchema(BaseModel):
    # No fields required for deleting the entire index.
    pass

class SaveMemoryInputSchema(BaseModel):
    content: str = Field(..., description="Content of the document.")
    metadata: Optional[str] = Field(None, description="Optional metadata.")
    type: Optional[str] = Field(None, description="Optional document type.")

class DeleteMemoryInputSchema(BaseModel):
    content: str = Field(..., description="The memory content to be deleted is first hashed and converted into an appropriate ID, which is then used to remove the memory.")

class MemoryVectorSearchInputSchema(BaseModel):
    search_text: str = Field(..., description="The text to embed for vector search.")
    top_n: int = Field(default=5, description="Number of closest matches to retrieve.")
    type_filter: Optional[str] = Field(
        None,
        description="An optional 'type' filter for memories, which may be set to 'Semantic', 'Episodic', or 'Procedural'—the recognized memory classifications. If None is provided, no filter is applied.")

class MemoryTextSearchInputSchema(BaseModel):
    search_text: str = Field(..., description="The text to search for.")
    top_n: int = Field(default=5, description="Number of results to retrieve.")
    type_filter: Optional[str] = Field(
        None,
        description="An optional 'type' filter for memories, which may be set to 'Semantic', 'Episodic', or 'Procedural'—the recognized memory classifications. If None is provided, no filter is applied.")

schema_mappings = {
    "save_memory": {
        "description": "Save a memory",
        "input_schema": SaveMemoryInputSchema,
    },
    "delete_memory": {
        "description": "Delete a memory by its content.",
        "input_schema": DeleteMemoryInputSchema,
    },
    "memory_vector_search": {
        "description": "Perform a vector similarity search (semantic search). "
            "The 'search_text' is internally embedded, and results are returned "
            "based on semantic closeness rather than exact keyword matching. "
            "Best used for concept-based or meaning-focused queries.",
        "input_schema": MemoryVectorSearchInputSchema,
    },
    "memory_text_search": {
        "description":  "Perform a text-based (lexical) search, matching terms in 'search_text' "
            "against the stored content. Best used when exact or near-exact term "
            "matching is required",
        "input_schema": MemoryTextSearchInputSchema,
    },
}