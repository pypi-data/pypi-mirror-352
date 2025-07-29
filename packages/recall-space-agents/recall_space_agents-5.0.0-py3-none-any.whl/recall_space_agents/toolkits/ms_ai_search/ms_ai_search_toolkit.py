import re
import string
import hashlib
from datetime import datetime, timezone

# For stemming
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# IMPORTANT: Use the asynchronous clients from Azure Cognitive Search
from azure.search.documents.aio import SearchClient as AsyncSearchClient
from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    VectorSearch,
    SearchField,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
)
from azure.search.documents.models import VectorizedQuery

from langchain_openai import AzureOpenAIEmbeddings

from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.toolkits.ms_ai_search.schema_mappings import schema_mappings
import operator
from typing import Annotated, List, TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langchain_core.documents import Document
from textwrap import dedent


class MSAISearchToolKit:
    """
    A toolkit class for managing documents in an Azure Cognitive Search index asynchronously.
    It provides async methods for creating/updating the index, adding/updating documents,
    reading, deleting, and performing searches.

    Includes:
    - A new field "optimized_text_search_content" for improved text searching.
    - A simple NLP preprocessing function with stemming.
    """

    def __init__(
        self,
        ai_search_base_url: str,
        ai_search_api_key: str,
        index_name: str,
        embeddings_url: str = None,
        embeddings_api_key: str = None,
        embedder=None,
        **kwargs
    ):
        self.ai_search_base_url = ai_search_base_url
        self.ai_search_api_key = ai_search_api_key
        self.index_name = index_name
        self._ensure_nltk_punkt_tab()

        # Asynchronous clients for Azure Cognitive Search
        self.index_client = AsyncSearchIndexClient(
            endpoint=ai_search_base_url,
            credential=AzureKeyCredential(ai_search_api_key),
        )
        self.search_client = AsyncSearchClient(
            endpoint=ai_search_base_url,
            index_name=index_name,
            credential=AzureKeyCredential(ai_search_api_key),
        )

        # If no embedder is provided, default to using AzureOpenAIEmbeddings.
        if embedder is None:
            self.embedder = AzureOpenAIEmbeddings(
                base_url=embeddings_url,
                api_key=embeddings_api_key
            )
        else:
            self.embedder = embedder(**kwargs)

        # Reference your schema mappings.
        self.schema_mappings = schema_mappings
        # This will store the most up-to-date "Core" memory summary
        self.current_memory_summary = ""

    async def create_memory_storage(self, dimensions: int = 1536):
        """
        Create or update the Azure Cognitive Search index, including vector search configurations.
        """
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                sortable=True,
                filterable=True,
            ),
            SearchableField(name="content", type=SearchFieldDataType.String),
            # New field for optimized text-based searching.
            SearchableField(name="optimized_text_search_content", type=SearchFieldDataType.String),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=dimensions,
                vector_search_profile_name="RecallProfile",
            ),
            SimpleField(
                name="timestamp",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
            ),
            SimpleField(
                name="metadata",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=False,
            ),
            SimpleField(
                name="type",
                type=SearchFieldDataType.String,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="recallHnsw")],
            profiles=[
                VectorSearchProfile(
                    name="RecallProfile",
                    algorithm_configuration_name="recallHnsw",
                )
            ],
        )

        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
        )

        result = await self.index_client.create_or_update_index(index)
        return {"status": "Index created or updated", "result": str(result)}

    async def save_memory(self, content: str, metadata="", type=""):
        """
        Create or update a document in the Azure Cognitive Search index.
        Also stores an 'optimized' version of the content for text-based searching.
        """
        doc_id = self._hash_string(content.strip())
        data = {
            "id": doc_id,
            "content": content,
            "embedding": self.embedder.embed_query(content),
            "metadata": metadata,
            "type": type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            # Store the preprocessed text in the new field
            "optimized_text_search_content": self._simple_text_preprocess(content),
        }

        result = await self.search_client.upload_documents(documents=[data])
        return {"status": "Document created or updated", "result": str(result)}

    async def read_document(self, identifier: str):
        """
        Read a document by its ID from the index.
        """
        result = await self.search_client.get_document(key=identifier)
        return {
            "status": "Document retrieved",
            "document": result,
        }

    async def delete_memory(self, content: str):
        """
        Delete a document by its content from the memory storage.
        """
        id = self._hash_string(content)
        result = await self.search_client.delete_documents(documents=[{"id": id}])
        return {"status": "Document deleted", "result": str(result)}

    async def memory_vector_search(self, search_text: str, top_n: int = 4, type_filter: str = None):
        """
        Perform a vector-based search using the given search_text.
        Optionally filters by the 'type' field if type_filter is provided.
        The text is embedded internally with AzureOpenAIEmbeddings.

        Returns documents with a search score above the given threshold.
        """
        # Generate the embedding inside this method
        embedding_vector = self.embedder.embed_query(search_text)
        vector_query = VectorizedQuery(
            vector=embedding_vector,
            k_nearest_neighbors=top_n,
            fields="embedding",
        )

        # If a type_filter is specified, add it to the filter condition

        # If a type_filter is specified, add it to the filter condition
        if type_filter is not None and (type_filter.capitalize() in ["Semantic","Episodic","Procedural", "Core"]):
            filter_condition = f"type eq '{type_filter.capitalize()}'"
        else:
            filter_condition = "type ne 'Core'"
        print(f"filter_condition: {filter_condition}")


        results_iterator = await self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            order_by=["timestamp desc"],
            filter=filter_condition
        )

        recalled = []
        async for item in results_iterator:
            recalled.append(
                {
                    "content": item.get("content"),
                    "timestamp": item.get("timestamp"),
                    "metadata": item.get("metadata", ""),
                    "type": item.get("type", "")
                }
            )
        return recalled

    async def memory_text_search(self, search_text: str, top_n: int = 4, type_filter: str = None):
        """
        Perform a text-based search for the given `search_text` 
        against the 'optimized_text_search_content' field.
        Returns documents with a search score above the given threshold.
        """

        search_text = self._simple_text_preprocess(search_text)

        # If a type_filter is specified, add it to the filter condition
        if type_filter is not None and (type_filter.capitalize() in ["Semantic","Episodic","Procedural", "Core"]):
            filter_condition = f"type eq '{type_filter.capitalize()}'"
        else:
            filter_condition = "type ne 'Core'"
        print(f"filter_condition: {filter_condition}")

        results_iterator = await self.search_client.search(
            search_text=search_text,
            top=top_n,
            order_by=["timestamp desc"],
            search_fields=["optimized_text_search_content"],
            filter=filter_condition
        )

        matched = []
        async for item in results_iterator:
            matched.append(
                {
                    "content": item.get("content"),
                    "timestamp": item.get("timestamp"),
                    "metadata": item.get("metadata", ""),
                    "type": item.get("type", ""),
                    "@search.score": item["@search.score"],
                }
            )
        return matched

    async def summarize_recent_memories(
        self,
        llm
    ) -> str:
        """
        Fetch the last 100 memories from the Azure Cognitive Search index, and perform
        a map-reduce summarization using Langchain-style prompts.

        This automatically incorporates self.current_memory_summary (the most recent 
        'Core' memory) as previous context in the final combination step.
        """

        # 1. Retrieve the most recent 100 memories from the index, ordered by timestamp descending
        results_iterator = await self.search_client.search(
            search_text="*",  # fetch all
            top=100,
            order_by=["timestamp desc"]
        )

        self.current_memory_summary = await self.search_client.search(
            search_text="*",
            top=1,
            order_by=["timestamp desc"],
            filter="type eq 'Core'"
        )
        print(f"current summary: {self.current_memory_summary}")

        # 2. Collect all documents' content into a list of Langchain Document objects
        docs = []
        async for item in results_iterator:
            content = item.get("content", "")
            if content:
                docs.append(Document(page_content=content, metadata={"type": item.get("type", "")}))

        # If no memories are present, simply return the current summary or empty
        if not docs:
            return ""

        # 3. Define your prompts for the map-reduce approach
        map_template = (
            "Write a concise summary of the following chunk of text:\n\n{context}"
        )
        reduce_template = dedent(f"""
        The following is a list of partial summaries from the 'map' step:
        {{docs}}

        We also have a 'previous_summary' for reference:
        {self.current_memory_summary}

        Based on the partial summaries and the previous summary (if any), 
        please distill these into a final, consolidated summary of the main themes.
        """)

        map_prompt = ChatPromptTemplate([("human", map_template)])
        reduce_prompt = ChatPromptTemplate([("human", reduce_template)])

        map_chain = map_prompt | llm | StrOutputParser()
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        class OverallState(TypedDict):
            contents: List[str]
            summaries: Annotated[list, operator.add]
            final_summary: str

        class SummaryState(TypedDict):
            content: str

        async def generate_summary(state: SummaryState):
            """
            Generates a summary for the given chunk of text using the map_chain.
            """
            response = await map_chain.ainvoke(state["content"])
            return {"summaries": [response]}

        def map_summaries(state: OverallState):
            return [
                Send("generate_summary", {"content": content})
                for content in state["contents"]
            ]

        async def generate_final_summary(state: OverallState):
            """
            Gathers partial summaries and combines them with the previous_summary 
            to produce a final summary.
            """
            response = await reduce_chain.ainvoke(state["summaries"])
            return {"final_summary": response}

        graph = StateGraph(OverallState)
        graph.add_node("generate_summary", generate_summary)
        graph.add_node("generate_final_summary", generate_final_summary)
        graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
        graph.add_edge("generate_summary", "generate_final_summary")
        graph.add_edge("generate_final_summary", END)

        # Compile the graph
        app = graph.compile()

        # 12. Run the graph with 'contents' being the text from each Document
        input_contents = {"contents": [d.page_content for d in docs]}
        final_result = await app.ainvoke(input_contents)

        # 13. Update self.current_memory_summary to the final summary
        self.current_memory_summary = final_result["final_summary"]
        # Also save it to the index as the new Core memory
        await self.save_memory(
            content=self.current_memory_summary,
            metadata="Core Lisa",
            type="Core"
        )
        return self.current_memory_summary

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in this toolkit.
        Each tool now references the async functions.
        """
        tools = []
        for method_name, method_config in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=method_name)
            tool_builder.set_function(eval(f"self.{method_name}"))
            tool_builder.set_coroutine(eval(f"self.{method_name}"))
            tool_builder.set_description(description=method_config["description"])
            tool_builder.set_schema(schema=method_config["input_schema"])
            tool = tool_builder.build()
            tools.append(tool)
        return tools

    def _simple_text_preprocess(self, text: str) -> str:
        """
        Simple NLP preprocessing: lowercasing, removing punctuation, tokenizing, and stemming.
        """
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Tokenize
        tokens = word_tokenize(text)
        # Instantiate the PorterStemmer
        stemmer = PorterStemmer()
        # Apply stemming
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        # Rejoin the processed tokens
        text = " ".join(stemmed_tokens)
        return text

    def _ensure_nltk_punkt_tab(self):
        """
        Checks if 'punkt_tab' is present; if not, download it.
        """
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab")

    def _hash_string(self, input_string: str) -> str:
        """
        Create a SHA-256 hash of the input string for use as a stable document ID.
        """
        hash_object = hashlib.sha256()
        hash_object.update(input_string.encode("utf-8"))
        return hash_object.hexdigest()