import requests
import json, os
from pathlib import Path
from dotenv import load_dotenv
from pandas.core.computation.common import result_type_many

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
json_path = BASE_DIR / "user_settings.json"

API_KEY = os.getenv("API_KEY")


def request_currency_data():
    """ Функция для получения котировок валют """
    """ Читаем json-файл с валютами """
    with open(json_path, 'r', encoding='utf-8') as json_file:
        settings = json.load(json_file)

    """ API-запрос для получения курсов всех валют """
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    data = response.json()

    """ Формирование словаря с курсами валют согласно user_settings """
    currency_rates = []
    index_currency = 0
    len_list_of_currencies = len(settings['user_currencies'])
    while index_currency < len_list_of_currencies:
        currency_code = settings['user_currencies'][index_currency]
        try:
            currency_rate = data['Valute'][settings['user_currencies'][index_currency]]['Value']
            currency_rates.append({"currency": currency_code, "rate": round(float(currency_rate), 2)})
        except KeyError:
            print(f"Валюта {currency_code} не найдена, пропускаем")
        index_currency += 1
    return currency_rates


def request_stocks_data():
    """ Функция для получения котировок акций """
    """ Читаем json-файл с акциями """
    with open(json_path, 'r', encoding='utf-8') as json_file:
        settings = json.load(json_file)

    """ Формирование словаря с курсами валют согласно user_settings """
    stocks_code = ", ".join(settings['user_stocks'])
    # Параметры запроса
    params = {
        "interval": "1day",
        "symbol": stocks_code,
        "apikey": API_KEY,
        "outputsize": 1
    }
    url = "https://api.twelvedata.com/time_series"
    response = requests.get(url, params=params)
    data = response.json()
    result = []
    for k, v in data.items():
        result.append({"stock": k, "price": round(float(v.get("values")[0].get("open")), 2)})
    return result


if __name__ == "__main__":
    print(request_stocks_data())
    #stocks_result = request_stocks_data()


# {'AAPL': {'meta': {'symbol': 'AAPL', 'interval': '1day',
# 'currency': 'USD', 'exchange_timezone': 'America/New_York',
# 'exchange': 'NASDAQ', 'mic_code': 'XNGS', 'type': 'Common Stock'},
# 'values': [{'datetime': '2026-02-06', 'open': '277.12000', 'high':
# '280.91000', 'low': '276.92999', 'close': '278.12000', 'volume':
# '50420700'}], 'status': 'ok'}, 'AMZN': {'meta': {'symbol': 'AMZN',
# 'interval': '1day', 'currency': 'USD', 'exchange_timezone':
# 'America/New_York', 'exchange': 'NASDAQ', 'mic_code': 'XNGS',
# 'type': 'Common Stock'}, 'values': [{'datetime': '2026-02-06',
# 'open': '202.70000', 'high': '211.44000', 'low': '200.31000', 'close':
# '210.32001', 'volume': '179021600'}], 'status': 'ok'},
# 'GOOGL': {'meta': {'symbol': 'GOOGL', 'interval': '1day', 'currency':
# 'USD', 'exchange_timezone': 'America/New_York', 'exchange': 'NASDAQ',
# 'mic_code': 'XNGS', 'type': 'Common Stock'}, 'values': [{'datetime':
# '2026-02-06', 'open': '327.17999', 'high': '330.38000', 'low': '319.92001',
# 'close': '322.85999', 'volume': '56294700'}], 'status': 'ok'}, 'MSFT':
# {'meta': {'symbol': 'MSFT', 'interval': '1day', 'currency': 'USD',
# 'exchange_timezone': 'America/New_York', 'exchange': 'NASDAQ', 'mic_code':
# 'XNGS', 'type': 'Common Stock'}, 'values': [{'datetime': '2026-02-06',
# 'open': '399.17001', 'high': '401.79001', 'low': '392.92001', 'close':
# '401.14001', 'volume': '53403600'}], 'status': 'ok'}, 'TSLA': {'meta':
# {'symbol': 'TSLA', 'interval': '1day', 'currency': 'USD',
# 'exchange_timezone': 'America/New_York', 'exchange': 'NASDAQ',
# 'mic_code': 'XNGS', 'type': 'Common Stock'}, 'values': [{'datetime':
# '2026-02-06', 'open': '400.87000', 'high': '414.54999', 'low': '397.75',
# 'close': '411.10999', 'volume': '62559600'}], 'status': 'ok'}}
