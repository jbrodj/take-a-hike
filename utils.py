import sqlite3

def createConnection(db):
  connection = sqlite3.connect(db)
  cursor = connection.cursor()
  return {'connection': connection, 'cursor': cursor}

def commitCloseConn(conn):
  conn.commit()
  conn.close()
  return


def addArea(areaName):
  dbConnection = createConnection('hikes.db')
  dbConnection['cursor'].execute('INSERT OR IGNORE INTO areas (area_name) VALUES (?)', (areaName,))
  commitCloseConn(dbConnection['connection'])

# addArea('Elora')
# addArea('Rouge National Urban Park')

def addTrail(areaName, trailName):
  dbConnection = createConnection('hikes.db')
  areaId = dbConnection['cursor'].execute('SELECT id FROM areas WHERE area_name == (?)', [areaName])
  arr = []
  for row in areaId:
    arr.append(row)
  id = arr[0][0]
  dbConnection['cursor'].execute('INSERT OR IGNORE INTO trails (area_id, trail_name) VALUES (?, ?)', [id, trailName])
  commitCloseConn(dbConnection['connection'])

# addTrail('Elora', 'Bissell Park')
# addTrail('Rouge National Urban Park', 'Woodland Trail')

def addHike():
  dbConnection = createConnection('hikes.db')
  dbConnection['cursor'].execute('INSERT INTO hikes () VALUES ()')
  commitCloseConn(dbConnection['connection'])

