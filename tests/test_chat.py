from src.services.chat import process_user_question
import asyncio
from unittest.mock import patch, MagicMock
from src.services.chat import validate_sql, generate_sql


def test_validate_sql_valid():
    assert validate_sql("SELECT * FROM transactions WHERE owner_id=1") is True


def test_validate_sql_invalid():
    assert validate_sql("DROP TABLE transactions;") is False
    assert validate_sql("delete from transactions where id=1;") is False
    assert validate_sql("UPDATE transactions SET amount=1;") is False
    assert validate_sql("INSERT INTO transactions VALUES (1);") is False
    assert validate_sql("ALTER TABLE transactions ADD COLUMN x INT;") is False
    assert validate_sql("TRUNCATE TABLE transactions;") is False
    assert validate_sql("select * from transactions; -- drop table") is False


@patch("src.services.chat.client.models.generate_content")
def test_generate_sql(mock_generate):
    # Setup mock
    mock_response = MagicMock()
    mock_response.text = (
        "```sql\n"
        "SELECT SUM(amount) FROM transactions "
        "WHERE category='Еда' AND owner_id=123;\n"
        "```"
    )
    mock_generate.return_value = mock_response

    # Call function
    sql = generate_sql("Сколько я потратил на еду?", 123)

    # Assertions
    assert "SELECT SUM(amount)" in sql
    assert "owner_id=123" in sql
    assert "```" not in sql  # Ensure markdown is stripped
    mock_generate.assert_called_once()


@patch("src.services.chat.generate_sql")
@patch("src.services.chat.client.models.generate_content")
def test_process_user_question(mock_generate_content, mock_generate_sql):
    mock_generate_sql.return_value = (
        "SELECT SUM(amount) FROM transactions WHERE owner_id=1;"
    )

    from unittest.mock import AsyncMock
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    # Mocking db_session.execute(text(sql)).fetchall() to return some fake data
    mock_result.fetchall.return_value = [(150.0,)]
    mock_db_session.execute.return_value = mock_result

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = "Вы потратили 150.0."
    mock_generate_content.return_value = mock_response

    answer = asyncio.run(
        process_user_question(
            "Сколько я потратил?",
            1,
            mock_db_session))

    assert answer == "Вы потратили 150.0."
    mock_db_session.execute.assert_called_once()
    mock_generate_content.assert_called_once()


@patch("src.services.chat.generate_sql")
def test_process_user_question_invalid_sql(mock_generate_sql):
    mock_generate_sql.return_value = "DROP TABLE transactions;"

    from unittest.mock import AsyncMock
    mock_db_session = AsyncMock()

    answer = asyncio.run(
        process_user_question(
            "Удали все",
            1,
            mock_db_session))

    assert answer == "Извините, не могу выполнить этот запрос."
    mock_db_session.execute.assert_not_called()


@patch("src.services.chat.client.models.generate_content")
def test_chat_history_context(mock_generate_content):
    from src.services.chat import _chat_history, process_user_question
    _chat_history.clear()

    from unittest.mock import AsyncMock, MagicMock
    mock_db_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(100.0,)]
    mock_db_session.execute.return_value = mock_result

    # First call: SQL generation -> Final answer
    # Second call: SQL generation -> Final answer
    mock_generate_content.side_effect = [
        MagicMock(
            text="```sql\nSELECT SUM(amount) FROM transactions;\n```"
        ),
        MagicMock(text="За август вы потратили 100."),
        MagicMock(
            text="```sql\nSELECT * FROM t WHERE id=1;\n```"
        ),
        MagicMock(text="На еду вы потратили 100.")
    ]

    ans1 = asyncio.run(
        process_user_question(
            "сколько за август?", 1, mock_db_session)
    )
    assert ans1 == "За август вы потратили 100."

    ans2 = asyncio.run(
        process_user_question(
            "на что?", 1, mock_db_session)
    )
    assert ans2 == "На еду вы потратили 100."

    assert 1 in _chat_history
    assert len(_chat_history[1]) == 4

    expected_q1 = {"role": "user", "content": "сколько за август?"}
    expected_a1 = {"role": "bot", "content": "За август вы потратили 100."}
    expected_q2 = {"role": "user", "content": "на что?"}
    expected_a2 = {"role": "bot", "content": "На еду вы потратили 100."}

    assert _chat_history[1][0] == expected_q1
    assert _chat_history[1][1] == expected_a1
    assert _chat_history[1][2] == expected_q2
    assert _chat_history[1][3] == expected_a2

    # Verify history is passed to generate_sql on the second call
    calls = mock_generate_content.call_args_list
    assert len(calls) == 4
    # The third call is generate_sql for the second question ("на что?")
    prompt_for_second_q = calls[2].kwargs['contents']
    assert "История предыдущих сообщений:" in prompt_for_second_q
    assert "User: сколько за август?" in prompt_for_second_q
    assert "Bot: За август вы потратили 100." in prompt_for_second_q


def test_chat_history_maxlen():
    from src.services.chat import get_chat_history, _chat_history
    _chat_history.clear()

    history = get_chat_history(2)
    for i in range(10):
        role = "user" if i % 2 == 0 else "bot"
        history.append({"role": role, "content": str(i)})

    assert len(history) == 6
    # The last 6 elements of 0-9 are 4, 5, 6, 7, 8, 9
    assert history[0]["content"] == "4"
    assert history[-1]["content"] == "9"
