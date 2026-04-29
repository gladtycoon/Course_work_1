import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (
    get_top_transactions,
    process_card_data,
    read_card_data_from_excel,
    request_currency_data,
)


def test_request_currency_data_success(mock_json_data, mock_api_valute_response):
    mock_json_content = json.dumps(mock_json_data)

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        with patch("requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_valute_response

            result = request_currency_data()

    expected = [
        {"currency": "USD", "rate": 80.0},
        {"currency": "EUR", "rate": 90.0},
        {"currency": "GBP", "rate": 100.0},
    ]
    assert result == expected


def test_request_currency_data_missing_currency(
    mock_json_data, mock_api_valute_response
):
    modified_api_response = {
        "Valute": {"USD": {"Value": 80.0}, "GBP": {"Value": 100.0}}
    }

    mock_json_content = json.dumps(mock_json_data)

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        with patch("requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = modified_api_response

            result = request_currency_data()

    expected = [{"currency": "USD", "rate": 80.0}, {"currency": "GBP", "rate": 100.0}]
    assert result == expected


def test_request_currency_data_empty_currencies():
    mock_json_data = {"user_currencies": []}
    mock_json_content = json.dumps(mock_json_data)

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        with patch("requests.get") as mock_get:
            result = request_currency_data()

    assert result == []


# ========== ТЕСТЫ ДЛЯ read_card_data_from_excel ==========


def test_read_excel_success():
    """Успешное чтение Excel"""
    mock_df = pd.DataFrame({"col1": [1, 2]})

    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = mock_df
        result = read_card_data_from_excel(Path("test.xlsx"))

        assert result is not None
        assert not result.empty
        assert len(result) == 2


def test_read_excel_file_not_found():
    """Файл не найден"""
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        result = read_card_data_from_excel(Path("nonexistent.xlsx"))

        assert result is None


def test_read_excel_general_error():
    """Общая ошибка при чтении"""
    with patch("pandas.read_excel", side_effect=Exception("Unknown error")):
        result = read_card_data_from_excel(Path("bad.xlsx"))

        assert result is None


def test_read_excel_empty_file():
    """Пустой Excel файл"""
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = pd.DataFrame()
        result = read_card_data_from_excel(Path("empty.xlsx"))

        assert result.empty


# ========== ТЕСТЫ ДЛЯ process_card_data ==========
def test_process_card_data_success(sample_transactions_df):
    """Успешная обработка данных по картам"""
    result = process_card_data(sample_transactions_df)

    expected = [
        {"last_digits": "3456", "total_spent": 1800.0, "cashback": 18},
        {"last_digits": "4321", "total_spent": 2000.0, "cashback": 20},
    ]
    assert result == expected


def test_process_card_data_empty_df(empty_df):
    """Пустой датафрейм"""
    result = process_card_data(empty_df)
    assert result == []


def test_process_card_data_none_df():
    """None вместо датафрейма"""
    result = process_card_data(None)
    assert result == []


def test_process_card_data_only_income():
    """Только доходы (нет отрицательных сумм)"""
    df = pd.DataFrame(
        {
            "Номер карты": ["1234567890123456", "1234567890123456"],
            "Сумма операции": [5000, 3000],
            "Категория": ["Пополнение", "Пополнение"],
        }
    )

    result = process_card_data(df)
    assert result == []


def test_process_card_data_short_card_number():
    """Короткий номер карты"""
    df = pd.DataFrame(
        {
            "Номер карты": ["1234"],
            "Сумма операции": [-500],
            "Категория": ["Супермаркеты"],
        }
    )

    result = process_card_data(df)

    # Должен вернуть весь номер, так как он короче 4 символов
    assert result[0]["last_digits"] == "1234"
    assert result[0]["total_spent"] == 500.0
    assert result[0]["cashback"] == 5


def test_process_card_data_rounding():
    """Проверка округления кэшбэка вниз"""
    df = pd.DataFrame(
        {
            "Номер карты": ["1234567890123456"],
            "Сумма операции": [-150],  # 150/100 = 1.5 → floor = 1
            "Категория": ["Супермаркеты"],
        }
    )

    result = process_card_data(df)
    assert result[0]["cashback"] == 1


# ========== ТЕСТЫ ДЛЯ get_top_transactions ==========


@pytest.fixture
def sample_transactions_for_top():
    return pd.DataFrame(
        {
            "Дата операции": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
                "2024-01-06",
            ],
            "Сумма операции": [
                -1500,
                -300,
                -2000,
                -100,
                -5000,
                1000,
            ],  # последний положительный
            "Категория": [
                "Супермаркеты",
                "Транспорт",
                "Супермаркеты",
                "Кафе",
                "Электроника",
                "Пополнение",
            ],
            "Описание": ["Продукты", "Метро", "Ашан", "Кофе", "Телефон", "Зарплата"],
        }
    )


def test_get_top_transactions_success(sample_transactions_for_top):
    """Успешное получение топ-5 транзакций"""
    result = get_top_transactions(sample_transactions_for_top, 3)

    expected = [
        {
            "date": "2024-01-05",
            "amount": 5000.0,
            "category": "Электроника",
            "description": "Телефон",
        },
        {
            "date": "2024-01-03",
            "amount": 2000.0,
            "category": "Супермаркеты",
            "description": "Ашан",
        },
        {
            "date": "2024-01-01",
            "amount": 1500.0,
            "category": "Супермаркеты",
            "description": "Продукты",
        },
    ]
    assert result == expected


def test_get_top_transactions_default_n(sample_transactions_for_top):
    """Проверка значения n по умолчанию (5)"""
    result = get_top_transactions(sample_transactions_for_top)

    # Должно вернуть 5 транзакций (все расходы)
    assert len(result) == 5
    assert result[0]["amount"] == 5000.0
    assert result[4]["amount"] == 100.0


def test_get_top_transactions_empty_df(empty_df):
    """Пустой датафрейм"""
    result = get_top_transactions(empty_df)
    assert result == []


def test_get_top_transactions_none_df():
    """None вместо датафрейма"""
    result = get_top_transactions(None)
    assert result == []


def test_get_top_transactions_no_expenses():
    """Нет расходов (только доходы)"""
    df = pd.DataFrame(
        {
            "Дата операции": ["2024-01-01", "2024-01-02"],
            "Сумма операции": [5000, 3000],
            "Категория": ["Зарплата", "Зарплата"],
            "Описание": ["Доход", "Доход"],
        }
    )

    result = get_top_transactions(df, 5)
    assert result == []


def test_get_top_transactions_less_than_n():
    """Расходов меньше, чем n"""
    df = pd.DataFrame(
        {
            "Дата операции": ["2024-01-01", "2024-01-02"],
            "Сумма операции": [-500, -300],
            "Категория": ["Супермаркет", "Транспорт"],
            "Описание": ["Продукты", "Метро"],
        }
    )

    result = get_top_transactions(df, 5)
    assert len(result) == 2
    assert result[0]["amount"] == 500.0
    assert result[1]["amount"] == 300.0
