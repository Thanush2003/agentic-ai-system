from rag_system.rag_tool import rag_search

rag_tool = {
    "name": "rag_search",

    "description":
    "Use this tool for question answering over internal PDF documents. Do NOT use for full document summarization.",

    "function": rag_search,

    "input_schema": {
        "query": "string"
    }
}