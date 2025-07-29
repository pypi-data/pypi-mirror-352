
import pandas as pd
from urllib import parse

def get_fnguide(code):
    get_param = {
        'pGB': 1,
        'gicode': 'A%s' % (code),
        'cID': '',
        'MenuYn': 'Y',
        'ReportGB': '',
        'NewMenuID': 101,
        'stkGb': 701,
    }
    get_param = parse.urlencode(get_param)
    url = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?%s" % (get_param)
    tables = pd.read_html(url, header=0)
    return tables

def get_annual_financial(code):
    tables = get_fnguide(code)
    annual_financial_highlights = tables[11]  # 11번째 테이블

    # 데이터프레임 생성
    df = annual_financial_highlights.copy()
    df.columns = df.iloc[0]  # 첫 번째 행을 열 이름으로 사용
    df = df.drop(0)  # 첫 번째 행 제거
    df = df.reset_index(drop=True)
    df = df.set_index("IFRS(연결)")

    return df

def get_quarterly_financial(code):
    tables = get_fnguide(code)
    quarterly_financial_highlights = tables[12]  # 12번째 테이블

    # 데이터프레임 생성
    df = quarterly_financial_highlights.copy()
    df.columns = df.iloc[0]  # 첫 번째 행을 열 이름으로 사용
    df = df.drop(0)  # 첫 번째 행 제거
    df = df.reset_index(drop=True)
    df = df.set_index("IFRS(연결)")

    return df

def get_annual_financial_separate(code):
    tables = get_fnguide(code)
    annual_financial_separate = tables[14]  # 14번째 테이블

    # 데이터프레임 생성
    df = annual_financial_separate.copy()
    df.columns = df.iloc[0]  # 첫 번째 행을 열 이름으로 사용
    df = df.drop(0)  # 첫 번째 행 제거
    df = df.reset_index(drop=True)
    df = df.set_index("IFRS(별도)")

    return df

def get_quarterly_financial_separate(code):
    tables = get_fnguide(code)
    quarterly_financial_separate = tables[15]  # 15번째 테이블

    # 데이터프레임 생성
    df = quarterly_financial_separate.copy()
    df.columns = df.iloc[0]  # 첫 번째 행을 열 이름으로 사용
    df = df.drop(0)  # 첫 번째 행 제거
    df = df.reset_index(drop=True)
    df = df.set_index("IFRS(별도)")

    return df
