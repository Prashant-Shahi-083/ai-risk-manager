# Razorpay Submission Guide — Riskline

## 1. Public GitHub upload commands — Windows PowerShell

Open PowerShell in the project folder and run the following commands. Replace only `YOUR_GITHUB_USERNAME` with your actual GitHub username.

```powershell
git init
git add .
git commit -m "Build Riskline AI Risk Manager MVP"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-risk-manager.git
git push -u origin main
```

If the GitHub repository has not been created yet, create a **public** repository named `ai-risk-manager` on GitHub first, without adding a README, `.gitignore`, or license there. The commands above assume that the local project is the source of truth. If a remote already exists locally, use `git remote -v` to inspect it and update it with `git remote set-url origin https://github.com/YOUR_GITHUB_USERNAME/ai-risk-manager.git`.

For a completely fresh local setup, these commands are safe after extracting the project archive:

```powershell
Set-Location .\ai-risk-manager
git init
git add .
git commit -m "Build Riskline AI Risk Manager MVP"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-risk-manager.git
git push -u origin main
```

## 2. GitHub upload checklist

### Upload these files

| Include | Items |
|---|---|
| Yes | `backend/` |
| Yes | `frontend/` |
| Yes | `backend/requirements.txt` |
| Yes | `frontend/package.json` and `frontend/package-lock.json` |
| Yes | `backend/tests/` |
| Yes | `README.md` |
| Yes | `.env.example` |
| Yes | `backend/Dockerfile` |
| Yes | `docker-compose.yml` |
| Yes | `.gitignore` |
| Yes | `SUBMISSION_GUIDE.md` |

### Do not upload these files or values

| Exclude | Reason |
|---|---|
| No | `.env` — local configuration and possible secrets |
| No | API keys, passwords, tokens, or credentials |
| No | `backend/.venv/` or any virtual environment |
| No | `frontend/node_modules/` |
| No | `__pycache__/`, `.pytest_cache/`, or other caches |
| No | `frontend/dist/` or other generated build output |
| No | `backend/risk_manager.db` — local demo data |

Before pushing, run `git status --short` and confirm that no forbidden path appears. The repository’s `.gitignore` already excludes these paths, and the committed source was scanned for secret-like values. `.env.example` contains placeholders only.

## 3. Razorpay AI internship form answers

These answers are intentionally concise and honest. Adjust the wording only if the form asks for a character limit or if you want to add your own personal details.

### Project Name

**Riskline — AI Risk Manager**

### Project Objectives

**To build a transparent decision-support prototype that analyzes AI-assisted decisions or generated outputs, scores privacy, security, financial/fraud, bias/fairness, hallucination/factuality, compliance, and safety risks, explains the signals behind the score, and recommends human-review mitigations. The MVP is designed to run offline in deterministic demo mode, while keeping an optional structured-output LLM provider modular for future evaluation.**

### GitHub Repository Description

**Offline-first AI risk triage MVP with FastAPI, React, SQLite, transparent weighted scoring, explainable signals, mitigation recommendations, analysis history, and optional schema-validated LLM analysis.**

### Suggested project link note, if the form has a comments field

**The repository includes a runnable README, FastAPI API documentation, React dashboard, deterministic demo scenarios, unit tests, Docker Compose configuration, responsible-AI limitations, and exact local run instructions.**

## 4. Five-minute pitch outline

| Time | Segment | What to demonstrate |
|---:|---|---|
| 0:00–0:30 | Introduction | State the project name and the internship track. |
| 0:30–1:00 | Problem | Explain why opaque AI-assisted decisions create review and accountability gaps. |
| 1:00–1:35 | Why it matters | Connect the problem to money, privacy, security, fairness, factuality, compliance, and safety. |
| 1:35–2:10 | Solution | Show the scenario input, score, risk level, explanations, and mitigation plan. |
| 2:10–2:40 | Architecture | Walk through React, FastAPI, Pydantic, modular analyzer service, risk engine, and SQLite. |
| 2:40–3:25 | Live demo | Run the loan-bias example, then a neutral-summary example, and reopen history. |
| 3:25–4:00 | Scoring | Explain seven category weights, capped category scores, weighted score, and high-signal floor. |
| 4:00–4:25 | Technical implementation | Mention validation, deterministic mode, optional schema-validated LLM mode, rate limiting, and tests. |
| 4:25–4:45 | Challenges | Discuss avoiding an opaque score, keeping the MVP offline-first, and preventing severe signals from being diluted. |
| 4:45–5:00 | Future and closing | State production improvements and end with the honest prototype boundary. |

