from typing import List, Optional, Dict
import datetime

from db_hj3415.myredis.corps import Corps
from db_hj3415 import mymongo

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, level='WARNING')


class C108(Corps):
    REDIS_RECENT_DATE_SUFFIX = 'recent_date'

    def __init__(self, code: str):
        super().__init__(code, 'c108')
        self.mymongo_c108 = mymongo.C108(code)

    @property
    def code(self) -> str:
        return super().code

    @code.setter
    def code(self, code: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C108, self.__class__).code.__set__(self, code) # type:ignore
        self.mymongo_c108.code = code

    def list_rows(self, refresh=False):
        redis_name = self.code_page + '_rows'
        return super()._list_rows(self.mymongo_c108, redis_name, refresh)

    def get_recent_date(self, refresh=False) -> Optional[datetime.datetime]:
        redis_name = f"{self.code_page}_{self.REDIS_RECENT_DATE_SUFFIX}"

        def fetch_get_recent_date() -> Optional[datetime.datetime]:
            return self.mymongo_c108.get_recent_date()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent_date)

    @classmethod
    def bulk_get_recent_date(cls, codes: List[str], refresh=False) -> Dict[str, datetime.datetime]:
        redis_names = [f"{code}.c108_{cls.REDIS_RECENT_DATE_SUFFIX}" for code in codes]
        return cls.bulk_get_or_compute(
            redis_names,
            lambda redis_name: cls(redis_name.split('.')[0]).get_recent_date(refresh=True),
            refresh=refresh)

    def get_recent(self, refresh=False) -> Optional[List[dict]]:
        """
        저장된 데이터에서 가장 최근 날짜의 딕셔너리를 가져와서 리스트로 포장하여 반환한다.

        Returns:
            list: 한 날짜에 c108 딕셔너리가 여러개 일수 있어서 리스트로 반환한다.
        """
        redis_name = self.code_page + '_recent'

        def fetch_get_recent() -> Optional[List[dict]]:
            return self.mymongo_c108.get_recent()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent)