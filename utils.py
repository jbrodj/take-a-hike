'''Using sqlite3 to create our db'''
import sqlite3

def create_connection(db):
    '''Takes sqlite3 db file as parameter.
        Returns library containing connection and cursor objects
    '''
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    return {'connection': connection, 'cursor': cursor}

def commit_close_conn(conn):
    '''Takes connection object as parameter.
        Commits changes and closes connection.
    '''
    conn.commit()
    conn.close()

def get_area_id(area_name, db):
    '''Takes area name string and db file
        Returns area id.
    '''
    db_connection = create_connection(db)
    area_id = db_connection['cursor'].execute(
        'SELECT id FROM areas WHERE area_name = (?)', [area_name])[0]
    db_connection['connection'].close()
    print(area_id)
    return area_id

def add_area(area_name):
    '''Takes area name from form.
        Inserts area data into areas table.
    '''
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'INSERT OR IGNORE INTO areas (area_name) VALUES (?)', (area_name,))
    commit_close_conn(db_connection['connection'])

# add_area('Elora')
# add_area('Rouge National Urban Park')

def add_trail(area_name, trail_name):
    '''Takes area name and trail name from form.
        Retrieves area ID from db, and inserts trail data into db.
    '''
    db_connection = create_connection('hikes.db')
    area_id_data = db_connection['cursor'].execute(
        'SELECT id FROM areas WHERE area_name == (?)', [area_name])
    arr = []
    for row in area_id_data:
        arr.append(row)
    area_id = arr[0][0]
    area_id = area_id_data[0]
    db_connection['cursor'].execute(
        'INSERT OR IGNORE INTO trails (area_id, trail_name) VALUES (?, ?)', [area_id, trail_name])
    commit_close_conn(db_connection['connection'])

# add_trail('Elora', 'Bissell Park')
# add_trail('Rouge National Urban Park', 'Woodland Trail')

def add_hike(hike_data):
    '''Takes hike data from form.
        Creates new hike in hikes table and inserts data.
    '''
    print(hike_data)
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'INSERT INTO hikes () VALUES ()')
    commit_close_conn(db_connection['connection'])