## 5. Natural speaking script

### Introduction — 30 seconds

“Hello, I’m presenting Riskline, an AI Risk Manager MVP built for the AI Risk Manager track. The goal is simple: before an AI-assisted decision ships, make its potential risk signals visible and give a reviewer a practical next step. I designed this as a reproducible prototype rather than claiming that it is a certified compliance or safety system.”

### Problem and motivation — 65 seconds

“AI systems are increasingly used to support decisions involving customers, employees, money, and sensitive information. The problem is that a single model answer or confidence score does not tell an engineering or risk team what could go wrong. A decision can create privacy exposure, security abuse, financial loss, unfair treatment, unsupported factual claims, compliance issues, or even physical safety concerns. Riskline turns the free-form input into a structured triage result: an overall score, seven category scores, the signals that caused those scores, and prioritized mitigations.”

### Solution and live demo — 105 seconds

“On the dashboard, I can enter a scenario, prompt, or generated output. I’ll start with this loan approval example: the AI recommends denying an applicant because of age and religion without evidence. When I run it, Riskline identifies the bias and fairness signal, calculates the overall exposure, and recommends removing unnecessary sensitive attributes, measuring subgroup outcomes, and adding human review before an adverse decision.

“Now I’ll try the neutral product-announcement summary. This is intentionally low signal, and the result shows that no strong rule was triggered. That is important because the system does not equate every AI use with high risk. I can also click a previous history item to reopen the original input and its full assessment. The history is stored in SQLite so the demo has a basic audit-friendly workflow.”

### Architecture — 45 seconds

“The frontend is React with Vite and a responsive CSS dashboard. It calls a FastAPI backend through a small API service. FastAPI validates the request with Pydantic, sends the text to an analysis service, and persists the result through SQLAlchemy into SQLite. The analysis service isolates the provider choice. By default it uses the deterministic engine, so this project works without an API key. There is also an optional LLM path that asks for JSON, validates the response against the same Pydantic schema, and falls back to deterministic mode if the provider is unavailable.”

### Scoring explanation — 35 seconds

“The engine scores seven categories independently. Privacy, security, and financial or fraud risk each have a 16 percent weight. Bias and fairness and hallucination or factuality each have 14 percent. Compliance and safety each have 12 percent. The base score is the rounded weighted sum. I also apply a documented 75 percent floor of the highest category so that a severe signal in one category is not hidden by unrelated zeroes. The levels are Low, Medium, High, and Critical. The rule set is intentionally small and explainable, so the result is a triage heuristic rather than a calibrated model.”

### Technical choices and challenges — 45 seconds

“The main technical challenge was balancing usefulness with honesty. A black-box score would be difficult to debug or defend, so each rule returns a category, contribution, signal, rationale, and mitigation. I also added input length validation, CORS configuration, rate limiting, a responsible-AI disclaimer, unit tests, and a safe environment-variable pattern. The application can be run locally in demo mode, which makes evaluation reproducible and avoids requiring a reviewer to provide an API key.”

### Future improvements and closing — 35 seconds

“For a production version, I would add a labelled benchmark for calibration, domain-specific policy packs, evidence retrieval and fact checks, subgroup fairness metrics, a human review queue, authentication and tenant isolation, retention controls, immutable audit logs, and red-team evaluation. The current project does not claim to replace a risk professional. It demonstrates the core workflow: surface risk, explain why it was detected, and guide the next human review. That is the problem I wanted to make concrete with Riskline.”

## 6. Demo order before recording

Start the backend and frontend using the commands in `README.md`. Open the dashboard, click **Loan approval assistant**, run the analysis, point out the category breakdown and mitigation owner, then click **Medical answer** or **Suspicious refund decision** to show a different risk profile. Finish by clicking the neutral summary and reopening one history item. Avoid using real personal data in the recording.
