'''This module houses all utility functions used in the python server'''
from functools import wraps
import re
import sqlite3
import cloudinary
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


# ==== INSERT DATA ====

def convert_to_dict(tuple_list, dictionary):
    '''Takes a list of tuples and an empty dictionary
    Returns a dictionary.
    '''
    dictionary = dict(tuple_list)
    return dictionary


def add_user(db, username, password_hash):
    '''Takes username string and hashed password string
    '''
    # Break out for nonexistent string arg
    if not username or not password_hash:
        return 'Error: Required value not provided'
    db_connection = create_connection(db)
    try:
        db_connection['cursor'].execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
    except sqlite3.Error as error:
        print(error)
        return error
    commit_close_conn(db_connection['connection'])
    return 0


def add_area(db, area_name):
    '''Takes area name from form.
        Inserts area data into areas table.
    '''
    # Break out for nonexistent area name string
    if not area_name:
        return 'Error: Required value not provided'
    db_connection = create_connection(db)
    try:
        db_connection['cursor'].execute(
            'INSERT OR IGNORE INTO areas (area_name) VALUES (?)', (area_name, ))
    except sqlite3.Error as error:
        print(error)
        return 1
    commit_close_conn(db_connection['connection'])
    return 0


def add_trail(db, area_id, trail_names):
    '''Takes area name and comma-separated list of trail names from form.
        Retrieves area ID from db, and inserts trail data into db.
    '''
    trail_list = trail_names.split(', ')
    db_connection = create_connection(db)
    for trail_name in trail_list:
        try:
            db_connection['cursor'].execute(
                'INSERT OR IGNORE INTO trails (area_id, trail_name) VALUES (?, ?)',
                [area_id, trail_name])
        except sqlite3.Error as error:
            print(error)
            return 1
    commit_close_conn(db_connection['connection'])
    return 0


def add_hike(db, user_id, area_id, form_data):
    '''Takes hike data from form and area id from database.
        Creates new hike in hikes table and inserts data.
    '''
    # Get list of keys from form data and append additional keys for user id and area id args
    keys_list = list(form_data.keys()) + ['user_id', 'area_id']
    # Convert list to comma-separated string
    keys_string = ", ".join(keys_list)
    # Get list of values from form data and append user_id and area_id
    values_list = list(form_data.values()) + [user_id, area_id]
    placeholders_string = '?, ' * (len(values_list))
    # Create command string with list of keys and corresponding number of placeholder values
    insert_cmd_string = f'INSERT INTO hikes ({keys_string}) VALUES ({placeholders_string.strip(" ,")})'

    db_connection = create_connection(db)
    try:
        db_connection['cursor'].execute(insert_cmd_string, values_list)
    except sqlite3.Error as error:
        print(error)
        return error
    commit_close_conn(db_connection['connection'])
    return 0


def update_hike(db, existing_hike_data, updated_hike_data):
    '''Takes preexisting hike data, and data from updade hike form'''
    hike_id = existing_hike_data.get('id')
    # Get keys from hike form data and create string of keys & placeholders for SET command
    keys_string = ' = (?), '.join(updated_hike_data.keys()) + ' = (?)'
    # Construct tuple of updated values plus the hike id to pass as second arg.
    values_tuple = tuple(updated_hike_data.values()) + (hike_id,)
    db_connection = create_connection(db)
    try:
        db_connection['cursor'].execute(f'UPDATE hikes SET {keys_string} WHERE id = (?)', values_tuple)
    except sqlite3.Error as error:
        print(error)
        return error
    commit_close_conn(db_connection['connection'])
    return 0


def delete_hike(db, hike_id, user_id):
    '''Takes the id of selected hike and id of logged in user'''
    db_connection = create_connection(db)
    try:
        db_connection['cursor'].execute(
            'DELETE FROM hikes WHERE id = (?) AND user_id = (?)',
            (hike_id, user_id,)
        )
        commit_close_conn(db_connection['connection'])
    except sqlite3.Error as error:
        print(error)
        return error
    return 0


# ==== RETRIEVE DATA FROM DATABASE ====

def get_area_id(area_name, db):
    '''Takes area name string and db file
        Returns area id.
    '''
    db_connection = create_connection(db)
    try:
        area_id_data = db_connection['cursor'].execute(
            'SELECT id FROM areas WHERE area_name = (?)', (area_name, ))
    except sqlite3.Error as error:
        print(error)
        return ''
    arr = []
    for row in area_id_data:
        arr.append(row)
    area_id = arr[0][0] if arr and arr[0] else None
    area_id = int(area_id) if area_id else None
    db_connection['connection'].close()
    return area_id


def get_hike_img_src(db, user_id):
    '''Takes database file and user id
        Returns string
    '''
    most_recent_hike = get_hikes(db, user_id, most_recent=True)
    if not most_recent_hike:
        return ''
    img_src = most_recent_hike[0].get('image_url')
    return img_src


