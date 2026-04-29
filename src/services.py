import json
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from src.utils import read_card_data_from_excel

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "data" / "operations.xlsx"


def increased_cashback(
    df: DataFrame, user_input_year: int, user_input_month: int
) -> dict:
    """Функция для расчета увеличенного кэшбэка"""
    if df is None or df.empty:
        print("Нет данных для обработки")
        return {}
    try:
        if not pd.api.types.is_datetime64_any_dtype(df["Дата платежа"]):
            df["Дата платежа"] = pd.to_datetime(
                df["Дата платежа"], dayfirst=True, errors="coerce"
            )
        mask = (df["Дата платежа"].dt.year == user_input_year) & (
            df["Дата платежа"].dt.month == user_input_month
        )
        filtered_data = df[mask].copy()
        if filtered_data.empty:
            print(f"Нет данных за {user_input_month}.{user_input_year}")
            return {}

        df_mask = df[mask]
        filtered_data = df_mask.groupby("Категория")["Сумма операции"].sum()
        return filtered_data

    except Exception as e:
        print(f"Ошибка при анализе данных: {e}")
        return {}


if __name__ == "__main__":
    df = read_card_data_from_excel(file_path)
    result = increased_cashback(df, 2021, 1)
    result_dict = result.to_dict()

    # Если нужно сделать суммы положительными (модуль)
    result_dict = {k: abs(int(v / 100)) for k, v in result_dict.items()}
    sorted_result = result.sort_values(ascending=False)
    print(json.dumps(result_dict, ensure_ascii=False, indent=2))
