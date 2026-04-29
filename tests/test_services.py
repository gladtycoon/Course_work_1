import pandas as pd

from src.services import increased_cashback


def test_increased_cashback_success(sample_dataframe):
    """Тест: успешный расчёт кэшбэка за январь 2021"""
    result = increased_cashback(sample_dataframe, 2021, 1)

    # Превращаем Series в словарь
    result_dict = result.to_dict()

    expected = {"Супермаркеты": -1500, "Транспорт": -300, "Рестораны": -1000}

    assert result_dict == expected


def test_increased_cashback_no_data_for_month(sample_dataframe):
    """Тест: нет данных за указанный месяц"""
    result = increased_cashback(sample_dataframe, 2021, 6)
    assert result == {}


def test_increased_cashback_empty_dataframe():
    """Тест: пустой датафрейм"""
    empty_df = pd.DataFrame()
    result = increased_cashback(empty_df, 2021, 1)
    assert result == {}


def test_increased_cashback_none_dataframe():
    """Тест: None вместо датафрейма"""
    result = increased_cashback(None, 2021, 1)
    assert result == {}
