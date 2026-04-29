import datetime
import json
from pathlib import Path

from src.services import increased_cashback
from src.utils import (
    get_top_transactions,
    process_card_data,
    read_card_data_from_excel,
    request_currency_data,
    request_stocks_data,
)
from src.views import get_greeting_by_time

BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "data" / "operations.xlsx"  # выносим в общую переменную


def main() -> str:
    user_input_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # user_input_date = input("Введите дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС:\n")
    greeting = get_greeting_by_time(user_input_date)
    df = read_card_data_from_excel(file_path)
    cards_list = process_card_data(df)
    top_transactions = get_top_transactions(df, 5)
    currency_rates = request_currency_data()
    stocks_rates = request_stocks_data()
    response = {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stocks_rates": stocks_rates,
    }

    return json.dumps(response, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Основной отчет
    result_json = main()
    print(result_json)

    # Дополнительно: расчет кэшбэка
    df = read_card_data_from_excel(file_path)
    result = increased_cashback(df, 2021, 1)

    # Обрабатываем результат
    if hasattr(result, "to_dict"):
        result_dict = {k: abs(int(v / 100)) for k, v in result.to_dict().items()}
        print("\nРезультат расчета кэшбэка:")
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))
    else:
        print(result)

        # 2026-04-29 23:13:00
