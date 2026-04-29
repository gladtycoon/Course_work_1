import pytest

from src.views import get_greeting_by_time


@pytest.mark.parametrize(
    "time_str, expected",
    [
        ("2025-04-10 00:00:00", "Доброй ночи"),
        ("2025-04-10 06:00:00", "Доброе утро"),
        ("2025-04-10 12:00:00", "Добрый день"),
        ("2025-04-10 18:00:00", "Добрый вечер"),
    ],
)
def test_greeting_by_hour(time_str, expected):
    assert get_greeting_by_time(time_str) == expected


@pytest.mark.parametrize(
    "invalid_input",
    [
        "2025/04/10 15:30:00",
        "10-04-2025 15:30:00",
        "2025-04-10 25:00:00",
        "2025-04-10 15:30",
        "2025-04-10",
        "не дата",
        "",  # пустая строка
    ],
)
def test_invalid_input_returns_error(invalid_input):
    assert get_greeting_by_time(invalid_input) == "Ошибка формата даты"
