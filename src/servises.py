import requests
import json
from dotenv import load_dotenv


""" Читаем json-файл с валютами и акциями """
with open('../user_settings.json', 'r', encoding='utf-8') as json_file:
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
        currency_rates.append({"currency": currency_code, "rate": currency_rate})
    except KeyError:
        print(f"Валюта {currency_code} не найдена, пропускаем")
    index_currency += 1


""" API-запрос для получения курса акции """
# Параметры запроса
params = {
    "function": "GLOBAL_QUOTE",
    "symbol": "stock_code",
    "apikey": 'B92RBAJGB7OZ33WZ'
}
stocks_rates = []
index_stock = 0
len_list_of_stocks = len(settings['user_stocks'])
while index_stock < len_list_of_stocks:
    stock_code = settings['user_stocks'][index_stock]
    try:
        response = requests.get("https://www.alphavantage.co/query", params=params)
        data = response.json()
    except KeyError:
        print(f"Акция {stock_code} не найдена, пропускаем")
    index_stock += 1
    print(data)




# {
#   "user_currencies": ["USD", "EUR"],
#   "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
# }
