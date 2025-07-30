import os
from pymongo import MongoClient, database, collection

from utils_hj3415 import setup_logger
mylogger = setup_logger(__name__,'WARNING')

"""
db구조 비교 - 통일성을 위해 몽고 클래스에서 사용하는 용어를 RDBMS로 사용한다.
RDBMS :     database    / tables        / rows      / columns
MongoDB :   database    / collections   / documents / fields
"""


class UnableConnectServerException(Exception):
    """
    몽고 서버 연결 에러를 처리하기 위한 커스텀 익셉션
    """
    def __init__(self, message="현재 서버에 접속할 수 없습니다.."):
        self.message = message
        super().__init__(self.message)


class DataIsNotInServerException(Exception):
    """
    원하는 데이터가 없는 경우 발생하는 익셉션
    """
    def __init__(self, message="테이블이나 데이터베이스가 서버에 없습니다."):
        self.message = message
        super().__init__(self.message)


def connect_to_mongo(addr: str, timeout=5) -> MongoClient:
    """
    몽고 클라이언트를 만들어주는 함수.
    resolve conn error - https://stackoverflow.com/questions/54484890/ssl-handshake-issue-with-pymongo-on-python3
    :param addr:
    :param timeout:
    :return:
    """
    import certifi
    ca = certifi.where()
    if addr.startswith('mongodb://'):
        # set a some-second connection timeout
        client = MongoClient(addr, serverSelectionTimeoutMS=timeout * 1000)
    elif addr.startswith('mongodb+srv://'):
        client = MongoClient(addr, serverSelectionTimeoutMS=timeout * 1000, tlsCAFile=ca)
    else:
        raise Exception(f"Invalid address: {addr}")
    try:
        srv_info = client.server_info()
        conn_str = f"Connect to Mongo Atlas v{srv_info['version']}..."
        mylogger.info(''.join([conn_str, f"Server Addr : {addr}"]))
        return client
    except Exception:
        raise UnableConnectServerException(f"현재 {addr} 에 연결할 수 없습니다..")



class Base:
    _client = None

    def __init__(self, db: str, table: str):
        self.mongo_client = self.get_client()
        self._db = self.mongo_client[db]
        try:
            self._col = self._db[table]
        except AttributeError:
            # 클래스 생성시 아직 테이블 설정이 안되었을 때
            mylogger.warning(f"{table} collection이 존재하지 않아 table을 None으로 설정합니다.")
            self._col = None

    def __str__(self):
        return f"db: {self.db}, table: {self.table}"

    @property
    def db(self) -> str:
        return self._db.name

    @db.setter
    def db(self, db: str):
        mylogger.debug(f'Change db : {self.db} -> {db}')
        self._db = self.mongo_client[db]
        try:
            self._col = self._db[self.table]
        except AttributeError:
            mylogger.warning(f"{self.table} collection이 존재하지 않아 table을 None으로 설정합니다.")
            # 클래스 생성시 아직 테이블 설정이 안되었을 때
            self._col = None

    @property
    def table(self) -> str:
        return self._col.name

    @table.setter
    def table(self, table: str):
        assert isinstance(self._db, database.Database), "You should set database first."
        mylogger.info(f'Change table : {self.table} -> {table}')
        self._col = self._db[table]

    # ========================End Properties=======================
    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            cls._client = connect_to_mongo(os.getenv('MONGO_ADDR'))
        return cls._client

    @classmethod
    def close_mongo_client(cls):
        if cls._client:
            cls._client.close()

    @classmethod
    def list_db_names(cls) -> list:
        return sorted(cls.get_client().list_database_names())

    @classmethod
    def list_table_names(cls, db: str) -> list:
        if cls.is_there(db=db):
            return sorted(cls.get_client()[db].list_collection_names())
        else:
            raise DataIsNotInServerException(f"{db} 이름을 가진 데이터베이스가 서버에 없습니다.")

    @classmethod
    def drop(cls, db=None, table=None) -> bool:
        # 에러 처리
        if not db:
            if table:
                raise Exception("테이블을 삭제하려면 db명이 반드시 필요합니다.")
            else:
                raise Exception("db명과 table명이 필요합니다.(Base.drop())")

        # 데이터베이스명만 입력한 경우
        if not table:
            if Base.is_there(db=db):
                mylogger.info(f"'{db}' 데이터베이스 삭제 중...")
                cls.get_client().drop_database(db)
                return True
            else:
                mylogger.warning(f"{db} 데이터베이스가 존재하지 않습니다.")
                return False

        # 데이터베이스명과 테이블명을 모두 입력한 경우
        if Base.is_there(db=db, table=table):
            mylogger.info(f"'{db}' 데이터베이스의 '{table}' 테이블 삭제 중...")
            cls.get_client()[db].drop_collection(table)
            return True
        else:
            mylogger.warning(f"{db} 데이터베이스 또는 {table} 테이블이 존재하지 않습니다.")
            return False

    @classmethod
    def is_there(cls, db=None, table=None) -> bool:
        """
        kwargs에 db나 table명을 넣어서 조회하면 서버에 있는지 확인하고 참거짓 반환
        :param db: 데이터베이스 이름
        :param table: 테이블 이름
        :return: 데이터베이스 또는 테이블 존재 여부 (True/False)
        """
        # 에러 처리
        if not db:
            if table:
                raise Exception("테이블 유무를 조회하려면 db명이 반드시 필요합니다.")
            else:
                raise Exception("db명과 table명이 필요합니다.(Base.is_there())")

        # 데이터베이스명만 입력한 경우
        if not table:
            dbs = cls.list_db_names()
            if db in dbs:
                return True
            mylogger.warning(f"{db} 데이터베이스가 서버에 없습니다.")
            return False

        # 데이터베이스명과 테이블명을 둘 다 입력한 경우
        try:
            tables = cls.list_table_names(db)
        except DataIsNotInServerException:
            mylogger.warning(f"{db} 데이터베이스가 서버에 없습니다.")
            return False

        if table in tables:
            return True

        mylogger.warning(f"{db} 데이터베이스의 {table} 테이블이 서버에 없습니다.")
        return False

    def list_rows(self, show_id=False) -> list:
        assert isinstance(self._col, collection.Collection), "You should set table first."
        rows = []
        if show_id:
            for row in self._col.find():
                rows.append(row)
        else:
            for row in self._col.find():
                del row['_id']
                rows.append(row)
        return rows

    def clear_table(self):
        """
        현재 설정된 컬렉션 안의 도큐먼트를 전부 삭제한다.
        (컬렉션 자체를 삭제하지는 않는다.)
        """
        assert isinstance(self._col, collection.Collection), "You should set table first."
        self._col.delete_many({})
        mylogger.info(f"{self.db}/{self.table}의 모든 도큐먼트 삭제하는 중..")

    def count_rows(self) -> int:
        assert isinstance(self._col, collection.Collection), "You should set table first."
        return self._col.count_documents({})

    def delete_row(self, query: dict):
        """
        query에 해당하는 도큐먼트를 삭제한다.
        """
        assert isinstance(self._col, collection.Collection), "You should set table first."
        self._col.delete_one(query)
