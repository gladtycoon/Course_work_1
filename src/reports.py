import json
from datetime import datetime
from functools import wraps
from pathlib import Path
import pandas as pd
from pandas import DataFrame


# ========== ДЕКОРАТОР ==========
def report_to_file(filename: str = None):
    """
    Декоратор для записи результата функции-отчета в файл.

    Без параметра: создает файл с именем report_ГГГГ-ММ-ДД_ЧЧ-ММ-СС.json
    С параметром: создает файл с указанным именем
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Выполняем функцию
            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_filename = f"report_{timestamp}.json"
            else:
                output_filename = filename

            # Создаем папку для отчетов (на уровень выше, в корне проекта)
            reports_dir = Path(__file__).resolve().parent.parent / "reports"
            reports_dir.mkdir(exist_ok=True)

            # Полный путь к файлу
            file_path = reports_dir / output_filename

            # Сохраняем результат
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(result, dict):
                    json.dump(result, f, ensure_ascii=False, indent=2)
                elif isinstance(result, (list, tuple)):
                    json.dump(result, f, ensure_ascii=False, indent=2)
                elif hasattr(result, 'to_dict'):
                    json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
                else:
                    json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"Отчет сохранен в файл: {file_path}")
            return result

        return wrapper

    return decorator


# ========== ФУНКЦИЯ ДЛЯ ЧТЕНИЯ ДАННЫХ ==========
def read_card_data_from_excel(file_path: Path) -> DataFrame:
    """Чтение данных из Excel-файла"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return pd.DataFrame()


# ========== ОТЧЕТ №1: УВЕЛИЧЕННЫЙ КЭШБЭК ==========
@report_to_file()  # без параметра — автоматическое имя
def increased_cashback_report(df: DataFrame, user_input_year: int, user_input_month: int) -> dict:
    """Отчет: расчет увеличенного кэшбэка по категориям"""
    if df is None or df.empty:
        return {}

    if not pd.api.types.is_datetime64_any_dtype(df['Дата платежа']):
        df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], dayfirst=True, errors='coerce')

    mask = (df['Дата платежа'].dt.year == user_input_year) & (df['Дата платежа'].dt.month == user_input_month)
    filtered_data = df[mask].copy()

    if filtered_data.empty:
        return {}

    result = filtered_data.groupby('Категория')['Сумма операции'].sum()
    result_dict = {k: abs(int(v)) for k, v in result.to_dict().items()}

    return result_dict


# ========== ОТЧЕТ №2: С УКАЗАННЫМ ИМЕНЕМ ФАЙЛА ==========
@report_to_file("cashback_january_2021.json")  # с параметром — указанное имя
def increased_cashback_report_named(df: DataFrame, user_input_year: int, user_input_month: int) -> dict:
    """Отчет с сохранением в указанный файл"""
    if df is None or df.empty:
        return {}

    if not pd.api.types.is_datetime64_any_dtype(df['Дата платежа']):
        df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], dayfirst=True, errors='coerce')

    mask = (df['Дата платежа'].dt.year == user_input_year) & (df['Дата платежа'].dt.month == user_input_month)
    filtered_data = df[mask].copy()

    if filtered_data.empty:
        return {}

    result = filtered_data.groupby('Категория')['Сумма операции'].sum()
    result_dict = {k: abs(int(v)) for k, v in result.to_dict().items()}

    return result_dict


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    # Путь к файлу с данными
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = BASE_DIR / "data" / "operations.xlsx"

    # Читаем данные
    df = read_card_data_from_excel(file_path)

    # Вызываем отчет с автоматическим именем
    print("=" * 50)
    print("Отчет с автоматическим именем файла:")
    result1 = increased_cashback_report(df, 2021, 1)
    print(f"Результат: {result1}\n")

    # Вызываем отчет с указанным именем файла
    print("=" * 50)
    print("Отчет с указанным именем файла:")
    result2 = increased_cashback_report_named(df, 2021, 1)
    print(f"Результат: {result2}\n")