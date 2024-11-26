import sqlite3
from sqlite3 import Error
import utils

separator = '=' * 24
print('Hold onto your butts...\n' + separator)
db = 'hikes.db'

try:
  with open('./tables/tables.sql', 'r') as tables:
    TABLES_COMMANDS = tables.read()
  dbConnection = utils.createConnection(db)
  print('Connection established...\n' + separator)
  dbConnection['cursor'].executescript(TABLES_COMMANDS)
  dbConnection['connection'].commit()
  dbConnection['cursor'].execute("SELECT name FROM sqlite_master WHERE type = 'table';")
  schema = dbConnection['cursor'].fetchall()
  print('Tables created: ')
  for table in schema:
    print(f'   * {table[0]}')
  print(separator)
  utils.commitCloseConn(dbConnection['connection'])
  print('Connection closed...\n')
except Error as error:
  print(error)