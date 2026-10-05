# 🏢 Enterprise Customer Retention Engine (`customer-retention-personalization`)
> **An asynchronous, resource-aware AI data pipeline mapping multi-source transactional context to streaming-ready Adobe XDM schemas with uncoupled cross-model compliance auditing.**

---

## 🏗️ End-to-End System Topology
The platform ingests fragmented, multi-source enterprise data logs (relational profiles, behavioural events, and unstructured support tickets / customer reviews) entirely on local, budget-tier GPU hardware. The pipeline enforces data contracts via a strict Pydantic validation parsing layer, structures insights into production-ready **Adobe Experience Platform (AEP) XDM** ingestion envelopes, and executes an independent **Model-as-a-Judge** governance loop to monitor operational business logic drift.

### 🗺️ Data Ingestion & Processing Architecture Flow

<img width="898" height="1047" alt="Screenshot 2026-10-02 at 11 11 01 AM" src="https://github.com/user-attachments/assets/b8a44a80-57cb-4efd-84ca-3035529a4140" />


---

## 🔍 Core Engineering Discoveries & Governance Insights

During production simulation runs across 150 unique profile states, our uncoupled cross-model validation architecture successfully surfaced critical algorithmic boundary drifts directly on the user interface:

### 🎯 Case A: "SLA vs. Sentiment Blindness" (Business Rule Decay)
*   **Operational Output (Qwen 7B):** Classified target profile `CUST-057` as a `MEDIUM` churn risk.
*   **Governance Audit (Gemma 12B):** Flagged the payload with a low Relevance Score of `3/5`.
*   **Architectural Root Cause:** The operational model strictly followed a rigid, programmed business timeline rule (*"unresolved tickets open 3-7 days = MEDIUM priority"*). However, the uncoupled judge applied advanced linguistic intuition to catch severe immediate churn threats hidden inside the unstructured text of a 1-star customer review showing 4 days of operational silence. This loop protects downstream automation from acting on lagging or incomplete business rules.

### 🎯 Case B: "Product Hierarchical Misalignment" (Cross-SKU Context Pollution)
*   **Operational Output:** Identified a stark logical contradiction—a `HIGH` churn risk flag paired with an enthusiastic 5-star product review.
*   **Architectural Root Cause:** The query infrastructure flattened the user transaction history into a single customer ID context block. The customer was fully satisfied with one product SKU, but experiencing a critical shipping failure on a completely separate second order SKU. 
*   **Production Mitigation:** This finding demonstrates the absolute necessity of strict upstream **Event-to-Product Hierarchy pre-processing** in data pipeline ETL layers before prompt serialization to isolate product contexts cleanly.

---

## ⚖️ Model Selection Procurement Strategy & Benchmark Matrix