def get_hikes(db, user_id, hike_id=None, most_recent=False):
    ''' Takes database file and user id
        Optionally a hike id, and boolean
        Returns formatted list of hike dictionaries to serve to UI.
        Returns empty list if no table is found.
    '''
    db_connection = create_connection(db)
    # If most_recent is passed, we wish to fetch the single most recent hike
    if most_recent:
        try:
            data = db_connection['cursor'].execute(
                'SELECT * FROM hikes WHERE user_id = ? ORDER BY hike_date DESC LIMIT 1', (user_id,))
            hikes_data = db_connection['cursor'].fetchall()
        except sqlite3.Error as error:
            print(error)
            return []
    # If hike_id is passed, we wish to fetch a single hike
    elif hike_id:
        try:
            data = db_connection['cursor'].execute(
                'SELECT * FROM hikes WHERE id = ? AND user_id = ?', (hike_id, user_id,))
            hikes_data = db_connection['cursor'].fetchall()
        except sqlite3.Error as error:
            print(error)
            return []
    # Otherwise get all records for specified user
    else:
        try:
            data = db_connection['cursor'].execute(
                'SELECT * FROM hikes WHERE user_id = ? ORDER BY hike_date DESC LIMIT 10', (user_id,))
            hikes_data = db_connection['cursor'].fetchall()
        except sqlite3.Error as error:
            print(error)
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
    for column in sql_data_object.description:
        keys.append(column[0])
    hikes_list = []
    for entry in fetched_hikes_values:
        # Convert each tuple in list to a dictionary by adding keys
        this_entry = {}
        for index, key in enumerate(keys):
            # Ensure max of 1 decimal place for distance (UI spacing only supports 1 dp)
            if key == 'distance_km':
                this_entry[key] = round(entry[index], 1)
            # For some reason, user_id is being returned from db as string, even though
            # It is stored there as an int 🤔 Convert back to int.
            if key == 'user_id':
                this_entry[key] = int(entry[index])
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
    try:
        usernames_query = db_connection['cursor'].execute('SELECT username FROM users')
    except sqlite3.Error as error:
        print(error)
        return []
    usernames = []
    for row in usernames_query:
        usernames.append(row)
    return usernames


def get_user_by_username(db, username):
    '''Takes database file and username string
        Returns dict of user data from users table, or empty dictionary if no user found.
    '''
    keys = get_table_columns(db, 'users')
    db_connection = create_connection(db)
    try:
        user_data = db_connection['cursor'].execute('SELECT * FROM users WHERE username = ?', (username,))
    except sqlite3.Error as error:
        print(error)
        return {}
    values = []
    for row in user_data:
        for position in row:
            values.append(position)
    db_connection['connection'].close()
    if len(values) == 0:
        return {}
    user = generate_user_data_dict(keys, values)
    return user


def get_username_from_user_id(db, user_id):
    '''Takes db file and user_id
        Returns dict with user name related to id.
    '''
    db_connection = create_connection(db)
    try:
        data = db_connection['cursor'].execute('SELECT id, username from users WHERE id = (?)', (user_id,))
    except sqlite3.Error as error:
        print(error)
        return []
    user = {}
    for row in data:
        user['id'] = row[0]
        user['username'] = row[1]
    db_connection['connection'].close()
    return user


def get_similar_usernames(db, query):
    '''Takes database file and query string.
        Returns dict of usernames
        or empty dict.
    '''
    db_connection = create_connection(db)
    try:
        username_data = db_connection['cursor'].execute('SELECT username FROM users')
    except sqlite3.Error as error:
        print(error)
        return {}

    users_list = []
    for row in username_data:
        users_list.append(row[0])

    similar_users = {}
    for username in users_list:
        # Frequency is the number of occurrences where a char in the query matched a char in the username
        frequency = 0
        for char in query:
            if char in username:
                frequency +=1
        # Accuracy is the proportion of matching chars relative to the length of the username
        accuracy = frequency / len(username)
        match_factor = frequency * accuracy
        if frequency > 2 or accuracy >= 0.5:
            similar_users.update({username: match_factor})

    # Source: https://www.datacamp.com/tutorial/sort-a-dictionary-by-value-python
    sorted_similar_users = dict(sorted(similar_users.items(), key=lambda item: item[1], reverse=True))
    return sorted_similar_users


def follow(db, username, followee, action):
    '''Takes db file, username of auth user, username of user to follow and action (follow/unfollow)'''
    db_connection = create_connection(db)
    follower_id = get_user_by_username(db, username)['id']
    followee_id = get_user_by_username(db, followee)['id']
    if action == 'follow':
        try:
            db_connection['cursor'].execute('INSERT OR IGNORE INTO follows (follower_id, followee_id) VALUES (?, ?)', (follower_id, followee_id,))
        except sqlite3.Error as error:
            print(error)
            return error
    else:
        try:
            db_connection['cursor'].execute('DELETE FROM follows WHERE follower_id = (?) AND followee_id = (?)', (follower_id, followee_id,))
        except sqlite3.Error as error:
            print(error)
            return error
    commit_close_conn(db_connection['connection'])
    return 0


