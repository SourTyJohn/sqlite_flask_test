from data.db_session import sql_execute, last_id
from typing import Union


class AbstractModel:
    __table_name__ = ""
    __pk_name__ = ""
    __table_init_command__ = ""

    def __init_subclass__(cls, **kwargs):
        sql_execute(cls.__table_init_command__)

    @classmethod
    def create(cls, do_commit, **kwargs):
        fields = ', '.join([ f'"{f}"' for f in kwargs.keys() ])
        values = ', '.join([ f'"{v}"' for v in kwargs.values() ])
        sql_execute(
            f"""INSERT INTO {cls.__table_name__} ({fields}) VALUES ({values});""",
            do_commit=do_commit
        )
        return last_id()

    @classmethod
    def get_by_pk(cls, pk):
        return cls.get_all( sql_filter=f'{cls.__pk_name__}="{pk}"' )[0]

    @classmethod
    def get_all(cls, sql_filter: str = None) -> list:
        __full_sql_command = f"SELECT * FROM {cls.__table_name__}"

        if sql_filter is not None:
            __full_sql_command += f' WHERE ({sql_filter});'
        else:
            __full_sql_command += ';'

        query = sql_execute(__full_sql_command)
        return query.fetchall()


class User(AbstractModel):
    __table_name__ = "users"
    __pk_name__ = "fio"
    __table_init_command__ = f"""
        CREATE TABLE IF NOT EXISTS "{__table_name__}" (
            {__pk_name__}   VARCHAR(64) PRIMARY KEY,
            login           VARCHAR(32) NOT NULL,
            password        VARCHAR(32) NOT NULL
        );"""

    @classmethod
    def exists(cls, login: str, password: str) -> Union["tuple", None]:
        user = cls.get_all(
            sql_filter=f'login="{login}" AND password="{password}"'
        )
        return user[0][0] if len(user) != 0 else None

    @classmethod
    def check_login(cls, login: str) -> Union["tuple", None]:
        user = cls.get_all(
            sql_filter=f'login="{login}"'
        )
        return user[0] if len(user) != 0 else None


class Client(AbstractModel):
    __table_name__ = "clients"
    __pk_name__ = "client_id"
    __table_init_command__ = f"""
        CREATE TABLE IF NOT EXISTS "{__table_name__}" (
            {__pk_name__}   INTEGER PRIMARY KEY AUTOINCREMENT,

            account_number  INTEGER,
            lastname        VARCHAR(32),
            firstname       VARCHAR(32),
            fathername      VARCHAR(32),
            birth_date      DATE,
            inn_number      INTEGER,

            fio_user        VARCHAR(64),
            status          INTEGER,

            FOREIGN KEY (fio_user) REFERENCES users (fio) ON DELETE CASCADE
        );"""

    STATUS_TYPES = [
        "В работе",
        "Отказ",
        "Сделка закрыта"
    ]

    @classmethod
    def get_by_user(cls, user_fio):
        return cls.get_all(
            sql_filter=f'fio_user="{user_fio}"'
        )

    @classmethod
    def create(cls, do_commit, **kwargs):
        kwargs["status"] = Client.STATUS_TYPES[kwargs["status"]]
        super(Client, cls).create(do_commit, **kwargs)

    @classmethod
    def check_user(cls, client_id, user_fio) -> bool:
        """Checks if client belongs to user"""
        query = cls.get_all(sql_filter=f'client_id="{client_id}" AND fio_user="{user_fio}"')
        return len(query) == 1

    @classmethod
    def update(cls, client_id, sql_code: str):
        print(sql_code)
        sql_execute(f"""UPDATE {cls.__table_name__}
        SET {sql_code} WHERE "client_id"={client_id};""", do_commit=True, do_debug_print=True)
