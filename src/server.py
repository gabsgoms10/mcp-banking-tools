import logging

from fastmcp import FastMCP

from src.config import settings
from src.tools import (
    execute_check_blocked_pix_key,
    execute_get_account_balance,
    execute_transfer_pix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("mcp-banking-tools.server")

# FastMCP 1.2+ accepts only the server name in constructor
mcp = FastMCP("Banking-Tools")


@mcp.tool()
def get_account_balance(pix_key: str) -> dict:
    """Retrieves account details and balance (in cents) for a given PIX key or character name."""
    return execute_get_account_balance(pix_key)


@mcp.tool()
def check_blocked_pix_key(pix_key: str) -> dict:
    """Checks if a destination PIX key is flagged in the BACEN fraud registry (blocked_pix_keys)."""
    return execute_check_blocked_pix_key(pix_key)


@mcp.tool()
def transfer_pix(origin_pix_key: str, destination_pix_key: str, amount_cents: int) -> dict:
    """Executes an instant PIX transfer between accounts using integer cents."""
    return execute_transfer_pix(origin_pix_key, destination_pix_key, amount_cents)


if __name__ == "__main__":
    logger.info(
        f"Starting FastMCP Banking Tools Server on {settings.server_host}:{settings.server_port} (SSE mode)..."
    )
    # Pass host and port directly to run method
    mcp.run(transport="sse", host=settings.server_host, port=settings.server_port)
