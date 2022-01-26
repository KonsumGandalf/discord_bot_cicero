import psycopg2
from os.path import isfile

DB_PATH = './data/db/database.db'

DB_HOST = 'localhost'
DB_NAME = 'cicero_bot_DB'
DB_USER = 'David'
DB_PASS = 'Python123'
port_id = 6969

SCRIPT_PATH = '../../data/db'
filename = 'fetch_data.sql'

conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, port=port_id)

cur = conn.cursor()

def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner

@with_commit
def build():
    if isfile(BUILD_PATH:=SCRIPT_PATH+'/'+filename):
        scriptexec(BUILD_PATH)

def commit():
    conn.commit()

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
    cur.executeman(command, valueset)

def scriptexec(path):
    with open(path, 'r', encoding='utf-8') as script:
        cur.executescript(script.read())

