import requests
import pandas as pd
from tqdm import tqdm

class StockListing:
    def __init__(self, market):
        self.market = market
        self.base_urls = {
            "KOSPI": "https://m.stock.naver.com/api/stocks/marketValue/KOSPI?page={page}&pageSize=20",
            "KOSDAQ": "https://m.stock.naver.com/api/stocks/marketValue/KOSDAQ?page={page}&pageSize=20",
            "etf": "https://m.stock.naver.com/api/stocks/etf/marketValue?page={page}&pageSize=20",
            "etn": "https://m.stock.naver.com/api/stocks/etn?page={page}&pageSize=20",
            "NYSE": "https://api.stock.naver.com/stock/exchange/NYSE/marketValue?page={page}&pageSize=20",
            "NASDAQ": "https://api.stock.naver.com/stock/exchange/NASDAQ/marketValue?page={page}&pageSize=20",
            "AMEX": "https://api.stock.naver.com/stock/exchange/AMEX/marketValue?page={page}&pageSize=20",
            "SHANGHAI": "https://api.stock.naver.com/stock/exchange/SHANGHAI/marketValue?page={page}&pageSize=20",
            "SHENZHEN": "https://api.stock.naver.com/stock/exchange/SHENZHEN/marketValue?page={page}&pageSize=20",
            "HONG_KONG": "https://api.stock.naver.com/stock/exchange/HONG_KONG/marketValue?page={page}&pageSize=20",
            "TOKYO": "https://api.stock.naver.com/stock/exchange/TOKYO/marketValue?page={page}&pageSize=20",
            "HOCHIMINH": "https://api.stock.naver.com/stock/exchange/HOCHIMINH/marketValue?page={page}&pageSize=20",
            ".DJI": "https://api.stock.naver.com/index/.DJI/enrollStocks?page={page}&pageSize=10",
            ".INX": "https://api.stock.naver.com/index/.INX/enrollStocks?page={page}&pageSize=10",
            ".SOX": "https://api.stock.naver.com/index/.SOX/enrollStocks?page={page}&pageSize=10",
            "DJI": "https://api.stock.naver.com/index/.DJI/enrollStocks?page={page}&pageSize=10",
            "INX": "https://api.stock.naver.com/index/.INX/enrollStocks?page={page}&pageSize=10",
            "SOX": "https://api.stock.naver.com/index/.SOX/enrollStocks?page={page}&pageSize=10",
            "foreign_etf": "https://api.stock.naver.com/etf/priceTop?page={page}&pageSize=20",
            "largeCode": "https://api.stock.naver.com/etf/priceTop?page={page}&pageSize=20&{market}"
        }
        if self.market.startswith('largeCode'):
            self.url = self.base_urls.get("largeCode")
        else:
            self.url = self.base_urls.get(self.market.split('=')[0], "https://m.stock.naver.com/api/stocks/marketValue/{market}?page={page}&pageSize=20")

    def fetch_stocks(self, show_progress=False):
        special_stock_list = ['.DJI', '.INX', '.SOX', 'DJI', 'INX', 'SOX']
        special_stock_pages = {'.DJI': 4, '.INX': 51, '.SOX': 4, 'DJI': 4, 'INX': 51, 'SOX': 4}

        if self.market in special_stock_list:
            total_pages = special_stock_pages[self.market]
            page_size = 10
        else:
            response = requests.get(self.url.format(market=self.market, page=1))
            if response.status_code != 200:
                raise Exception(f"API request failed with status code: {response.status_code}")
            json_data = response.json()
            total_stocks = json_data.get('totalCount', 0)
            total_pages = (total_stocks // 20) + 1 if total_stocks % 20 != 0 else total_stocks // 20
            page_size = 20

        stocks = []

        for page in tqdm(range(1, total_pages + 1), desc=f"Fetching {self.market} stocks", disable=not show_progress):
            formatted_url = self.url.format(market=self.market, page=page)
            response = requests.get(formatted_url)
            if response.status_code != 200:
                continue  # Skip to next iteration if there's an error
            json_data = response.json()
            if self.market == 'foreign_etf' or self.market.startswith('largeCode'):
                new_stocks = pd.json_normalize(json_data.get("etfs", []))
            else:
                new_stocks = pd.json_normalize(json_data.get("stocks", []))
            if not new_stocks.empty:
                stocks.append(new_stocks)

        return pd.concat(stocks, ignore_index=True) if stocks else pd.DataFrame()

    def __str__(self):
        return f'StockListing for {self.market}'

# Example usage with progress bar enabled:
# listing = StockListing("KOSPI")
# stocks_df = listing.fetch_stocks(show_progress=True)
# print(stocks_df)

# Example usage without progress bar:
# listing = StockListing(".DJI")
# stocks_df = listing.fetch_stocks(show_progress=False)
# stocks_df.to_csv('.DJI.csv', index=False)
