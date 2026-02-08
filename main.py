from pathlib import Path
import json
from src.views import request_currency_data, request_stocks_data
from src.utils import get_greeting_by_time, read_card_data_from_excel
from src.utils import process_card_data, get_top_transactions


BASE_DIR = Path(__file__).resolve().parent


def main() -> str:
    user_input_date = input("Введите дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС:\n")
    greeting = get_greeting_by_time(user_input_date)
    file_path = BASE_DIR / "data/operations.xlsx"
    df = read_card_data_from_excel(file_path)
    cards_list = process_card_data(df)
    top_transactions = get_top_transactions(df, 5)
    currency_rates = request_currency_data()
    stocks_rates = request_stocks_data()
    response = {"greeting": greeting, "cards": cards_list, "top_transactions": top_transactions,
                "currency_rates": currency_rates, "stocks_rates": stocks_rates}

    return json.dumps(response, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    result_json = main()
    print(result_json)

# 2026-02-08 15:00:00
