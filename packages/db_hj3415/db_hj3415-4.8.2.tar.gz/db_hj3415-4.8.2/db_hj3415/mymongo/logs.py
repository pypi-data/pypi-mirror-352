from typing import List, Dict
from datetime import datetime

from db_hj3415.mymongo.base import Base
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')

class Logs(Base):
    """logs 데이터베이스 클래스

    Note:
        db - logs\n
        col - 'cli', 'mongo', 'dart'
        doc - timestamp, level, message\n
    """
    COL_TITLE = ('cli', 'mongo', 'dart')

    def __init__(self, table: str):
        super().__init__(db='logs', table=table)

    @property
    def table(self) -> str:
        return self.table

    @table.setter
    def table(self, table: str):
        assert table in self.COL_TITLE, f'Invalid value : {table}({self.COL_TITLE})'
        self.table = table

    # ========================End Properties=======================

    @classmethod
    def save(cls, table: str, level: str, message: str) -> bool:
        assert table in cls.COL_TITLE, f'Invalid value : {table}({cls.COL_TITLE})'
        assert level in ['DEBUG', 'INFO', 'WARNING',
                         'ERROR'], f"Invalid level : {level}({'DEBUG', 'INFO', 'WARNING', 'ERROR'})"
        data = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message
        }
        result = cls.get_client()['logs'][table].insert_one(data)
        return result.acknowledged

    def get_all(self, reverse=True, top='all') -> List[Dict]:
        log_list = list(self._col.find())

        """
        # timestamp를 분까지 나오도록 변환
        for log in log_list:
            if "timestamp" in log:  # timestamp 필드가 있을 경우에만 처리
                original_timestamp = log["timestamp"]
                # datetime 형식으로 변환 후 분까지만 포맷
                formatted_timestamp = original_timestamp.strftime("%Y-%m-%d %H:%M")
                log["timestamp"] = formatted_timestamp  # 기존 필드 업데이트
        """

        sorted_log_list = sorted(log_list, key=lambda x: x['timestamp'], reverse=reverse)
        if top == 'all':
            return sorted_log_list
        else:
            if isinstance(top, int):
                return sorted_log_list[:top]
            else:
                raise ValueError("top 인자는 'all' 이나 int형 이어야 합니다.")

    @classmethod
    def get_abnormals_in_all_logs(cls, reverse=True, top='all') -> List[Dict]:
        abnormals = []
        logs_db = cls._client['logs']
        for table in cls.COL_TITLE:
            collection = logs_db[table]

            # "level"이 "WARNING" 또는 "ERROR"인 문서 필터링
            query = {"level": {"$in": ["WARNING", "ERROR"]}}
            abnormals.extend(list(collection.find(query)))

            """
            # timestamp를 분까지 나오도록 변환
            for log in documents:
                if "timestamp" in log:  # timestamp 필드가 있을 경우에만 처리
                    original_timestamp = log["timestamp"]
                    # datetime 형식으로 변환 후 분까지만 포맷
                    formatted_timestamp = original_timestamp.strftime("%Y-%m-%d %H:%M")
                    log["timestamp"] = formatted_timestamp  # 기존 필드 업데이트
            """


        mylogger.info(f"abnormals : {abnormals}")

        sorted_abnormals = sorted(abnormals, key=lambda x: x['timestamp'], reverse=reverse)
        if top == 'all':
            return sorted_abnormals
        else:
            if isinstance(top, int):
                return sorted_abnormals[:top]
            else:
                raise ValueError("top 인자는 'all' 이나 int형 이어야 합니다.")