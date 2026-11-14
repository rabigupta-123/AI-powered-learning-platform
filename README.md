# AI-Powered Personalized Learning Platform
### Autonomous Multi-Agent Skill Gap Analysis, ROI-Optimized Curricula & Bayesian Knowledge Tracing

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat-square&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple.svg?style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat-square&logo=react)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-SQLite-red.svg?style=flat-square)
![OWASP](https://img.shields.io/badge/OWASP-ASVS%20v4.0-brightgreen.svg?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)

---

## 🌟 Application Previews

### 🌙 Dark Mode (Glassmorphism & Radial Glow)
![Dark Mode Dashboard](frontend-verification.png)

### ☀️ Light Mode (High Contrast WCAG AA)
![Light Mode Dashboard](frontend-verification-light.png)

---

## 1. Executive Summary & Problem Statement

Modern enterprises, universities, and self-directed learners face severe inefficiencies in career readiness:
1. **Generic Course Catalogs:** Static course recommendations ignore existing competencies, prior projects, and evidence.
2. **Disconnected Skill Assessment:** Self-assessments fail to correlate with validated quiz performance or cognitive retention.
3. **Lack of Dynamic Remediation:** Linear learning paths do not adapt when learners struggle with foundational prerequisite concepts.

This platform implements an advanced **Multi-Agent Pedagogical AI Architecture** coordinated via **LangGraph** on a shared `LearnerState` memory model. Five specialized AI agents collaborate deterministically to diagnose learner competencies, calculate mathematical skill gaps against enterprise role profiles, synthesize ROI-prioritized learning roadmaps, and track latent cognitive mastery in real time using **Bayesian Knowledge Tracing (BKT)**.

---

## 2. Multi-Agent AI Architecture (LangGraph StateGraph)

```
                            ┌────────────────────────┐
                            │   Learner / Client     │
                            │  (React Glass UI)      │
                            └───────────┬────────────┘
                                        │ REST API (JWT Authenticated)
                                        ▼
                            ┌────────────────────────┐
                            │   FastAPI API Router   │
                            │  (/assessment, /goal,  │
                            │  /settings, /mentor)   │
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │  Mentor / Orchestrator │ ◄── Dynamic Event Routing
                            │         Agent          │     (new_assessment, goal_change...)
                            └───────────┬────────────┘
                                        │
                 ┌──────────────────────┼──────────────────────┐
                 │                      │                      │
                 ▼                      ▼                      ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
        │  Skill Analysis  │  │ Career Matching  │  │  Progress Tracking  │
        │      Agent       │  │      Agent       │  │        Agent        │
        └────────┬─────────┘  └────────┬─────────┘  └──────────┬──────────┘
                 │                     │                       │
                 └──────────────┬──────┴───────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Recommendation Agent │ ◄── Re-triggered with difficulty -1
                    │  (ROI Priority Rank) │     if BKT flags poor performance
                    └───────────┬──────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Updated LearnerState │ ──► Real-Time React View
                    └──────────────────────┘
```

### The Five Pedagogical Agents:
1. **`SkillAnalysisAgent`:** Evaluates composite proficiency scores ($P_s = 0.2A_s + 0.5Q_s + 0.3E_s$) across self-assessment ($A_s$), quiz averages ($Q_s$), and verified project evidence ($E_s$).
2. **`CareerMatchingAgent`:** Compares learner competencies against target career requirements ($R_s$), generating granular deficits ($G_s = \max(0, R_s - P_s)$), importance-weighted readiness %, and vector-space CosineFit metrics.
3. **`RecommendationAgent`:** Computes ROI-based prioritization ($\text{Priority}_s = (G_s \cdot I_s) / T_s$) to maximize competency gain per study hour, lowering difficulty tiers by 1 when remediation is active.
4. **`ProgressTrackingAgent`:** Executes sequential Bayesian Knowledge Tracing ($P(L_0)=0.30$, $P(T)=0.15$, $P(G)=0.20$, $P(S)=0.10$), dynamically updating mastery beliefs after each assessment.
5. **`MentorAgent` (Orchestrator):** Routes pipeline events, injects live `LearnerState` context into LLM mentor prompts, triggers cognitive remediation when $P(L_n) < 0.50$ after 3+ attempts, and issues certificates when $P(L_n) \ge 0.80$.

---

## 3. Mathematical Formulations & Pedagogical Precision

All mathematical operations are implemented in deterministic backend functions:

### 3.1 Composite Skill Proficiency
$$P_s = 0.2A_s + 0.5Q_s + 0.3E_s$$

### 3.2 Skill Gap Metric
$$G_s = \max(0, R_s - P_s)$$

### 3.3 Importance-Weighted Career Readiness
$$\text{Readiness} = \min\left(100, \frac{\sum (P_s \cdot I_s)}{\sum (R_s \cdot I_s)} \times 100\right)$$
*Baseline Full Stack Developer Scenario:*  
$$\text{Readiness} = \frac{116.2}{335.0} \times 100 \approx 34.69\%$$

### 3.4 Vector-Space Cosine Alignment (CareerFit)
$$\text{CosineFit} = \frac{P \cdot R}{\|P\| \cdot \|R\|}$$

### 3.5 Learning ROI Recommendation Priority
$$\text{Priority}_s = \frac{G_s \cdot I_s}{T_s}$$
*(Ties broken via normalized tag-vector cosine similarity).*

### 3.6 Bayesian Knowledge Tracing (BKT)
* For a correct answer:
  $$P(L_n \mid \text{correct}) = \frac{P(L_{n-1}) \cdot (1 - P(S))}{P(L_{n-1}) \cdot (1 - P(S)) + (1 - P(L_{n-1})) \cdot P(G)}$$
* For an incorrect answer:
  $$P(L_n \mid \text{incorrect}) = \frac{P(L_{n-1}) \cdot P(S)}{P(L_{n-1}) \cdot P(S) + (1 - P(L_{n-1})) \cdot (1 - P(G))}$$
* Latent knowledge transition:
  $$P(L_n) = P(L_n \mid \text{evidence}) + (1 - P(L_n \mid \text{evidence})) \cdot P(T)$$

### 3.7 Elo Adaptive Difficulty (Separated from BKT)
$$E = \frac{1}{1 + 10^{\frac{D - R}{400}}}, \quad R_{\text{new}} = R_{\text{old}} + 32 \cdot (S - E)$$

---

## 4. Multi-Provider AI Mentor Integration

The AI Mentor supports live, grounded conversational mentoring across multiple leading LLM providers:

| Provider | Endpoint | Recommended Active Model | Authentication |
| :--- | :--- | :--- | :--- |
| **Groq** | `https://api.groq.com/openai/v1` | `qwen/qwen3.8-27b` / `openai/gpt-oss-120b` | Bearer Token |
| **NVIDIA NIM** | `https://integrate.api.nvidia.com/v1` | `minimaxai/minimax-m3.1-flash` | Bearer Token |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `meta-llama/llama-3.3-70b-instruct` | Bearer Token |
| **Google Gemini** | `generativelanguage.googleapis.com` | `gemini-1.5-flash` | Query Param Key |
| **Anthropic Claude**| `api.anthropic.com` | `claude-3-haiku-20240307` | `x-api-key` |

### Security & Privacy Guarantee:
* Keys are encrypted server-side using **AES-128 Fernet cryptography** (`gAAAAA...` ciphertext).
* Keys are **never** returned to the frontend or printed in server logs. Retrieval endpoints return only masked previews (`****1234`).
* Built-in connection testing endpoint: `POST /settings/llm-test` reports latency (ms) and HTTP status.

---

## 5. Course Catalog & Certified Cognitive Mastery

* **18 Real-World Free Learning Resources:** Hand-curated free resources across 6 skills and 5 categories from freeCodeCamp, MDN Web Docs, The Odin Project, Python Software Foundation, React Core Team, and Node.js Foundation.
* **Automated ReportLab PDF Certificates:** Automatically issued upon attaining $P(L_n) \ge 0.80$ with unique UUID verification codes and downloadable landscape PDFs.
* **Public Verification Endpoint:** `GET /certificates/verify/{verification_code}`.

---

## 6. Quick Start & Execution Guide

### Prerequisites
* Python 3.12+
* Node.js 18+ (for frontend bundling)

### One-Click Launch (PowerShell)
```powershell
.\run.ps1
```

### Manual Launch
```powershell
# 1. Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# 2. Run Database Seeding
$env:PYTHONPATH="backend"
python -m app.seeds.seed_data

# 3. Start FastAPI Server
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

**Demo Credentials:**
* Email: `demo@example.com`
* Password: `DemoPass123!`

---

## 7. Automated QA Swarm & Verification Suite

Run the full 5-agent verification swarm:
```powershell
python backend/qa/run_all_qa_agents.py
```

Run headless Playwright browser E2E tests:
```powershell
python backend/qa/verify_launch_e2e.py
```

| QA Agent | Target | Status |
| :--- | :--- | :--- |
| **Agent 1: Formula Cross-Check** | $P_s$, $G_s$, Readiness, CosineFit, BKT precision | ✅ PASSED (Exit Code 0) |
| **Agent 2: API Contract** | 10 REST endpoints, 401/422 boundaries | ✅ PASSED (Exit Code 0) |
| **Agent 3: Security & OWASP ASVS** | SQLi, JWT tampering, Fernet encryption-at-rest | ✅ PASSED (Exit Code 0) |
| **Agent 4: E2E Adaptation Flow** | 3 consecutive failures $\to$ Remediation tier -1 | ✅ PASSED (Exit Code 0) |
| **Agent 5: Accessibility & UX** | WCAG AA contrast $\ge 4.5:1$ in Dark and Light modes | ✅ PASSED (Exit Code 0) |
| **Playwright E2E UI Test** | DOM mounting, theme switching, 0 console errors | ✅ PASSED (Exit Code 0) |

---

## 8. License & Integrity

Distributed under the MIT License. Designed for academic and enterprise research into adaptive learning and multi-agent systems.
