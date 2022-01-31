import psycopg2
from sqlite3 import connect

from os.path import isfile


"""
While continuing the project the Postgres DataBase was switched to a SQLite one.
The following connection is just recommended to use in combination with Postgres


DB_HOST = 'localhost'
DB_NAME = 'cicero_bot_DB'
DB_USER = 'David'
DB_PASS = 'Python123'
port_id = 6969

conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, port=port_id)

"""
DB_PATH = 'data/db/database.db'

SCRIPT_PATH = 'data/db'
filename = 'build_action.sql'
BUILD_PATH = SCRIPT_PATH+'/'+filename

conn = connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

with open(BUILD_PATH, 'r', encoding='utf-8') as script:
    cur.execute(script.read())
    conn.commit()

def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner

@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)

def autosave(sched):
    print(BUILD_PATH)
    sched.add_job(commit, 'cron',  day_of_week="mon-fri", second='0,10,20,30')

def commit():
    conn.commit()

    scriptexec(BUILD_PATH)

def close():
    conn.close()

def field(command, *values):
    cur.execute(command, tuple(values))

    if (fetch := cur.fetchone()) is not None:
        return fetch[0]

def record(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchone()

def records(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchone()

def columns(command, *values):
    cur.execute(command, tuple(values))
    return [item[0] for item in cur.fetchone()]

def execute(command, *values):
    cur.execute(command, tuple(values))

def multiexec(command, valueset):
    cur.executemany(command, valueset)


def scriptexec(path):
    # print(path)
    # print(f'{isfile(BUILD_PATH)=}')
    with open(path, 'r', encoding='utf-8') as script:
        cur.executescript(script.read())
        # cur.execute(script.read()) methode for postgres
