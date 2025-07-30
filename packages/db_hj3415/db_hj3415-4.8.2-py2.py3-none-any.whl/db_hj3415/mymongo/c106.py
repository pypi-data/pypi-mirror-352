import pandas as pd
from pymongo import TEXT

from utils_hj3415 import tools, setup_logger
from db_hj3415.mymongo.corps import Corps

mylogger = setup_logger(__name__,'WARNING')

class C106(Corps):

    PAGES = ('c106y', 'c106q')

    def __init__(self, code: str, page: str):
        """
        page 는 c106y 또는 c106q
        :param code:
        :param page:
        """
        super().__init__(code=code, page=page)

    @classmethod
    def save(cls, code: str, page: str, c106_df: pd.DataFrame):
        assert tools.is_6digit(code), f'Invalid code : {code}'
        assert page in ['c106q', 'c106y'], f'Invalid page : {page}'

        client = cls.get_client()

        clear_table = False
        if client[code][page].count_documents({}) != 0:
            clear_table = True

        client[code][page].create_index([('항목', TEXT)], unique=True)
        cls._save_df(code=code, page=page, df=c106_df, clear_table=clear_table)

    def list_row_titles(self) -> list:
        titles = []
        for item in self.list_rows():
            titles.append(item['항목'])
        return list(set(titles))

    @staticmethod
    def make_like_c106(code: str, page: str, title: str) -> dict:
        """
        title에 해당하는 항목을 page(c103이나 c104)에서 찾아 c106의 형식으로 만들어서 반환한다.
        """
        from db_hj3415 import myredis

        data = {}
        if page in myredis.C104.PAGES:
            c1034 = myredis.C104(code, page)
        elif page in myredis.C103.PAGES:
            c1034 = myredis.C103(code, page)
        else:
            raise Exception(f"page - {page}는 C103,C104 페이지이어야 합니다.")

        for name_code in myredis.C106(code, 'c106y').get_rivals():
            mylogger.debug(f"{name_code}")
            _, code = str(name_code).split('/')
            try:
                c1034.code = code
            except AssertionError:
                # Unnamed 같이 종목명/코드 형식이 아닌 경우
                continue
            _, value = c1034.latest_value_pop2(title)
            data[name_code] = value

        return data

    def find(self, row_title: str, del_unnamed_key=True) -> dict:
        """
        title에 해당하는 항목을 딕셔너리로 반환한다.
        """
        data = self._col.find_one({'항목': {'$eq': row_title}})
        if data is None:
            mylogger.warning(f'{row_title} is not in {self.table}')
            data = {}
        if del_unnamed_key:
            data = self.del_unnamed_key(data)

        return Corps.refine_data(data, ['_id', '항목'])

    def get_rivals(self, del_unnamed_key=True) -> list:
        """
        c106의 경쟁사 리스트를 반환한다.
        :return:
        """
        # 컬렉션의 첫번째 아무 도큐먼트를 찾아낸다.
        data = self._col.find_one()
        if data is None:
            mylogger.warning(f'rival data is none.{self.table} seems empty.')
            return []
        if del_unnamed_key:
            data = self.del_unnamed_key(data)
        rival_list = list(data.keys())
        rival_list.remove('_id')
        rival_list.remove('항목')
        return rival_list