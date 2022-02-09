import psycopg2
from sqlite3 import connect

from os.path import isfile
from glob import glob

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
filename_prefix = 'elo.sql'
SQLS = [path for path in glob('data/db/build/*.sql')]
conn = connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
for path_ele in SQLS:
    with open(path_ele, 'r', encoding='utf-8') as script:
        cur.executescript(script.read())

def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner

@with_commit
def build():
    if isfile(SQLS[0]):
        scriptexec(SQLS[0])

def autosave(sched):
    sched.add_job(commit, 'cron',  day_of_week="mon-fri", second='0,10,20,30')

def commit():
    conn.commit()

    scriptexec(SQLS[0])

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
    return cur.fetchall()

def column(command, *values):
    cur.execute(command, tuple(values))
    return [item[0] for item in cur.fetchall()]

def execute(command, *values):
    cur.execute(command, tuple(values))

def multiexec(command, valueset):
    cur.executemany(command, valueset)


def scriptexec(path):
    with open(path, 'r', encoding='utf-8') as script:
        cur.executescript(script.read())
