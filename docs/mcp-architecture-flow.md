# 🔌 FastMCP Architecture & Execution Flow Specification
## Repository: `mcp-banking-tools`

This document details the internal design, connection pooling mechanism, and transaction isolation sequence of the FastMCP Banking Server.

---

## 🔄 1. Sequence Diagram: Tool Execution & Database Guarding

```mermaid
sequenceDiagram
    autonumber
    participant Agent as NeMo Guardrails / Agent
    participant MCP as mcp-banking-tools (FastMCP SSE)
    participant Pool as ThreadedConnectionPool
    participant DB as PostgreSQL (K3s Pod)

    Agent->>MCP: SSE HTTP POST /tools/transfer_pix (origin, dest, amount_cents)
    MCP->>Pool: Acquire DB Connection from Pool
    Pool-->>MCP: Connection & RealDictCursor Ready
    
    MCP->>DB: BEGIN TRANSACTION; SELECT balance_cents FROM characters FOR UPDATE;
    DB-->>MCP: Lock Acquired & Current Balance Returned
    
    alt Insufficient Funds or Invalid Amount
        MCP->>DB: ROLLBACK;
        MCP-->>Agent: { status: "error", message: "Insufficient funds" }
    else Valid Transaction & Account Exists
        MCP->>DB: SELECT reason FROM blocked_pix_keys WHERE pix_key = dest;
        alt Destination Key Flagged in BACEN Fraud Registry
            MCP->>DB: INSERT INTO transactions (status='BLOCKED', rail='BACEN_FRAUD_LIST'); COMMIT;
            MCP-->>Agent: { status: "blocked", reason: "BACEN Fraud Registry Flag" }
        else Clean Destination Key
            MCP->>DB: UPDATE characters SET balance_cents = balance_cents - amount WHERE origin;
            MCP->>DB: UPDATE characters SET balance_cents = balance_cents + amount WHERE dest;
            MCP->>DB: INSERT INTO transactions (status='APPROVED', rail='EXECUTION_RAIL'); COMMIT;
            MCP-->>Agent: { status: "success", new_origin_balance_cents: N }
        end
    end
    
    MCP->>Pool: Release Connection back to Pool
```

---

## 🔒 2. Concurrency & Race Condition Safeguards

1. **Row Locking (`FOR UPDATE`)**:
   When `transfer_pix` is invoked, PostgreSQL locks the sender's row in the `characters` table for update. This prevents race conditions if multiple concurrent LLM agent loops attempt to transfer funds simultaneously.

2. **Integer Monetary Precision (`amount_cents: int`)**:
   All monetary amounts are passed and stored as 64-bit integers representing cents (`$10.50` = `1050`). Floating-point arithmetic is strictly prohibited to guarantee exact mathematical balance integrity.

3. **Database Connection Pooling (`ThreadedConnectionPool`)**:
   Instead of creating a new TCP connection on every tool call (which causes socket exhaustion under high load), `src/db.py` uses a thread-safe connection pool (`minconn=1, maxconn=10`) with context manager release semantics.
