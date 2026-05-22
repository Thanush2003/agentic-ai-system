from agent.graph import (
    agent_graph
)


memory = []


while True:

    query = input(
        "\nUser: "
    )

    if not query.strip():
        print(
        "Please enter a query."
        )

        continue

    if query.lower() == "exit":

        break

    initial_state = {
        "user_query": query,

        "plan": [],

        "tool_results": [],

        "final_answer": "",

        "memory": memory,

        "retry_count": 0,
        
        "reflection_score": 0.0
    }

    result = agent_graph.invoke(
        initial_state
    )

    memory = result["memory"]

    print(
        "\nAssistant:",
        result["final_answer"]
    )





























































































# from rag_system.rag_tool import rag_search

# question = "What percentage does the automobile industry contribute to India's GDP?"

# answer = rag_search(question)

# print(answer)



# from tools.calculator_tool import calculate

# result = calculate("25 * 4")

# print(result)



# from tools.web_search_tool import web_search

# result = web_search(
#     "Who won FIFA 2022?"
# )

# print(result)

# from tools.summarize_tool import (
#     summarize_document
# )

# result = summarize_document(
#     "education_policy.pdf"
# )

# print(result)

# from tools.registry import TOOLS

# for tool in TOOLS:

#     print(tool["name"])

# from agent.planner import (
#     create_plan
# )

# query = (
#     "What is 45 * 12?"
# )

# plan = create_plan(query)

# print(plan)