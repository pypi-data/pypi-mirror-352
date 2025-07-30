import pandas as pd
from pymongo import TEXT
from typing import Tuple
from utils_hj3415 import tools
from db_hj3415.mymongo.c1034 import C1034


class C103(C1034):

    PAGES = ('c103손익계산서q', 'c103재무상태표q', 'c103현금흐름표q', 'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y')

    def __init__(self, code: str, page: str):
        """
        :param code:
        :param page: 'c103손익계산서q', 'c103재무상태표q', 'c103현금흐름표q', 'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y'
        """
        super().__init__(code=code, page=page)

    @classmethod
    def save(cls, code: str, page: str, c103_df: pd.DataFrame):
        """데이터베이스에 저장

        Example:
            c103_list 예시\n
            [{'항목': '자산총계', '2020/03': 3574575.4, ... '전분기대비': 3.9},
            {'항목': '유동자산', '2020/03': 1867397.5, ... '전분기대비': 5.5}]

        Note:
            항목이 중복되는 경우가 있기 때문에 c104처럼 각 항목을 키로하는 딕셔너리로 만들지 않는다.
        """
        assert tools.is_6digit(code), f'Invalid code : {code}'
        assert page in ['c103손익계산서q', 'c103재무상태표q', 'c103현금흐름표q', 'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y'], f'Invalid page : {page}'

        client = cls.get_client()
        clear_table = False
        if client[code][page].count_documents({}) != 0:
            clear_table = True

        client[code][page].create_index([('항목', TEXT)])
        cls._save_df(code=code, page=page, df=c103_df, clear_table=clear_table)

    def find(self, row_title: str, remove_yoy=False, del_unnamed_key=True) -> Tuple[int, dict]:
        """
        :param row_title: 해당하는 항목을 반환한다.
        :param remove_yoy: 전분기대비, 전년대비를 삭제할지 말지
        :param del_unnamed_key: Unnamed키를 가지는 항목삭제
        :return: 중복된 항목은 합쳐서 딕셔너리로 반환하고 중복된 갯수를 정수로 반환
        """
        if remove_yoy:
            refine_words = ['항목', '^전.+대비.*']
        else:
            refine_words = ['항목']

        c, dict_list = super(C103, self)._find(row_title=row_title, refine_words=refine_words)

        if c > 1:
            return_dict = self.sum_each_data(dict_list)
        elif c == 0:
            return_dict = {}
        else:
            return_dict = dict_list[0]

        if del_unnamed_key:
            return_dict = self.del_unnamed_key(return_dict)

        return c, return_dict