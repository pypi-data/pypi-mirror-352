from pymongo import errors, ASCENDING, DESCENDING

from utils_hj3415 import tools
from .corps import Corps

from utils_hj3415 import setup_logger
mylogger = setup_logger(__name__,'WARNING')


class C101(Corps):
    PAGES = ('c101',)

    def __init__(self, code: str):
        super().__init__(code=code, page='c101')

    @classmethod
    def save(cls, code: str,  c101_data: dict) -> bool:
        """
        c101의 구조에 맞는 딕셔너리값을 받아서 구조가 맞는지 확인하고 맞으면 저장한다.
        """
        assert tools.is_6digit(code), f'Invalid value : {code}'
        page = 'c101'
        client = cls.get_client()

        c101_template = ['date', 'code', '종목명', '업종', '주가', '거래량', 'EPS', 'BPS', 'PER', '업종PER', 'PBR',
                         '배당수익률', '최고52주', '최저52주', '거래대금', '시가총액', '베타52주', '발행주식', '유동비율', '외국인지분율']

        # 리스트 비교하기
        # reference from https://codetorial.net/tips_and_examples/compare_two_lists.html
        if c101_data['code'] != code:
            raise Exception("Code isn't equal input data and db data..")
        mylogger.debug(c101_data.keys())
        # c101 데이터가 c101_template의 내용을 포함하는가 확인하는 if문
        # refered from https://appia.tistory.com/101
        if (set(c101_template) - set(c101_data.keys())) == set():
            # 스크랩한 날짜 이후의 데이터는 조회해서 먼저 삭제한다.
            del_query = {'date': {"$gte": c101_data['date']}}
            client[code][page].create_index([('date', ASCENDING)], unique=True)
            try:
                result = client[code][page].insert_one(c101_data)
            except errors.DuplicateKeyError:
                client[code][page].delete_many(del_query)
                result = client[code][page].insert_one(c101_data)
            return result.acknowledged
        else:
            raise Exception('Invalid c101 dictionary structure..')

    @staticmethod
    def merge_intro(c101_dict: dict) -> dict:
        # intro를 합치기 위해 내부적으로 사용
        c101_dict['intro'] = c101_dict.get('intro1', '') + c101_dict.get('intro2', '') + c101_dict.get('intro3', '')
        try:
            del c101_dict['intro1']
        except KeyError:
            pass
        try:
            del c101_dict['intro2']
        except KeyError:
            pass
        try:
            del c101_dict['intro3']
        except KeyError:
            pass
        return c101_dict

    def get_recent(self, merge_intro=False) -> dict:
        """
        저장된 데이터에서 가장 최근 날짜의 딕셔너리를 반환한다.
        """
        try:
            d = dict(self._col.find({'date': {'$exists': True}}, {"_id": 0}).sort('date', DESCENDING).next())
            # del doc['_id'] - 위의 {"_id": 0} 으로 해결됨.
            if merge_intro:
                d = C101.merge_intro(d)
        except StopIteration:
            mylogger.warning("There is no data on C101")
            d = {}
        return d

    def find(self, date: str, merge_intro=False) -> dict:
        """
        해당 날짜의 데이터를 반환한다.
        만약 리턴값이 없으면 {} 을 반환한다.

        Args:
            date (str): 예 - 20201011(6자리숫자)
            merge_intro: intro를 합칠 것인지
        """
        assert tools.isYmd(date), f'Invalid date format : {date}(ex-20201011(8자리숫자))'
        converted_date = date[:4] + '.' + date[4:6] + '.' + date[6:]
        try:
            d = dict(self._col.find_one({'date': converted_date}))
        except TypeError:
            mylogger.warning(f"There is no data (date:{date}) on C101")
            return {}

        if merge_intro:
            d = C101.merge_intro(d)
        del d['_id']
        return d

    def get_trend(self, title: str) -> dict:
        """
        title에 해당하는 데이터베이스에 저장된 모든 값을 {날짜: 값} 형식의 딕셔너리로 반환한다.

        title should be in ['BPS', 'EPS', 'PBR', 'PER', '주가', '배당수익률', '베타52주', '거래량']

        리턴값 - 주가
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
        titles = ['BPS', 'EPS', 'PBR', 'PER', '주가', '배당수익률', '베타52주', '거래량']
        assert title in titles, f"title should be in {titles}"
        items = dict()
        for doc in self._col.find({'date': {'$exists': True}}, {"_id": 0, "date": 1, f"{title}": 1}).sort('date', ASCENDING):
            items[doc['date']] = doc[f'{title}']
        return items