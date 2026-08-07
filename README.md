# 🔌 mcp-banking-tools

> **Deterministic Financial Tooling Microservice**: High-performance, production-grade Model Context Protocol (MCP) server built with **FastMCP Python (SSE Mode)**, **Threaded Database Connection Pooling**, **Bandit SAST Security Scanning**, and **Pytest Unit Testing**, containerized and published to **GitHub Container Registry (`ghcr.io`)**.

---

## 🎯 Executive Summary & Architectural Purpose

In autonomous AI agent systems, granting language models direct database access or relying on probabilistic text instructions is a catastrophic security risk. 

`mcp-banking-tools` acts as the **isolated deterministic execution bridge** between AI Agents (via NVIDIA NeMo Guardrails) and the core financial ledger (PostgreSQL). Every action is encapsulated within type-safe, auditable tools enforcing strict integer-cents monetary precision (`amount_cents: int`).

---

## 🏛️ Strategic Architecture & DevSecOps Matrix

```text
                                 [ Kubernetes Cluster (K3s) ]
                                 
  +-----------------------+      SSE (HTTP :8001)      +---------------------------------+
  |  NVIDIA NeMo Server   |  ----------------------->  |  mcp-banking-tools (FastMCP)    |
  |  / Agentic Framework  |                            |  - Threaded Connection Pool     |
  +-----------------------+                            +---------------------------------+
                                                                       |
                                                                       | SQL (TCP :5432)
                                                                       v
                                                       +---------------------------------+
                                                       |  PostgreSQL 16 Alpine           |
                                                       |  - characters (balances)        |
                                                       |  - blocked_pix_keys (BACEN)     |
                                                       |  - transactions (audit ledger)  |
                                                       +---------------------------------+
```

### 🛡️ Quality & DevSecOps Pipeline
Every push to `main` triggers a 2-stage GitHub Actions pipeline enforcing enterprise standards:

| Tooling Layer | Technology | Engineering Guarantee |
|---|---|---|
| **Linter & Formatter** | **Ruff** & **Black** | 100% PEP 8 compliant, ultra-fast Python code formatting. |
| **Static Type Checker** | **Mypy** | Enforces strict static typing on all tool parameters. |
| **SAST Security Scanner** | **Bandit** | Scans for SQL injection risks, hardcoded credentials, and unsafe sockets. |
| **Automated Unit Tests** | **Pytest** + **pytest-mock** | Validates tool logic, balance checks, and transaction edge cases. |
| **Container Registry** | **GHCR (`ghcr.io`)** | Multi-architecture builds (`linux/amd64`, `linux/arm64`) pushed to GitHub Container Registry. |

---

## 🛠️ Provided FastMCP Tools Registry

### 1. `get_account_balance(pix_key: str)`
- **Description**: Fetches real-time account balances (in cents and BRL) and risk profiles for test characters (`Leo Vance`, `Maria Silva`, `Enterprise X Corp`).
- **Return Contract**: `{ "status": "success", "name": str, "pix_key": str, "balance_cents": int, "balance_brl": float, "risk_profile": str }`

### 2. `check_blocked_pix_key(pix_key: str)`
- **Description**: Queries the BACEN (Central Bank of Brazil) fraud registry table (`blocked_pix_keys`) for malicious PIX keys (`fraudster@pix.com`).
- **Return Contract**: `{ "status": "blocked" | "clean", "is_fraud": bool, "pix_key": str, "reason": str }`

### 3. `transfer_pix(origin_pix_key: str, destination_pix_key: str, amount_cents: int)`
- **Description**: Executes an atomic, thread-safe PIX financial transfer between accounts.
- **Financial Precision**: Enforces integer cents (`amount_cents: int`) to eliminate floating-point IEEE 754 rounding vulnerabilities. Applies `FOR UPDATE` row locking in PostgreSQL to prevent race conditions.

---

## 📖 Auxiliary Technical Documentation
- 📄 **[FastMCP Execution & Sequence Flow Specification](./docs/mcp-architecture-flow.md)**

---

## 🚀 Local Development & Testing

```bash
# 1. Install dependencies & quality tools
pip install -r requirements.txt

# 2. Run code quality checks
ruff check src/ tests/
black --check src/ tests/
mypy src/
bandit -r src/

# 3. Run unit tests
pytest -v tests/

# 4. Start FastMCP Server locally (SSE mode)
python -m src.server
```
