# 🤖 ASIC Triage Agent V2: Multi-Agent Automated Error Analysis Engine

An event-driven, local AI-powered engineering triage pipeline that monitors hardware simulation logs, groups them into semantic vector clusters using an embedding database, and deploys an asynchronous swarm of specialized LLM agents to perform structural Root Cause Analysis (RCA).

Built using **FastAPI**, **ChromaDB**, **Ollama (Llama 3.2 via Metal GPU acceleration)**, and **Streamlit**.

---

## 🏗️ Architectural Topology

The pipeline consists of three independent, highly decoupled stages running locally on-device:

1. **The Ingestion Gate (Watchdog & FastAPI):** An event-driven background file-system watcher monitors local directories.
2. **The Vector Engine Guardrail (ChromaDB):** Log files are stripped of dynamic noise and converted into vector embeddings.
3. **The Asynchronous Agent Swarm (Ollama):** A specialized multi-agent pipeline is initialized asynchronously.

---

## 🚀 Local Installation & Setup

Follow these steps to run the pipeline locally on your machine.

### Prerequisites
* **Python:** Version 3.10 or higher
* **Ollama:** Fully optimized for Apple Silicon Metal acceleration

### 1. Model Preparation
Open a terminal and download the local weights for the specialized agent model:

```bash
ollama run llama3.2:1b
Verify that Ollama is running in the background.
2. Clone and Install Dependencies
Navigate into the project directory and install the necessary Python packages:
Bash
pip3 install fastapi uvicorn chromadb httpx watchdog streamlit pandas
3. Initialize the Application Stack
You will need three terminal windows open to run the full automated system:
Terminal 1: The Local Inference Server
Bash
ollama serve
Terminal 2: The Event-Driven Backend Engine
Bash
python3 -m uvicorn server:app --reload --port 8001
Terminal 3: The Analytics Frontend Dashboard
Bash
python3 -m streamlit run app.py
🔬 Verifying the Triage Engine Pipeline
To observe the pipeline executing completely in real-time, generate a fresh failure entry:
Create a new log file inside the ./logs/ directory named test_protocol_deadlock.log.
Paste the following mock hardware error into it and save:
Plaintext
[CRITICAL] 2026-06-18 17:40:22 - DMA_Controller_A
Descriptor Corruption: Core_0 memory read mismatch at address 0x0000FFCC.
AXI-Stream Interface dropped to State_Deadlock due to backpressure timeout.
Status: Data cache coherence error across processing blocks. Missing ACK signal.
Observe: The backend terminal will fire an event handler, compute a high distance delta, map it to a brand-new cluster, and print out the multi-agent consensus report.
Visualize: Open your browser to the Streamlit local address, hit Force Refresh Database, and select the new cluster to read your technical triage dossier visually.

---

### 🚀 Push to GitHub

