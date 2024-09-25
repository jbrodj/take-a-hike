import sqlite3

# def createConnection(db):
#   connection = sqlite3.connect(db)
#   cursor = connection.cursor()
#   return [connection, cursor]

# def closeConnection(conn):
#   conn.commit()
#   conn.close()
#   return

def addArea(areaName):
  connection = sqlite3.connect("hikes.db")
  cursor = connection.cursor()
  cursor.execute('INSERT INTO areas (area_name) VALUES (?)', (areaName,))
  connection.commit()
  connection.close()

addArea('Elora')
addArea('Rouge National Urban Park')

def addTrail(areaName, trailName):
  connection = sqlite3.connect("hikes.db")
  cursor = connection.cursor()
  areaId = cursor.execute('SELECT id FROM areas WHERE area_name == (?)', [areaName])
  arr = []
  for row in areaId:
    arr.append(row)
  id = arr[0][0]
  cursor.execute('INSERT INTO trails (area_id, trail_name) VALUES (?, ?)', [id, trailName])
  connection.commit()
  connection.close()

addTrail('Elora', 'Bissell Park')
addTrail('Rouge National Urban Park', 'Woodland Trail')

def addHike():
  connection = sqlite3.connect("hikes.db")
  cursor = connection.cursor()
  cursor.execute("INSERT INTO hikes () VALUES ()")
  connection.commit()
  connection.close()
