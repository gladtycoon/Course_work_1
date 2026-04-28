from datetime import datetime


def get_greeting_by_time(user_input_date: str) -> str:
    """Принимает строку с датой и возвращает приветствие"""
    try:
        user_date_obj = datetime.strptime(user_input_date, "%Y-%m-%d %H:%M:%S")
        hour = user_date_obj.hour

        if hour == 23 or 0 <= hour < 6:
            return "Доброй ночи"
        elif 6 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 18:
            return "Добрый день"
        else:
            return "Добрый вечер"
    except ValueError:
        return "Ошибка формата даты"
