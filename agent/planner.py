import json

import ollama

from tools.registry import TOOLS


def create_plan(user_query):

    # -----------------------------
    # BUILD TOOL DESCRIPTIONS
    # -----------------------------
    tool_descriptions = ""

    for tool in TOOLS:

        tool_descriptions += (
            f"Tool Name: {tool['name']}\n"
            f"Description: "
            f"{tool['description']}\n\n"
        )

    # -----------------------------
    # PLANNER PROMPT
    # -----------------------------
    planner_prompt = f"""
You are an AI planning agent.

Your job is to create a short ordered plan
for solving the user's question.

You have access to these tools:

{tool_descriptions}

Rules:
1. Choose the most relevant tools.
2. Return ONLY valid JSON.
3. Each step must contain:
   - step
   - tool
   - task
4. Do not explain anything.
5. Keep plan short and clear.

User Question:
{user_query}
"""

    # -----------------------------
    # CALL LLM PLANNER
    # -----------------------------
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": planner_prompt
            }
        ],
        options={
            "temperature": 0
        }
    )

    plan_text = (
        response["message"]["content"]
        .strip()
    )

    # -----------------------------
    # PARSE JSON OUTPUT
    # -----------------------------
    try:

        plan = json.loads(plan_text)

        return plan

    except Exception:

        return [
            {
                "step": 1,
                "tool": "rag_search",
                "task":
                "Fallback retrieval from PDFs"
            }
        ]