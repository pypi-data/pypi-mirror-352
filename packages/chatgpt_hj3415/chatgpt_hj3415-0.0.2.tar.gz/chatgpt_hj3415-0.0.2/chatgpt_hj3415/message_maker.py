from typing import Dict, List, Iterator
from db_hj3415 import myredis
from utils_hj3415.tools import replace_nan_to_none, to_int
import pandas as pd

def _make_table_data(cxxx) -> Dict[str, List[dict]]:
    # C103, C104, C106 의 전체 테이블의 열을 반환한다.
    rows_per_page = {}
    for page in cxxx.PAGES:
        cxxx.page = page
        rows_per_page[page] = replace_nan_to_none(cxxx.list_rows())
        # print(rows_per_page[page])
    return rows_per_page

def to_csv(records: List[dict], cleaning: bool = True)-> str:
    df = pd.DataFrame(records)
    df.set_index('항목', inplace=True)

    if cleaning:
        # 모든 값이 NaN(또는 빈 문자열 등)인 행 삭제
        df_cleaned = df.dropna(how='all', axis=1)  # 열 전체가 NaN일 경우 열 제거
        df_cleaned = df_cleaned.dropna(how='all', axis=0)  # 행 전체가 NaN일 경우 행 제거

        # 또는 아래와 같이 빈 셀('')로 이루어진 행 제거도 가능
        df_cleaned = df_cleaned.loc[~(df_cleaned == '').all(axis=1)]

        csv_text = df_cleaned.to_csv(index=True)
    else:
        csv_text = df.to_csv(index=True)
    return csv_text

def get_c103_data(code:str)-> Iterator[tuple[str, str]]:
    c103 = myredis.C103(code, 'c103손익계산서q')
    data = _make_table_data(c103)

    for page, records in data.items():
        yield page, to_csv(records, cleaning=True)

def get_c104_data(code: str)-> Iterator[tuple[str, str]]:
    c104 = myredis.C104(code, 'c104q')
    data = _make_table_data(c104)

    for page, records in data.items():
        yield page, to_csv(records, cleaning=True)

def get_c106_data(code: str)-> Iterator[tuple[str, str]]:
    c106 = myredis.C106(code, 'c106q')
    data = _make_table_data(c106)

    for page, records in data.items():
        yield page, to_csv(records, cleaning=True)


def get_c101_chart_data(code: str, last_days) -> list:
    trend = myredis.C101(code).get_trend('주가')
    data = []
    """
    {'2025.02.18': '55376', '2025.02.19': 57981.0} 
    -> [{'x': '2025-02-18', 'y': '55376'}, {'x': '2025-02-19', 'y': '57981.0'}]
    """
    for x, y in trend.items():
        data.append({'x': str(x).replace("'", '"').replace(".", "-"),
                     'y': to_int(str(y).replace("'", ""))})
    return data[-last_days:]


