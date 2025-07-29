
import unittest
from unittest.mock import patch
import pandas as pd
from nfinance import download

class TestNFinance(unittest.TestCase):
    @patch('nfinance.stock_data.requests.get')
    def test_download_successful(self, mock_get):
        # Setup
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'localDate': '2022-01-01',
            'closePrice': '70000',
            'openPrice': '69000',
            'highPrice': '70500',
            'lowPrice': '68800',
            'accumulatedTradingVolume': '123456',
            'foreignRetentionRate': '53.4'
        }]

        # Action
        result = download(ticker="005930", start_date="2022-01-01", end_date="2022-01-31")

        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.loc[pd.Timestamp('2022-01-01')]['Close'], 70000)
        self.assertEqual(result.loc[pd.Timestamp('2022-01-01')]['Open'], 69000)

    @patch('nfinance.stock_data.requests.get')
    def test_download_failure(self, mock_get):
        # Setup
        mock_response = mock_get.return_value
        mock_response.status_code = 404

        # Action & Assert
        with self.assertRaises(Exception) as context:
            download(ticker="005930", start_date="2022-01-01", end_date="2022-01-31")

        self.assertIn('Failed to fetch data', str(context.exception))

if __name__ == '__main__':
    unittest.main()
