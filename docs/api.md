# Trust-Aware SOAR: REST API Documentation

The FastAPI backend exposes an interactive OpenAPI Swagger UI at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## 1. Authentication Endpoints

### `POST /api/auth/login`
Authenticates a user via PBKDF2-HMAC password verification and returns an HS256 JWT bearer token.
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "adminpassword123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "role": "ADMIN",
    "username": "admin"
  }
  ```

### `GET /api/auth/me`
Returns current user profile.

---

## 2. Ingestion & Security Alerts

### `POST /api/alerts`
Ingests an alert from Suricata, Zeek, or test generator. Automatically links or creates an active incident.
- **Request Body:**
  ```json
  {
    "source": "SURICATA",
    "alert_type": "DOS_SYN_FLOOD",
    "severity": "HIGH",
    "source_ip": "10.0.0.99",
    "destination_ip": "10.0.0.10",
    "destination_port": 80,
    "protocol": "TCP",
    "signature": "ET DOS Possible SYN Flood"
  }
  ```

### `GET /api/alerts`
Returns recent ingested alerts with filtering by `severity` and `source`.

---

## 3. Incident Lifecycle Pipeline

### `GET /api/incidents`
Lists all security incidents.

### `GET /api/incidents/{id}`
Returns details for a specific incident.

### `POST /api/incidents/{id}/analyze`
**Stage 1:** Runs feature extraction and local Scikit-Learn Isolation Forest anomaly detection. Computes normalized anomaly score, boundary uncertainty, and composite threat confidence.

### `POST /api/incidents/{id}/evaluate-responses`
**Stage 2:** Generates candidate responses (`BLOCK_IP`, `RATE_LIMIT`, `ISOLATE_HOST`), retrieves case history from Experience Memory, calculates Response Reliability scores (Engine 1), enforces Policy/Constraint rules (Engine 2), computes Autonomy Trust scores (Engine 3), and assigns execution modes (Engine 4).

### `POST /api/incidents/{id}/execute`
**Stage 3:** Enforces response action through SDN Network Adapter (Ryu or Mock). Strict verification that human approval was granted if required. Triggers post-execution telemetry and Outcome Evaluation (Engine 5). Updates Experience Memory (Engine 6).

---

## 4. Human Approval Center

### `GET /api/approvals/pending`
Returns queue of responses requiring human analyst approval.

### `POST /api/approvals/{id}/approve`
Approves a pending response with operator audit notes.

### `POST /api/approvals/{id}/reject`
Rejects a proposed response and halts autonomous execution.

---

## 5. Trust, Outcomes & Experience Memory

### `GET /api/trust/history`
Returns time-series logs of dynamic self-trust adjustments and factor penalties.

### `GET /api/outcomes`
Returns evaluations comparing predicted vs actual attack reduction and collateral QoS degradation.

### `GET /api/experience`
Queries Case-Based Reasoning records of previous incident outcomes.

---

## 6. System & Telemetry

### `GET /api/system/status`
Returns live system health, database mode, and active network adapter (`MOCK` vs `RYU`).

### `GET /api/system/topology`
Returns SDN switches, virtual hosts, and monitored asset inventory.

### `GET /api/metrics/summary`
Telemetry feed for SOC dashboard and Prometheus monitoring.

