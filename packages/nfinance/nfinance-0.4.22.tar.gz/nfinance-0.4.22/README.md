text

# nfinance
```
nfinance/
│
├── nfinance/
│   ├── __init__.py
│   └── stock_data.py
│   └── stock_listing.py
│   └── rsi.py
│   └── financials.py
│
├── tests/
│   ├── __init__.py
│   └── test_stock_data.py
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

## 1. 설명
`stock_data.py`는 네이버 파이낸스의 데이터를 가져오는 Python 라이브러리입니다.
`stock_listing.py`는 네이버 파이낸스의 종목 list를 가져오는 Python 라이브러리입니다.
`rsi.py`는 Relative Strength Index를 구하는 Python 라이브러리입니다.

## 2. 설치 방법
pip install nfinance

## 3-1. 사용 예제
```python
import nfinance as nf

ticker = '005930'  # Samsung Electronics Co., Ltd
start_date = '2023-01-01'
end_date = '2023-05-01'

try:
    data = nf.download(ticker, start_date, end_date)
    print(data.head())
except Exception as e:
    print(e)
```
## 3-2. 사용 예제
```python
import nfinance as nf

# 코스피 전체 주식 목록 가져오기
stocks_kospi = nf.StockListing('KOSPI')
df_kospi = stocks_kospi.fetch_stocks()
print(df_kospi)

# 코스닥 전체 주식 목록 가져오기
stocks_kosdaq = nf.StockListing('KOSDAQ')
df_kosdaq = stocks_kosdaq.fetch_stocks()
print(df_kosdaq)

```
## 3-3. 사용 예제
```python
import nfinance

df_annual = nfinance.get_annual_financial('005930')  # 예시: 삼성전자 코드
print(df_annual)
print("df_annual['2019/12']['매출액']", df_annual['2019/12']['매출액'])
print("df_annual.loc['매출액']", df_annual.loc['매출액'])
print("df_annual.loc['매출액'].tolist()", df_annual.loc['매출액'].tolist())
```

## 4. LICENSE

MIT 라이선스를 예로 듭니다. 실제로 사용하려면 올바른 라이선스를 선택해야 합니다.

```plaintext
MIT License

Copyright (c) 2024 lega001

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
