from typing import Tuple
from pymongo import ASCENDING, DESCENDING

from db_hj3415.mymongo.base import Base
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')

class MI(Base):
    """mi 데이터베이스 클래스

    Note:
        db - mi\n
        col - 'aud', 'chf', 'gbond3y', 'gold', 'silver', 'kosdaq', 'kospi', 'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'usdidx' - 총 13개\n
        doc - date, value\n
    """
    COL_TITLE = ('aud', 'chf', 'gbond3y', 'gold', 'silver', 'kosdaq', 'kospi',
                 'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'usdidx')

    def __init__(self, index: str):
        super().__init__(db='mi', table=index)

    @property
    def index(self) -> str:
        return self.table

    @index.setter
    def index(self, index: str):
        assert index in self.COL_TITLE, f'Invalid value : {index}({self.COL_TITLE})'
        self.table = index

    # ========================End Properties=======================

    def get_recent(self) -> Tuple[str, float]:
        """저장된 가장 최근의 값을 반환하는 함수
        """
        try:
            d = dict(self._col.find({'date': {'$exists': True}}, {"_id": 0}).sort('date', DESCENDING).next())
            # del doc['_id'] - 위의 {"_id": 0} 으로 해결됨.
            return str(d['date']), float(d['value'])
        except StopIteration:
            mylogger.warning(f"There is no data on {self.index}")
            return '', float('nan')

    def get_trend(self) -> dict:
        """
        해당하는 인덱스의 전체 트렌드를 딕셔너리로 반환한다.
        리턴값 - index
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
        items = dict()
        for doc in self._col.find({'date': {'$exists': True}}, {"_id": 0, "date": 1, "value": 1}).sort('date', ASCENDING):
            items[doc['date']] = doc['value']
        return items

    @classmethod
    def save(cls, index: str, mi_data: dict) -> bool:
        """MI 데이터 저장

        Args:
            index (str): 'aud', 'chf', 'gbond3y', 'gold', 'silver', 'kosdaq', 'kospi', 'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'usdidx'
            mi_data (dict): ex - {'date': '2021.07.21', 'value': '1154.50'}
        """
        assert index in cls.COL_TITLE, f'Invalid value : {index}({cls.COL_TITLE})'
        client = cls.get_client()

        client['mi'][index].create_index([('date', ASCENDING)], unique=True)
        # scraper에서 해당일 전후로 3일치 데이터를 받아오기때문에 c101과는 다르게 업데이트 한다.
        result = client['mi'][index].update_one(
            {'date': mi_data['date']}, {"$set": {'value': mi_data['value']}}, upsert=True)
        return result.acknowledged
