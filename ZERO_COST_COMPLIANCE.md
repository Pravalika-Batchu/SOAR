# Zero-Cost Compliance Audit & Verification

## 1. Compliance Statement
This project strictly complies with the **Zero-Cost Requirement (₹0 / $0 spend)**. 
Every component, library, runtime, framework, dataset, and monitoring tool utilized in this research project is free and open-source software (FOSS) or freely available without paid tiers, subscriptions, credit cards, or external cloud API costs.

---

## 2. Dependency Audit & License Verification

| Component / Dependency | Category | License | Purpose in Project | Cost Status | Verification Method |
|---|---|---|---|---|---|
| **Python 3.10+** | Runtime | PSF License | Core backend and ML execution | Free ($0) | Open-source runtime |
| **FastAPI** | Backend Framework | MIT | REST API engine, dependency injection, async I/O | Free ($0) | Open-source package |
| **Uvicorn** | ASGI Server | BSD 3-Clause | Asynchronous HTTP server for FastAPI | Free ($0) | Open-source package |
| **Pydantic v2** | Data Validation | MIT | Data models, request/response schema validation | Free ($0) | Open-source package |
| **SQLAlchemy 2.0** | Database ORM | MIT | Relational mapping, query abstraction, connection pooling | Free ($0) | Open-source package |
| **SQLite** | Database | Public Domain | Zero-configuration local persistent database | Free ($0) | Embedded public domain engine |
| **PostgreSQL** | Database | PostgreSQL License | High-performance production relational DB (optional local) | Free ($0) | Open-source community edition |
| **Scikit-learn** | Machine Learning | BSD 3-Clause | Isolation Forest anomaly detection & metrics | Free ($0) | Open-source package |
| **NumPy & Pandas** | Data Processing | BSD 3-Clause | Vectorized metric calculation & dataset processing | Free ($0) | Open-source package |
| **React 18** | Frontend Framework | MIT | Declarative component UI | Free ($0) | Open-source library |
| **TypeScript** | Frontend Language | Apache 2.0 | Type safety across API models and UI components | Free ($0) | Open-source language |
| **Vite** | Build Tool | MIT | Frontend development server and bundle optimization | Free ($0) | Open-source tooling |
| **Tailwind CSS** | Styling | MIT | Utility-first responsive SOC design system | Free ($0) | Open-source utility |
| **Recharts** | Visualization | MIT | Reactive charts for QoS, trust scores, and telemetry | Free ($0) | Open-source package |
| **Lucide React** | Icons | ISC | SOC and security status iconography | Free ($0) | Open-source icon set |
| **Suricata (Ingestion & EVE format)** | Security IDS/IPS | GPLv2 | Intrusion alert format and packet inspection | Free ($0) | Open-source NIDS |
| **Zeek (Ingestion & TSV/JSON)** | Network Analysis | BSD 3-Clause | Network metadata, flow and connection log analysis | Free ($0) | Open-source framework |
| **Mininet & OpenFlow** | SDN Simulation | BSD 3-Clause | Virtual software-defined network testbed | Free ($0) | Open-source SDN emulator |
| **Ryu SDN Controller** | Network Controller | Apache 2.0 | Dynamic OpenFlow rule installation & flow management | Free ($0) | Open-source SDN controller |
| **Scapy & iPerf3** | Traffic & Testing | GPLv2 / BSD | Controlled packet crafting and throughput benchmarking | Free ($0) | Open-source network tools |
| **Pytest & HTTPX** | Testing | MIT / BSD | Automated unit, integration, and API testing | Free ($0) | Open-source testing libraries |
| **Prometheus** | Metrics Engine | Apache 2.0 | Time-series telemetry and operational metrics | Free ($0) | Open-source monitoring |
| **Grafana OSS** | Dashboarding | AGPLv3 | Open-source monitoring dashboard | Free ($0) | Open-source community edition |

---

## 3. Disallowed Technologies Audit
The following technologies are strictly **EXCLUDED**:
- ❌ OpenAI API (Paid inference)
- ❌ Google Gemini API / Claude API (Commercial cloud inference)
- ❌ AWS / Azure / GCP Cloud Services (Pay-as-you-go infrastructure)
- ❌ Paid SaaS SIEM/SOAR platforms (Splunk Enterprise, Palo Alto Cortex XSOAR, etc.)
- ❌ Paid Threat Intelligence feeds (Recorded Future, VirusTotal Enterprise, etc.)

---

## 4. Local Execution & Fallback Architecture
- **Decision Engine & AI:** 100% locally implemented in pure Python using mathematical scoring formulas and local Scikit-Learn Isolation Forest models.
- **Database Fallback:** Direct SQLite file persistence with zero installation barriers, with complete SQLAlchemy compatibility for PostgreSQL.
- **SDN Execution:** Dual-mode architecture offering native Ryu/Mininet execution for Linux/WSL2 environments, paired with an exact mock network flow-table simulation adapter for Windows.

