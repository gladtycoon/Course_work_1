import math, json, requests, os
from dotenv import load_dotenv
from pathlib import Path

import pandas as pd
from pandas import DataFrame

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
json_path = BASE_DIR / "user_settings.json"

API_KEY = os.getenv("API_KEY")


def request_currency_data():
    """Функция для получения котировок валют"""
    """ Читаем json-файл с валютами """
    with open(json_path, "r", encoding="utf-8") as json_file:
        settings = json.load(json_file)

    """ API-запрос для получения курсов всех валют """
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    data = response.json()

    """ Формирование словаря с курсами валют согласно user_settings """
    currency_rates = []
    index_currency = 0
    len_list_of_currencies = len(settings["user_currencies"])
    while index_currency < len_list_of_currencies:
        currency_code = settings["user_currencies"][index_currency]
        try:
            currency_rate = data["Valute"][settings["user_currencies"][index_currency]][
                "Value"
            ]
            currency_rates.append(
                {"currency": currency_code, "rate": round(float(currency_rate), 2)}
            )
        except KeyError:
            print(f"Валюта {currency_code} не найдена, пропускаем")
        index_currency += 1
    return currency_rates


def request_stocks_data():
    """Функция для получения котировок акций"""
    """ Читаем json-файл с акциями """
    with open(json_path, "r", encoding="utf-8") as json_file:
        settings = json.load(json_file)

    """ Формирование словаря с курсами валют согласно user_settings """
    stocks_code = ", ".join(settings["user_stocks"])
    # Параметры запроса
    params = {
        "interval": "1day",
        "symbol": stocks_code,
        "apikey": API_KEY,
        "outputsize": 1,
    }
    """ API-запрос для получения курсов заданных акций """
    url = "https://api.twelvedata.com/time_series"
    response = requests.get(url, params=params)
    data = response.json()
    result = []
    for k, v in data.items():
        result.append(
            {"stock": k, "price": round(float(v.get("values")[0].get("open")), 2)}
        )
    return result


def read_card_data_from_excel(file_path) -> DataFrame | None:
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
    """Функция приминает DataFrame и n и возвращает топ-5 транзакций по сумме платежа"""
    if df is None or df.empty:
        return []

    filtered_df = df[df["Сумма операции"] < 0].copy()
    if filtered_df.empty:
        return []

    filtered_df["max_amount"] = filtered_df["Сумма операции"].abs()
    top_transactions = filtered_df.nlargest(n, "max_amount")
    result = []
    for index, row in top_transactions.iterrows():
        result.append(
            {
                "date": str(row.get("Дата операции", "")),
                "amount": abs(row["Сумма операции"]),
                "category": str(row.get("Категория", "")),
                "description": str(row.get("Описание", "")),
            }
        )
    return result


# 2026-02-07 17:00:00
