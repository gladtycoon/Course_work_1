from src.utils import get_greeting_by_time, read_card_data_from_excel
from src.utils import process_card_data, get_top_transactions
from src.servises import currency_rates
import json


def main() -> str:
    user_input_date = input("Введите дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС:\n")
    greeting = get_greeting_by_time(user_input_date)

    df = read_card_data_from_excel()
    cards_list = process_card_data(df)
    top_transactions = get_top_transactions(df, 5)

    response = {"greeting": greeting, "cards": cards_list, "top_transactions": top_transactions, "currency_rates": currency_rates}

    return json.dumps(response, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    result_json = main()
    print(result_json)

# 2026-01-30 18:45:00