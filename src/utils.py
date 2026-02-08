import math
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import DataFrame


def get_greeting_by_time(user_input_date: str) -> str:
    """Принимает строку с датой и возвращает приветствие"""
    try:
        user_date_obj = datetime.strptime(user_input_date, "%Y-%m-%d %H:%M:%S")
        hour = user_date_obj.hour

        if 0 <= hour < 6:
            return "Доброй ночи"
        elif 6 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 18:
            return "Добрый день"
        else:
            return "Добрый вечер"
    except ValueError:
        return "Ошибка формата даты"


def read_card_data_from_excel(file_path) -> DataFrame|None:
    """Чтение данных из Excel файла"""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def process_card_data(df: DataFrame) -> list[dict]:
    """Анализ данных по картам"""
    if df is None or df.empty:
        return []

    filtered_df = df[df["Сумма операции"] < 0]
    if filtered_df.empty:
        return []

    grouped_df = filtered_df.groupby("Номер карты")
    result_series = grouped_df["Сумма операции"].sum().abs()
    cards_list = []
    for card_number, total_price in result_series.items():
        card_number_str = str(card_number)
        cards_list.append(
            {
                "last_digits": (
                    card_number_str[-4:]
                    if len(card_number_str) >= 4
                    else card_number_str
                ),
                "total_spent": round(total_price, 2),
                "cashback": math.floor(total_price / 100),  # округляем вниз
            }
        )
    return cards_list


def get_top_transactions(df: DataFrame, n: int = 5) -> list[dict]:
    """ Функция приминает DataFrame и n и возвращает топ-5 транзакций по сумме платежа """
    if df is None or df.empty:
        return []

    filtered_df = df[df["Сумма операции"] < 0].copy()
    if filtered_df.empty:
        return []

    filtered_df['max_amount'] = filtered_df["Сумма операции"].abs()
    top_transactions = filtered_df.nlargest(n, 'max_amount')
    result = []
    for index, row in top_transactions.iterrows():
        result.append({
            "date": str(row.get("Дата операции", "")),
            "amount": abs(row["Сумма операции"]),
            "category": str(row.get("Категория", "")),
            "description": str(row.get("Описание", ""))
        })
    return result

# 2026-02-07 17:00:00