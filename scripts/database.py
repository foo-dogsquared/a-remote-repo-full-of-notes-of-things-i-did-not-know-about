# native packages
from contextlib import contextmanager
from re import compile
import sqlite3

# own defined packages
from scripts.constants import NOTES_DB_SQL_SCHEMA, NOTES_DB_FILEPATH

__all__ = ["init_db"]


def regex_match(string, pattern):
    regex_pattern = compile(pattern)
    return regex_pattern.search(string) is not None


@contextmanager
def init_db(db_path=NOTES_DB_FILEPATH):
    notes_db = sqlite3.connect(db_path)
    notes_db.row_factory = sqlite3.Row

    notes_db.create_function("REGEXP", 2, regex_match)
    notes_db.executescript(NOTES_DB_SQL_SCHEMA)
    try:
        cursor = notes_db.cursor()
        yield cursor
        cursor.close()
        notes_db.commit()
    except sqlite3.DatabaseError as error:
        notes_db.rollback()
        raise error
    finally:
        notes_db.close()
