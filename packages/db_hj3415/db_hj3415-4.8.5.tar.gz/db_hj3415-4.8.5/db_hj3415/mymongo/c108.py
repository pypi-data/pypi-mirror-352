from pymongo import ASCENDING, DESCENDING
from typing import Optional, Any
import datetime
import pandas as pd
import time

from utils_hj3415 import tools, setup_logger
from db_hj3415.mymongo.corps import Corps

mylogger = setup_logger(__name__,'WARNING')

class C108(Corps):
    def __init__(self, code: str):
        super().__init__(code=code, page='c108')

    @classmethod
    def save(cls, code: str, c108_data: pd.DataFrame):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        client = cls.get_client()
        page = 'c108'

        if c108_data.empty:
            mylogger.warning(f'입력된 {code}/{page} 데이터프레임이 비어서 저장은 하지 않습니다.')
            return

        mylogger.info(f"데이터를 저장하기 전, {code} / {page} 데이터베이스를 삭제합니다.")
        cls.drop(db=code, table=page)
        time.sleep(1)

        client[code][page].create_index([('날짜', ASCENDING)], unique=False)

        mylogger.debug(c108_data)
        # 이제 df를 각 row(dict) 형태로 변환
        records = c108_data.to_dict('records')
        mylogger.debug(records)
        result = client[code][page].insert_many(records)
        mylogger.debug(f"Inserted document IDs: {result.inserted_ids}")

    def get_recent_date(self) -> Optional[datetime.datetime]:
        """
        Finds the most recent date available in the stored database for a specific field.

        Summary:
        This method interacts with the database collection to retrieve the most
        recent date from records containing a specific field '날짜'. It utilizes
        database operations like sorting and retrieves the first entry sorted in
        descending order by date. If no such field exists in the collection, it
        returns None. The date is then converted from a string format to a
        datetime object before returning.

        Returns:
            Optional[datetime.datetime]: The most recent date in the collection
            as a datetime object, or None if no valid date is found within the data.
        """
        # 저장되어 있는 데이터베이스의 최근 날짜를 찾는다.
        try:
            r_date = self._col.find({'날짜': {'$exists': True}}).sort('날짜', DESCENDING).next()['날짜']
        except StopIteration:
            # 날짜에 해당하는 데이터가 없는 경우
            return None

        return datetime.datetime.strptime(r_date, '%y/%m/%d')

    def get_recent(self) -> Optional[list[Any]]:
        """

        저장된 데이터에서 가장 최근 날짜의 딕셔너리를 가져와서 리스트로 포장하여 반환한다.

        Returns:
            list: 한 날짜에 c108 딕셔너리가 여러개 일수 있어서 리스트로 반환한다.
        """
        try:
            r_date = self.get_recent_date().strftime('%y/%m/%d')
        except AttributeError:
            # 최근데이터가 없어서 None을 반환해서 에러발생한 경우
            return None
        # 찾은 날짜를 바탕으로 데이터를 검색하여 리스트로 반환한다.
        r_list = []
        for r_c108 in self._col.find({'날짜': {'$eq': r_date}}):
            del r_c108['_id']
            r_list.append(r_c108)
        return r_list

