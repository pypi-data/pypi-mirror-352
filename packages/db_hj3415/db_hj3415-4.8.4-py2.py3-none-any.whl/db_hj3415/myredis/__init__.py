"""
redis 서버를 이용해서 mongodb의 데이터를 캐시한다.
데이터의 캐시 만료는 데이터를 업데이트 시키는 모듈인 scraper_hj3415에서 담당하고
여기서 재가공해서 만들어지는 데이터는 만료기간을 설정한다.
장고에서 필요한 데이터를 보내는 기능이 주임.
"""

from db_hj3415.myredis.base import Base, connect_to_redis
from db_hj3415.myredis.c101 import C101
from db_hj3415.myredis.c106 import C106
from db_hj3415.myredis.c108 import C108
from db_hj3415.myredis.c1034 import C103, C104
from db_hj3415.myredis.corps import Corps
from db_hj3415.myredis.dart import Dart
from db_hj3415.myredis.dart_today import DartToday
from db_hj3415.myredis.mi import MI
