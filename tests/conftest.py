import pytest
import pandas as pd


@pytest.fixture
def mock_json_data():
    return {
        "user_currencies": ["USD", "EUR", "GBP"]
    }


@pytest.fixture
def mock_api_response():
    return {
        "Valute": {
            "USD": {"Value": 80.0},
            "EUR": {"Value": 90.0},
            "GBP": {"Value": 100.0}
        }
    }


@pytest.fixture
def mock_settings():
    """Фикстура с настройками для тестов"""
    return {"user_stocks": ["AAPL", "GOOGL", "MSFT"]}


@pytest.fixture
def mock_api_response():
    """Фикстура с успешным ответом API"""
    return {
        "AAPL": {"values": [{"open": "150.50"}]},
        "GOOGL": {"values": [{"open": "2800.30"}]},
        "MSFT": {"values": [{"open": "330.75"}]},
        "status": "ok"
    }



@pytest.fixture
def sample_dataframe():
    """Фикстура с тестовыми данными"""
    return pd.DataFrame({
        'Дата платежа': ['01.01.2021', '15.01.2021', '05.02.2021', '20.01.2021', '10.03.2021'],
        'Категория': ['Супермаркеты', 'Транспорт', 'Супермаркеты', 'Рестораны', 'Транспорт'],
        'Сумма операции': [-1500, -300, -2000, -1000, -500]
    })


@pytest.fixture
def sample_dataframe_with_income():
    """Фикстура с данными, содержащими доходы"""
    return pd.DataFrame({
        'Дата платежа': ['01.01.2021', '15.01.2021', '05.02.2021'],
        'Категория': ['Пополнения', 'Супермаркеты', 'Пополнения'],
        'Сумма операции': [50000, -1500, 30000]
    })