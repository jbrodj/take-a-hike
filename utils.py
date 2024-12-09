'''Using sqlite3 to create our db'''
import sqlite3
from flask import render_template
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
# INSERT AND FORMAT DATA

def format_hike_form_data(data):
    '''Takes multidict object from form submission
        Returns list of dictionaries containing formatted form data. 
    '''
    def convert_to_dict(tuple_list, dictionary):
        dictionary = dict(tuple_list)
        return dictionary
    formatted_data = convert_to_dict(data, {})
    # print(f'formatted_data: {formatted_data}')
    return formatted_data


def add_user(username, password_hash):
    '''Takes username string and hashed password string
    '''
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
    commit_close_conn(db_connection['connection'])


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
    hike_date, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info = hike_data.values()
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'INSERT INTO hikes (hike_date, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [hike_date, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info])
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


def get_hikes_for_ui(db):
    ''' Takes database file
        Returns formatted list of hike dictionaries to serve to UI.
        Returns empty list if no table is found.
    '''
    db_connection = create_connection(db)
    try:
        data = db_connection['cursor'].execute(
            'SELECT * FROM hikes ORDER BY hike_date DESC LIMIT 10')
    except sqlite3.OperationalError:
        return []
    hikes_data = db_connection['cursor'].fetchall()
    keys = []
    for key in data.description:
        keys.append(key[0])
    hikes_list = []
    for entry in hikes_data:
        # Convert each tuple in list to a dictionary by adding keys
        this_entry = {}
        for index, key in enumerate(keys):
            this_entry[key] = entry[index]
        # Add key/value pair containing list of trail strings
        trails_list = this_entry['trails_cs'].split(', ')
        this_entry['trails_list'] = trails_list
        hikes_list.append(this_entry)
    commit_close_conn(db_connection['connection'])
    # print(f'data returned from get_hikes_for_ui: {hikes_list}')
    return hikes_list


def get_all_usernames(db):
    '''Takes database file
        Returns list of all names in database
    '''
    db_connection = create_connection(db)
    usernames = db_connection['cursor'].execute('SELECT username FROM users')
    print(f'usernames in get_all fn: {usernames}')
    # db_connection['connection'].close()
    return usernames


def get_user(db, username):
    '''Takes database file and username string
        Returns user data from users table.
    '''
    db_connection = create_connection(db)
    user = db_connection['cursor'].execute('SELECT * FROM users WHERE username = (?)', username)
    # TODO format user object before returning it
    db_connection['connection'].close()
    return user


#  ERROR HANDLING

def handle_error(url, message, code=400):
    '''Takes an error code number and string describing the cause of the error
        Returns error template.
    '''
    return render_template('error.html', url=url, message=message, code=code,)
