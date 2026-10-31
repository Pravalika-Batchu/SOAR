# Trust-Aware SOAR Architecture Specification

## 1. System Overview & Multi-Layer Architecture

The Trust-Aware Security Orchestration, Automation, and Response (SOAR) framework extends traditional automation by evaluating not only whether a threat exists, but also whether candidate responses are reliable, policy-compliant, and safe to execute autonomously.

```mermaid
flowchart TB
    subgraph L1["Layer 1: Network & Ingestion Layer"]
        M1["Mininet SDN / Mock Network"]
        SUR["Suricata NIDS (EVE JSON)"]
        ZEEK["Zeek Network Monitor"]
        ING["Unified Ingestion Pipeline"]
        M1 --> SUR
        M1 --> ZEEK
        SUR --> ING
        ZEEK --> ING
    end

    subgraph L2["Layer 2: AI & Anomaly Detection"]
        FEAT["Feature Extraction Pipeline"]
        IFOREST["Isolation Forest Model (Local Scikit-Learn)"]
        ING --> FEAT
        FEAT --> IFOREST
    end

    subgraph L3["Layer 3: Six Core Research Engines"]
        direction TB
        CR1["1. Response Reliability Engine\n(Multi-factor scoring)"]
        CR2["2. Policy & Constraint Engine\n(Asset criticality & QoS safety)"]
        CR3["3. Autonomy Trust Engine\n(System self-trust: 0.0 to 1.0)"]
        CR4["4. Dynamic Autonomy Controller\n(Zero-Touch | Guarded | Human Approval)"]
        CR5["5. Outcome Evaluation Engine\n(Mitigation vs Collateral Impact)"]
        CR6["6. Experience Memory\n(Case-Based Feedback & Historical Weights)"]

        IFOREST --> CR1
        CR1 --> CR2
        CR2 --> CR3
        CR3 --> CR4
        CR4 --> CR5
        CR5 --> CR6
        CR6 -.->|"Adapt Future Reliability & Trust"| CR1
    end

    subgraph L4["Layer 4: Network Execution & SDN Enforcement"]
        ADAPT{"Network Adapter Interface"}
        RYU["Ryu OpenFlow Controller (Linux/WSL2)"]
        MOCK["High-Fidelity Mock Adapter (Windows)"]
        ADAPT --> RYU
        ADAPT --> MOCK
        CR4 -->|"Execute Approved Actions"| ADAPT
    end

    subgraph L5["Layer 5: Presentation & SOC Dashboard"]
        UI["React + TypeScript + Vite SOC Dashboard"]
        API["FastAPI REST & WebSocket Layer"]
        DB[("PostgreSQL / SQLite Storage")]
        API <--> DB
        UI <--> API
        L3 <--> API
    end
```

---

## 2. Six Core Research Engines & Decision Pipeline

The central research contribution lies in the interaction among the 6 modular engines:

```mermaid
sequenceDiagram
    autonumber
    participant INC as Incident Ingestion
    participant RRE as 1. Response Reliability Engine
    participant PCE as 2. Policy/Constraint Engine
    participant ATE as 3. Autonomy Trust Engine
    participant DAC as 4. Dynamic Autonomy Controller
    participant NET as Network Adapter (Ryu/Mock)
    participant OEE as 5. Outcome Evaluation Engine
    participant EXP as 6. Experience Memory

    INC->>RRE: Evaluates candidate responses (Block, Rate-Limit, Isolate)
    EXP->>RRE: Supplies historical success rates for similar incidents
    RRE->>PCE: Scores candidates & ranks by reliability
    PCE->>PCE: Checks asset criticality, service SLAs & QoS constraints
    PCE->>ATE: Decisions (ALLOW, REJECT, RESTRICT, ESCALATE)
    ATE->>ATE: Computes Autonomy Trust Score (0.0 - 1.0)
    ATE->>DAC: Passes trust score, uncertainties, and risk profile
    
    alt Trust >= 0.85 & Policy ALLOW
        DAC->>NET: Zero-Touch Automation (Immediate Execution)
    else 0.55 <= Trust < 0.85 or RESTRICT
        DAC->>NET: Guarded Automation (Time-limited, rate-limited, monitored)
    else Trust < 0.55 or ESCALATE
        DAC->>DAC: Pauses for Human Approval (SOC Analyst)
        Note over DAC: Analyst approves or rejects
        DAC->>NET: Executes on Analyst Approval
    end

    NET-->>OEE: Pre & Post network telemetry (loss, latency, throughput)
    OEE->>OEE: Evaluates actual mitigation vs collateral QoS degradation
    OEE->>EXP: Stores incident tuple, predicted vs actual outcome
    EXP->>EXP: Updates case memory & historical weights for future incidents
```

