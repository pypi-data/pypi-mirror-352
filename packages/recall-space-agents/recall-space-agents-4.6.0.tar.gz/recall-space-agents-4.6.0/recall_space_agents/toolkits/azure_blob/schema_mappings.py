from pydantic import BaseModel, Field

# ------------------- SCHEMA DEFINITIONS -------------------
# Container name removed from the schemas since it's now part of initialization


class ListFilesInFolderInputSchema(BaseModel):
    folder_path: str = Field(
        ...,
        description="Folder path prefix to list blobs under (e.g., 'some-folder/').",
    )


class ReadFileInputSchema(BaseModel):
    blob_name: str = Field(..., description="The blob name (path) to read.")


class ReadPickleInputSchema(BaseModel):
    blob_name: str = Field(
        ..., description="The blob name (path) of the pickled object."
    )


# ------------------- SCHEMA MAPPINGS -------------------
schema_mappings = {
    "alist_files_in_folder": {
        "description": "List files/folders in the specified path in Azure Blob Storage.",
        "input_schema": ListFilesInFolderInputSchema,
    },
    "aread_file": {
        "description": "Read the contents of a blob and return raw bytes.",
        "input_schema": ReadFileInputSchema,
    },
    "aread_pickle": {
        "description": "Read the contents of a blob as a Python pickled object.",
        "input_schema": ReadPickleInputSchema,
    },
}
