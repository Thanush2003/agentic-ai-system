def create_plan(user_query, memory=None):

    query = user_query.lower()

    # -----------------------------
    # MEMORY-AWARE FOLLOW UP
    # -----------------------------

    math_symbols = [
        "+",
        "-",
        "*",
        "/"
    ]

    is_math_query = (

        any(
            symbol in user_query
            for symbol in math_symbols
        )

        and

        any(
            char.isdigit()
            for char in user_query
        )
    )

    # DO NOT ADD MEMORY TO CALCULATIONS
    if is_math_query:

        enhanced_query = user_query

    # SHORT FOLLOW-UP QUESTIONS
    elif memory and len(query.split()) <= 5:

        last_memory = " ".join(memory[-2:])

        enhanced_query = (
            f"{last_memory} {user_query}"
        )

    else:

        enhanced_query = user_query

    # -----------------------------
    # SUMMARIZATION
    # -----------------------------
    if "summarize" in query:

        return [
            {
                "step": 1,
                "tool": "summarize_document",
                "task": enhanced_query
            }
        ]

    # -----------------------------
    # CALCULATOR
    # -----------------------------
    math_symbols = [
        "+",
        "*",
        "/"
    ]

    if (
        any(
            symbol in user_query
            for symbol in math_symbols
        )

        and

        any(
            char.isdigit()
            for char in user_query
        )
    ):

        return [
            {
                "step": 1,
                "tool": "calculator",
                "task": enhanced_query
            }
        ]

    # -----------------------------
    # DEFAULT -> RAG FIRST
    # -----------------------------
    return [
        {
            "step": 1,
            "tool": "rag_search",
            "task": enhanced_query
        }
    ]