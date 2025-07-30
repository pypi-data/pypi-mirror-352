from typing import Optional, List

from db_hj3415.mymongo.base import Base
from utils_hj3415 import setup_logger
from dataclasses import dataclass, asdict
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

mylogger = setup_logger(__name__, level='INFO')

class Flask(Base):
    COL_TITLE = ('favorites',)

    def __init__(self, table: str):
        super().__init__(db='flask', table=table)

    @property
    def table(self) -> str:
        return self.table

    @table.setter
    def table(self, table: str):
        assert table in self.COL_TITLE, f'Invalid value : {table}({self.COL_TITLE})'
        self.table = table

@dataclass
class Stock:
    code: str
    name: str
    purchase_price: float
    purchase_quantity: int


class Favorites(Flask):
    def __init__(self):
        super().__init__('favorites')
        self._col.create_index("code", unique=True)

    def save(self, data: Stock) -> bool:
        try:
            result = self._col.insert_one(asdict(data)) # type: ignore
            return result.acknowledged
        except DuplicateKeyError:
            mylogger.error(f"이미 동일한 code가 존재합니다: {data.code}")
            return False

    def get(self, code: str) -> Optional[Stock]:
        data = self._col.find_one({"code": code}, {"_id": 0})  # _id 제외
        if data:
            stock_obj = Stock(**data)  # dict → dataclass 변환
            mylogger.debug(f'Stock : {stock_obj}')
            return stock_obj
        return None

    def get_all(self) -> List[Stock]:
        documents = list(self._col.find({}, {"_id": 0}))  # 모든 문서 조회, _id 제외
        return [Stock(**doc) for doc in documents]  # 변환

    def get_all_codes(self) -> list:
        return [stock.code for stock in self.get_all()]

    def update(self, new_data: Stock) -> Optional[Stock]:
        """code를 이용해 Stock 데이터를 업데이트하고, 업데이트된 데이터를 반환"""
        updated_data = self._col.find_one_and_update(
            {"code": new_data.code},  # 조회 조건
            {"$set": asdict(new_data)},  # type: ignore
            return_document=ReturnDocument.AFTER  # 업데이트 후의 문서를 반환
        )
        if updated_data:
            updated_data.pop("_id", None)  # type: ignore
            return Stock(**updated_data)  # dict → dataclass 변환
        return None  # 업데이트 실패 (해당 코드 없음)

    def delete(self, code: str) -> bool:
        """code를 이용해 Stock 데이터를 삭제"""
        result = self._col.delete_one({"code": code})
        return result.deleted_count > 0  # 삭제 성공 여부 반환

