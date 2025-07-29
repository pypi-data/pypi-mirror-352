from datetime import datetime
import requests
import pandas as pd
import time
import re

class StockDataDownloader:
    def __init__(self, ticker, start_date, end_date, interval='day', max_retries=3, retry_delay=5):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = self.set_base_url()

    def set_base_url(self):
        if re.match(r'^\d{6}$', self.ticker) or re.match(r'^\d{5}K$', self.ticker):
            return "https://api.stock.naver.com/chart/domestic/item/"
        else:
            return "https://api.stock.naver.com/chart/foreign/item/"

    def download(self):
        start_datetime = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(self.end_date, '%Y-%m-%d')
        start_str = start_datetime.strftime('%Y%m%d') + "0000"
        end_str = end_datetime.strftime('%Y%m%d') + "2359"

        url = f"{self.base_url}{self.ticker}/{self.interval}?startDateTime={start_str}&endDateTime={end_str}"

        for attempt in range(self.max_retries):
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        return self.parse_data(data)
                    else:
                        print(f"Attempt {attempt + 1} failed: Received null response. URL: {url}")
                except ValueError:
                    print(f"Attempt {attempt + 1} failed: Invalid JSON response. URL: {url}")
            else:
                print(f"Attempt {attempt + 1} failed: {response.status_code}. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

        # If all attempts fail, raise an exception with the debug message
        raise Exception(f"Failed to fetch data after {self.max_retries} attempts. URL: {url}, Status Code: {response.status_code}")

    @staticmethod
    def parse_data(data):
        df = pd.DataFrame(data)
        df['localDate'] = pd.to_datetime(df['localDate'])
        df.set_index('localDate', inplace=True)

        columns = {
            'closePrice': 'Close',
            'openPrice': 'Open',
            'highPrice': 'High',
            'lowPrice': 'Low',
            'accumulatedTradingVolume': 'Volume'
        }

        # Check if 'foreignRetentionRate' is in the data
        if 'foreignRetentionRate' in df.columns:
            columns['foreignRetentionRate'] = 'ForeignHold'

        df.rename(columns=columns, inplace=True)

        # Convert relevant columns to numeric
        numeric_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
        if 'ForeignHold' in df.columns:
            numeric_columns.append('ForeignHold')

        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)

        return df

# Example usage:
# downloader = StockDataDownloader('005930', '2023-01-01', '2023-12-31')
# df = downloader.download()
# print(df)
