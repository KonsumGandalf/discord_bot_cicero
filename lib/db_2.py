import psycopg2

script_path = '../data/db'

DB_HOST = 'localhost'
DB_NAME = 'cicero_bot_DB'
DB_USER = 'David'
DB_PASS = 'Python123'
port_id = 6969
conn, cur = None, None

try:
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, port=port_id)

    cur = conn.cursor()

except Exception as error:
    print(error)


def script_read(filename):
    path = script_path + '/' + filename
    with open(path, 'r', encoding='utf-8') as script:
        lines = script.read()
    return lines


def operate_on_table():
    script_read('fetch_data.sql')
    cur.execute(script_read('fetch_data.sql'))
    print(cur.fetchall())


def main():
    operate_on_table()
    if conn:
        conn.close()
    if cur:
        cur.close()


if __name__ == '__main__':
    main()