---

## 3. Mathematical Foundations

### Component 1: Response Reliability Score
$$\text{Reliability}(r) = w_1 \cdot C_{\text{threat}} + w_2 \cdot S_{\text{hist}}(r) + w_3 \cdot P_{\text{fit}}(r) - w_4 \cdot Q_{\text{risk}}(r) - w_5 \cdot R_{\text{risk}}(r) - w_6 \cdot U$$
Normalized to $[0, 1]$, where:
- $C_{\text{threat}}$: Threat detection confidence $[0, 1]$
- $S_{\text{hist}}$: Historical response success from Experience Memory $[0, 1]$
- $P_{\text{fit}}$: Policy compatibility score $[0, 1]$
- $Q_{\text{risk}}$: Predicted Quality-of-Service disruption risk $[0, 1]$
- $R_{\text{risk}}$: Infrastructure resource consumption risk $[0, 1]$
- $U$: Epistemic & statistical uncertainty $[0, 1]$
- Weights: $\sum_{i=1}^6 w_i = 1.0$ (configurable in settings)

### Component 3: Autonomy Trust Score
$$\text{Trust}(r) = \alpha \cdot \text{Reliability}(r) + \beta \cdot C_{\text{threat}} + \gamma \cdot (1 - Q_{\text{risk}}) - \delta \cdot U - \lambda \cdot F_{\text{hist}}$$
Where $F_{\text{hist}}$ is the historical failure/override penalty.

### Component 4: Autonomy Mode Selection
$$\text{Mode} = \begin{cases}
\text{ZERO\_TOUCH} & \text{if } \text{Trust} \ge \tau_{\text{high}} \text{ and Policy} = \text{ALLOW} \\
\text{GUARDED} & \text{if } \tau_{\text{low}} \le \text{Trust} < \tau_{\text{high}} \text{ or Policy} = \text{RESTRICT} \\
\text{HUMAN\_APPROVAL} & \text{if } \text{Trust} < \tau_{\text{low}} \text{ or Policy} \in \{\text{ESCALATE}, \text{REJECT}\}
\end{cases}$$
Default thresholds: $\tau_{\text{high}} = 0.85$, $\tau_{\text{low}} = 0.55$. Mandatory safety policies always strictly override trust scores.

---

## 4. Dual-Mode Network Execution Architecture

```mermaid
classDiagram
    class INetworkAdapter {
        <<interface>>
        +apply_block_rule(target_ip, duration_sec) bool
        +apply_rate_limit(target_ip, rate_kbps) bool
        +isolate_host(target_ip) bool
        +remove_rule(rule_id) bool
        +get_network_metrics() NetworkTelemetry
        +get_flow_table() List~FlowRule~
    }
    class RyuOpenFlowAdapter {
        -ryu_endpoint: str
        +apply_block_rule(target_ip, duration_sec)
        +apply_rate_limit(target_ip, rate_kbps)
        +isolate_host(target_ip)
        +remove_rule(rule_id)
        +get_network_metrics()
        +get_flow_table()
    }
    class MockNetworkAdapter {
        -flow_rules: Dict
        -active_mitigations: Dict
        -simulated_traffic: TrafficSimulator
        +apply_block_rule(target_ip, duration_sec)
        +apply_rate_limit(target_ip, rate_kbps)
        +isolate_host(target_ip)
        +remove_rule(rule_id)
        +get_network_metrics()
        +get_flow_table()
    }
    INetworkAdapter <|-- RyuOpenFlowAdapter
    INetworkAdapter <|-- MockNetworkAdapter
```

