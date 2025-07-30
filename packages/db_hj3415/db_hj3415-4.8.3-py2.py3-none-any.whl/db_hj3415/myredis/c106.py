from db_hj3415.myredis.corps import Corps
from db_hj3415 import mymongo


class C106(Corps):
    PAGES = mymongo.C106.PAGES

    def __init__(self, code: str, page: str):
        """
        :param code:
        :param page: 'c106y', 'c106q
        """
        super().__init__(code, page)
        self.mymongo_c106 = mymongo.C106(code, page)

    @property
    def code(self) -> str:
        return super().code

    @code.setter
    def code(self, code: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C106, self.__class__).code.__set__(self, code)
        self.mymongo_c106.code = code

    @property
    def page(self) -> str:
        return super().page

    @page.setter
    def page(self, page: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C106, self.__class__).page.__set__(self, page)
        self.mymongo_c106.page = page

    def list_row_titles(self, refresh=False) -> list:
        redis_name = self.code_page + '_list_row_titles'

        def fetch_list_row_titles() -> list:
            return self.mymongo_c106.list_row_titles()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_list_row_titles)

    def list_rows(self, refresh=False):
        redis_name = self.code_page + '_rows'
        return super()._list_rows(self.mymongo_c106, redis_name, refresh)

    def find(self, row_title: str, refresh=False) -> dict:
        redis_name = self.code_page + '_find_' + row_title

        def fetch_find(row_title_in: str) -> dict:
            return self.mymongo_c106.find(row_title_in)

        return self.fetch_and_cache_data(redis_name, refresh, fetch_find, row_title)

    @classmethod
    def make_like_c106(cls, code: str, page: str, title: str, refresh=False) -> dict:
        redis_name = code + '.c106' + '_make_like_c106_' + page + '_' + title

        def fetch_make_like_c106(code_in, page_in, title_in) -> dict:
            return mymongo.C106.make_like_c106(code_in, page_in, title_in)

        return cls.fetch_and_cache_data(redis_name, refresh, fetch_make_like_c106, code, page, title)

    def get_rivals(self, refresh=False) -> list:
        redis_name = self.code_page + '_rivals'

        def fetch_get_rivals() -> list:
            return self.mymongo_c106.get_rivals()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_rivals)