# Riskline — AI Risk Manager

Riskline is a functional, offline-first MVP for the Razorpay AI Risk Manager internship track. It analyzes an AI-assisted decision or generated output, assigns a transparent risk score, explains the signals it found, and proposes human-review mitigations.

> **Responsible-AI boundary:** Riskline is a decision-support prototype. It is not legal, compliance, financial, medical, safety, or security advice, and it does not provide certified compliance decisions.

## Why this problem matters

AI systems increasingly influence decisions involving money, people, privacy, security, and access. A useful risk workflow should do more than return a single opaque label: it should make the contributing categories visible, preserve an audit-friendly history, and make the next human review step explicit. Riskline is designed as a small, inspectable foundation for that workflow.

## Proposed solution

The MVP accepts free-form text such as a prompt, scenario, decision, or AI-generated answer. A modular analysis service sends the text either to the deterministic demo engine or to an optional structured-output LLM provider. The deterministic engine is the default so the project runs without an API key. It detects explainable signals across seven categories, combines them with documented weights, persists the result in SQLite, and exposes it through a FastAPI API consumed by a React dashboard.

## Features

| Capability | What the MVP does |
|---|---|
| Scenario analysis | Validates and analyzes 10–10,000 characters of user-provided text. |
| Seven risk categories | Privacy, security, financial/fraud, bias/fairness, hallucination/factuality, compliance, and safety. |
| Transparent score | Computes a 0–100 weighted score from independently capped category scores. |
| Risk level | Maps scores to Low, Medium, High, or Critical. |
| Explanations | Shows triggered signals and a category rationale. |
| Mitigations | Recommends prioritized actions and a likely review owner. |
| History | Persists analyses in SQLite and allows previous results to be reopened. |
| Demo data | Includes four scenarios for immediate demonstration. |
| Offline-first | The deterministic engine needs no API key or network call. |
| Optional LLM mode | Supports schema-validated JSON from an OpenAI-compatible API, with deterministic fallback. |
| Basic protection | Input validation, CORS allow-listing, and configurable rate limiting are included. |

## Architecture

```text
┌────────────────────────┐       HTTP/JSON       ┌──────────────────────────┐
│ React + Vite dashboard │ ────────────────────> │ FastAPI application       │
│ Riskline UI            │ <──────────────────── │ /api/analyses            │
└────────────┬───────────┘                       │ /api/demos /api/health   │
             │                                  └─────────────┬────────────┘
             │                                                │
             │                                      ┌─────────▼─────────┐
             │                                      │ Analysis service   │
             │                                      │ demo or optional   │
             │                                      │ structured LLM     │
             │                                      └─────────┬─────────┘
             │                                                │
             │                                      ┌─────────▼─────────┐
             └────────────────────────────────────│ SQLite + SQLAlchemy│
                                                    └───────────────────┘
```

The backend is intentionally modular. `app/services/analyzer.py` selects the provider, `app/risk_engine/deterministic.py` contains the transparent demo logic, and `app/schemas/risk.py` is the contract that both the API and optional LLM output must satisfy.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2 |
| Storage | SQLite for local development |
| Frontend | React 18, Vite, plain CSS, Lucide icons |
| Testing | Pytest and FastAPI-compatible HTTP tooling |
| Packaging | `requirements.txt`, `package.json`, Dockerfile, Docker Compose |

## Risk-scoring methodology

Each category receives a score from 0 to 100. The deterministic engine adds capped contributions when transparent keyword rules match. It does not claim that a missing keyword proves safety.

| Category | Weight |
|---|---:|
| Privacy | 16% |
| Security | 16% |
| Financial / fraud | 16% |
| Bias / fairness | 14% |
| Hallucination / factuality | 14% |
| Compliance | 12% |
| Safety | 12% |
| **Total** | **100%** |

The base overall score is the rounded weighted sum of category scores. To prevent a severe signal in one category from being diluted by unrelated zeroes, the final score applies a high-signal floor at 75% of the highest category score:

```text
weighted_score = round(sum(category_score × category_weight))
overall_score = max(weighted_score, round(0.75 × highest_category_score))
```

Risk levels are mapped as follows:

| Score | Level |
|---:|---|
| 0–24 | Low |
| 25–49 | Medium |
| 50–74 | High |
| 75–100 | Critical |

This is a triage heuristic for demonstration and education. A production system would require a validated evaluation set, domain-specific thresholds, calibration, abuse testing, monitoring, privacy review, and qualified human governance.

## Repository structure

```text
ai-risk-manager/
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── database/core.py
│   │   ├── models/analysis.py
│   │   ├── risk_engine/deterministic.py
│   │   ├── schemas/risk.py
│   │   ├── services/analyzer.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/test_risk_engine.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/App.jsx
│   ├── src/main.jsx
│   ├── src/services/api.js
│   ├── src/styles.css
│   ├── index.html
│   └── package.json
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## API documentation

The backend serves interactive OpenAPI documentation at `http://localhost:8000/docs` when running.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Returns service status, mode, and version. |
| `GET` | `/api/demos` | Returns sample scenarios for the dashboard. |
| `POST` | `/api/analyses` | Validates, analyzes, persists, and returns an assessment. |
| `GET` | `/api/analyses?limit=20` | Returns the latest history entries. |
| `GET` | `/api/analyses/{id}` | Returns a previously persisted assessment. |

