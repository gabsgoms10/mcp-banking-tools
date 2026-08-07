# 🔌 mcp-banking-tools

> **FastMCP Python Server**: Model Context Protocol (MCP) server providing deterministic banking tools connected to PostgreSQL inside the K3s cluster.

---

## 🛠️ Provided FastMCP Tools

- **`get_account_balance(pix_key: str)`**: Fetches account details and balance in cents for a character (`Leo Vance`, `Maria Silva`, `Enterprise X Corp`).
- **`check_blocked_pix_key(pix_key: str)`**: Queries BACEN fraud registry (`blocked_pix_keys`) for malicious PIX keys (`fraudster@pix.com`).
- **`transfer_pix(origin_pix_key: str, destination_pix_key: str, amount_cents: int)`**: Executes atomic, deterministic transfers between accounts with audit logging.

---

## 🐳 Docker & GHCR Integration

This repository automatically builds and publishes multi-architecture Docker images (`linux/amd64`, `linux/arm64`) to **GitHub Container Registry (`ghcr.io`)** via `.github/workflows/docker-publish.yml`.
