from pymilvus import (
    connections,
    Collection
)

import ollama


# -----------------------------
# CONNECT TO MILVUS
# -----------------------------
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

collection = Collection(
    "pdf_rag"
)

collection.load()


# -----------------------------
# SUMMARIZE DOCUMENT
# -----------------------------
def summarize_document(doc_id):

    try:

        print("Fetching chunks...")

        # CLEAN QUERY
        doc_name_lower = (
            doc_id.lower()
        )

        query_words = [
            word
            for word in doc_name_lower.split()

            if word not in [
                "summarize",
                "summary",
                "pdf",
                "the",
                "document"
            ]
        ]

        # FETCH MATCHING DOCUMENT CHUNKS
        matching_chunks = []

        all_chunks = collection.query(

            expr="id >= 0",

            output_fields=[
                "text",
                "source"
            ],

            limit=10000
        )

        for chunk in all_chunks:

            source = (
                chunk["source"]
                .lower()
            )

            # MATCH DOCUMENT NAME
            if any(
                word in source
                for word in query_words
            ):

                matching_chunks.append(
                    chunk
                )

        print(
            "Chunks found:",
            len(matching_chunks)
        )

        # NO DOCUMENT FOUND
        if not matching_chunks:

            return (
                "Document not found."
            )

        # REMOVE DUPLICATES
        unique_texts = []

        seen = set()

        for chunk in matching_chunks:

            text = chunk["text"]

            if text not in seen:

                seen.add(text)

                unique_texts.append(text)

        # COMBINE TEXT
        full_text = "\n".join(
            unique_texts
        )

        # LIMIT CONTEXT SIZE
        full_text = full_text[:4000]

        print(
            "Generating summary..."
        )

        # PROMPT
        prompt = f"""
You are a helpful AI assistant.

Summarize the following document.

Focus on:
- key concepts
- main ideas
- important points
- conclusions

Document Content:
{full_text}
"""

        # GENERATE SUMMARY
        response = ollama.chat(

            model="llama3",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        summary = (
            response["message"]["content"]
        )

        print(
            "Summary generated!"
        )

        return summary

    except Exception:

        return (
            "Document summarization failed."
        )

# -----------------------------
# TOOL WRAPPER
# -----------------------------
summarize_tool = {

    "name":
    "summarize_document",

    "description":
    "Use this tool when the user asks to summarize an existing PDF document from the corpus/database.",

    "function":
    summarize_document,

    "input_schema": {
        "doc_id": "string"
    }
}