Rather than selecting open-source foundation models based on popularity, our platform implements a rigorous procurement framework grounded in independent empirical data from **Artificial Analysis** (https://artificialanalysis.ai). Models were systematically audited against three architectural pillars: **Intelligence Index Weight**, **Cost-per-Task Token Efficiency**, **Local VRAM Hardware Footprint Constraints**, **Low Halucination**, **Instruction Following** and **generating structured outputs especially JSON**

### 📊 Architectural Trade-Off Analysis Matrix

| Targeted Model Layer | Selected Architecture | Primary Selection Rationale & Benchmark Grounding | Local VRAM Footprint |
| :--- | :--- | :--- | :--- |
| **Operational Ingestion** | `Qwen/Qwen2.5-7B-Instruct` | Chosen for its elite performance on **Structured JSON Instruction Following** and complex data extraction tasks. It balances high token throughput with structural accuracy, outperforming larger legacy models on strict schema formatting contracts. | ~4.5 GB |
| **Data Governance** | `google/gemma-4-12b-it` | Selected due to its outstanding position on the **Artificial Analysis Intelligence Index** for open-weights reasoning. It provides frontier-class semantic analysis and linguistic tone tracking necessary to detect subtle business rule anomalies. | ~6.5 GB (4-bit NF4) |

### 🧠 The Quantization & Resource Guardrail Justification
Deploying a combined **19 Billion parameters** natively across standard hardware would typically require an enterprise-tier cloud GPU array cluster, resulting in high costs and severe vendor lock-in. 

To bypass this infrastructure penalty, we applied **8-bit quantization** to `Qwen/Qwen2.5-7B` and **4-bit Normal Float (NF4) quantization** to `Gemma-4-12B` governance layer. This optimized weight compression strategy successfully flattened our structural memory floor, enabling the entire dual-model extraction and compliance suite to execute deterministically within a strict **11 GB GPU VRAM ceiling** on a single budget-tier workstation. This layout guarantees total data privacy, eliminates API dependency, and delivers absolute runtime cost efficiency.

---

## 📂 Repository Directory Layout & Data Hygiene
```text
project/
├── 📂 config/
│   └── .env.template                 # Public environmental variable contract placeholder
├── 📂 src/
│   ├── 📂 utils/                     # Independent Data Setup & Engineering Utilities
│   │   ├── generate_sql_data.py      # Mock script populating structural SQL tables
│   │   └── generate_chroma_data.py   # Mock script populating unstructured vector text stores
│   ├── customer_data_orchestrator.py # Class handling multi-source relational & vector context
│   └── xdm_schema_models.py          # Strict Pydantic Data Contract Class definitions
├── 📂 storage/                       # LOCAL RUNTIME SANDBOX (Firewalled on Git via .gitignore)
│   └── .gitkeep                      # Hidden placeholder tracking empty folder shape for portability
├── 📜 1_pipeline_batch_run.ipynb     # Consolidated operational worker extraction loop (Qwen)
├── 📜 2_gemma_governance_audit.ipynb  # Uncoupled 4-bit compliance evaluation loop (Gemma 4)
├── 📜 3_gradio_analytics_cockpit.ipynb # Interactive 3-pillar front-end executive dashboard
├── 📄 requirements.txt               # Bounded production package dependency manager registry
└── 📖 README.md                       # High-level technical platform engineering specification

```
*Note: The `storage/` folder is explicitly bounded by our `.gitignore` policy to firewall operational SQLite binaries, Chroma indices, and streaming JSON payloads from entering the public domain, maintaining strict data governance discipline.*

---

## 🛠️ Environment Configuration & Deployment

To run this pipeline portably across cloud containers or local desktop machines, initialize your dynamic parent project root path via a standard environment file:

1. **Create a local `.env` file at the root level of your project directory:**
   ```env
   PROJECT_ROOT=/your/local/system/path/to/capstone_project
   ```

2. **Install the production package requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute the notebooks sequentially** (`1_pipeline_batch_run.ipynb` -> `2_gemma_governance_audit.ipynb` -> `3_gradio_analytics_cockpit.ipynb`) to ingest data, execute compliance audits, and launch the interactive analytics UI cockpit panel.

## 🎛️ Platform Workspace Interface Cockpit


### 🎯 Executive Aggregated Analytics
---
<img width="1939" height="924" alt="Screenshot 2026-10-02 at 12 41 43 PM" src="https://github.com/user-attachments/assets/c5c03497-fae9-464b-b693-39a221617ff2" />

### 🎯 Operational Profile Ingestion Layer
---
<img width="1937" height="588" alt="Screenshot 2026-10-02 at 12 44 14 PM" src="https://github.com/user-attachments/assets/b3fbea5b-7838-4d8f-bd99-970f75ac3b46" />

### 🎯 Cross Model Data Governance Audit
---
<img width="1931" height="475" alt="Screenshot 2026-10-02 at 12 46 22 PM" src="https://github.com/user-attachments/assets/a49bc4a5-8746-4ef4-95be-30a233312b03" />


