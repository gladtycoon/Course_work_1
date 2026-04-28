import json
from unittest.mock import mock_open, patch
from src.utils import request_currency_data, request_stocks_data


def test_request_currency_data_success(mock_json_data, mock_api_response):
    mock_json_content = json.dumps(mock_json_data)

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        with patch("requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.json.return_value = mock_api_response

            result = request_currency_data()

    expected = [
        {"currency": "USD", "rate": 80.0},
        {"currency": "EUR", "rate": 90.0},
        {"currency": "GBP", "rate": 100.0}
    ]
    assert result == expected


def test_request_currency_data_missing_currency(mock_json_data, mock_api_response):
    modified_api_response = {
        "Valute": {
            "USD": {"Value": 80.0},
            "GBP": {"Value": 100.0}
        }
    }

    mock_json_content = json.dumps(mock_json_data)

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        with patch("requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.json.return_value = modified_api_response

            result = request_currency_data()

    expected = [
        {"currency": "USD", "rate": 80.0},
        {"currency": "GBP", "rate": 100.0}
    ]
    assert result == expected


def test_request_currency_data_empty_currencies():
    mock_json_data = {"user_currencies": []}
    mock_json_content = json.dumps(mock_json_data)

    with patch("builtins.open", mock_open(read_data=mock_json_content)):
        with patch("requests.get") as mock_get:
            result = request_currency_data()

    assert result == []




