from pymongo import ASCENDING, DESCENDING
from typing import Optional
from datetime import datetime
from chatgpt_hj3415 import chatgpt

from utils_hj3415 import tools, setup_logger
from db_hj3415.mymongo.corps import Corps

mylogger = setup_logger(__name__,'WARNING')

class AIReport(Corps):
    def __init__(self, code: str):
        super().__init__(code=code, page='ai_report')

    @classmethod
    def save(cls, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        client = cls.get_client()
        page = 'ai_report'

        # MongoDB는 datetime.date 타입을 저장할 수 없고 datetime.datetime만 허용
        today = datetime.today()
        report_date = datetime(today.year, today.month, today.day)
        report_text = chatgpt.run(code)

        client[code][page].create_index([('report_date', ASCENDING)], unique=True)

        # 덮어쓰기 (업서트)
        client[code][page].update_one(
            {"report_date": report_date},  # 조건: 오늘 날짜
            {
                "$set": {
                    "content": report_text
                }
            },
            upsert=True  # 없으면 insert, 있으면 update
        )


    def get_recent_date(self) -> Optional[datetime]:
        """
        저장된 보고서 중 가장 최근 report_date 를 반환.
        저장 문서가 하나도 없으면 None 반환.
        """
        # report_date 내림차순 정렬 후 맨 위 문서 하나 조회
        doc = self._col.find_one(
            {},  # 조건 없음 (컬렉션 전체)
            sort=[("report_date", DESCENDING)],  # 최신순
            projection={"_id": 0, "report_date": 1}
        )

        return doc["report_date"] if doc else None

    def get_recent(self) -> Optional[str]:
        """
        저장된 AI 리포트 중 가장 최근 날짜의 content를 반환.
        없으면 None 반환.
        """
        # 가장 최근(report_date DESC) 한 건 조회
        doc = self._col.find_one(
            {},  # 조건: 해당 종목 전체
            {"_id": 0, "content": 1},  # projection: content만
            sort=[("report_date", DESCENDING)]  # 최신순 정렬
        )

        return doc["content"] if doc else None
