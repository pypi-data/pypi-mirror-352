from typing import List

from db_hj3415.myredis.base import Base
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


class DartToday(Base):
    redis_name = 'dart_today'

    def save(self, data: List[dict]):
        # 이전 내용을 삭제하고...
        self.delete(self.redis_name)
        # 데이터를 Redis에 캐싱, 60분후 키가 자동으로 제거됨
        self.set_value(self.redis_name, data)

    def get(self) -> List[dict]:
        cached_data = self.get_value(self.redis_name)
        mylogger.debug(type(cached_data))
        mylogger.debug(cached_data)
        if cached_data is None:
            mylogger.debug(f"dart today data : []")
            return []
        else:
            # rcept_no를 기준으로 정렬한다.
            sorted_list = sorted(cached_data, key=lambda x: x['rcept_no'])
            mylogger.debug(f"dart today data(total:{len(sorted_list)}) : {sorted_list[:1]}..")
            return sorted_list