'''Using sqlite3 to create our db'''
import sqlite3
# pylint: disable=line-too-long

# ===================
# DATABASE CONNECTION

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


# =========
# FORM DATA

def format_form_data(data):
    '''Takes multidict object from form submission
        Returns list of dictionaries containing formatted form data. 
    '''
    def convert_to_dict(tuple_list, dictionary):
        dictionary = dict(tuple_list)
        return dictionary
    formatted_data = convert_to_dict(data, {})
    print(f'formatted_data: {formatted_data}')
    return formatted_data


def add_area(area_name):
    '''Takes area name from form.
        Inserts area data into areas table.
    '''
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'INSERT OR IGNORE INTO areas (area_name) VALUES (?)', (area_name, ))
    commit_close_conn(db_connection['connection'])


def add_trail(area_id, trail_names):
    '''Takes area name and comma-separated list of trail names from form.
        Retrieves area ID from db, and inserts trail data into db.
    '''
    trail_list = trail_names.split(', ')
    # area_id = get_area_id(area_name, 'hikes.db')
    db_connection = create_connection('hikes.db')
    for trail_name in trail_list:
        db_connection['cursor'].execute(
            'INSERT OR IGNORE INTO trails (area_id, trail_name) VALUES (?, ?)',
            [area_id, trail_name])

    commit_close_conn(db_connection['connection'])


def add_hike(hike_data, area_id):
    '''Takes hike data from form and area id from database.
        Creates new hike in hikes table and inserts data.
    '''
    hike_date, area_name, trailhead, trails_cs, distance_km, map_link, other_info = hike_data.values()
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'INSERT INTO hikes (hike_date, area_id, area_name, trailhead, trails_cs, distance_km, map_link, other_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            [hike_date, area_id, area_name, trailhead, trails_cs, distance_km, map_link, other_info])
    commit_close_conn(db_connection['connection'])

# RETRIEVE DATA FROM DATABASE

def get_area_id(area_name, db):
    '''Takes area name string and db file
        Returns area id.
    '''
    db_connection = create_connection(db)
    area_id_data = db_connection['cursor'].execute(
        'SELECT id FROM areas WHERE area_name = (?)', (area_name, ))
    arr = []
    for row in area_id_data:
        arr.append(row)
    area_id = arr[0][0]
    area_id = int(area_id)
    db_connection['connection'].close()
    return area_id
