from typing import Tuple, Optional

from db_hj3415 import mymongo
from db_hj3415.myredis.corps import Corps

from utils_hj3415 import setup_logger
mylogger = setup_logger(__name__,'WARNING')


class C1034(Corps):
    def __init__(self, code: str, page: str):
        super().__init__(code, page)
        # 자식 클래스에서 C103이나 C104를 생성해서 할당함
        self.mymongo_c1034: Optional[mymongo.C1034] = None

    @property
    def code(self) -> str:
        return super().code

    @code.setter
    def code(self, code: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C1034, self.__class__).code.__set__(self, code)
        self.mymongo_c1034.code = code

    @property
    def page(self) -> str:
        return super().page

    @page.setter
    def page(self, page: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C1034, self.__class__).page.__set__(self, page)
        self.mymongo_c1034.page = page

    def list_rows(self, refresh=False):
        redis_name = self.code_page + '_rows'
        return super()._list_rows(self.mymongo_c1034, redis_name, refresh)

    def list_row_titles(self, refresh=False) -> list:
        redis_name = self.code_page + '_list_row_titles'

        def fetch_list_row_titles() -> list:
            return self.mymongo_c1034.list_row_titles()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_list_row_titles)

    def latest_value(self, title: str, pop_count = 2, refresh=False) -> Tuple[str, float]:
        redis_name = self.code_page + f'_latest_value_pop{pop_count}_' + title

        def fetch_latest_value(title_in: str, pop_count_in: int) -> Tuple[str, float]:
            return self.mymongo_c1034.latest_value(title_in, pop_count_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_latest_value, title, pop_count)

    def latest_value_pop2(self, title: str, refresh=False) -> Tuple[str, float]:
        redis_name = self.code_page + '_latest_value_pop2_' + title

        def fetch_latest_value_pop2(title_in: str) -> Tuple[str, float]:
            return self.mymongo_c1034.latest_value(title_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_latest_value_pop2, title)

    def find(self, row_title: str, remove_yoy=False, del_unnamed_key=True, refresh=False) -> Tuple[int, dict]:
        """
        :param row_title: 해당하는 항목을 반환한다.
        :param remove_yoy: 전분기대비, 전년대비를 삭제할지 말지
        :param del_unnamed_key: Unnamed키를 가지는 항목삭제
        :param refresh:
        :return: 중복된 항목은 합쳐서 딕셔너리로 반환하고 중복된 갯수를 정수로 반환
        """
        if remove_yoy:
            suffix = '_find_without_yoy_'
        else:
            suffix = '_find_with_yoy_'

        redis_name = self.code_page + suffix + row_title

        def fetch_find(row_title_in: str, remove_yoy_in, del_unnamed_key_in) -> Tuple[int, dict]:
            return self.mymongo_c1034.find(row_title=row_title_in, remove_yoy=remove_yoy_in, del_unnamed_key=del_unnamed_key_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_find, row_title, remove_yoy, del_unnamed_key)

    def find_yoy(self, row_title: str, refresh=False) -> float:
        """
        항목에서 전월/분기 증감율만 반환한다.
        중복되는 title 은 첫번째것 사용
        :param row_title:
        :param refresh:
        :return:
        """
        redis_name = self.code_page + '_find_yoy_' + row_title

        def fetch_find_yoy(row_title_in: str) -> float:
            return self.mymongo_c1034.find_yoy(row_title_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_find_yoy, row_title)

    def sum_recent_4q(self, row_title: str, refresh=False) -> Tuple[str, float]:
        mylogger.debug('In myredis sum_resent_4q..')
        redis_name = self.code_page + '_sum_recent_4q_' + row_title
        def fetch_sum_recent_4q(row_title_in: str) -> Tuple[str, float]:
            return self.mymongo_c1034.sum_recent_4q(row_title_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_sum_recent_4q, row_title)


class C103(C1034):
    PAGES = mymongo.C103.PAGES

    def __init__(self, code: str, page: str):
        """
        :param code:
        :param page: 'c103손익계산서q', 'c103재무상태표q', 'c103현금흐름표q', 'c103손익계산서y', 'c103재무상태표y', 'c103현금흐름표y'
        """
        super().__init__(code, page)
        self.mymongo_c1034 = mymongo.C103(code, page)


class C104(C1034):
    PAGES = mymongo.C104.PAGES

    def __init__(self, code: str, page: str):
        """
        :param code:
        :param page: 'c104y', 'c104q
        """
        super().__init__(code, page)
        self.mymongo_c1034 = mymongo.C104(code, page)
