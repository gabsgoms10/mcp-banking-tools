import logging
from typing import Any, Dict
from src.db import get_db_cursor

logger = logging.getLogger("mcp-banking-tools.tools")


def execute_get_account_balance(pix_key: str) -> Dict[str, Any]:
    """Retrieves account details and balance for a given PIX key or character name."""
    logger.info(f"Tool Invoked [get_account_balance]: key='{pix_key}'")
    try:
        with get_db_cursor() as (_, cur):
            cur.execute(
                "SELECT id, name, pix_key, balance_cents, risk_profile FROM characters WHERE pix_key = %s OR name ILIKE %s;",
                (pix_key, f"%{pix_key}%"),
            )
            account = cur.fetchone()

        if account:
            return {
                "status": "success",
                "account_id": account["id"],
                "name": account["name"],
                "pix_key": account["pix_key"],
                "balance_cents": account["balance_cents"],
                "balance_brl": account["balance_cents"] / 100.0,
                "risk_profile": account["risk_profile"],
            }
        return {"status": "error", "message": f"Account not found for PIX key: '{pix_key}'"}
    except Exception as err:
        logger.error(f"Failed to execute get_account_balance: {err}")
        return {"status": "error", "message": str(err)}


def execute_check_blocked_pix_key(pix_key: str) -> Dict[str, Any]:
    """Checks if a PIX key exists in the BACEN fraud registry (blocked_pix_keys)."""
    logger.info(f"Tool Invoked [check_blocked_pix_key]: key='{pix_key}'")
    try:
        with get_db_cursor() as (_, cur):
            cur.execute(
                "SELECT pix_key, reason, added_at FROM blocked_pix_keys WHERE pix_key = %s;",
                (pix_key,),
            )
            blocked = cur.fetchone()

        if blocked:
            return {
                "status": "blocked",
                "is_fraud": True,
                "pix_key": blocked["pix_key"],
                "reason": blocked["reason"],
                "added_at": str(blocked["added_at"]),
            }
        return {
            "status": "clean",
            "is_fraud": False,
            "pix_key": pix_key,
            "message": "PIX key is clear for transfer",
        }
    except Exception as err:
        logger.error(f"Failed to execute check_blocked_pix_key: {err}")
        return {"status": "error", "message": str(err)}


def execute_transfer_pix(origin_pix_key: str, destination_pix_key: str, amount_cents: int) -> Dict[str, Any]:
    """Executes an instant PIX transfer between accounts using integer cents."""
    logger.info(f"Tool Invoked [transfer_pix]: {amount_cents} cents from '{origin_pix_key}' to '{destination_pix_key}'")
    if amount_cents <= 0:
        return {"status": "error", "message": "Transfer amount_cents must be strictly greater than zero"}

    try:
        with get_db_cursor() as (conn, cur):
            # 1. Lock sender row for update
            cur.execute(
                "SELECT id, name, balance_cents FROM characters WHERE pix_key = %s OR name ILIKE %s FOR UPDATE;",
                (origin_pix_key, f"%{origin_pix_key}%"),
            )
            origin = cur.fetchone()

            if not origin:
                conn.rollback()
                return {"status": "error", "message": f"Sender account '{origin_pix_key}' not found"}

            if origin["balance_cents"] < amount_cents:
                conn.rollback()
                return {
                    "status": "error",
                    "message": f"Insufficient funds. Current balance: {origin['balance_cents']} cents, Requested: {amount_cents} cents",
                }

            # 2. Check BACEN Fraud Registry
            cur.execute("SELECT reason FROM blocked_pix_keys WHERE pix_key = %s;", (destination_pix_key,))
            blocked = cur.fetchone()

            if blocked:
                cur.execute(
                    "INSERT INTO transactions (origin_character_id, destination_key, amount_cents, status, decisive_rail, reason) VALUES (%s, %s, %s, 'BLOCKED', 'BACEN_FRAUD_LIST', %s);",
                    (origin["id"], destination_pix_key, amount_cents, f"Blocked key: {blocked['reason']}"),
                )
                conn.commit()
                return {
                    "status": "blocked",
                    "reason": f"Destination key '{destination_pix_key}' is blocked by BACEN fraud registry: {blocked['reason']}",
                }

            # 3. Perform atomic transfer
            cur.execute("UPDATE characters SET balance_cents = balance_cents - %s WHERE id = %s;", (amount_cents, origin["id"]))
            cur.execute("UPDATE characters SET balance_cents = balance_cents + %s WHERE pix_key = %s;", (amount_cents, destination_pix_key))

            cur.execute(
                "INSERT INTO transactions (origin_character_id, destination_key, amount_cents, status, decisive_rail, reason) VALUES (%s, %s, %s, 'APPROVED', 'EXECUTION_RAIL', 'Transaction executed successfully');",
                (origin["id"], destination_pix_key, amount_cents),
            )
            conn.commit()

            return {
                "status": "success",
                "message": f"Successfully transferred {amount_cents / 100.0:.2f} BRL to {destination_pix_key}",
                "amount_cents": amount_cents,
                "new_origin_balance_cents": origin["balance_cents"] - amount_cents,
            }
    except Exception as err:
        logger.error(f"Failed to execute transfer_pix: {err}")
        return {"status": "error", "message": str(err)}
