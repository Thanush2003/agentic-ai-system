# Agentic AI System

An advanced multi-tool Agentic AI system built using LangGraph, Hybrid RAG, Milvus, Ollama, and multiple reasoning tools.

---

# Features

- Hybrid RAG retrieval
- Planner + Executor workflow
- Calculator tool
- Web search tool
- Document summarization
- Failure handling
- RAGAS evaluation

---

# Setup

## 1. Clone Repository

```bash
git clone <your_repo_url>
cd Agentic-AI-System
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 4. Install Ollama

Download and install Ollama:

https://ollama.com/download

Verify installation:

```bash
ollama --version
```

---

## 5. Pull Llama3 Model

```bash
ollama pull llama3
```

---

## 6. Start Ollama

```bash
ollama run llama3
```

Keep Ollama running while using the agent.

---

## 7. Start Milvus

```bash
docker compose up -d
```

---

## 8. Run PDF Ingestion

```bash
py rag_system/ingest.py
```

---

## 9. Run Agent

```bash
py main.py
```
---

# Evaluation

## Full Agent Evaluation

```bash
py evaluation/evaluate_agent.py
```
