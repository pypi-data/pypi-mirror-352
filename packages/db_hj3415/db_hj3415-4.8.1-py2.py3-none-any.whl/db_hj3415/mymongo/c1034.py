import math
import copy
from abc import ABC, abstractmethod
from typing import List, Tuple
from collections import OrderedDict

from utils_hj3415 import tools, setup_logger

from db_hj3415.mymongo.corps import Corps

mylogger = setup_logger(__name__,'WARNING')


class C1034(Corps, ABC):
    def __init__(self, code: str, page: str):
        super().__init__(code=code, page=page)

    def list_row_titles(self) -> list:
        titles = []
        for item in self.list_rows():
            titles.append(item['항목'])
        return list(set(titles))

    def _find(self, row_title: str, refine_words=None) -> Tuple[int, List[dict]]:
        """
        _id는 내부에서 제거하기때문에 refine 하지 않아도 됨.
        c103의 경우는 중복되는 이름의 항목이 있기 때문에
        이 함수는 반환되는 딕셔너리 리스트와 갯수로 구성되는 튜플을 반환한다.
        :param row_title: 해당하는 항목을 검색하여 딕셔너리를 포함한 리스트로 반환
        :param refine_words: 리스트 형식으로 없애자하는 col_title을 넣어준다.
        :return:
        """
        if refine_words is None:
            # 빈리스트는 아무 col_title도 없애지 않는다는 뜻임
            refine_words = []
        else:
            assert isinstance(refine_words, List), "refine_words 는 리스트 형식이어야 합니다."

        # _id는 삭제하기 위해 넣어준다.
        refine_words.append('_id')

        count = 0
        data_list = []
        for data in self._col.find({'항목': {'$eq': row_title}}):
            # 도큐먼트에서 title과 일치하는 항목을 찾아낸다.
            count += 1
            # refine_data함수를 통해 삭제를 원하는 필드를 제거하고 data_list에 추가한다.
            data_list.append(Corps.refine_data(data, refine_words))
        return count, data_list

    @abstractmethod
    def find(self, row_title: str, remove_yoy: bool, del_unnamed_key: bool) -> Tuple[int, dict]:
        """
        :param row_title: 해당하는 항목을 반환한다.
        :param remove_yoy: 전분기대비, 전년대비를 삭제할지 말지
        :param del_unnamed_key: Unnamed키를 가지는 항목삭제
        :return: 중복된 항목은 합쳐서 딕셔너리로 반환하고 중복된 갯수를 정수로 반환
        """
        pass




    @staticmethod
    def sum_each_data(data_list: List[dict]) -> dict:
        """
        검색된 딕셔너리를 모은 리스트를 인자로 받아서 각각의 기간에 맞춰 합을 구해 하나의 딕셔너리로 반환한다.
        """
        # 전분기에 관련항목은 더하는 것이 의미없어서 제거한다.
        new_data_list = []
        for data in data_list:
            new_data_list.append(C1034.refine_data(data, ['^전.+대비.*', ]))

        sum_dict = {}
        periods = list(new_data_list[0].keys())
        # 여러딕셔너리를 가진 리스트의 합 구하기
        for period in periods:
            sum_dict[period] = sum(tools.nan_to_zero(data[period]) for data in new_data_list)
        return sum_dict

    @staticmethod
    def get_latest_value_from_dict(data: dict, pop_count=2) -> Tuple[str, float]:
        """
        가장 최근 년/분기 값 - evaltools에서도 사용할수 있도록 staticmethod로 뺐음.

        해당 타이틀의 가장 최근의 년/분기 값을 튜플 형식으로 반환한다.

        Args:
            data (dict): 찾고자하는 딕셔너리 데이터
            pop_count: 유효성 확인을 몇번할 것인가

        Returns:
            tuple: ex - ('2020/09', 39617.5) or ('', 0)

        Note:
            만약 최근 값이 nan 이면 찾은 값 바로 직전 것을 한번 더 찾아 본다.\n
            데이터가 없는 경우 ('', nan) 반환한다.\n
        """

        def is_valid_value(value) -> bool:
            """
            숫자가 아닌 문자열이나 nan 또는 None의 경우 유효한 형식이 아님을 알려 리턴한다.
            """
            if isinstance(value, str):
                # value : ('Unnamed: 1', '데이터가 없습니다.') 인 경우
                is_valid = False
            elif math.isnan(value):
                # value : float('nan') 인 경우
                is_valid = False
            elif value is None:
                # value : None 인 경우
                is_valid = False
            else:
                is_valid = True
            """
            elif value == 0:
                is_valid = False
            """
            return is_valid

        # print(f'raw data : {data}')
        # remove_yoy
        data = Corps.refine_data(data,['^전.+대비.*'])
        # print(f'after remove_yoy : {data}')

        # 데이터를 추출해서 사용하기 때문에 원본 데이터는 보존하기 위해서 카피해서 사용
        data_copied = copy.deepcopy(data)

        for i in range(pop_count):
            try:
                d, v = data_copied.popitem()
            except KeyError:
                # when dictionary is empty
                return '', float('nan')
            if str(d).startswith('20') and is_valid_value(v):
                mylogger.debug(f'last_one : {v}')
                return d, v

        return '', float('nan')

    def latest_value(self, title: str, pop_count=2) -> Tuple[str, float]:
        """
        해당 타이틀의 가장 최근의 년/분기 값을 튜플 형식으로 반환한다.

        Args:
            title (str): 찾고자 하는 타이틀
            pop_count: 유효성 확인을 몇번할 것인가

        Returns:
            tuple: ex - ('2020/09', 39617.5) or ('', 0)

        Note:
            만약 최근 값이 nan 이면 찾은 값 바로 직전 것을 한번 더 찾아 본다.\n
            데이터가 없는 경우 ('', nan) 반환한다.\n
        """
        c, row_data = self.find(title, remove_yoy=True, del_unnamed_key=True)
        # print(row_data)
        od = OrderedDict(sorted(row_data.items(), reverse=False))
        # print(f'{title} : {od}')
        return C1034.get_latest_value_from_dict(od, pop_count)

    def sum_recent_4q(self, title: str) -> Tuple[str, float]:
        """최근 4분기 합

        분기 페이지 한정 해당 타이틀의 최근 4분기의 합을 튜플 형식으로 반환한다.

        Args:
            title (str): 찾고자 하는 타이틀

        Returns:
            tuple: (계산된 4분기 중 최근분기, 총합)

        Raises:
            TypeError: 페이지가 q가 아닌 경우 발생

        Note:
            분기 데이터가 4개 이하인 경우 그냥 최근 연도의 값을 찾아 반환한다.
        """
        mylogger.debug('In mymongo sum_recent_4q')
        if self.page.endswith('q'):
            # 딕셔너리 정렬 - https://kkamikoon.tistory.com/138
            # reverse = False 이면 오래된것부터 최근순으로 정렬한다.
            od_q = OrderedDict(sorted(self.find(title, remove_yoy=True, del_unnamed_key=True)[1].items(), reverse=False))
            mylogger.debug(f'{title} : {od_q}')

            if len(od_q) < 4:
                # od_q의 값이 4개 이하이면 그냥 최근 연도의 값으로 반환한다.
                origin_page = self.page
                self.page = self.page[:-1] + 'y'
                v = self.latest_value(title)
                self.page = origin_page
                return v
            else:
                q_sum = 0
                date_list = list(od_q.keys())
                while True:
                    try:
                        latest_period = date_list.pop()
                    except IndexError:
                        latest_period = ""
                        break
                    else:
                        if str(latest_period).startswith('20'):
                            break

                for i in range(4):
                    # last = True 이면 최근의 값부터 꺼낸다.
                    d, v = od_q.popitem(last=True)
                    mylogger.debug(f'd:{d} v:{v}')
                    q_sum += 0 if math.isnan(v) else v
                return str(latest_period), round(q_sum, 2)
        else:
            raise TypeError(f'Not support year data..{self.page} on sum_recent_4q')

    def find_yoy(self, title: str) -> float:
        """

        타이틀에 해당하는 전년/분기대비 값을 반환한다.\n

        Args:
            title (str): 찾고자 하는 타이틀

        Returns:
            float: 전년/분기대비 증감율

        Note:
            중복되는 title 은 첫번째것 사용\n
        """

        c, dict_list = self._find(title, ['항목'])

        if c == 0:
            return math.nan
        else:
            # C103의 경우 합치지 않고 그냥 첫번째 것을 사용한다.
            data = dict_list[0]
        #print(data)
        if self.page.endswith('q'):
            return data['전분기대비']
        else:
            return data['전년대비 1']
