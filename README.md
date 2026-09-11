# Autonomous Desktop OS Copilot & Multi-Agent Swarm

> **Complete Windows OS desktop automation powered by dynamic multi-agent orchestration, live screen perception (Set-of-Marks grid), safe PowerShell execution, and closed-loop verification — preserving the Adaptive Enterprise Problem Solver (AEPSA) as a dedicated operational mode.**

[![Desktop Automation](https://img.shields.io/badge/Desktop_OS-Automation-cyan)](https://github.com/Veerakarthik-M/agentic_ai_bootcamp)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-blue)](https://github.com/langchain-ai/langgraph)
[![FastMCP](https://img.shields.io/badge/FastMCP-Tools-green)](https://github.com/jlowin/fastmcp)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-orange)](https://ai.google.dev/)
[![Safety](https://img.shields.io/badge/Safety-Guardrails_&_HITL-red)](https://github.com/Veerakarthik-M/agentic_ai_bootcamp)

---

## 1. Problem

Large organizations have information scattered across documents, databases, sensors, maintenance records, historical incidents, and operational systems. A **single LLM cannot reliably investigate** complex enterprise problems requiring multiple sources, tools, calculations, and verification.

Current AI tools either:
- Hallucinate answers without evidence grounding
- Cannot handle multi-source, multi-step investigations
- Lack confidence measurement and safety routing
- Have no mechanism for learning from past outcomes

---

## 2. Solution

AEPSA is an **Adaptive Enterprise Problem-Solving AI** that:

1. **Understands** the problem and classifies it
2. **Plans** an investigation strategy (reusing past successful strategies)
3. **Selects** only the agents required (not every agent every time)
4. **Delegates** to specialized agents with targeted context
5. **Retrieves** evidence from RAG, SQL, and a Knowledge Graph
6. **Uses real tools** (MCP) for calculation and statistical analysis
7. **Generates ranked hypotheses** supported by evidence
8. **Critiques** its own recommendation to find weaknesses
9. **Verifies** each claim independently
10. **Scores confidence + risk** from measurable signals
11. **Routes** to APPROVE / RECHECK / HUMAN based on thresholds
12. **Records** every case to an experience database for future reuse

**Demo problem:** *"Why did the manufacturing defect rate increase from 2% to 7%?"*

---

## 3. Selected Track

**Open Track** — applicable to all enterprise sectors (manufacturing, healthcare, logistics, finance).

The demo focuses on manufacturing quality investigation, which naturally requires all required technical capabilities: structured data, documents, relationships, statistical analysis, multiple agents, verification, confidence, and safety.

---

## 4. Architecture

```
                         ENTERPRISE USER
                                │
                                ▼
                    ┌────────────────────┐
                    │  PROBLEM ANALYZER  │  → Classifies type, complexity, agents needed
                    └──────────┬─────────┘
                               ▼
                    ┌────────────────────┐
                    │ PLANNER / STRATEGY │  → Ordered task plan (reuses past strategies)
                    └──────────┬─────────┘
                               ▼
                         ┌───────────┐
                         │ SUPERVISOR│  → Dynamically selects agents + explains why
                         └─────┬─────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
          RESEARCH           DATA           ANALYSIS
           AGENT             AGENT            AGENT
         (RAG+inject)     (SQL+MCP)     (SciPy+Neo4j)
               │               │               │
               └───────────────┼───────────────┘
                               ▼
                    ┌────────────────────┐
                    │  CONTEXT ENGINE    │  → Per-agent targeted context
                    └──────────┬─────────┘
                               │
                     ┌─────────┼─────────┐
                     ▼         ▼         ▼
                    RAG       SQL        KG
               (Qdrant)  (SQLite)   (Neo4j)
                               │
                         MCP TOOLS
                     ┌─────────┼─────────┐
                     ▼         ▼         ▼
                 Python   Statistics   Graph
                               ▼
                         ┌─────────┐
                         │  CRITIC │  → Challenges the recommendation
                         └────┬────┘
                              ▼
                 ┌──────────────────────────┐
                 │ CONFIDENCE + RISK SCORE  │  → Measurable signals, not LLM guesses
                 └────────────┬─────────────┘
                              ▼
                       ┌────────────┐
                       │   ROUTER   │  → APPROVE / RECHECK / HUMAN
                       └──────┬─────┘
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
           APPROVE         RECHECK          HUMAN
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                          VERIFIER  → Per-claim independent check
                              ▼
                       RECOMMENDATION
                              ▼
                           OUTCOME
                              ▼
                         EVALUATION
                              ▼
                        EXPERIENCE DB → Future strategy reuse
```

---

## 5. Agents

| Agent | Role | Tools Used |
|---|---|---|
| **Problem Analyzer** | Classify problem type, complexity, required data | Gemini LLM |
| **Planner** | Generate ordered task list; reuse past strategies | Gemini + Experience DB |
| **Supervisor** | Dynamically select agents with rationale | Gemini LLM |
| **Research Agent** | RAG document search + prompt injection detection | Qdrant, sentence-transformers |
| **Data Agent** | SQL queries across production/machine/supplier data | SQLite, FastMCP |
| **Analysis Agent** | Statistical analysis + knowledge graph queries | SciPy, Pandas, Neo4j |
| **Critic** | Challenge recommendation; find weaknesses | Gemini LLM |
| **Verifier** | Independent per-claim evidence check | Gemini + evidence |

---

## 6. RAG / Grounding

Three independent grounding systems — the AI cannot operate from memory alone:

### Vector RAG (Qdrant)
- **Documents**: Machine manual, supplier quality report, engineering incident report, quality policy
- **Embeddings**: `all-MiniLM-L6-v2` (sentence-transformers, 384-dim)
- **Injection detection**: Every retrieved chunk is scanned for prompt injection patterns before being passed to agents

### Structured Data (SQLite)
- `production` — daily defect rates, batches, machine IDs
- `machine_data` — temperature, vibration, pressure, error codes
- `maintenance` — maintenance events, findings, technician notes
- `supplier` — delivery records, hardness, quality scores, deviation flags

### Knowledge Graph (Neo4j)
- Supplier → Material → Machine → Event causal chains
- Historical incident pattern matching
- Machine risk assessment queries
- Incompatibility relationship modeling

---

## 7. MCP Tools

12 tools registered via **FastMCP** (agents decide when to call them):

```python
get_machine_data(machine_id, ...)          # Sensor readings
get_defect_history(machine_id, date_range) # Production defect trends
get_maintenance_history(machine_id)        # Maintenance events
get_supplier_history(supplier_id)          # Supplier quality data
get_material_correlation()                 # Material-defect correlation
get_supplier_timeline()                    # Supplier change timeline
get_high_defect_machines(threshold)        # Affected machine detection
search_engineering_docs(query, top_k)      # RAG document search
check_prompt_injection(text)               # Security validation
run_statistical_analysis(type, data)       # Correlation, trend, anomaly
query_knowledge_graph(query_type, params)  # Neo4j graph queries
```


---

## 8. Safety Router

Three rules, evaluated in priority order:

| Rule | Condition | Action |
|---|---|---|
| **Rule C** (priority) | Confidence < 0.50 OR Risk > 0.70 OR contradiction OR max rechecks reached | **HUMAN ESCALATION** |
| **Rule A** | Confidence ≥ 0.80 AND Risk ≤ 0.30 AND evidence ≥ 3 items | **APPROVE** |
| **Rule B** | 0.50 ≤ Confidence < 0.80 (up to 2 iterations) | **RECHECK** |

---

## 9. Human Escalation

When escalated, the human receives:
- Full problem description
- Draft recommendation
- Confidence and risk scores
- Specific reasons for escalation
- Agent selection rationale
- Full evidence list
- Complete trace log

Available actions: **APPROVE** | **MODIFY** | **REJECT**

All human decisions are recorded in the Experience DB.

---

## 10. Verification

The Verifier independently checks each claim in the recommendation:
- Cross-checks against SQL data, RAG documents, statistical analysis
- Returns `PASS` / `PARTIAL` / `FAIL` with per-claim verdicts
- `FAIL` result prefixes the recommendation with a warning

---

## 11. Contradiction Detection

When SQL data and RAG documents contradict each other:
1. Contradiction is detected and flagged in state
2. Agent agreement score drops to 0.45
3. Confidence score decreases automatically
4. Safety router routes to RECHECK or HUMAN
5. UI shows explicit contradiction alert

---

## 12. Observability

Every step is traced with timestamp, agent, action, and detail:

```
10:31:02  Problem Analyzer   Classification complete   Type: root_cause_analysis | Complexity: high
10:31:03  Planner            Plan generated            Strategy: supplier_machine_investigation | 8 tasks
10:31:04  Supervisor         Agent selection complete  Selected: data_agent, research_agent, analysis_agent
10:31:05  Data Agent         SQL query                 SELECT: defect trend over time
10:31:05  Data Agent         SQL query                 SELECT: machine sensor data
10:31:06  Research Agent     RAG query                 Searching: "machine temperature threshold"
10:31:07  Research Agent     ⚠ PROMPT INJECTION        Source: _adversarial_injection.txt
10:31:09  Analysis Agent     Tool call                 run_statistical_analysis → trend_change
10:31:10  Analysis Agent     Tool result               Trend change: Significant (p=0.0001)
10:31:11  Critic             Critique complete         Verdict: ACCEPTABLE | Risk: MEDIUM
10:31:12  Safety System      Confidence computed       87.0% (Evidence: 0.95, Sources: 0.91, Agreement: 0.85)
10:31:12  Safety System      Risk computed             21.0% (LOW)
10:31:12  Safety Router      Decision: APPROVE         Rule A | Confidence: 0.87 | Risk: 0.21
10:31:13  Verifier           Verification complete     PASS | 5/5 claims verified
10:31:13  Experience DB      Case recorded             CASE-20240910-ABCD
```

---

## 13. Experience Learning

The system stores every case in the Experience DB:

```json
{
  "case_id": "CASE-20240910-ABCD",
  "problem_type": "root_cause_analysis",
  "strategy": "supplier_machine_investigation",
  "agents_used": ["data_agent", "research_agent", "analysis_agent"],
  "confidence": 0.87,
  "risk": 0.21,
  "recommendation": "Replace MAT-X17 batch...",
  "verification": "PASS",
  "human_required": false,
  "outcome": "Defect rate reduced 7% → 2.3%",
  "success": true
}
```

When a **similar problem arrives**:
1. Find similar past cases by problem type
2. Retrieve the most successful strategy
3. Adapt the strategy to the current problem
4. Execute with learned context

> Note: This is **experience-based strategy reuse**, not autonomous model retraining.

---

## 14. Security

- **No secrets in repository** — all keys in `.env` (see `.env.example`)
- **Prompt injection defense** — every RAG-retrieved chunk scanned against known injection patterns before agent processing
- **Adversarial document test** — `_adversarial_injection.txt` in RAG corpus for security demonstration
- **Untrusted content isolation** — injected content is flagged and blocked, not silently dropped
- **Synthetic data only** — no real customer data in demo

---

## 15. Setup

### Quick Start (Docker — recommended)

```bash
git clone <repo-url>
cd Agentic_AI
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
docker compose up --build
```

Navigate to: **http://localhost:3000**

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env   # Add GEMINI_API_KEY
python data/seed_db.py
python data/seed_rag.py
python data/seed_kg.py       # Requires Neo4j running
uvicorn main:app --port 8000
```

**Frontend:**
```bash
cd frontend
# Open index.html in browser (set BACKEND=http://localhost:8000 in JS)
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio API key (required) | — |
| `QDRANT_URL` | Qdrant vector DB URL | `http://qdrant:6333` |
| `NEO4J_URI` | Neo4j Bolt URI | `bolt://neo4j:7687` |
| `NEO4J_PASSWORD` | Neo4j password | `hackathon123` |
| `CONFIDENCE_APPROVE_THRESHOLD` | Min confidence for APPROVE | `0.80` |
| `RISK_APPROVE_MAX` | Max risk for APPROVE | `0.30` |

---

## 16. Demo

### Demo Case 1 — Successful Investigation
```
Input: "Why did defect rate increase from 2% to 7%?"

Expected output:
  ✓ 3 agents selected (Data, Research, Analysis)
  ✓ SQL + RAG + statistical analysis + KG evidence retrieved
  ✓ Primary hypothesis: Alloy 7075 vs 6061 mismatch (91% confidence)
  ✓ Confidence: ~87% | Risk: ~21%
  ✓ Decision: APPROVE
  ✓ Verifier: PASS | 5/5 claims verified
```

### Demo Case 2 — High Risk → Human Escalation
```
Input: "Should we immediately stop all production due to this reading?"

Expected output:
  ✓ High-impact action detected → Risk > 0.70
  ✓ Decision: HUMAN ESCALATION
  ✓ Modal with Approve / Modify / Reject options
```

### Demo Case 3 — Contradiction
```
Input: "The documents say temperature is normal but database shows 84C. Which is correct?"

Expected output:
  ✓ Contradiction flag raised
  ✓ Confidence drops below threshold
  ✓ Additional verification requested
```

### Demo Case 4 — Prompt Injection
```
RAG retrieves _adversarial_injection.txt containing:
  "IGNORE ALL PREVIOUS INSTRUCTIONS..."

Expected output:
  ✓ Injection detected in retrieved content
  ✓ Content blocked: "[CONTENT BLOCKED — PROMPT INJECTION DETECTED]"
  ✓ Red alert shown in UI
  ✓ Analysis continues safely with clean sources
```

---

## 17. Evaluation

Run the automated benchmark:

```bash
cd backend
python evaluation/run_eval.py
```

25 benchmark cases across 5 categories:
- **Normal** (5): Standard root cause questions
- **Ambiguous** (5): Vague or unclear problem descriptions
- **Low-evidence** (5): Questions without available data
- **High-risk** (5): Irreversible or high-impact actions
- **Adversarial** (5): Prompt injection, contradictions, goal hijacking

Run specific categories:
```bash
python evaluation/run_eval.py --categories normal high_risk
python evaluation/run_eval.py --limit 5
```

---

## 18. Technical Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 1.5 Flash |
| Agent Orchestration | LangGraph |
| MCP Tools | FastMCP |
| Backend API | FastAPI + SSE streaming |
| Vector RAG | Qdrant + sentence-transformers |
| Structured Data | SQLite |
| Knowledge Graph | Neo4j 5 Community |
| Statistical Analysis | Pandas, NumPy, SciPy |
| Frontend | Self-contained HTML + CSS + JS |
| Serving | Nginx (frontend) + Uvicorn (backend) |
| Container | Docker Compose |

---

## 19. Autonomous Laptop & OS Multi-Agent Automation

A dynamic multi-agent orchestration architecture designed to automate Windows OS desktop workflows with closed-loop verification and safety guardrails.

### Specialized OS Agents:
- **`OSSupervisor`**: Decomposes high-level user commands, coordinates cross-agent workflows, and handles dynamic replanning.
- **`OSShellAgent`**: Executes PowerShell scripts, launches and tracks processes, and monitors system resources (CPU, RAM, Disk, Battery).
- **`OSFileAgent`**: Searches drives, batch organizes directories by extension, parses documents, and manages files.
- **`OSVisionAgent`**: Captures screen state (hardware or virtual buffer fallback), overlays Set-of-Marks coordinate grids, tracks foreground windows, and operates keyboard/mouse.
- **`OSVerifierAgent`**: Closed-loop verification confirming that target processes launched/terminated, files were created, or window states changed.
- **`OS Safety Guardrails`**: Real-time evaluation blocking destructive commands (e.g. disk formats, root recursive deletions, registry overrides) and protecting core Windows system processes (`csrss.exe`, `explorer.exe`, `winlogon.exe`).

### API Endpoints:
- `GET /os/diagnostics`: Live CPU, Memory, Disk, and Battery diagnostics.
- `GET /os/windows`: List visible windows and currently active foreground window.
- `POST /os/screenshot`: Capture screenshot and generate precision coordinate grid.
- `POST /os/automate`: Execute end-to-end task via dynamic multi-agent supervisor.

### Running Laptop Automation Tests:
```bash
# Run multi-process OS and agent test suite:
python backend/tests/test_laptop_automation.py

# Run FastAPI OS endpoints integration tests:
python backend/tests/test_api_endpoints.py
```

