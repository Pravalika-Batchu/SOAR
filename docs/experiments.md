# Experimental Scenarios & Research Evaluation Guide

## 1. Experimental Objectives
Traditional SOAR architectures suffer from two extremes:
1. **Unconstrained Static Automation:** Executes blunt playbooks (e.g. host isolation) regardless of collateral damage to critical assets.
2. **Exhaustive Manual Review:** Creates severe analyst fatigue and introduces intolerable human response delays during high-volume attacks.

This research prototype evaluates whether the **Trust-Aware SOAR** can safely balance speed and precision across 5 distinct threat scenarios.

---

## 2. Experimental Scenarios

### Scenario 1: High-Rate DoS SYN Flood
- **Simulated Traffic:** 2,500 packets/sec TCP SYN flood from attacker `10.0.0.99` targeting critical Web Server `10.0.0.10`.
- **Baseline A (Fixed Automation):** Blindly isolated the entire web server host. Result: Attacker blocked, but legitimate client traffic suffered 100% outage.
- **Proposed (Trust-Aware):** Policy Engine flagged `10.0.0.10` as a `CRITICAL` asset with strict QoS sensitivity. Proposed System rejected host isolation and dynamically selected **Guarded Rate-Limiting** (`250 kbps`).
- **Outcome:** 96.2% attack reduction with only 3.5% legitimate throughput impact.

### Scenario 2: Distributed Port Scanning
- **Simulated Traffic:** Rapid multi-port SYN sweep from `10.0.0.99` against corporate workstation `10.0.0.101`.
- **Proposed (Trust-Aware):** High threat confidence (92%), low target criticality (`LOW`), and zero QoS collateral risk resulted in an Autonomy Trust score of **89.5%**. Routed to **Zero-Touch Automation**. Immediate OpenFlow flow rule installed in 12 ms without requiring human analyst intervention.

### Scenario 3: Brute-Force Authentication Activity
- **Simulated Traffic:** Repeated SSH connection attempts against database cluster `10.0.0.20`.
- **Proposed (Trust-Aware):** Selected **Guarded Automation** with time-limited IP blocking (300 seconds) and automatic rollback expiration.

### Scenario 4: Unknown / Out-of-Distribution Network Anomaly
- **Simulated Traffic:** High-entropy UDP packet velocity deviations unseen during normal training.
- **Proposed (Trust-Aware):** Isolation Forest flagged boundary ambiguity; uncertainty calculated at **52.0%**. Autonomy Governor policy strictly overrode autonomy, forcing routing to **Human Approval Center**.

### Scenario 5: QoS-Sensitive Traffic on Core Infrastructure
- **Simulated Traffic:** Flooding targeting core DNS resolver `10.0.0.53` during high legitimate DNS query traffic.
- **Proposed (Trust-Aware):** Mandatory safety policy prevented broad isolation. System requested explicit SOC confirmation with non-disruptive rate-limiting alternatives.

---

## 3. How to Reproduce All Experiments

Run the reproducible benchmark runner locally:
```bash
python experiments/run_experiments.py
```
This script executes all 5 scenarios against the 3 architectural baselines, verifies outputs against policy constraints, and regenerates:
- `experiments/results/evaluation_metrics.json`
- `experiments/results/evaluation_metrics.csv`
- `experiments/reports/research_findings.md`

