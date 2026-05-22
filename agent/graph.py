from typing import TypedDict
from typing import List


class AgentState(TypedDict):

    user_query: str

    plan: list

    tool_results: list

    final_answer: str

    memory: List[str]

    retry_count: int
    
    reflection_score: float

from agent.planner import (
    create_plan
)


def planner_node(state):

    query = state["user_query"]

    state["retry_count"] += 1

    plan = create_plan(query)

    state["plan"] = plan

    return state

from tools.registry import (
    TOOLS
)


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

                    # TOOL EXECUTION
                    result = tool[
                        "function"
                    ](
                        state["user_query"]
                    )

                except Exception:

                    result = (
                        "Tool execution failed."
                    )

                results.append({

                    "tool": tool_name,

                    "result": result
                })

        # UNKNOWN TOOL
        if not tool_found:

            results.append({

                "tool": tool_name,

                "result":
                "Unknown tool requested."
            })

    state["tool_results"] = results

    return state

import ollama


def answer_node(state):

    tool_results = (
        state["tool_results"]
    )

    # TOOL OUTPUT TEXT
    tool_outputs = str(
        tool_results
    ).lower()

    # FAILURE / EMPTY RETRIEVAL CHECK
    if (

        "document not found"
        in tool_outputs

        or

        "no relevant information found"
        in tool_outputs

        or

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

        or

        "document summarization failed"
        in tool_outputs

        or

        "calculation failed"
        in tool_outputs

        or

        "web search unavailable"
        in tool_outputs

    ):

        answer = (
            "I do not have enough "
            "reliable information "
            "to answer that accurately."
        )

    else:

        memory = (
            "\n".join(state["memory"])
        )

        prompt = f"""
You are an AI agent.

Conversation Memory:
{memory}

User Question:
{state["user_query"]}

Tool Results:
{tool_results}

Generate a final helpful answer.
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

    # UPDATE MEMORY
    state["memory"].append(
        f"User: {state['user_query']}"
    )

    state["memory"].append(
        f"Assistant: {answer}"
    )

    return state

def reflection_node(state):

    prompt = f"""
You are an AI reflection evaluator.

Evaluate the following answer.

Score from 0 to 1 based on:

1. Groundedness
- Is answer supported by tool results?

2. Completeness
- Does answer fully address question?

Return ONLY a decimal number.

User Question:
{state["user_query"]}

Tool Results:
{state["tool_results"]}

Final Answer:
{state["final_answer"]}
"""

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    score_text = (
        response["message"]["content"]
        .strip()
    )

    try:

        score = float(score_text)

    except Exception:

        score = 0.0

    state["reflection_score"] = score

    return state

def should_retry(state):

    score = state["reflection_score"]

    retries = state["retry_count"]

    if score < 0.7 and retries < 2:

        return "retry"

    return "finish"







from langgraph.graph import (
    StateGraph,
    END
)


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