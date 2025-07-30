import pandas as pd
from typing import List, Optional
from pymongo import UpdateOne
import time

from utils_hj3415 import tools, setup_logger

from db_hj3415.mymongo.base import Base

mylogger = setup_logger(__name__,'WARNING')

class Corps(Base):
    """
    mongodb의 데이터 중 기업 코드로 된 데이터 베이스를 다루는 클래스
    """
    COLLECTIONS = ('c101', 'c104y', 'c104q', 'c106y', 'c106q', 'c108',
                   'c103손익계산서q', 'c103재무상태표q', 'c103현금흐름표q',
                   'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y',
                   'dart', 'etc')

    def __init__(self, code: str = '', page: str = ''):
        super().__init__(db=code, table=page)

    @property
    def code(self) -> str:
        return self.db

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        self.db = code

    @property
    def page(self) -> str:
        return self.table

    @page.setter
    def page(self, page: str):
        assert page in self.COLLECTIONS, f'Invalid value : {page}({self.COLLECTIONS})'
        self.table = page

    # ========================End Properties=======================
    @staticmethod
    def del_unnamed_key(data: dict) -> dict:
        """
        Unnamed로 시작하는 모든 키를 삭제
        :param data:
        :return:
        """
        keys_to_delete = [key for key in data if key.startswith('Unnamed')]
        for key in keys_to_delete:
            del data[key]
        return data

    @classmethod
    def list_all_codes(cls) -> list:
        """
        기업 코드를 데이터베이스명으로 가지는 모든 6자리 숫자 코드의 db 명 반환
        """
        codes = []
        for db_name in cls.list_db_names():
            if tools.is_6digit(db_name):
                codes.append(db_name)
        return sorted(codes)

    @classmethod
    def drop_all_codes(cls) -> bool:
        """
        모든 코드를 삭제하고 결과를 리턴한다.
        :return:
        """
        codes = cls.list_all_codes()
        all_success = True  # 모든 작업의 성공 여부를 추적하는 변수

        for code in codes:
            if not cls.drop(db=code):
                all_success = False  # 하나라도 실패하면 False로 설정

        return all_success  # 모든 작업이 성공했으면 True, 실패가 있으면 False

    @classmethod
    def drop_code(cls, code: str) -> bool:
        return cls.drop(db=code)

    @classmethod
    def get_name(cls, code: str) -> Optional[str]:
        """
        code를 입력받아 종목명을 반환한다.
        """
        from .c101 import C101
        c101 = C101(code)
        name = c101.get_recent().get('종목명', None)
        if name is None:
            mylogger.warning(f"코드 {code}에 해당하는 종목명이 없습니다.")
        return name

    @classmethod
    def _save_df(cls, code: str, page: str, df: pd.DataFrame, clear_table: bool):
        # c103, c104, c106에서 주로 사용하는 저장방식
        if df.empty:
            mylogger.warning(f'입력된 {code}/{page} 데이터프레임이 비어서 저장은 하지 않습니다.')
            return

        # [조건] 만약 딱 1행이고, '항목'과 'Unnamed: 1'이 모두 '데이터가 없습니다.' 라면 스킵
        if len(df) == 1:
            row = df.iloc[0]
            if row.get('항목') == '데이터가 없습니다.' and row.get('Unnamed: 1') == '데이터가 없습니다.':
                mylogger.warning(f"{code}/{page} => '데이터가 없습니다.' 문구만 존재하므로 저장 스킵합니다.")
                return

        if clear_table:
            # 페이지가 비어 있지 않으면 먼저 지운다.
            mylogger.info(f"데이터를 저장하기 전, {code} / {page} 데이터베이스를 삭제합니다.")
            cls.drop(db=code, table=page)
            time.sleep(1)

        mylogger.debug(df)
        # 이제 df를 각 row(dict) 형태로 변환
        records = df.to_dict('records')
        mylogger.debug(records)

        # 중복 방지를 위해, bulk_write()에서 upsert 사용
        requests = []
        for rec in records:
            # '항목' 필드가 존재하지 않는다면, 예외처리가 필요할 수 있음
            항목_value = rec.get('항목')
            if 항목_value is None:
                # 항목 필드가 없으면, 그냥 insert하거나 스킵하는 등 원하는 로직
                continue

            filter_doc = {"항목": 항목_value}
            update_doc = {"$set": rec}

            # upsert=True: 항목 값이 이미 있으면 update, 없으면 새로 insert
            requests.append(
                UpdateOne(filter_doc, update_doc, upsert=True)
            )

        # bulk_write로 한 번에 처리
        if requests:
            cls._client[code][page].bulk_write(requests, ordered=False)


    @staticmethod
    def refine_data(data: dict, refine_words: list) -> dict:
        """
        주어진 딕셔너리에서 refine_words에 해당하는 키를 삭제해서 반환하는 유틸함수.
        c10346에서 사용
        refine_words : 정규표현식 가능
        """
        copy_data = data.copy()
        import re
        for regex_refine_word in refine_words:
            # refine_word에 해당하는지 정규표현식으로 검사하고 매치되면 삭제한다.
            p = re.compile(regex_refine_word)
            for title, _ in copy_data.items():
                # data 내부의 타이틀을 하나하나 조사한다.
                m = p.match(title)
                if m:
                    del data[title]
        return data

    @classmethod
    def chk_integrity(cls, *args: str) -> dict:
        """
        종목의 필수 컬렉션이 있는지 확인하고 없으면 없는 컬렉션을 리턴한다.
        :param args: 종목코드를 인자로 여러개 받을수 있다.
        :return: {'종목코드': [없는 컬렉션리스트],}
        """
        requrired_collections = ('c101', 'c104y', 'c104q', 'c106y', 'c106q', 'c103손익계산서q',
                                 'c103재무상태표q', 'c103현금흐름표q','c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y',)
        missing_items = {}
        for code in args:
            missing_collections = []
            for collection in requrired_collections:
                if not cls.is_there(db=code, table=collection):
                    missing_collections.append(collection)
            if len(missing_collections) != 0:
                missing_items[code] = missing_collections
        return missing_items

    @classmethod
    def get_status(cls, code: str) -> dict:
        """
        종목의 모든 컬렉션을 조사하여 도큐먼트의 갯수를 가진 딕셔너리를 반환한다.
        :param code:
        :return: {'종목코드': 도큐먼트갯수,}
        """
        status_dict = {}
        if cls.is_there(db=code):
            for table in cls.list_table_names(code):
                rows = []
                for row in cls._client[code][table].find():
                    rows.append(row)
                status_dict[table] = len(rows)
                mylogger.info(f"{code} / {table} / {len(rows)}")
        return status_dict


    def _load_df(self) -> pd.DataFrame:
        try:
            df = pd.DataFrame(self.list_rows())
        except KeyError:
            mylogger.warning(f"{self.db} / {self.table}에 데이터가 없습니다.")
            df = pd.DataFrame()
        return df

    def _load_list(self) -> List[dict]:
        items = []
        for doc in self._col.find():
            del doc['_id']
            items.append(doc)
        return items

    def load(self, to: str = 'df'):
        """
        데이터베이스에 저장된 페이지를 다양한 형식으로 반환한다.
        """
        types = ('df', 'list')
        assert to in types, f"to의 형식이 맞지 않습니다.{types}"

        if to == 'df':
            return self._load_df()
        elif to == 'list':
            return self._load_list()