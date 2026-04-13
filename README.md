
# 🤖 Enterprise IT Triage Agent (Serverless RAG)

An autonomous IT Helpdesk Copilot designed to instantly triage and resolve enterprise employee tickets. Built with a modern AI stack and deployed to a serverless Google Cloud environment.

### 🚀 **[Try the Live Demo Here](https://autotriage-service-390897383172.us-central1.run.app)**
*(Note: As this runs on a serverless scale-to-zero instance, the initial load may take 10-15 seconds to cold-start. Subsequent queries will be instant).*

---

## 🎯 The Business Value
Instead of forcing employees to navigate static knowledge bases or wait for human L1 support, this agent:
1. Ingests the IT issue in natural language.
2. Queries a localized vector database of company protocols.
3. Streams context-aware, highly accurate troubleshooting steps with ultra-low latency.

## 🏗️ Architecture & Tech Stack

* **Backend Framework:** Python 3.10 / FastAPI
* **LLM Orchestration:** LangChain
* **Inference Engine:** Groq (Llama 3 / Mixtral)
* **Vector Database:** ChromaDB 
* **Embeddings Model:** HuggingFace (`all-MiniLM-L6-v2`)
* **Infrastructure:** Docker, Google Cloud Platform (GCP Cloud Run)

---

## 🛠️ Engineering Challenges & Problem Solving

Moving this application from a local environment to a production cloud server presented several infrastructure bottlenecks, which were successfully diagnosed and resolved:

### 1. Cloud Memory Allocation (OOM Crashes)
* **The Issue:** GCP Cloud Run defaults to 512MB of RAM. During the cold-boot initialization of ChromaDB and the LangChain HuggingFace wrapper, the container would exceed memory limits and silently crash.
* **The Fix:** Configured the deployment pipeline to explicitly bind `--memory 2Gi` and `--cpu 2` to the container, ensuring stable ML workloads.

### 2. Third-Party Rate Limiting (HTTP 429)
* **The Issue:** The ephemeral cloud server was continually blocked by the HuggingFace Hub when attempting to download the `all-MiniLM-L6-v2` embedding model anonymously, resulting in server timeout failures.
* **The Fix:** Generated a dedicated read token and engineered a secure code-level injection (`os.environ["HF_TOKEN"]`) at the absolute top of the runtime script, forcing the downstream libraries to authenticate and bypass the 4-minute wait loops.

### 3. Containerized Portability
* **The Issue:** Ensuring the complex underlying OS-level C++ dependencies required by AI libraries did not break upon deployment.
* **The Fix:** Packaged the entire architecture using Docker. This decoupled the application from the underlying cloud provider, ensuring strict dependency isolation, deterministic builds, and zero vendor lock-in.

---

## 💻 Running the Project Locally

If you wish to run this architecture on your local machine:

**1. Clone the repository**
```bash
git clone [https://github.com/your-username/enterprise-ticket-resolution-agent.git](https://github.com/your-username/enterprise-ticket-resolution-agent.git)
cd enterprise-ticket-resolution-agent
