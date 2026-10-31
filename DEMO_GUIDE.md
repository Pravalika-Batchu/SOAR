# Trust-Aware SOAR: Dynamic Real-Time Demonstration Guide

## 1. Project Overview
This project demonstrates an adaptive **Security Orchestration, Automation, and Response (SOAR)** system incorporating dynamic autonomy and multi-factor trust evaluation.

Instead of statically hardcoding responses or alerts, the system continuously runs a **Network Traffic Simulation Engine** (`network_simulator.py`) that generates live telemetry, synthesizes benign background traffic, models attack spikes, and executes the complete SOAR decision lifecycle.

---

## 2. Real vs. Simulated Components Architecture

For academic integrity and technical defense:

| Subsystem | Mode / Implementation | Description |
|-----------|------------------------|-------------|
| **Response Reliability Engine** | **REAL (Deterministic Multi-Criteria)** | Mathematical model balancing threat confidence, QoS safety, history, and policy constraints |
| **Policy Constraint Engine** | **REAL (Enforcement)** | Hard security policies, QoS sensitivity guardrails, mandatory operator overrides |
| **Autonomy Trust Engine** | **REAL (Scoring)** | Multi-factor trust computation determining Zero-Touch vs. Guarded vs. Human Approval |
| **Dynamic Autonomy Controller**| **REAL (State Engine)** | Enforces HTTP 403 authorization boundary on sensitive or QoS-critical assets |
| **Experience Memory (CBR)** | **REAL (Persistent DB + Adaptive Index)** | Historical case-based reasoning updating adaptation penalties and failure weights |
| **Machine Learning Detection** | **REAL (Isolation Forest)** | Local scikit-learn Isolation Forest model estimating anomaly scores and boundary uncertainty |
| **Network Telemetry & Traffic** | **SIMULATED (Realistic Local Testbed)** | Emulated telemetry streams (throughput, pps, latency, jitter, packet loss) modeling SDN switch datapath metrics |
| **SDN OpenFlow Adapter** | **DUAL-MODE (Mock + Ryu OpenFlow)** | Simulated mock adapter for zero-cost standalone execution, with plug-and-play Ryu REST client support |

---

## 3. How to Run the Demonstration

### Step 1: Start Backend Server
```powershell
cd backend
.\venv\Scripts\Activate
uvicorn app.main:app --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Simulation automatically starts in the background and logs telemetry cycles every 5 seconds.

### Step 2: Start Frontend Application
In a separate terminal:
```powershell
cd frontend
npm run dev
```
- Open your browser at `http://localhost:5173` (or the port Vite provides).

---

## 4. Key Demonstration Scenarios

### Scenario A: Real-Time Network Simulation (`Simulation Control` Tab)
1. In the sidebar, select **Simulation Control**.
2. Notice the live time-series chart showing simulated network throughput, packet rates, and switch latency updating every 4 seconds.
3. Observe the engine status (Running / Stopped, cycle count, alerts generated).

### Scenario B: Triggering an Attack & Observing Incident Creation
1. Click **Trigger Attack Scenario** (e.g., `DoS SYN Flood` or `Port Scan`).
2. Telemetry will spike (high packets/second, latency increase, throughput drop).
3. The system generates a `SecurityAlert` (labeled `[SIMULATION]`) and links it to an `Incident`.
4. The frontend will navigate to the incident and show the real ML-evaluated anomaly score and uncertainty.

### Scenario C: QoS-Sensitive Critical Asset Protection (Human-in-the-Loop)
1. Select the **QoS Sensitive** trigger in the top navbar or trigger a DNS flood on `10.0.0.53`.
2. Notice that despite high detection confidence, the **Policy Constraint Engine** flags the DNS Resolver (`qos_sensitivity = 0.95`).
3. The candidate actions will be placed into `HUMAN_APPROVAL` mode.
4. Navigate to **Human Approval**:
   - The pending approval card appears with rich incident metadata and escalation rationale.
   - Direct execution without approval is blocked by the backend (HTTP 403).
   - Approving the request authorizes execution, records audit logs, updates post-telemetry, and stores experience memory.

---

## 5. Running the Test Suite
All backend tests can be verified using pytest:
```powershell
cd backend
.\venv\Scripts\python -m pytest tests -v
```
Output: **23 passed tests** covering APIs, policy constraints, trust scoring, human approval workflows, and simulation engines.

