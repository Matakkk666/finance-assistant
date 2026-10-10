import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, User


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.text = "/sync"
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
@patch("src.bot.handlers.get_owner_id", return_value=123)
@patch("src.bot.handlers.sync_user_bank")
async def test_bot_sync_handler(mock_sync, mock_get_owner, mock_message):
    mock_sync.return_value = {
        "fetched": 5,
        "new": 2,
        "categories": {"Food": 1, "Transport": 1},
    }

    # once we write it. Let's assume we name it `cmd_sync`.
    from src.bot.handlers import cmd_sync

    await cmd_sync(mock_message)

    # Check if sync_user_bank was called
    mock_sync.assert_called_once()

    # In my handler I'll probably do answer("...") and edit_text("...")
    assert mock_message.answer.call_count >= 1

    # Also test with args e.g. "/sync tbank"
    mock_message.text = "/sync tbank"
    await cmd_sync(mock_message)
    assert mock_sync.call_count == 2
