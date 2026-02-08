import json
from unittest.mock import patch, mock_open

from src.views import request_currency_data


def test_request_currency_data():
    user_settings_data = json.dumps({
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    })
    with patch("builtins.open", mock_open(read_data=user_settings_data)):
        with patch("requests.get") as mock_request:
            mock_request.return_value.json.return_value = {'Valute':{'USD':{'Value': 80.001}}}
            assert request_currency_data() == [{'currency': 'USD', 'rate': 80.001}]
