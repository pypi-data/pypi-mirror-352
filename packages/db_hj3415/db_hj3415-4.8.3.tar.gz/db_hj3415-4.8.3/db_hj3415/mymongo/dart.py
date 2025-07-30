from pymongo import ASCENDING, DESCENDING, errors
from typing import Optional, List, Dict
import datetime

from utils_hj3415 import tools, setup_logger
from db_hj3415.mymongo.corps import Corps
from db_hj3415.mymongo.logs import Logs

mylogger = setup_logger(__name__,'WARNING')


class Dart(Corps):
    """
    공시 overview 예시
    {'corp_cls': 'Y',
    'corp_code': '00414850',
    'corp_name': '효성 ITX',
    'flr_nm': '효성 ITX',
    'rcept_dt': '20240830',
    'rcept_no': '20240830800804',
    'report_nm': '[기재정정]거래처와의거래중단',
    'rm': '유',
    'stock_code': '094280'}
    """
    def __init__(self, code: str):
        super().__init__(code=code, page='dart')

    @classmethod
    def save(cls, code: str, dart_data: dict) -> bool:
        """
        dart overview의 구조에 맞는 딕셔너리값을 받아서 구조가 맞는지 확인하고 맞으면 저장한다.
        공시 dart_data 예시
        {'corp_cls': 'Y',
        'corp_code': '00414850',
        'corp_name': '효성 ITX',
        'flr_nm': '효성 ITX',
        'rcept_dt': '20240830',
        'rcept_no': '20240830800804',
        'report_nm': '[기재정정]거래처와의거래중단',
        'rm': '유',
        'stock_code': '094280'}
        :param code:
        :param dart_data:
        :return:
        """
        assert tools.is_6digit(code), f'Invalid value : {code}'
        client = cls.get_client()
        page = 'dart'

        dart_template = ['corp_cls', 'corp_code', 'corp_name', 'flr_nm', 'rcept_dt', 'rcept_no', 'report_nm', 'rm', 'stock_code', 'link']

        # 리스트 비교하기
        # reference from https://codetorial.net/tips_and_examples/compare_two_lists.html
        if dart_data['stock_code'] != code:
            raise Exception("Code isn't equal input data and db data..")
        mylogger.debug(dart_data.keys())

        # dart 데이터가 dart_template의 내용을 포함하는가 확인하는 if문
        # refered from https://appia.tistory.com/101
        if (set(dart_template) - set(dart_data.keys())) == set():
            client[code][page].create_index([('rcept_no', ASCENDING)], unique=True)
            try:
                result = client[code][page].insert_one(dart_data)
                Logs.save('dart', 'INFO', f"{code} / {dart_data['corp_name']} / {dart_data['report_nm'].strip()} 을 저장")
                return result.acknowledged
            except errors.DuplicateKeyError:
                return True
        else:
            raise Exception('dart 딕셔너리 구조가 맞지 않습니다. 혹시 link를 추가하는 것을 잊었을까요..')

    def get_all(self) -> List[Dict]:
        """
        각 아이템의 구조 - ['corp_cls', 'corp_code', 'corp_name', 'flr_nm', 'rcept_dt', 'rcept_no', 'report_nm', 'rm', 'stock_code', 'link']
        """
        return list(self._col.find({}, {"_id": 0}).sort('rcept_no', DESCENDING))

    def get_recent_date(self) -> Optional[datetime.datetime]:
        # 저장되어 있는 데이터베이스의 최근 날짜를 찾는다.
        try:
            r_date = self._col.find({'rcept_dt': {'$exists': True}}).sort('rcept_dt', DESCENDING).next()['rcept_dt']
        except StopIteration:
            # 날짜에 해당하는 데이터가 없는 경우
            return None

        return datetime.datetime.strptime(r_date, '%Y%m%d')