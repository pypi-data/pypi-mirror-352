import datetime
from typing import Tuple
from pymongo import TEXT
import pandas as pd

from utils_hj3415 import tools, setup_logger
from db_hj3415.mymongo.c1034 import C1034

mylogger = setup_logger(__name__,'WARNING')

class C104(C1034):
    PAGES = ('c104y', 'c104q')

    def __init__(self, code: str, page: str):
        """
        :param code:
        :param page: c104q, c104y
        """
        super().__init__(code=code, page=page)

    @classmethod
    def save(cls, code: str, page: str, c104_df: pd.DataFrame):
        """데이터베이스에 저장

        c104는 4페이지의 자료를 한 컬렉션에 모으는 것이기 때문에
        stamp 를 검사하여 12시간 전보다 이전에 저장된 자료가 있으면
        삭제한 후 저장하고 12시간 이내의 자료는 삭제하지 않고
        데이터를 추가하는 형식으로 저장한다.

        Example:
            c104_data 예시\n
            [{'항목': '매출액증가율',...'2020/12': 2.78, '2021/12': 14.9, '전년대비': 8.27, '전년대비1': 12.12},
            {'항목': '영업이익증가율',...'2020/12': 29.62, '2021/12': 43.86, '전년대비': 82.47, '전년대비1': 14.24}]
        """
        assert tools.is_6digit(code), f'Invalid code : {code}'
        assert page in ['c104q', 'c104y'], f'Invalid page : {page}'

        client = cls.get_client()

        time_now = datetime.datetime.now()
        clear_table = False
        try:
            stamp = client[code][page].find_one({'항목': 'stamp'})['time']
            if stamp < (time_now - datetime.timedelta(days=.005)):  # 약 7분
                # 스템프가 약 10분 이전이라면..연속데이터가 아니라는 뜻이므로 컬렉션을 초기화한다.
                clear_table = True
        except TypeError:
            # 스템프가 없다면...
            clear_table = True

        try:
            client[code][page].drop_index("항목_text")
        except:
            # 인덱스가 없을 수도 있으므로 pass
            pass
        client[code][page].create_index([('항목', TEXT)])
        cls._save_df(code=code, page=page, df=c104_df, clear_table=clear_table)
        # 항목 stamp를 찾아 time을 업데이트하고 stamp가 없으면 insert한다.
        client[code][page].update_one({'항목': 'stamp'}, {"$set": {'time': time_now}}, upsert=True)

    def list_row_titles(self) -> list:
        """
        c104는 stamp항목이 있기 때문에 삭제하고 리스트로 반환한다.
        """
        titles = super().list_row_titles()
        try:
            titles.remove('stamp')
        except ValueError:
            # stamp 항목이 없는 경우 그냥넘어간다.
            pass
        return titles

    def list_rows(self, show_id=False) -> list:
        """
        Base.list_rows()에서 항목 stamp를 제한다.
        :return:
        """
        return [x for x in super().list_rows(show_id=show_id) if x['항목'] != 'stamp']

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

        c, l = super(C104, self)._find(row_title=row_title, refine_words=refine_words)

        if c == 0:
            return_dict = {}
        else:
            return_dict = l[0]

        if del_unnamed_key:
            return_dict = self.del_unnamed_key(return_dict)

        return c, return_dict

    def get_stamp(self) -> datetime.datetime:
        """
        c104y, c104q가 작성된 시간이 기록된 stamp 항목을 datetime 형식으로 리턴한다.
        """
        return self._col.find_one({"항목": "stamp"})['time']

    def modify_stamp(self, days_ago: int):
        """
        인위적으로 타임스템프를 수정한다 - 주로 테스트 용도
        """
        try:
            before = self._col.find_one({'항목': 'stamp'})['time']
        except TypeError:
            # 이전 타임 스탬프가 없는 경우
            before = None
        time_2da = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        self._col.update_one({'항목': 'stamp'}, {"$set": {'time': time_2da}}, upsert=True)
        after = self._col.find_one({'항목': 'stamp'})['time']
        mylogger.info(f"Stamp changed: {before} -> {after}")