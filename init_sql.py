'''Uses Error for error reporting'''
from sqlite3 import Error
from utils import create_connection, commit_close_conn
from constants import DB

SEPARATOR = '=' * 24

def runner(environment='development'):
    '''Takes optional environment arg to run init fn with'''
    # Run init on test.db file if env is test, otherwise run on DB constant for development
    if environment == 'test':
        init_sql('test.db')
        return
    init_sql(DB)
    return


def init_sql(db):
    '''Takes database file. Prints table schema.'''
    print('Hold onto your butts...\n' + SEPARATOR)
    try:
        with open('./tables/tables.sql', 'r', encoding='utf-8') as tables:
            tables_commands = tables.read()
        db_connection = create_connection(db)
        print('Connection established...\n' + SEPARATOR)
        db_connection['cursor'].executescript(tables_commands)
        db_connection['connection'].commit()
        db_connection['cursor'].execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        schema = db_connection['cursor'].fetchall()
        print('Tables created: ')
        for table in schema:
            print(f'   * {table[0]}')
        print(SEPARATOR)
        commit_close_conn(db_connection['connection'])
        print('Connection closed...\n')
    except Error as error:
        print(error)

runner()
