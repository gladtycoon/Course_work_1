import json
import math
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
json_path = BASE_DIR / "user_settings.json"

API_KEY = os.getenv("API_KEY")


def request_currency_data():
    """Функция для получения котировок валют"""
    # Читаем json-файл с валютами
    try:
        with open(json_path, "r", encoding="utf-8") as json_file:
            settings = json.load(json_file)
    except FileNotFoundError:
        print(f"Файл настроек не найден: {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка в JSON файле: {e}")
        return []

    # Проверяем наличие ключа user_currencies
    user_currencies = settings.get("user_currencies", [])
    if not user_currencies:
        print("Список валют пуст")
        return []

    # API-запрос для получения курсов всех валют
    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    try:
        response = requests.get(url, timeout=10)

        # Проверяем статус ответа
        if response.status_code != 200:
            print(f"API вернул код ошибки: {response.status_code}")
            return []

        data = response.json()

    except requests.exceptions.Timeout:
        print("Таймаут при запросе к API")
        return []
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения к API")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка при обработке JSON: {e}")
        return []

    # Формирование списка с курсами валют согласно user_settings
    currency_rates = []

    for currency_code in user_currencies:
        try:
            currency_rate = data["Valute"][currency_code]["Value"]
            currency_rates.append(
                {"currency": currency_code, "rate": round(float(currency_rate), 2)}
            )
        except KeyError:
            print(f"Валюта {currency_code} не найдена, пропускаем")

    # Если список валют не пустой, но результат пуст — выводим сообщение
    if user_currencies and not currency_rates:
        print("Не удалось получить курсы валют")

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