def get_followees(db, username):
    '''Takes db file and username.
        Returns list of user ids.
    '''
    followees_list = []
    db_connection = create_connection(db)
    follower_id = get_user_by_username(db, username).get('id')
    try:
        data = db_connection['cursor'].execute('SELECT followee_id FROM follows WHERE follower_id = (?)', (follower_id,))
    except sqlite3.Error as error:
        print(error)
        return []
    for row in data:
        followees_list.append(row[0])
    return followees_list


def get_feed(db, username):
    '''Takes db file and username.
        Returns list of hikes.
    '''
    db_connection = create_connection(db)
    followees_list = get_followees(db, username)
    try:
        data = db_connection['cursor'].execute('SELECT * FROM hikes ORDER BY hike_date DESC LIMIT 1000')
        hikes_data = db_connection['cursor'].fetchall()
    except sqlite3.Error as error:
        print(error)
        return []
    hikes_list = format_hikes(data, hikes_data)
    feed_list = []
    for hike in hikes_list:
        if int(hike['user_id']) in followees_list:
            username = get_username_from_user_id(db, hike.get('user_id')).get('username')
            hike['username'] = username
            feed_list.append(hike)
    return feed_list


def get_table_columns(db, table):
    '''Takes db file and table name as string
        Returns a list of provided table's column names
    '''
    db_connection = create_connection(db)
    query = f'PRAGMA table_info({table})'
    # This query returns a sqlite object containing rows of tuples, each representing a column in the table
        # The column heading is at the [1]th index of each tuple

    try:

        table_info = db_connection['cursor'].execute(query)
    except sqlite3.Error as error:
        print(error)
        return []

    keys = []
    for column in table_info:
        keys.append(column[1])

    commit_close_conn(db_connection['connection'])

    return keys


def generate_user_data_dict(keys, values):
    '''Takes two lists with same number of indecies.
        Returns list with left vals as keys, right vals as values.
    '''
    user = {}
    for index, key in enumerate(keys):
        user[key] = values[index]
    return user


def format_hike_form_data(data):
    '''Takes multidict object from form submission
        Returns list of dictionaries containing formatted form data. 
    '''
    formatted_data = convert_to_dict(data, {})
    return formatted_data


# ==== CLOUDINARY FILE HANDLING ====

def process_img_upload(file, existing_file=''):
    '''Takes file location from file input, and optional existing file from prev import
        Returns cloudinary public_id string
    '''
    # Use existing file (or default value of '' if no file is uploaded)
    # Editing an existing hike will keep previous image, new hike will submit with no image.
    if not file:
        return existing_file
    # Create public_id from username image filename without file type extension
    filename = file.filename.split('.')[0]
    public_id = session.get('username') + filename
    # Call cloudinary store function (passing file location and public id)
    cloudinary.uploader.upload(
        file,
        public_id=public_id,
        unique_filename=False,
        overwrite=True,
        eager='c_lfill,w_900|q_auto:best')
    return public_id


#  ==== FORM VALIDATION ====

# pylint: disable=too-many-return-statements
def validate_hike_form(form_data):
    '''Takes form data
        Returns error type (string) or None
    '''
    # Validate that required fields have values
    for field in form_data:
        if form_data.get(field) == '' and hike_form_content[field]['required'] is True:
            return 'missing_values'
    # Validate that distance field is numbers and decimal chars only
    for char in form_data.get('distance_km'):
        if not char.isnumeric() and not char == '.':
            return 'invalid_number'
    # Validate that numeric string can be converted to float
    try:
        float(form_data.get('distance_km'))
    except ValueError:
        return 'invalid_number'
    # Validate that distance value is between 0 and 100
    distance = float(form_data.get('distance_km'))
    if distance < 0 or distance > 99.9:
        return 'out_of_range'
    # Check for url in form values to eliminate unexpected urls and validate expected ones
    for field in form_data:
        url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls_list = re.findall(url_regex, form_data.get(field))
        # Reject form if non-url field contains url
        if not field == 'map_link' and urls_list:
            return 'unaccepted_url'
        # Validate that map_link field contains valid url if any value is present
        if field == 'map_link' and form_data.get(field) and not urls_list:
            return 'invalid_url'
    return None
# pylint: enable=too-many-return-statements


#  ==== ERROR HANDLING ====

def handle_error(url, message, code=400):
    '''Takes an error code number and string describing the cause of the error
        Returns error template.
    '''
    return render_template('error.html', url=url, message=message, code=code,)


#  ==== DECORATORS ====

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


#  UI HELPERS

def get_context_string_from_referrer(referrer, current_path, username):
    '''Takes http request referrer & path, and username from session.
        Returns string or None.
    '''
    # If 'my-hikes' in query string, user was routed from main nav
    if 'my-hikes' in str(current_path):
        return None
    if 'delete' in str(current_path):
        return 'Hike deleted.'
    if 'cancel' in str(current_path):
        return 'Edits discarded.'
    tmp_list = referrer.split('/')
    routes_dict = {
        'login': f'Logged in as {username.upper()}.',
        'new-hike': 'New hike added.',
        'edit-hike': 'Hike saved.'
    }
    # pylint: disable=consider-using-dict-items
    for route in routes_dict:
        if route in tmp_list:
            return routes_dict[route]
    return None
