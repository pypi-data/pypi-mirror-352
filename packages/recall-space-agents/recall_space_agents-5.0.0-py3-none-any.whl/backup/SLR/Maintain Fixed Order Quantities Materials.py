from typing import TypedDict, List, Optional, Dict, Any
import os
import pickle
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from langsmith import traceable
from recall_space_utils.connectors.blob.azure_blob_connector import AzureBlobConnector
from langchain_openai import AzureChatOpenAI


class FixedOrderQuantityUpdateList(TypedDict):
    class FixedOrderQuantityUpdate(TypedDict):
        material_id: str
        fixed_quantity: int
    updates: List[FixedOrderQuantityUpdate]

class MaintainFixedOrderQuantitiesState(Dict):
    class FixedOrderQuantityUpdate(TypedDict):
        material_id: str
        fixed_quantity: int
    instruction: str
    parsed_updates: Optional[List[FixedOrderQuantityUpdate]]
    error_message: Optional[str]

BLOB_PATH = "inputs/fixed_quantities_materials_dict.pkl"
workflow_llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
)

async def parse_instruction_llm(state: MaintainFixedOrderQuantitiesState) -> MaintainFixedOrderQuantitiesState:
    """
    Use LLM to parse the instruction into a list of updates for fixed order quantities,
    wrapped as `updates`.
    """
    prompt = f"""
    Extract all material IDs and their requested fixed order quantities from the following instruction.
    Each result should have:
      - material_id (string)
      - fixed_quantity (integer, e.g. 4000)
    Wrap the list in a key 'updates'.
    Instruction: {state['instruction']}
    """
    output: FixedOrderQuantityUpdateList = await workflow_llm.with_structured_output(
        FixedOrderQuantityUpdateList, strict=True
    ).ainvoke(prompt)
    state['parsed_updates'] = output['updates']
    return state

async def update_and_store_fixed_order_quantities(state: MaintainFixedOrderQuantitiesState) -> Command:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("SYSTEM_CONTAINER_NAME", "material-planning")
    blob = AzureBlobConnector(conn_str, container)
    try:
        # Check if blob exists by listing blobs with exact name
        blob_exists = False
        blobs = await blob.list_blobs(prefix=BLOB_PATH)
        for name in blobs:
            if name == BLOB_PATH:
                blob_exists = True
                break

        if blob_exists:
            downloaded = await blob.download_blob_as_bytes(BLOB_PATH)
            fixed_quantities_materials_dict = pickle.loads(downloaded)
        else:
            fixed_quantities_materials_dict = {}

        for update in state["parsed_updates"]:
            # Use string keys for material_id, int values for fixed_quantity
            fixed_quantities_materials_dict[str(update["material_id"])] = int(update["fixed_quantity"])
        upload_bytes = pickle.dumps(fixed_quantities_materials_dict)
        await blob.upload_blob_bytes(BLOB_PATH, upload_bytes, overwrite=True)
        return Command(goto=END, update={"error_message": None})
    except Exception as e:
        return Command(goto=END, update={"error_message": str(e)})

builder = StateGraph(MaintainFixedOrderQuantitiesState)
builder.add_node("parse_instruction_llm", parse_instruction_llm)
builder.add_node("update_and_store_fixed_order_quantities", update_and_store_fixed_order_quantities)
builder.add_edge(START, "parse_instruction_llm")
builder.add_edge("parse_instruction_llm", "update_and_store_fixed_order_quantities")
builder.add_edge("update_and_store_fixed_order_quantities", END)
workflow_graph = builder.compile()

@traceable(name="Maintain Fixed Order Quantities Materials", project_name="Maintain Fixed Order Quantities Materials")
async def main(data: Dict[str, Any]) -> Dict[str, Any]:
    input_state: MaintainFixedOrderQuantitiesState = {
        "instruction": data.get("instruction", ""),
        "parsed_updates": None,
        "error_message": None,
    }
    if not input_state["instruction"]:
        return {"error_message": "Instruction input is required.", "parsed_updates": []}
    response = await workflow_graph.ainvoke(input_state)
    return response