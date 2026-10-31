# Trust-Aware SOAR for Adaptive Cybersecurity Response and Dynamic Autonomy

An academic major project and research-grade Security Orchestration, Automation, and Response (SOAR) framework featuring **explainable Response Reliability scoring**, **Policy & Constraint enforcement**, **Autonomy Trust evaluation**, **Dynamic Autonomy control (Zero-Touch, Guarded, Human Approval)**, **Outcome-based Telemetry Evaluation**, and **Experience-Based Feedback Learning**.

Developed with **100% Free and Open-Source Software (FOSS) at ₹0 / $0 cost**.

---

## Key Research Contributions

1. **Response Reliability Evaluation:** Prevents the naive assumption that the most aggressive security action is always the best. Balances threat confidence, historical success, policy fit, QoS disruption risk, and uncertainty.
2. **Policy / Constraint Overrides:** Mandatory safety guardrails protect critical assets (e.g., Core DNS, Web Portals, Database clusters) from catastrophic autonomous disruption. Mandatory policies strictly override trust scores.
3. **Autonomy Trust Engine:** Quantifies the system's self-trust in executing responses autonomously (0.0 to 1.0) while incorporating epistemic uncertainty and past operator overrides.
4. **Dynamic Autonomy Controller:** Selects among three execution modes:
   - **Zero-Touch Automation:** Trust $\ge 0.85$ and Policy ALLOW.
   - **Guarded Automation:** $0.55 \le \text{Trust} < 0.85$ or Policy RESTRICT (rate-limited, reversible, time-bounded).
   - **Human Approval:** Trust $< 0.55$ or Policy ESCALATE / REJECT.
5. **Outcome Evaluation:** Differentiates rule installation success from actual security response success by comparing pre vs post attack velocity against collateral QoS degradation.
6. **Experience Memory:** Case-Based Reasoning index that stores prior incident decisions and empirical results to dynamically adapt future reliability and trust weights.

---

## Technology Stack (100% Free & Open-Source)

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React
- **Machine Learning:** Scikit-Learn (Isolation Forest local anomaly detection)
- **Database:** SQLite (embedded zero-install persistent DB) & PostgreSQL compatible
- **Network & SDN:** OpenFlow 1.3, Mininet (Linux/WSL2), Ryu Controller, and High-Fidelity Mock Network Adapter (Windows native)
- **Monitoring & Metrics:** Prometheus scrape exporter, Grafana OSS dashboard configs

---

## Quick Start Guide (Windows / Linux)

### 1. Run the FastAPI Backend
```powershell
# Set PYTHONPATH to include backend
$env:PYTHONPATH="backend"

# Run FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Documentation (Swagger): `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### 2. Run the React SOC Dashboard
```powershell
cd frontend
npm run dev
```
- Dashboard Interface: `http://localhost:5173`

### 3. Run Automated Tests
```powershell
$env:PYTHONPATH="backend"
pytest backend/tests/ -v
```
All unit tests and end-to-end integration tests pass with 100% success.

### 4. Run Reproducible Research Experiments
```powershell
python experiments/run_experiments.py
```
Outputs:
- `experiments/results/evaluation_metrics.json`
- `experiments/results/evaluation_metrics.csv`
- `experiments/reports/research_findings.md`

---

## SOC Dashboard Views

The frontend includes 10 dedicated operational views:
1. **Overview Dashboard:** Total alerts, active threats, pending approvals, autonomy distribution, recent incidents, and live QoS metrics.
2. **Security Monitoring:** Suricata EVE alerts, Zeek flow metadata, raw payload inspectors, and severity filters.
3. **Incident Lifecycle:** Complete end-to-end workflow tracing detection, ML anomaly assessment, candidate scoring, policy checks, trust calculation, and execution.
4. **Reliability Comparison:** Multi-factor comparative bar charts of candidate responses.
5. **Human Approval Center:** Human-in-the-loop review queue with audit notes and confirmation safeguards.
6. **Autonomy Monitoring:** Time-series tracking of dynamic system self-trust, factor contributions, and penalties.
7. **Outcome Evaluation:** Empirical pre vs post execution telemetry charts (attack reduction vs collateral QoS drop).
8. **Experience Memory:** Case-Based Reasoning history with dynamic adaptation penalty indicators.
9. **Policy Management:** Configuration of critical asset rules, QoS SLA thresholds, and mandatory overrides.
10. **Network Topology:** Visualization of Mininet switches (`s1`, `s2`), host attachments, and asset status.

---

## Zero-Cost Compliance Verification
See [ZERO_COST_COMPLIANCE.md](ZERO_COST_COMPLIANCE.md) for the complete dependency audit verifying $0 spend, permissive open-source licenses, and zero paid API dependencies.

