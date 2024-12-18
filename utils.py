''' wraps copies original function's data to decorated function '''
from functools import wraps
import sqlite3
from flask import render_template, session, redirect
from content import hike_form_content
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

def convert_to_dict(tuple_list, dictionary):
    '''Takes a list of tuples and an empty dictionary
    Returns a dictionary.
    '''
    dictionary = dict(tuple_list)
    return dictionary


def format_hike_form_data(data):
    '''Takes multidict object from form submission
        Returns list of dictionaries containing formatted form data. 
    '''
    formatted_data = convert_to_dict(data, {})
    return formatted_data


def add_user(username, password_hash):
    '''Takes username string and hashed password string
    '''
    db_connection = create_connection('hikes.db')
    try:
        db_connection['cursor'].execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
    except sqlite3.Error as error:
        print(error)
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
    db_connection = create_connection('hikes.db')
    for trail_name in trail_list:
        db_connection['cursor'].execute(
            'INSERT OR IGNORE INTO trails (area_id, trail_name) VALUES (?, ?)',
            [area_id, trail_name])

    commit_close_conn(db_connection['connection'])


def add_hike(user_id, area_id, form_data):
    '''Takes hike data from form and area id from database.
        Creates new hike in hikes table and inserts data.
    '''
    hike_date, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info = form_data.values()
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'INSERT INTO hikes (hike_date, user_id, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [hike_date, user_id, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info])
    commit_close_conn(db_connection['connection'])


def update_hike(existing_hike_data, updated_hike_data):
    '''Takes preexisting hike data, and data from updade hike form'''
    hike_id = existing_hike_data.get('id')
    hike_date, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info = updated_hike_data.values()
    db_connection = create_connection('hikes.db')
    db_connection['cursor'].execute(
        'UPDATE hikes SET hike_date = (?), area_name = (?), trailhead = (?), trails_cs = (?), distance_km = (?), image_url = (?), image_alt = (?), map_link = (?), other_info = (?) WHERE id = (?)',
        (hike_date, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info, hike_id,)
    )
    commit_close_conn(db_connection['connection'])


def delete_hike(hike_id, user_id):
    '''Takes the id of selected hike and id of logged in user'''
    db_connection = create_connection('hikes.db')
    try:
        db_connection['cursor'].execute(
            'DELETE FROM hikes WHERE id = (?) AND user_id = (?)',
            (hike_id, user_id,)
        )
        commit_close_conn(db_connection['connection'])
    except sqlite3.OperationalError:
        print('Error: No hike found matching user id and hike id')


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


def get_hikes(db, user_id, hike_id=None):
    ''' Takes database file
        Returns formatted list of hike dictionaries to serve to UI.
        Returns empty list if no table is found.
    '''
    db_connection = create_connection(db)
    # If hike_id is passed, we wish to fetch a single hike
    if hike_id:
        try:
            data = db_connection['cursor'].execute(
                'SELECT * FROM hikes WHERE id = ? AND user_id = ?', (hike_id, user_id,))
            hikes_data = db_connection['cursor'].fetchall()
            hikes_list = format_hikes(data, hikes_data)
            commit_close_conn(db_connection['connection'])
            return hikes_list
        except sqlite3.OperationalError:
            print('Error: No hike found matching user id and hike id')
            return []
    # Otherwise get all records for specified user
    else:
        try:
            data = db_connection['cursor'].execute(
                'SELECT * FROM hikes WHERE user_id = ? ORDER BY hike_date DESC LIMIT 10', (user_id,))
            hikes_data = db_connection['cursor'].fetchall()
        except sqlite3.OperationalError:
            print('Error: No hikes found matching user id')
            return []
    hikes_list = format_hikes(data, hikes_data)
    commit_close_conn(db_connection['connection'])
    return hikes_list


