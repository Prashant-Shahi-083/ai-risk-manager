import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, ArrowUpRight, CheckCircle2, Clock3, FileSearch, History, LoaderCircle, ShieldCheck, Sparkles, X } from "lucide-react";
import { createAnalysis, fetchAnalysis, fetchDemos, fetchHistory } from "./services/api";
import "./styles.css";

const categoryLabels = {
  privacy: "Privacy",
  security: "Security",
  financial_fraud: "Financial / fraud",
  bias_fairness: "Bias / fairness",
  hallucination_factuality: "Hallucination / factuality",
  compliance: "Compliance",
  safety: "Safety",
};

const initialText = "An AI assistant recommends denying a loan applicant because of their age, religion, and neighborhood, without showing evidence.";

function formatDate(value) {
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function levelClass(level) {
  return level.toLowerCase();
}

function ScoreRing({ score }) {
  const angle = Math.max(0, Math.min(360, score * 3.6));
  return (
    <div className="score-ring" style={{ "--score-angle": `${angle}deg` }}>
      <div className="score-ring-inner">
        <span className="score-value">{score}</span>
        <span className="score-label">/ 100</span>
      </div>
    </div>
  );
}

function CategoryRow({ name, item }) {
  return (
    <div className="category-row">
      <div className="category-heading">
        <span>{categoryLabels[name] || name}</span>
        <strong>{item.score}</strong>
      </div>
      <div className="progress-track"><div className={`progress-fill ${item.score >= 70 ? "danger" : item.score >= 40 ? "warn" : "safe"}`} style={{ width: `${item.score}%` }} /></div>
      <p>{item.rationale}</p>
    </div>
  );
}

export default function App() {
  const [input, setInput] = useState(initialText);
  const [assessment, setAssessment] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const [history, setHistory] = useState([]);
  const [demos, setDemos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([fetchHistory(), fetchDemos()])
      .then(([historyData, demoData]) => { setHistory(historyData); setDemos(demoData); })
      .catch(() => setError("Backend is not reachable. Start FastAPI on port 8000 and refresh."));
  }, []);

  const activeCount = useMemo(() => history.filter((item) => item.risk_level === "High" || item.risk_level === "Critical").length, [history]);

  async function handleAnalyze(event) {
    event.preventDefault();
    if (input.trim().length < 10) { setError("Enter at least 10 characters for a meaningful analysis."); return; }
    setError(""); setIsLoading(true); setSelectedHistory(null);
    try {
      const result = await createAnalysis(input);
      setAssessment(result.assessment); setAnalysisId(result.id);
      setHistory(await fetchHistory());
    } catch (err) { setError(err.message || "Analysis failed. Please try again."); }
    finally { setIsLoading(false); }
  }

  async function openHistory(item) {
    try {
      const result = await fetchAnalysis(item.id);
      setInput(result.input_text); setAssessment(result.assessment); setAnalysisId(result.id); setSelectedHistory(item.id);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) { setError("Could not load that analysis."); }
  }

  function selectDemo(demo) { setInput(demo.text); setError(""); window.scrollTo({ top: 0, behavior: "smooth" }); }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><ShieldCheck size={18} /></div><div><span className="brand-name">Riskline</span><span className="brand-subtitle">AI RISK MANAGER</span></div></div>
        <div className="topbar-right"><span className="status-dot" /> <span>DEMO ENGINE ONLINE</span><span className="version">v1.0</span></div>
      </header>

      <main className="content">
        <section className="hero-row">
          <div><p className="eyebrow">DECISION SUPPORT PROTOTYPE <span>•</span> AI RISK MANAGER</p><h1>Make risky decisions<br /><em>visible before they ship.</em></h1><p className="hero-copy">Analyze an AI-assisted decision, surface hidden risk signals, and turn uncertainty into an actionable review plan.</p></div>
          <div className="hero-meta"><div className="meta-item"><span className="meta-number">{history.length.toString().padStart(2, "0")}</span><span>analyses<br />logged</span></div><div className="meta-item accent"><span className="meta-number">{activeCount.toString().padStart(2, "0")}</span><span>high-risk<br />flags</span></div></div>
        </section>

        <section className="workspace-grid">
          <div className="panel input-panel">
            <div className="panel-kicker"><span className="step-number">01</span><span>SUBMIT A SCENARIO</span><span className="panel-rule" /></div>
            <div className="form-heading"><div><h2>What should we inspect?</h2><p>Paste a prompt, decision, or AI-generated output. Avoid real personal data.</p></div><FileSearch size={24} strokeWidth={1.5} /></div>
            <form onSubmit={handleAnalyze}>
              <textarea value={input} onChange={(event) => setInput(event.target.value)} maxLength={10000} placeholder="Describe the AI-assisted scenario..." />
              <div className="input-footer"><span>{input.length.toLocaleString()} / 10,000 characters</span><button className="primary-button" disabled={isLoading}>{isLoading ? <><LoaderCircle className="spin" size={16} /> ANALYZING</> : <><Sparkles size={16} /> RUN ANALYSIS <ArrowUpRight size={16} /></>}</button></div>
            </form>
            {error && <div className="error-message"><AlertTriangle size={16} /> {error}</div>}
            <div className="demo-strip"><span className="demo-title">TRY A DEMO</span>{demos.map((demo) => <button key={demo.id} className="demo-chip" onClick={() => selectDemo(demo)}>{demo.title}</button>)}</div>
          </div>

          <div className="panel result-panel">
            <div className="panel-kicker"><span className="step-number">02</span><span>RISK ASSESSMENT</span><span className="panel-rule" /></div>
            {!assessment ? <div className="empty-state"><div className="empty-icon"><ShieldCheck size={28} /></div><h3>Awaiting a scenario</h3><p>Your assessment will appear here with a transparent score, category breakdown, and mitigation plan.</p></div> : <>
              <div className="score-summary"><ScoreRing score={assessment.overall_score} /><div><span className={`level-badge ${levelClass(assessment.risk_level)}`}>{assessment.risk_level.toUpperCase()} RISK</span><h2>Overall exposure</h2><p>{assessment.summary}</p><span className="engine-tag">{assessment.engine === "llm" ? "LLM + schema validated" : "Deterministic demo engine"} <span>•</span> Analysis #{analysisId}</span></div></div>
              <div className="section-divider" />
              <div className="subsection-heading"><h3>Category breakdown</h3><span>Weighted signal scores</span></div>
              <div className="category-list">{Object.entries(assessment.categories).map(([name, item]) => <CategoryRow key={name} name={name} item={item} />)}</div>
              <div className="section-divider" />
              <div className="subsection-heading"><h3>Recommended mitigations</h3><span>{assessment.mitigations.length} actions</span></div>
              <div className="mitigation-list">{assessment.mitigations.map((mitigation, index) => <div className="mitigation" key={`${mitigation.action}-${index}`}><div className={`priority-dot ${mitigation.priority.toLowerCase()}`} /><div><div className="mitigation-topline"><strong>{mitigation.priority} priority</strong><span>{mitigation.owner}</span></div><p>{mitigation.action}</p></div></div>)}</div>
              <div className="disclaimer"><AlertTriangle size={15} /><span><strong>Prototype boundary.</strong> This is a decision-support prototype, not legal, compliance, safety, or financial advice. Validate high-impact decisions with qualified reviewers.</span></div>
            </>}
          </div>
        </section>

        <section className="lower-grid">
          <div className="panel history-panel"><div className="panel-kicker"><span className="step-number">03</span><span>ANALYSIS HISTORY</span><span className="panel-rule" /><History size={17} /></div>{history.length === 0 ? <div className="small-empty">No analyses yet. Run your first scenario above.</div> : <div className="history-list">{history.map((item) => <button className={`history-item ${selectedHistory === item.id ? "selected" : ""}`} key={item.id} onClick={() => openHistory(item)}><div className={`history-score ${levelClass(item.risk_level)}`}>{item.overall_score}</div><div className="history-copy"><strong>{item.input_preview}</strong><span><Clock3 size={13} /> {formatDate(item.created_at)}</span></div><span className={`history-level ${levelClass(item.risk_level)}`}>{item.risk_level}</span><ArrowUpRight size={16} /></button>)}</div>}</div>
          <div className="panel method-panel"><div className="panel-kicker"><span className="step-number">04</span><span>HOW THE SCORE WORKS</span><span className="panel-rule" /></div><h2>Transparent by design.</h2><p>The demo engine combines seven independently scored risk categories using documented weights. Every result includes the triggered signals and a suggested human review action.</p><div className="weight-grid">{Object.entries(categoryLabels).map(([key, label]) => <div className="weight-item" key={key}><span>{label}</span><strong>{Math.round(({privacy:.16,security:.16,financial_fraud:.16,bias_fairness:.14,hallucination_factuality:.14,compliance:.12,safety:.12}[key])*100)}%</strong></div>)}</div><div className="method-note"><CheckCircle2 size={16} /> <span>Offline-first: runs without an API key.</span></div></div>
        </section>
      </main>
      <footer><span>RISKLINE / AI RISK MANAGER</span><span>Built as a responsible-AI internship MVP <span className="footer-dot">•</span> No sensitive data required</span></footer>
    </div>
  );
}
