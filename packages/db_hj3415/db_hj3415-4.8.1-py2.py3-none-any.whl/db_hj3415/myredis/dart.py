from typing import Optional, List, Dict
import datetime

from db_hj3415.myredis.corps import Corps
from db_hj3415 import mymongo


class Dart(Corps):
    REDIS_RECENT_DATE_SUFFIX = 'recent_date'

    def __init__(self, code: str):
        super().__init__(code, 'dart')
        self.mymongo_dart = mymongo.Dart(code)

    def get_recent_date(self, refresh=False) -> Optional[datetime.datetime]:
        redis_name = f"{self.code_page}_{self.REDIS_RECENT_DATE_SUFFIX}"

        def fetch_get_recent_date() -> Optional[datetime.datetime]:
            return self.mymongo_dart.get_recent_date()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent_date)

    @classmethod
    def bulk_get_recent_date(cls, codes: List[str], refresh=False) -> Dict[str, datetime.datetime]:
        redis_names = [f"{code}.dart_{cls.REDIS_RECENT_DATE_SUFFIX}" for code in codes]
        return cls.bulk_get_or_compute(
            redis_names,
            lambda redis_name: cls(redis_name.split('.')[0]).get_recent_date(refresh=True),
            refresh=refresh)

