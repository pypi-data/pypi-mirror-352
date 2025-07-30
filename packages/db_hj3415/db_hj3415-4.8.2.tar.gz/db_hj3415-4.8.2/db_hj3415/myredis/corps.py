from typing import Optional, Dict, List, Callable, Any

from utils_hj3415 import tools
from scraper_hj3415 import krx

from .base import Base
from db_hj3415 import mymongo
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')

class Corps(Base):
    COLLECTIONS = mymongo.Corps.COLLECTIONS

    def __init__(self, code: str = '', page: str = ''):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        assert page in self.COLLECTIONS, f'Invalid value : {page}({self.COLLECTIONS})'
        self.code_page = code + '.' + page
        self._code = code
        self._page = page
        # redis에서 name으로 사용하는 변수의 기본으로 문미에 문자열을 추가로 첨가해서 사용하는 역할을 함.
        super().__init__()

    def __str__(self):
        return f"redis name : {self.code_page}"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        self.code_page = code + self.code_page[6:]
        mylogger.info(f'Change code : {self.code} -> {code}')
        self._code = code

    @property
    def page(self) -> str:
        return self._page

    @page.setter
    def page(self, page: str):
        assert page in self.COLLECTIONS, f'Invalid value : {page}({self.COLLECTIONS})'
        self.code_page = self.code_page[:7] + page
        mylogger.info(f'Change page : {self.page} -> {page}')
        self._page = page

    def get_name(self, data_from='krx', refresh=False) -> Optional[str]:
        """
        종목명을 반환한다. 데이터소스는 data_from 인자로 결정하며 krx 또는 mongo가 가능하다.
        :param data_from: ['krx', 'mongo']
        :param refresh:
        :return:
        """
        redis_name = self.code + '_name'

        def fetch_get_name(code: str, data_from_in: str) -> Optional[str]:
            """
            종목명을 반환한다. 데이터소스는 data_from인자로 결정하며 krx 또는 mongo가 가능하다.
            :param code:
            :param data_from_in: ['krx', 'mongo']
            :return:
            """
            assert data_from_in in ['krx', 'mongo'], "data_from 인자는 krx 또는 mongo 중 하나입니다."
            if data_from_in == 'krx':
                mylogger.info(f"{code} 종목명으로 krx로부터 받아옵니다.")
                return krx.get_name(code)
            elif data_from_in == 'mongo':
                mylogger.info(f"{code} 종목명으로 mongo.C101로부터 받아옵니다.")
                return mymongo.Corps.get_name(code)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_name, self.code, data_from)

    @classmethod
    def get_all_codes_names(cls, refresh=False) -> Dict[str, str]:
        redis_name = 'all_codes_names'

        def fetch_get_all_codes_names() -> dict:
            corps = {}
            for code in cls.list_all_codes(refresh):
                corps[code] = mymongo.Corps.get_name(code)
            return corps

        return cls.fetch_and_cache_data(redis_name, refresh, fetch_get_all_codes_names)

    @classmethod
    def list_all_codes(cls, refresh=False) -> list:
        """
        redis_name = 'all_codes'
        :return:
        """
        redis_name = 'all_codes'

        def fetch_list_all_codes() -> list:
            codes = []
            for db_name in mymongo.Corps.list_db_names():
                if tools.is_6digit(db_name):
                    codes.append(db_name)
            return sorted(codes)

        return cls.fetch_and_cache_data(redis_name, refresh, fetch_list_all_codes)

    @classmethod
    def _list_rows(cls, func: mymongo.Corps, redis_name: str, refresh=False) -> list:
        """
        C103468에서 내부적으로 사용
        :param func:
        :param redis_name:
        :return:
        """
        def fetch_list_rows(func_in: mymongo.Corps) -> list:
            mylogger.debug(func_in.list_rows())
            return func_in.list_rows()
        return cls.fetch_and_cache_data(redis_name, refresh, fetch_list_rows, func)

    @classmethod
    def bulk_get_or_compute(cls,
                            keys: List[str],
                            compute_function: Callable[[str], Any],
                            refresh: bool) -> Dict[str, Any]:
        """
        {레디스명: 값} -> {코드: 값} 리턴값으로 변환
        """
        redis_key_data = Base.bulk_get_or_compute(keys, compute_function, refresh)
        mylogger.debug(redis_key_data)
        code_data = {}
        for redis_key, data in redis_key_data.items():
            code_data[redis_key[:6]] = data
        return code_data
