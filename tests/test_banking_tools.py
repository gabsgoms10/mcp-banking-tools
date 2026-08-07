from unittest.mock import MagicMock, patch

from src.tools import execute_get_account_balance, execute_transfer_pix


@patch("src.tools.get_db_cursor")
def test_get_account_balance_success(mock_get_db_cursor):
    """Test get_account_balance returns account info when user exists."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = {
        "id": 1,
        "name": "Leo Vance",
        "pix_key": "leo.vance@pix.com",
        "balance_cents": 250000,
        "risk_profile": "STANDARD",
    }
    mock_get_db_cursor.return_value.__enter__.return_value = (mock_conn, mock_cur)

    res = execute_get_account_balance("leo.vance@pix.com")
    assert res["status"] == "success"
    assert res["name"] == "Leo Vance"
    assert res["balance_cents"] == 250000
    assert res["balance_brl"] == 2500.0


def test_transfer_pix_invalid_amount():
    """Test transfer_pix rejects negative or zero amounts immediately."""
    res = execute_transfer_pix("leo.vance@pix.com", "maria.silva@pix.com", 0)
    assert res["status"] == "error"
    assert "greater than zero" in res["message"]
