
#version='0.4.22',
from .rsi import compute_rsi
from .stock_listing import StockListing
from .stock_data import StockDataDownloader
from .financials import (
    get_fnguide,
    get_annual_financial,
    get_quarterly_financial,
    get_annual_financial_separate,
    get_quarterly_financial_separate
)

def download(ticker, start_date, end_date, interval='day', max_retries=3, debug=False):
    downloader = StockDataDownloader(ticker, start_date, end_date, interval, max_retries=max_retries, debug=debug)
    return downloader.download()
