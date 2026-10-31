# Trust-Aware SOAR: Implementation Details

## 1. Modular Directory Organization

```
trust-aware-soar/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (auth, alerts, incidents, responses, etc.)
│   │   ├── core/            # Configuration and PBKDF2 / HS256 security
│   │   ├── database/        # SQLAlchemy session & seed initializers
│   │   ├── engines/         # The Six Core Research Engines
│   │   │   ├── response_reliability/
│   │   │   ├── policy_constraint/
│   │   │   ├── autonomy_trust/
│   │   │   ├── dynamic_autonomy/
│   │   │   ├── outcome_evaluation/
│   │   │   └── experience_memory/
│   │   ├── ml/              # Scikit-Learn Isolation Forest & feature extraction
│   │   ├── integrations/    # Ryu OpenFlow & Mock Network Adapter drivers
│   │   ├── models/          # Relational ORM models
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   ├── services/        # End-to-end incident orchestration service
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Automated Pytest integration suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, Sidebar, modals
│   │   ├── pages/           # 10 dedicated SOC views
│   │   ├── services/        # Strongly typed API client
│   │   ├── types/           # TypeScript data interfaces
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── network/                 # Mininet topologies & Ryu OpenFlow apps
├── attack_simulation/       # Controlled Scapy/Python attack generators
├── experiments/             # Automated research benchmarks & report generators
├── docs/                    # Architecture, API, and experimental documentation
└── ZERO_COST_COMPLIANCE.md  # FOSS zero-cost audit & verification
```

---

## 2. Six Core Research Engines Implementation Highlights

1. **Response Reliability Engine (`ResponseReliabilityEngine`):**
   Computes explainable, multi-factor reliability:
   $$\text{Reliability} = (0.25 \cdot C_{\text{threat}}) + (0.25 \cdot S_{\text{hist}}) + (0.20 \cdot P_{\text{fit}}) - (0.15 \cdot Q_{\text{risk}}) - (0.05 \cdot R_{\text{risk}}) - (0.10 \cdot U)$$
   Normalized to $[0.0, 1.0]$.

2. **Policy / Constraint Engine (`PolicyConstraintEngine`):**
   Enforces operational constraints: Asset criticality, QoS SLAs, and broadcast/gateway shield rules. Returns decisions (`ALLOW`, `REJECT`, `RESTRICT`, `ESCALATE`). **Mandatory safety rules always override high trust scores.**

3. **Autonomy Trust Engine (`AutonomyTrustEngine`):**
   Evaluates system self-trust by balancing response reliability and threat confidence against epistemic uncertainty and past failure penalties.

4. **Dynamic Autonomy Controller (`DynamicAutonomyController`):**
   Routes candidate actions to:
   - `ZERO_TOUCH`: Trust $\ge 0.85$ and Policy `ALLOW`
   - `GUARDED`: $0.55 \le \text{Trust} < 0.85$ or Policy `RESTRICT`
   - `HUMAN_APPROVAL`: Trust $< 0.55$ or Policy `ESCALATE / REJECT`

5. **Outcome Evaluation Engine (`OutcomeEvaluationEngine`):**
   Differentiates flow rule execution success from actual security response success. Assesses post-mitigation attack drops vs collateral QoS degradation.

6. **Experience Memory Engine (`ExperienceMemoryEngine`):**
   Stores empirical outcome records. Uses Case-Based Reasoning to adjust historical success rates and apply adaptation penalties to future similar incidents.

