# System Architecture

# Overview

The Agentic AI System is a multi-tool AI assistant built using LangGraph orchestration and Hybrid RAG.

The system combines:

- Retrieval
- Planning
- Tool execution
- Answer generation

---

# Workflow

```text
User Query
   ↓
Planner Node
   ↓
Executor Node
   ↓
Tools
 ├── Hybrid RAG
 ├── Calculator
 ├── Web Search
 └── Document Summarizer
   ↓
Answer Node
   ↓
Final Response
```

---

# Components

## Planner Node

Selects tools dynamically based on user query.

---

## Hybrid RAG

Uses:

- Dense retrieval
- BM25 retrieval
- Reciprocal Rank Fusion
- Cross-encoder reranking

---

## Tool Executor

Executes tools selected by planner.

Supported tools:

- RAG Search
- Calculator
- Web Search
- Document Summarization

---

## Answer Node

Generates final grounded response using Ollama.

---

# Failure Handling

The system handles:

- Empty retrieval
- Tool failures
- Missing documents
- Invalid calculations
- Out-of-scope questions

The system abstains safely instead of hallucinating.

---

# Evaluation

The system is evaluated using:

- Faithfulness
- Answer relevancy
- RAGAS metrics