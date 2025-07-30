from typing import List, Dict

from db_hj3415 import mymongo
from db_hj3415.myredis.corps import Corps

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, level='WARNING')


class C101(Corps):
    REDIS_RECENT_SUFFIX = 'recent_data'
    def __init__(self, code: str):
        super().__init__(code, 'c101')
        self.mymongo_c101 = mymongo.C101(code)

    @property
    def code(self) -> str:
        return super().code

    @code.setter
    def code(self, code: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C101, self.__class__).code.__set__(self, code) # type: ignore
        self.mymongo_c101.code = self.code

    def get_recent(self, refresh=False) -> dict:
        # code_page 앞 11글자가 코드와 c101 페이지임.
        redis_name = f"{self.code_page}_{self.REDIS_RECENT_SUFFIX}"

        def fetch_get_recent() -> dict:
           return self.mymongo_c101.get_recent(merge_intro=True)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent)

    def get_trend(self, title: str, refresh=False) -> dict:
        """
        title에 해당하는 데이터베이스에 저장된 모든 값을 {날짜: 값} 형식의 딕셔너리로 반환한다.

        title should be in ['BPS', 'EPS', 'PBR', 'PER', '주가', '배당수익률', '베타52주', '거래량']

        리턴값 - 주가
        {'2023.04.05': '63900',
         '2023.04.06': '62300',
         '2023.04.07': '65000',
         '2023.04.10': '65700',
         '2023.04.11': '65900',
         '2023.04.12': '66000',
         '2023.04.13': '66100',
         '2023.04.14': '65100',
         '2023.04.17': '65300'}
        """
        # code_page 앞 11글자가 코드와 c101 페이지임.
        redis_name = self.code_page + '_trend'

        def fetch_get_trend(title_in) -> dict:
            return self.mymongo_c101.get_trend(title_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_trend, title)

    @classmethod
    def bulk_get_recent(cls, codes: List[str], refresh=False) -> Dict[str, dict]:
        redis_names = [f"{code}.c101_{cls.REDIS_RECENT_SUFFIX}" for code in codes]
        return cls.bulk_get_or_compute(
            redis_names,
            lambda redis_name: cls(redis_name.split('.')[0]).get_recent(refresh=True),
            refresh=refresh)