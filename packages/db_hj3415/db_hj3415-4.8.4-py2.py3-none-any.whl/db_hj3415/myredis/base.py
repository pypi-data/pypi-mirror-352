from typing import Optional, Callable, Any, List, Dict
import os
import redis
import pickle

from utils_hj3415 import setup_logger, tools
mylogger = setup_logger(__name__,'WARNING')


def connect_to_redis(addr: str, password: str) -> redis.Redis:
    mylogger.info(f"Connect to Redis ... Server Addr : {addr}")
    # decode_responses=False 로 설정해서 바이트 반환시켜 피클을 사용할 수 있도록한다.
    return redis.StrictRedis(host=addr, port=6379, db=0, decode_responses=False, password=password)


class Base:
    """
    Redis 캐싱을 위한 기본 클래스
    """
    _client = None
    _expire_time_h = None

    def __init__(self):
        self.redis_client = self.get_client()

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = connect_to_redis(addr=os.getenv('REDIS_ADDR'), password=os.getenv('REDIS_PASSWORD', ''))
        if cls._expire_time_h is None:
            cls._expire_time_h = tools.to_int(os.getenv('REDIS_EXPIRE_TIME_H', '48'))
        return cls._client

    @classmethod
    def exists(cls, key_name: str) -> bool:
        """
        주어진 키가 Redis에 존재하는지 확인합니다.

        :param key_name: 확인할 Redis 키 이름
        :return: 키가 존재하면 True, 그렇지 않으면 False
        """
        if cls.get_client().exists(key_name):
            return True
        else:
            return False

    @classmethod
    def get_ttl(cls, redis_name: str) -> Optional[int]:
        """
        Redis에서 특정 키의 TTL(남은 유효 시간)을 가져옵니다.

        :param redis_name: TTL을 확인할 Redis 키 이름
        :return: TTL 값(초 단위), 키가 없거나 TTL이 없을 경우 None
        """
        ttl = cls.get_client().ttl(redis_name)

        if ttl == -1:
            mylogger.warning(f"{redis_name}는 만료 시간이 설정되어 있지 않습니다.")
            return None
        elif ttl == -2:
            mylogger.warning(f"{redis_name}는 Redis에 존재하지 않습니다.")
            return None
        else:
            mylogger.debug(f"{redis_name}의 남은 시간은 {ttl}초입니다.")
            return ttl


    @classmethod
    def delete(cls, redis_name: str):
        """
        Redis에서 특정 키를 삭제합니다. 키가 존재하지 않아도 오류 없이 진행됩니다.

        :param redis_name: 삭제할 Redis 키 이름
        """
        mylogger.debug(Base.list_redis_names())
        cls.get_client().delete(redis_name)
        mylogger.debug(Base.list_redis_names())

    @classmethod
    def delete_all_with_pattern(cls, pattern: str):
        """
        주어진 패턴과 일치하는 모든 Redis 키를 삭제합니다.

        :param pattern: 삭제할 키의 패턴 (예: 'prefix*'는 prefix로 시작하는 모든 키를 삭제)
        """
        mylogger.debug(cls.list_redis_names())
        # SCAN 명령어를 사용하여 패턴에 맞는 키를 찾고 삭제
        client = cls.get_client()
        cursor = '0'
        while cursor != 0:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=1000)
            if keys:
                client.delete(*keys)

        mylogger.debug(cls.list_redis_names())


    @classmethod
    def list_redis_names(cls, filter:str="all") -> list:
        """
        Redis에서 특정 필터와 일치하는 키 목록을 반환합니다.

        :param filter: 검색할 키의 필터. 기본값은 "all" (모든 키 반환)
        :return: 필터에 맞는 Redis 키 목록 (정렬됨)
        """
        # SCAN 명령어 파라미터
        pattern = b"*" if filter == "all" else f"*{filter}*".encode('utf-8')  # 부분 일치: *filter*
        mylogger.debug(f"pattern : {pattern}")
        cursor = "0"
        matched_keys = []

        while True:
            # SCAN 호출
            cursor, keys = cls.get_client().scan(cursor=cursor, match=pattern, count=1000)
            mylogger.debug(f"cursor : {cursor}/{type(cursor)}")
            matched_keys.extend(keys)
            # 커서가 '0'이면 스캔이 끝났다는 의미
            if str(cursor) == "0":
                break

        return sorted(matched_keys)

    @classmethod
    def set_value(cls, redis_name: str, value: Any) -> None:
        """
        Redis에 데이터를 저장합니다.

        :param redis_name: 저장할 Redis 키 이름
        :param value: 저장할 데이터 (pickle을 사용하여 직렬화)
        """
        cls.get_client().setex(redis_name, cls._expire_time_h*3600, pickle.dumps(value))
        mylogger.debug(f"Redis 캐시에 저장 (만료시간: {cls._expire_time_h}시간) - redis_name : {redis_name}")


    @classmethod
    def get_value(cls, redis_name: str) -> Any:
        """
        Redis에서 데이터를 가져옵니다.

        :param redis_name: 가져올 Redis 키 이름
        :return: 저장된 데이터 (pickle을 사용하여 역직렬화)
        """
        stored_data = cls.get_client().get(redis_name)  # 키 "my_key"의 값을 가져옴
        value = pickle.loads(stored_data) if stored_data is not None else None # type: ignore
        return value


    @classmethod
    def fetch_and_cache_data(cls, redis_name: str, refresh: bool, fetch_function: Callable, *args) -> Any:
        """
        Redis에서 캐시된 데이터를 가져오거나, 존재하지 않으면 제공된 함수를 실행하여 데이터를 가져온 후 캐시에 저장합니다.

        :param redis_name: Redis에 저장할 키 이름
        :param refresh: True이면 캐시를 강제로 갱신
        :param fetch_function: 데이터를 가져오는 함수
        :param args: fetch_function에 전달할 추가 인자
        :return: 가져온 데이터 (pickle을 사용하여 역직렬화 가능)
        """
        if not refresh:
            value = cls.get_value(redis_name)
            ttl_hours = round(cls.get_client().ttl(redis_name) / 3600, 1)
            mylogger.debug(f"Redis 캐시에서 데이터 가져오기 (남은시간: {ttl_hours} 시간) - redis_name : {redis_name}")
            if value:
                return value

        # 캐시된 데이터가 없거나 refresh=True인 경우
        value = fetch_function(*args)

        if value:
            cls.set_value(redis_name=redis_name, value=value)
        return value

    @classmethod
    def bulk_get_data(cls, redis_names: List[str]) -> Dict[str, Any]:
        pipe = cls.get_client().pipeline()
        for redis_name in redis_names:
            pipe.get(redis_name)
        results_from_redis = pipe.execute()  # [val1, val2, ...]

        final_results = {}

        for redis_name, val in zip(redis_names, results_from_redis):
            if val is None:
                final_results[redis_name] = None
            else:
                # Redis에 pickled 데이터가 있다면 언피클해서 담기
                data = pickle.loads(val)
                final_results[redis_name] = data

        return final_results

    @classmethod
    def bulk_get_or_compute(cls,
                            keys: List[str],
                            compute_function: Callable[[str], Any],
                            refresh: bool) -> Dict[str, Any]:
        """
        Redis 캐싱을 활용하여 데이터 조회 또는 계산 수행

        :param keys: Redis 키 목록
        :param compute_function: Redis에 없을 경우 실행할 함수 (입력값: key)
        :param refresh: True면 기존 캐시를 무시하고 다시 계산
        :return: {key: value} 형태의 결과 딕셔너리
        """
        client = cls.get_client()
        pipe = client.pipeline()

        # --- (1) Redis에서 기존 값 조회 ---
        for key in keys:
            pipe.get(key)
        results_from_redis = pipe.execute()  # [val1, val2, ...]

        final_results = {}
        missing_keys = []

        # refresh=True이면 기존 데이터를 무시하고 새로 계산
        if refresh:
            missing_keys = keys[:]
        else:
            # refresh=False이면 Redis 값이 None인 것만 다시 계산
            for key, val in zip(keys, results_from_redis):
                if val is None:
                    missing_keys.append(key)
                else:
                    final_results[key] = pickle.loads(val)  # Redis에서 불러온 데이터 언피클링

        # --- (2) 캐시에 없는 값 계산 ---
        newly_computed_data = {}
        for key in missing_keys:
            computed_data = compute_function(key)
            newly_computed_data[key] = computed_data

        # --- (3) Redis에 새 값 저장 ---
        if newly_computed_data:
            pipe = client.pipeline()
            for key, data in newly_computed_data.items():
                pickled_data = pickle.dumps(data)
                pipe.setex(key, cls._expire_time_h*3600, pickled_data)
            pipe.execute()

        # 최종 결과 반환 (캐시에서 찾은 것 + 새로 계산한 것)
        final_results.update(newly_computed_data)
        return final_results