def format_hikes(sql_data_object, fetched_hikes_values):
    '''Takes sql response object (to get keys) and fetched hike data (values).
        Returns list of hikes as dictionaries.
    '''
    # Create list of keys from data object
    keys = []
    for key in sql_data_object.description:
        keys.append(key[0])
    hikes_list = []
    for entry in fetched_hikes_values:
        # Convert each tuple in list to a dictionary by adding keys
        this_entry = {}
        for index, key in enumerate(keys):
            # Ensure max of 1 decimal place for distance (UI spacing only supports 1 dp)
            if key == 'distance_km':
                this_entry[key] = round(entry[index], 1)
            else:
                this_entry[key] = entry[index]
        # Add key/value pair containing list of trail strings
        trails_list = this_entry.get('trails_cs').split(', ')
        this_entry['trails_list'] = trails_list
        hikes_list.append(this_entry)
    return hikes_list


def get_all_usernames(db):
    '''Takes database file
        Returns list of all names in database
    '''
    db_connection = create_connection(db)
    usernames_query = db_connection['cursor'].execute('SELECT username FROM users')
    usernames = []
    for row in usernames_query:
        usernames.append(row)
    return usernames


def get_user_by_username(db, username):
    '''Takes database file and username string
        Returns dict of user data from users table, or empty dictionary if no user found.
    '''
    db_connection = create_connection(db)
    user_data = db_connection['cursor'].execute('SELECT * FROM users WHERE username = ?', (username,))
    keys = ['id', 'username', 'password_hash']
    values = []

    for row in user_data:
        for position in row:
            values.append(position)
    db_connection['connection'].close()
    if len(values) == 0:
        return {}
    user = generate_user_data_dict(keys, values)
    return user


def get_similar_usernames(db, query):
    '''Takes database file and query string.
        Returns dict of usernames
        or empty dict.
    '''
    db_connection = create_connection(db)
    users_list = []
    for char in query:
        like_query = f'%{char}%'
        username_data = db_connection['cursor'].execute('SELECT username FROM users WHERE username LIKE ?', (like_query,))
        for row in username_data:
            users_list.append(row[0])
    similar_users = {}
    for user in users_list:
        # Frequency is the number of occurrences where a char in the query matched a char in the username
        frequency = users_list.count(user)
        # Accuracy is the proportion of matching chars relative to the length of the username
        accuracy = frequency / len(user)
        match = frequency * accuracy
        if frequency > 3 or accuracy > 0.5:
            similar_users.update({user: match})
    # Source: https://www.datacamp.com/tutorial/sort-a-dictionary-by-value-python
    sorted_similar_users = dict(sorted(similar_users.items(), key=lambda item: item[1], reverse=True))
    return sorted_similar_users


def generate_user_data_dict(keys, values):
    '''Takes two lists with same number of indecies.
        Returns list with left vals as keys, right vals as values.
    '''
    user = {}
    for index, key in enumerate(keys):
        user[key] = values[index]
    return user


#  FORM VALIDATION

def validate_hike_form(form_data):
    '''Takes form data
        Returns error type (string) or None
    '''
    for field in form_data:
        if form_data.get(field) == '' and hike_form_content[field]['required'] is True:
            return 'missing_values'
    # Validate that distance field is numbers and decimal chars only
    for char in form_data.get('distance_km'):
        if not char.isnumeric() and not char == '.':
            return 'invalid_number'
    # Validate that distance value is between 0 and 100
    distance = float(form_data.get('distance_km'))
    if distance < 0 or distance > 99.9:
        return 'out_of_range'
    return None


#  ERROR HANDLING

def handle_error(url, message, code=400):
    '''Takes an error code number and string describing the cause of the error
        Returns error template.
    '''
    return render_template('error.html', url=url, message=message, code=code,)


#  DECORATORS

# Source: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
def login_required(function):
    '''Takes view function.
        Returns decorated view function with /login redirect.
    '''
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return function(*args, **kwargs)
    return decorated_function