Example request:

```bash
curl -X POST http://localhost:8000/api/analyses \
  -H 'Content-Type: application/json' \
  -d '{"input_text":"An AI assistant recommends denying a loan applicant because of their age and religion without evidence."}'
```

The response contains `overall_score`, `risk_level`, `summary`, category objects with `score`, `rationale`, and `signals`, prioritized `mitigations`, assumptions, and the selected engine name.

## Installation and local run

### 1. Clone or enter the repository

```bash
git clone <your-github-repository-url>
cd ai-risk-manager
```

### 2. Configure the environment

```bash
cp .env.example .env
```

The default `RISK_ENGINE_MODE=demo` runs locally without an API key. To try optional LLM mode, set `RISK_ENGINE_MODE=llm`, provide `OPENAI_API_KEY`, and optionally set `OPENAI_MODEL` or `OPENAI_BASE_URL`. Do not commit `.env`.

### 3. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Start the frontend in a second terminal

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend defaults to `http://localhost:8000/api`; set `VITE_API_URL` if the backend runs elsewhere.

### Docker Compose

From the repository root:

```bash
docker compose up --build
```

Then open `http://localhost:5173` and the API docs at `http://localhost:8000/docs`.

## Demo scenarios

The dashboard loads these examples automatically:

1. A loan approval assistant using age, religion, and neighborhood.
2. A suspicious refund decision involving a bank account and chargeback abuse.
3. A medical answer with incomplete records and an unsafe dosage.
4. A neutral public product-announcement summary.

Use them to show the difference between low-signal and high-signal triage while explaining that the result is a prototype heuristic.

## Testing

Run the backend tests from the backend directory:

```bash
cd backend
pytest -q
```

The tests cover safe-input behavior, multi-category detection, score boundaries, and high-risk security signals. A useful next step would be adding API contract tests and a labelled evaluation fixture for score calibration.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./risk_manager.db` | SQLAlchemy database URL. |
| `RISK_ENGINE_MODE` | `demo` | `demo` or `llm`; invalid values are rejected. |
| `OPENAI_API_KEY` | empty | Optional provider credential; never hardcoded. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Optional structured-output model name. |
| `OPENAI_BASE_URL` | empty | Optional OpenAI-compatible endpoint. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allow-list. |
| `MAX_INPUT_LENGTH` | `10000` | Documented input size limit. |
| `RATE_LIMIT_PER_MINUTE` | `30` | Per-client request limit. |
| `DEFAULT_USER_ID` | `demo-user` | Local demo partition key. |
| `VITE_API_URL` | `http://localhost:8000/api` | Frontend backend URL. |

## Security and privacy notes

The MVP stores the submitted text because it is needed for history. Do not paste real personal, financial, medical, authentication, or confidential company data. A production version should add authentication, tenant isolation, encrypted storage, retention and deletion controls, structured redaction, stronger rate limiting at the edge, audit-log integrity, dependency scanning, threat modeling, and a formal security review.

The optional LLM mode validates the returned JSON against a Pydantic schema and falls back to the deterministic engine if the provider fails. This prevents a provider outage from breaking the local demo, but it does not eliminate prompt injection, model bias, data leakage, or factuality risk.

## Limitations

The demo engine uses a small keyword rule set and therefore has false positives and false negatives. It does not understand context, verify external facts, infer intent reliably, or prove that a decision is compliant. Category scores are not statistically calibrated. The local demo has no authentication or multi-user authorization, and SQLite is not intended as the final store for a high-volume multi-tenant deployment.

## Future improvements

A strong next iteration would introduce a labelled risk benchmark, hybrid retrieval for evidence checks, policy packs per domain, subgroup fairness metrics, configurable approval gates, model and prompt versioning, analyst feedback loops, red-team test cases, immutable audit trails, role-based access control, and a review queue for unresolved high-impact cases.

## Interview explanation

> “I built Riskline as an offline-first AI Risk Manager MVP. It accepts an AI-assisted decision or generated output and scores seven risk categories with documented weights. Instead of hiding the result behind a single model label, it surfaces triggered signals, explains the score, and recommends a human review action. The backend is FastAPI with Pydantic validation and SQLite history, while the React dashboard makes the workflow demonstrable. I kept the deterministic engine as the default so the project is reproducible without an API key, and I isolated an optional structured-output LLM provider behind the same schema. I present it honestly as a triage prototype, not a certified compliance system.”

## Submission guide

See [`SUBMISSION_GUIDE.md`](./SUBMISSION_GUIDE.md) for Windows PowerShell Git commands, a public-repository checklist, concise Razorpay form answers, and a five-minute pitch outline and speaking script.

## GitHub commands

From the repository root:

```bash
git init
git add .
git commit -m "Build Riskline AI Risk Manager MVP"
git branch -M main
gh repo create ai-risk-manager --private --source=. --remote=origin --push
```

If the repository already exists on GitHub:

```bash
git remote add origin https://github.com/<your-username>/ai-risk-manager.git
git branch -M main
git push -u origin main
```

## References

[1]: https://fastapi.tiangolo.com/ "FastAPI documentation"
[2]: https://docs.pydantic.dev/latest/ "Pydantic documentation"
[3]: https://react.dev/ "React documentation"
[4]: https://vite.dev/guide/ "Vite documentation"
