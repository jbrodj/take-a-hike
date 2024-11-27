'''Uses Error for error reporting'''
from sqlite3 import Error
import utils

SEPARATOR = '=' * 24
print('Hold onto your butts...\n' + SEPARATOR)
DB = 'hikes.db'

try:
    with open('./tables/tables.sql', 'r', encoding='utf-8') as tables:
        TABLES_COMMANDS = tables.read()
    dbConnection = utils.create_connection(DB)
    print('Connection established...\n' + SEPARATOR)
    dbConnection['cursor'].executescript(TABLES_COMMANDS)
    dbConnection['connection'].commit()
    dbConnection['cursor'].execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    schema = dbConnection['cursor'].fetchall()
    print('Tables created: ')
    for table in schema:
        print(f'   * {table[0]}')
    print(SEPARATOR)
    utils.commit_close_conn(dbConnection['connection'])
    print('Connection closed...\n')
except Error as error:
    print(error)
