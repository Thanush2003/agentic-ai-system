from typing import TypedDict
from typing import List

import ollama

from langgraph.graph import (
    StateGraph,
    END
)

from agent.planner import (
    create_plan
)

from tools.registry import (
    TOOLS
)


# =====================================================
# STATE
# =====================================================

class AgentState(TypedDict):

    user_query: str

    plan: list

    tool_results: list

    final_answer: str

    memory: List[str]

    retry_count: int

    reflection_score: float


# =====================================================
# PLANNER NODE
# =====================================================

def planner_node(state):

    query = state["user_query"]

    # ---------------------------------
    # CREATE PLAN ONLY ONCE
    # ---------------------------------
    if not state.get("plan"):

        state["plan"] = create_plan(
            query,
            state["memory"]
        )

    print(
        "PLANNER PLAN:",
        state["plan"]
    )

    return state


# =====================================================
# EXECUTOR NODE
# =====================================================

def executor_node(state):

    plan = state["plan"]

    results = []

    for step in plan:

        tool_name = step["tool"]

        task = step["task"]

        tool_found = False

        for tool in TOOLS:

            if tool["name"] == tool_name:

                tool_found = True

                try:

                    result = tool["function"](task)

                except Exception:

                    result = (
                        "Tool execution failed."
                    )

                results.append({

                    "tool": tool_name,

                    "result": result
                })

        # ---------------------------------
        # UNKNOWN TOOL
        # ---------------------------------
        if not tool_found:

            results.append({

                "tool": tool_name,

                "result":
                "Unknown tool requested."
            })

    state["tool_results"] = results

    return state


# =====================================================
# ANSWER NODE
# =====================================================

def answer_node(state):

    tool_results = (
        state["tool_results"]
    )

    print(tool_results)

    tool_outputs = str(
        tool_results
    ).lower()

    # =================================================
    # FAILURE HANDLING
    # =================================================

    if (

        "tool execution failed"
        in tool_outputs

        or

        "unknown tool requested"
        in tool_outputs

        or

        "vector database unavailable"
        in tool_outputs

        or

        "rag retrieval failed"
        in tool_outputs

    ):

        answer = (

            "I do not have enough "
            "reliable information "
            "to answer that accurately."
        )

    # =================================================
    # DOCUMENT NOT FOUND
    # =================================================

    elif (

        "document not found"
        in tool_outputs

    ):

        answer = (

            "The requested document "
            "was not found in the database."
        )

    # =================================================
    # NORMAL ANSWER GENERATION
    # =================================================

    # =================================================
    # EMPTY RETRIEVAL
    # =================================================

    elif (

        "could not find relevant information"
        in tool_outputs

    ):

        answer = (
            "I could not find relevant "
            "information in the provided documents."
        )

    # =================================================
    # NORMAL ANSWER GENERATION
    # =================================================

    else:

        memory = (
            "\n".join(state["memory"])
        )

        prompt = f"""
    You are a factual AI assistant.

    Use conversation memory only for maintaining context.

    Answer ONLY using the provided tool results.

    STRICT RULES:
    - Give direct factual answers only.
    - Use exact values from tool results if available.
    - Never repeat the user question.
    - Keep answers concise.
    - Maximum 2 sentences.
    - Never explain reasoning.
    - Never add unnecessary introductory text.
    - Never use outside knowledge.
    - Never hallucinate answers.
    - If answer is unavailable in tool results, say so clearly.

    Conversation Memory:
    {memory}

    User Question:
    {state["user_query"]}

    Tool Results:
    {tool_results}
    """

        try:

            response = ollama.chat(

                model="llama3",

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = (
                response["message"]["content"]
            )

        except Exception:

            answer = (
                "Answer generation failed."
            )

    state["final_answer"] = answer

    # =================================================
    # MEMORY UPDATE
    # =================================================

    state["memory"].append(
        f"User: {state['user_query']}"
    )

    state["memory"].append(
        f"Assistant: {answer}"
    )

    return state


# =====================================================
# REFLECTION NODE
# =====================================================

def reflection_node(state):

    tool_results = str(
        state["tool_results"]
    ).lower()

    answer = (
        state["final_answer"]
        .lower()
    )

    # ---------------------------------
    # FAILED ANSWERS
    # ---------------------------------
    if (

        "could not find relevant information"
        in answer

        or

        "tool execution failed"
        in answer

        or

        "unknown tool requested"
        in answer

        or

        "rag retrieval failed"
        in answer

        or

        "not enough reliable information"
        in answer

    ):

        score = 0.0

    # ---------------------------------
    # GOOD ANSWER
    # ---------------------------------
    else:

        score = 1.0

    state["reflection_score"] = score

    print(
        "REFLECTION SCORE:",
        score
    )

    # ---------------------------------
    # SWITCH TO WEB SEARCH
    # ---------------------------------
    if (

        (
            "could not find relevant information"
            in answer
        )

        or

        (
            "rag retrieval failed"
            in answer
        )

    ):

        if state["retry_count"] < 2:

            state["plan"] = [
                {
                    "step": 1,
                    "tool": "web_search",
                    "task": state["user_query"]
                }
            ]

            print(
                "SWITCHED TO WEB SEARCH"
            )

    return state


# =====================================================
# RETRY LOGIC
# =====================================================

def should_retry(state):

    score = state["reflection_score"]

    retries = state["retry_count"]

    print(
        "RETRY COUNT:",
        retries
    )

    # ---------------------------------
    # GOOD ANSWER
    # ---------------------------------
    if score >= 0.7:

        return "finish"

    # ---------------------------------
    # RETRY
    # ---------------------------------
    if retries < 2:

        state["retry_count"] += 1

        return "retry"

    return "finish"


# =====================================================
# GRAPH
# =====================================================

graph = StateGraph(
    AgentState
)

graph.add_node(
    "planner",
    planner_node
)

graph.add_node(
    "executor",
    executor_node
)

graph.add_node(
    "answer",
    answer_node
)

graph.add_node(
    "reflection",
    reflection_node
)

graph.set_entry_point(
    "planner"
)

graph.add_edge(
    "planner",
    "executor"
)

graph.add_edge(
    "executor",
    "answer"
)

graph.add_edge(
    "answer",
    "reflection"
)

graph.add_conditional_edges(

    "reflection",

    should_retry,

    {

        "retry": "planner",

        "finish": END
    }
)

agent_graph = graph.compile()