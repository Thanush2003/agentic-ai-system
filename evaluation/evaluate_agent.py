import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)
import json
import pandas as pd

from datasets import Dataset

from ragas import evaluate
from langchain_community.chat_models import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings

from ragas.llms import LangchainLLMWrapper

from ragas.metrics import (
    faithfulness,
    answer_relevancy
)

from agent.graph import (
    agent_graph
)


# -----------------------------
# LOAD GOLDEN DATASET
# -----------------------------
with open(
    "evaluation/golden_qa.json",
    "r",
    encoding="utf-8"
) as f:

    golden_data = json.load(f)


# -----------------------------
# STORE RESULTS
# -----------------------------
questions = []

answers = []

contexts = []

ground_truths = []


# -----------------------------
# RUN AGENT
# -----------------------------
print(
    "\nRUNNING FULL AGENT EVALUATION...\n"
)

for item in golden_data:

    question = item["question"]

    ground_truth = item[
        "ground_truth"
    ]

    print("=" * 60)

    print(
        f"\nQUESTION: {question}"
    )

    try:

        response = agent_graph.invoke({

            "user_query": question,

            "plan": [],

            "tool_results": [],

            "final_answer": "",

            "memory": [],

            "reflection": "",

            "retry_count": 0
        })

        answer = response[
            "final_answer"
        ]

        tool_results = response[
            "tool_results"
        ]

        context_text = str(
            tool_results
        )

        print(
            f"\nANSWER:\n{answer}"
        )

    except Exception as e:

        answer = (
            "Evaluation failed."
        )

        context_text = ""

        print(
            f"\nERROR: {str(e)}"
        )

    questions.append(
        question
    )

    answers.append(
        answer
    )

    contexts.append(
        [context_text]
    )

    ground_truths.append(
        ground_truth
    )


# -----------------------------
# CREATE DATASET
# -----------------------------
dataset = Dataset.from_dict({

    "question": questions,

    "answer": answers,

    "contexts": contexts,

    "ground_truth": ground_truths
})


# -----------------------------
# RUN RAGAS METRICS
# -----------------------------
print(
    "\nRUNNING RAGAS METRICS...\n"
)

ollama_llm = LangchainLLMWrapper(

    ChatOllama(
        model="llama3"
    )
)

embedding_model = HuggingFaceEmbeddings(

    model_name=
    "sentence-transformers/all-MiniLM-L6-v2"
)

result = evaluate(

    dataset=dataset,

    llm=ollama_llm,

    embeddings=embedding_model,

    metrics=[
        faithfulness,
        answer_relevancy
    ]
)


# -----------------------------
# RESULTS TABLE
# -----------------------------
df = result.to_pandas()

print("\n" + "=" * 60)

print(
    "\nFINAL EVALUATION RESULTS\n"
)

print(df)

print("\n" + "=" * 60)

print(
    "\nAVERAGE SCORES\n"
)

print(df.mean(numeric_only=True))