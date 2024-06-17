import sqlite3
from paths import DB_PATH


__all__ = (
    'sql_execute',
    'last_id'
)


__connector = sqlite3.connect(DB_PATH, check_same_thread=False)
__cursor = sqlite3.Cursor(__connector)


def __db_commit():
    __connector.commit()


def sql_execute(command: str, do_commit=False, do_debug_print=False):
    try:
        result = __cursor.execute(command)

        if do_debug_print:
            print('EXECUTED:', command)

        if do_commit:
            __db_commit()

        return result

    except sqlite3.OperationalError as err:
        print('ERROR IN:', command)
        raise err


def last_id():
    return __cursor.lastrowid
