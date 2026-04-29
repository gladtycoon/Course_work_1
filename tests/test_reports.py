from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd

from src.reports import (
    increased_cashback_report,
    increased_cashback_report_named,
    read_card_data_from_excel,
    report_to_file,
)

# ========== ТЕСТЫ ДЛЯ read_card_data_from_excel ==========


def test_read_excel_success():
    """Успешное чтение Excel"""
    mock_df = pd.DataFrame({"col": [1, 2]})

    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = mock_df
        result = read_card_data_from_excel(Path("test.xlsx"))

        assert not result.empty
        assert len(result) == 2


def test_read_excel_error():
    """Ошибка при чтении Excel"""
    with patch("pandas.read_excel", side_effect=Exception("Ошибка")):
        result = read_card_data_from_excel(Path("nonexistent.xlsx"))

        assert result.empty


def test_read_excel_empty():
    """Пустой Excel файл"""
    with patch("pandas.read_excel") as mock_read:
        mock_read.return_value = pd.DataFrame()
        result = read_card_data_from_excel(Path("empty.xlsx"))

        assert result.empty


# ========== ТЕСТЫ ДЛЯ increased_cashback_report ==========


def test_cashback_report_success(sample_df):
    """Успешный расчёт кэшбэка"""
    with patch("src.reports.report_to_file", lambda *args, **kwargs: lambda f: f):
        result = increased_cashback_report(sample_df, 2021, 1)

    expected = {"Супермаркеты": 1500, "Транспорт": 300, "Рестораны": 1000}
    assert result == expected


def test_cashback_report_no_data(sample_df):
    """Нет данных за месяц"""
    with patch("src.reports.report_to_file", lambda *args, **kwargs: lambda f: f):
        result = increased_cashback_report(sample_df, 2021, 6)

    assert result == {}


def test_cashback_report_empty_df(empty_df):
    """Пустой датафрейм"""
    with patch("src.reports.report_to_file", lambda *args, **kwargs: lambda f: f):
        result = increased_cashback_report(empty_df, 2021, 1)

    assert result == {}


def test_cashback_report_none_df():
    """None вместо датафрейма"""
    with patch("src.reports.report_to_file", lambda *args, **kwargs: lambda f: f):
        result = increased_cashback_report(None, 2021, 1)

    assert result == {}


# ========== ТЕСТЫ ДЛЯ increased_cashback_report_named ==========


def test_cashback_report_named_success(sample_df):
    """Успешный расчёт с указанным именем"""
    with patch("src.reports.report_to_file", lambda *args, **kwargs: lambda f: f):
        result = increased_cashback_report_named(sample_df, 2021, 1)

    expected = {"Супермаркеты": 1500, "Транспорт": 300, "Рестораны": 1000}
    assert result == expected


def test_cashback_report_named_no_data(sample_df):
    """Нет данных за месяц"""
    with patch("src.reports.report_to_file", lambda *args, **kwargs: lambda f: f):
        result = increased_cashback_report_named(sample_df, 2021, 6)

    assert result == {}


# ========== ТЕСТЫ ДЛЯ ДЕКОРАТОРА ==========


def test_decorator_auto_filename():
    """Декоратор: автоматическое имя файла"""

    @report_to_file()
    def test_func():
        return {"status": "ok"}

    with patch("builtins.open", mock_open()) as mock_file:
        with patch("src.reports.datetime") as mock_dt:
            mock_dt.now.return_value.strftime.return_value = "2026-04-30_12-00-00"
            with patch("pathlib.Path.mkdir"):
                result = test_func()

    assert result == {"status": "ok"}

    # Проверяем имя файла
    call_args = mock_file.call_args[0][0]
    assert "report_2026-04-30_12-00-00.json" in str(call_args)


def test_decorator_custom_filename():
    """Декоратор: указанное имя файла"""

    @report_to_file("custom.json")
    def test_func():
        return {"status": "ok"}

    with patch("builtins.open", mock_open()) as mock_file:
        with patch("pathlib.Path.mkdir"):
            result = test_func()

    assert result == {"status": "ok"}

    # Проверяем имя файла
    call_args = mock_file.call_args[0][0]
    assert "custom.json" in str(call_args)


def test_decorator_with_list():
    """Декоратор: сохраняет список"""

    @report_to_file("list.json")
    def test_func():
        return [1, 2, 3]

    with patch("builtins.open", mock_open()) as mock_file:
        with patch("pathlib.Path.mkdir"):
            result = test_func()

    assert result == [1, 2, 3]


def test_decorator_with_dataframe():
    """Декоратор: сохраняет DataFrame"""
    df = pd.DataFrame({"a": [1, 2]})

    @report_to_file("df.json")
    def test_func():
        return df

    with patch("builtins.open", mock_open()) as mock_file:
        with patch("pathlib.Path.mkdir"):
            result = test_func()

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
