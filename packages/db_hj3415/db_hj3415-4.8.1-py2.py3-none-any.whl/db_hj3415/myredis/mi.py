from typing import Tuple

from db_hj3415.myredis.base import Base
from db_hj3415 import mymongo
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


class MI(Base):
    def __init__(self, index: str):
        """mi 데이터베이스 클래스

        Note:
            db - mi\n
            col - 'aud', 'chf', 'gbond3y', 'gold', 'silver', 'kosdaq', 'kospi', 'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'usdidx' - 총 13개\n
            doc - date, value\n
        """
        assert index in mymongo.MI.COL_TITLE, f'Invalid value : {index}({mymongo.MI.COL_TITLE})'
        self.mymongo_mi = mymongo.MI(index)
        self.mi_index = 'mi' + '.' + index
        self._index = index
        super().__init__()

    def __str__(self):
        return f"redis name : {self.mi_index}"

    @property
    def index(self) -> str:
        return self._index

    @index.setter
    def index(self, index: str):
        assert index in mymongo.MI.COL_TITLE, f'Invalid value : {index}({mymongo.MI.COL_TITLE})'
        mylogger.info(f'Change index : {self.index} -> {index}')
        self.mymongo_mi.index = index
        self.mi_index = self.mi_index[:3] + index
        self._index = index

    def get_recent(self, refresh=False) -> Tuple[str, float]:
        redis_name = self.mi_index + '_recent'

        def fetch_get_recent() -> Tuple[str, float]:
            return self.mymongo_mi.get_recent()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent)

    def get_trend(self, refresh=False) -> dict:
        redis_name = self.mi_index + '_trend'

        def fetch_get_trend() -> dict:
            return self.mymongo_mi.get_trend()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_trend)
