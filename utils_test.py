'''Unit tests for all python utility functions'''
import os
from init_sql import runner
from utils import  (
        add_area,
        add_hike,
        add_user,
        commit_close_conn,
        convert_to_dict,
        create_connection,
        delete_hike,
        follow,
        get_all_usernames,
        get_area_id,
        get_context_string_from_referrer,
        get_feed,
        get_followees,
        get_hikes,
        get_similar_usernames,
        get_user_by_username,
        get_username_from_user_id,
        update_hike,
        validate_hike_form,
        )
# pylint: disable=line-too-long


def test_convert_to_dict():
    '''Test convert_to_dict fn'''
    tuple_list = [('name', 'steve'), ('occupation', 'nozzgobbler')]
    assert convert_to_dict(tuple_list, {}) == {'name': 'steve', 'occupation': 'nozzgobbler'}


def test_get_context_string_from_referrer():
    '''Tests that the correct context string is returned from the given referrer, path and username'''
    mock_referrer = 'http://takeahike.com/users/coolstuff/evencoolerstuff/wow/login/seriouslysocool/'
    mock_current_path = 'http://takeahike.com/users/myname'
    mock_username = 'frannie'

    # Check that referrer logic produces correct string and that username is correctly displayed for login referrer.
    assert get_context_string_from_referrer(mock_referrer ,mock_current_path, mock_username) == f'Logged in as {mock_username.upper()}.'
    # Check that path logic produces expected string
    mock_deleted_current_path = 'http://takeahike.com/users/myname?deleted'
    assert get_context_string_from_referrer(mock_referrer ,mock_deleted_current_path, mock_username) == 'Hike deleted.'
    # Check for no context string if routed from main nav
    mock_nav_current_path = 'http://takeahike.com/users/myname?my-hikes'
    assert get_context_string_from_referrer(mock_referrer ,mock_nav_current_path, mock_username) is None
    # Check for no context string if referrer and path don't contain any specified strings
    mock_null_referrer = 'https://takeahike.com/cool/stuff/wow/users/more-users/even-more-users/coolstuffwow'
    mock_null_current_path = 'https://takeahike.com/reasons-why-this-is-the-best-app-ever/even-more-reasons-why'
    assert get_context_string_from_referrer(mock_null_referrer ,mock_null_current_path, mock_username) is None


# Cleanup
def cleanup(self):
    '''Runs cleanup operations for tests that use the sqlite database'''
    # Rm temporary db file if it exists
    db_path = f'./{self.DB}'
    if os.path.exists(db_path):
        os.remove(db_path)
    # Verify file is removed
    assert os.path.exists(db_path) is False


class TestAddAndRetrieveUser:
    '''Test functionality of adding and retreiving users from the users SQLite table. 
        Must be run as a suite because the subsequent tests use the database entries that
        `test_add_user` test sets up.
    '''
    # Construct mock data
    DB = 'test.db'

    mock_users = [
        {'username': 'Suze', 'password_hash': 'abcdefghijklmnopqrstuvwxyz123456'},
        {'username': 'Frank', 'password_hash': '654321zyxwvutsrqponmlkjihgfedcba'},
    ]

    def setup(self, db=DB):
        '''Creates database table schema. Clears users table if any data exists.'''
        cleanup(self)
        # Run init_sql with test environment arg to create table schema in a temporary db file
        runner('test')
        # Clear users from table
        db_connection = create_connection(db)
        db_connection['cursor'].execute('DELETE FROM users')
        commit_close_conn(db_connection['connection'])


    def test_add_user(
            self,
            db=DB,
            user_1=mock_users[0],
            user_2=mock_users[1],
            run_cleanup=True
            ):
        '''Test add_user util. Takes username string, pw hash string and db file'''
        # Run setup
        self.setup()
        # Add a user to table with valid args and check success (ie. 0 return value)
        assert add_user(db, user_1['username'], user_1['password_hash']) == 0
        # Add a uuser with blank username/pw and check failure
        assert add_user(db, '', user_1['password_hash']) == 'Error: Required value not provided'
        assert add_user(db, user_1['username'], '') == 'Error: Required value not provided'
        # Add a user to table with duplicate username and check failure
        #   (ie. there is return value from sqlite error)
        assert add_user(db, user_1['username'], 'differentpasswordhash123') != 0
        # Add a second valid username to table
        assert add_user(db, user_2['username'], user_2['password_hash']) == 0
        # Run cleanup if running this test on its own
        if run_cleanup:
            # self.cleanup()
            cleanup(self)


    def test_get_all_usernames(
            self,
            db = DB,
            num_of_users=len(mock_users),
            username_1=mock_users[0]['username'],
            username_2=mock_users[1]['username']
            ):
        '''Test get_all_usernames util.'''
        # Run test_add_user to setup users
        self.test_add_user(run_cleanup=False)
        # Check list of usernames for expected values
        assert len(get_all_usernames(db)) == num_of_users
        assert (username_1,) and (username_2,) in get_all_usernames(db)
        # Cleanup
        cleanup(self)


    def test_get_user_by_username(
            self,
            db=DB,
            username=mock_users[0]['username'],
            password_hash=mock_users[0]['password_hash']
            ):
        '''Test get_user_by_username util. Takes username string, pw hash string and db file'''
        # Retrieve user by username and check dict structure and values
        # Run test_add_user to setup database and add users
        self.test_add_user(run_cleanup=False)
        expected_user_structure = {'id': 1, 'username': username, 'password_hash': password_hash}
        # Check for expected user structure
        assert get_user_by_username(db, username) == expected_user_structure
        # Cleanup
        cleanup(self)


    def test_get_username_from_user_id(
            self,
            db=DB,
            username=mock_users[0]['username']
            ):
        '''Test get_username_from_user_id util.'''
        # Run test_add_user to setup database and add users
        self.test_add_user(run_cleanup=False)
        # Call get username from user id and assert correct username returned.
        # User ID is created sequentially by the database when a user is stored
        #   - so user 0 will have an id of 1.
        expected_structure = {'id': 1, 'username': username}
        assert get_username_from_user_id(db, 1) == expected_structure
        # Check for expected value when user isn't found
        assert get_username_from_user_id(db, 9) == {}
        # Cleanup
        cleanup(self)


    def test_get_similar_usernames(
            self,
            db=DB,
            username_1=mock_users[0]['username'],
            username_2=mock_users[1]['username']
            ):
        '''Test get_similar_usernames util.'''
        # Run test_add_user to setup database and add users
        self.test_add_user(run_cleanup=False)
        # Queries where num of chars matching is >=50% of query length,
        #   or where >=3 total chars match should return result.
        assert username_1 in get_similar_usernames(db, 'Sus')
        assert username_1 in get_similar_usernames(db, 'Suzanne')
        assert username_2 in get_similar_usernames(db, 'Fronk')
        # Queries that don't match at least three chars should return empty dict
        # pylint: disable=use-implicit-booleaness-not-comparison
        assert get_similar_usernames(db, 'KSZ Fblthp 12354467890') == {}
        # Queries matching multiple names should return multiple results
        assert len(get_similar_usernames(db, 'franksuz')) > 1
        # Dict should be sorted by match factor (descending) when multiple results are returned.
        ordered_matches = get_similar_usernames(db, 'SuzFrank')
        assert ordered_matches[username_2] > ordered_matches[username_1]
        ordered_matches = get_similar_usernames(db, 'SuzFra')
        assert ordered_matches[username_1] > ordered_matches[username_2]
        # Cleanup
        cleanup(self)


class TestFollowUnfollowFeedFlows:
    '''Test flow where user follows another user, '''

    DB = 'test.db'
    # Create mocked data
    mock_users = [
        {'username': 'Suze', 'password_hash': 'abcdefghijklmnopqrstuvwxyz123456'},
        {'username': 'Frank', 'password_hash': '654321zyxwvutsrqponmlkjihgfedcba'},
    ]

    # Setup:
    def setup(self):
        '''Run setup operations for tests'''
        cleanup(self)
        # Run init_sql runner fn with test environment arg to create table schema in a temporary db file
        runner('test')
        # Create two users
        db_connection = create_connection(self.DB)
        for user in self.mock_users:
            db_connection['cursor'].execute('INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)', (user['username'], user['password_hash'],))
        commit_close_conn(db_connection['connection'])
        # Verify users in db
        assert len(get_all_usernames(self.DB)) == len(self.mock_users)


    def test_follow(self, user_1=mock_users[0]['username'], user_2=mock_users[1]['username'], run_cleanup=True):
        '''Test ability to follow a user and retrieve expected followees list'''
        # Run setup
        self.setup()
        # Check follow for error or successful return
        assert follow(self.DB, user_1, user_2, 'follow') == 0
        # Check get_followees for expected followees list
        assert len(get_followees(self.DB, user_1)) == 1
        db_connection = create_connection(self.DB)
        # Fetch the user id for user_2
        id_data = db_connection['cursor'].execute('SELECT id FROM users WHERE username = (?)', (user_2,))
        for row in id_data:
            user_2_id = row[0]
        db_connection['connection'].close()
        # Check for user_2's id in followees list
        assert user_2_id in get_followees(self.DB, user_1)
        # Run cleanup
        if run_cleanup:
            cleanup(self)


    def test_unfollow(self, user_1=mock_users[0]['username'], user_2=mock_users[1]['username'], run_cleanup=True):
        '''Test ability to unfollow a user and retrieve expected followees list'''
        # Set up by running the follow flow
        self.test_follow(run_cleanup=False)
        # Check unfollow action for error or successful return
        assert follow(self.DB, user_1, user_2, 'unfollow') == 0
        # Check get_followees again for expected empty followees list
        assert len(get_followees(self.DB, user_1)) == 0
        # Run cleanup
        if run_cleanup:
            cleanup(self)


# pylint: disable=too-many-locals
    def test_get_feed(self, user_1=mock_users[0]['username'], user_2=mock_users[1]['username']):
        '''Test ability to generate list of hikes from user's followees list'''
        # Set up by running the follow flow to create two users and have the first user follow the second user
        self.test_follow(run_cleanup=False)
        # Add a hike to second user
        # Fetch the user id for user_2
        db_connection = create_connection(self.DB)
        id_data = db_connection['cursor'].execute('SELECT id FROM users WHERE username = (?)', (user_2,))
        for row in id_data:
            user_2_id = row[0]
        db_connection['connection'].close()
        mock_hike = {
            'hike_date': '2025-01-01',
            'user_id': str(user_2_id),
            'area_id': 1,
            'area_name': 'Kewl Place',
            'trailhead': 'Awesome Trailhead',
            'trails_cs': 'Rad Trail, Tubular Trail',
            'distance_km': '4.9',
            'image_url': 'very-kewl-image',
            'image_alt': 'This is a very kewl image',
            'map_link': 'https://maps.google.com',
            'other_info': 'Woah this trail is kewl!' 
        }
        hike_date, user_id, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info = mock_hike.values()
        # Add hike to table
        db_connection = create_connection(self.DB)
        db_connection['cursor'].execute(
            'INSERT INTO hikes (hike_date, user_id, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [hike_date, user_id, area_id, area_name, trailhead, trails_cs, distance_km, image_url, image_alt, map_link, other_info])
        commit_close_conn(db_connection['connection'])
        # Check get_feed for the first user's expected feed list
        feed = get_feed(self.DB, user_1)
        assert len(feed) == 1
        # Set up by running the unfollow flow
        self.test_unfollow(run_cleanup=False)
        # Check for expected empty feed list after unfollowing user_2
        feed = get_feed(self.DB, user_1)
        assert len(feed) == 0
        # Run cleanup
        cleanup(self)


class TestAddUpdateDeleteRetreiveHike:
    '''Tests user adding, updating, deleting hikes and accessing their hikes list.'''
    DB = 'test.db'
    user = {'username': 'frannie', 'password_hash': 'abcdefghijklmnopqrstuvwxyz123456'}
    mock_hikes = [
        {
            'hike_date': '2025-01-01',
            'area_name': 'Neat Place',
            'trailhead': 'Awesome Trailhead',
            'trails_cs': 'Rad Trail, Tubular Trail',
            'distance_km': '4.9',
            'image_alt': 'This is a very kewl image',
            'other_info': 'Woah this trail is kewl!',
            'map_link': 'https://maps.google.com/map1',
            'image_url': 'very-kewl-image1'
        },
        {
            'hike_date': '2025-01-02',
            'area_name': 'Neat Place',
            'trailhead': 'Neat Trailhead',
            'trails_cs': 'Incredible Trail, Wowzers Trail',
            'distance_km': '6.3',
            'image_alt': 'This is a great image!',
            'other_info': 'Woah this trail is very nice!',
            'map_link': 'https://maps.google.com/map2',
            'image_url': 'very-kewl-image2'
        }
    ]

    # Setup database table schema
    def setup(self, db=DB):
        '''Creates database table schema. Adds one user to a clean user table.'''
        # Cleanup before running
        cleanup(self)
        # Run init_sql with test environment arg to create table schema in a temporary db file
        runner('test')
        # Clear users from table
        db_connection = create_connection(db)
        db_connection['cursor'].execute('DELETE FROM users')
        commit_close_conn(db_connection['connection'])
        # Add a user - user id will be 1
        db_connection = create_connection(db)
        add_user(db, self.user['username'], self.user['password_hash'])
        commit_close_conn(db_connection['connection'])


    def test_add_hike(self, db=DB, run_cleanup=True):
        '''Test adding hike to database from data dict'''
        # Run setup to add user to database
        self.setup()
        # User id and area id will both be 1 because we have only created one area and one user
        user_id = 1
        area_id = 1
        # Check success adding a hike to database
        assert add_hike(db, user_id, area_id, self.mock_hikes[0]) == 0
        # Add second hike to same user
        assert add_hike(db, user_id, area_id, self.mock_hikes[1]) == 0
        # Run cleanup
        if run_cleanup:
            cleanup(self)


    def test_update_hike(self, db=DB, run_cleanup=True):
        '''Test updating the content of an existing hike'''
        # Run test_add_hike to setup db, add user, and add a hike to database.
        self.test_add_hike(run_cleanup=False)
        # Mocked data
        mock_existing_hike_data = {'id': 1}
        mock_updated_hike_data = {
        'hike_date': '2025-01-03',
        'area_name': 'Another Neat Place',
        'trailhead': 'Kewl Trailhead',
        'trails_cs': 'Awesome Trail, Really Neat Trail',
        'distance_km': '12.1',
        'image_alt': 'A particularly neat image',
        'other_info': 'What a stupendous trail!',
        'map_link': 'https://maps.google.com/map123',
        'image_url': 'image-that-is-also-quite-kewl'
        }
        # Change some values in existing hike and check for success
        assert update_hike(db, mock_existing_hike_data, mock_updated_hike_data) == 0
        # Run cleanup
        if run_cleanup:
            cleanup(self)


    def test_get_all_hikes(self, db=DB):
        '''Test `get_hikes` fn -- retreiving list of all hikes with correct values and structure'''
        expected_hike_structure = {
            'id': 1,
            'hike_date': '2025-01-01',
            'user_id': 1,
            'area_id': 1,
            'area_name': 'Neat Place',
            'trailhead': 'Awesome Trailhead',
            'trails_cs': 'Rad Trail, Tubular Trail',
            'distance_km': 4.9,
            'image_url': 'very-kewl-image1',
            'image_alt': 'This is a very kewl image',
            'map_link': 'https://maps.google.com/map1',
            'other_info': 'Woah this trail is kewl!',
            'trails_list': ['Rad Trail', 'Tubular Trail']
            }
        # Run test_add_hike to setup and add two hikes to user's list
        self.test_add_hike(run_cleanup=False)
        # Verify expected hike content and structure
        hikes_list = get_hikes(db, expected_hike_structure['user_id'])
        assert len(hikes_list) == 2
        assert hikes_list[1] == expected_hike_structure
        # Verify list is sorted by date in descending order
        assert hikes_list[0]['hike_date'] > hikes_list[1]['hike_date']
        # Run cleanup
        cleanup(self)


    def test_updated_get_hikes(self, db=DB):
        '''Test `get_hikes` fn -- retreiving hikes that have had values updated'''
        # Retrieve values for an updated hike to check for correct values and structure
        # Run test_update_hike to update the values of the existing hike
        self.test_update_hike(run_cleanup=False)
        expected_updated_structure = {
            'id': 1,
            'hike_date': '2025-01-03',
            'user_id': 1,
            'area_id': 1,
            'area_name': 'Another Neat Place',
            'trailhead': 'Kewl Trailhead',
            'trails_cs': 'Awesome Trail, Really Neat Trail',
            'distance_km': 12.1,
            'image_alt': 'A particularly neat image',
            'other_info': 'What a stupendous trail!',
            'map_link': 'https://maps.google.com/map123',
            'image_url': 'image-that-is-also-quite-kewl',
            'trails_list': ['Awesome Trail', 'Really Neat Trail']
        }
        updated_hikes_list = get_hikes(db, expected_updated_structure['user_id'])
        assert updated_hikes_list[0] == expected_updated_structure


    def test_get_specific_hike(self, db=DB):
        '''Test `get_hikes` fn -- retrieving single hike by hike id'''
        expected_hike_structure = {
            'id': 2,
            'hike_date': '2025-01-02',
            'user_id': 1,
            'area_id': 1,
            'area_name': 'Neat Place',
            'trailhead': 'Neat Trailhead',
            'trails_cs': 'Incredible Trail, Wowzers Trail',
            'distance_km': 6.3,
            'image_url': 'very-kewl-image2',
            'image_alt': 'This is a great image!',
            'map_link': 'https://maps.google.com/map2',
            'other_info': 'Woah this trail is very nice!',
            'trails_list': ['Incredible Trail', 'Wowzers Trail']
            }
        # Run test_add_hike to setup and add a hike to user's list
        self.test_add_hike(run_cleanup=False)
        # Verify expected hike content and structure
        hikes_list = get_hikes(db, expected_hike_structure['user_id'], expected_hike_structure['id'])
        assert hikes_list[0] == expected_hike_structure


    def test_get_most_recent_hike(self, db=DB):
        '''Test `get_hikes` fn -- retrieving single most recent hike by user id'''
        # Run test_add_hike to setup db and add hikes to user's list
        self.test_add_hike(run_cleanup=False)
        # Verify that a single hike is returned, and that it is the mocked hike with the most recent date
        expected_date = self.mock_hikes[1]['hike_date']
        hikes_list = get_hikes(db, 1, hike_id=None, most_recent=True)
        assert len(hikes_list) == 1
        assert hikes_list[0]['hike_date'] == expected_date
        # Run cleanup
        cleanup(self)


    def test_delete_hike(self, db=DB):
        '''Test deleting an existing hike'''
        # Run test_add_hike to setup test database, create user and add a hike.
        self.test_add_hike(run_cleanup=False)
        # Hike id and user id will both be 1 because we are only creating one user and one hike
        user_id = 1
        hike_id = 1
        # Delete hike and check success
        assert delete_hike(db, hike_id, user_id) == 0
        # Check get_hikes to see expected length of 1 for hikes list
        assert len(get_hikes(db, user_id)) == 1
        # Run cleanup
        cleanup(self)


class TestValidateHikeForm:
    '''Tests `validate_hike_form` to check validation of new/edit hike form'''

    def setup(self):
        '''Create mock form data dictionary with valid values for all fields'''
        mock_form_data = {
            'hike_date': '2025-01-03',
            'area_name': 'Another Neat Place',
            'trailhead': 'Kewl Trailhead',
            'trails_cs': 'Awesome Trail, Really Neat Trail',
            'distance_km': '12.1',
            'image_alt': 'A particularly neat image',
            'other_info': 'What a stupendous trail!',
            'map_link': 'https://maps.google.com/map123',
            'image_url': 'image-that-is-also-quite-kewl'
            }
        return mock_form_data


    def test_validate_required_fields(self):
        '''Tests for missing values in required fields'''
        # Run setup to create valid form data dict
        form_data = self.setup()
        # Empty non-required field and check for no error message
        form_data['image_url'] = ''
        assert not validate_hike_form(form_data)
        # Empty required field and check for correct error message
        form_data['area_name'] = ''
        assert validate_hike_form(form_data) == 'missing_values'

    def test_validate_numeric_distance(self):
        '''Tests validation of `distance_km` value'''
        # Run setup to create valid form data dict
        form_data = self.setup()
        # Assert that valid distance value returns no error
        assert not validate_hike_form(form_data)
        # Add non-numeric char to distance field
        form_data['distance_km'] += 'abc'
        assert validate_hike_form(form_data) == 'invalid_number'
        form_data['distance_km'] = '-1'
        assert validate_hike_form(form_data) == 'invalid_number'
        # Add too many decimal characters to make float conversion impossible
        form_data['distance_km'] = '12.1.1'
        assert validate_hike_form(form_data) == 'invalid_number'
        # Add out of range numeric value
        form_data['distance_km'] = '101.1'
        assert validate_hike_form(form_data) == 'out_of_range'


    def test_urls(self):
        '''Tests validation of expected and unexpected url strings'''
        # Run setup to create valid form data dict
        form_data = self.setup()
        # Assert that valid urls return no error
        assert not validate_hike_form(form_data)
        # Add unexpected url to a non-url field and check for correct error
        form_data['area_name'] = 'https://scary-website-you-shouldnt-visit.net/'
        assert validate_hike_form(form_data) == 'unaccepted_url'
        form_data = self.setup()
        # Add invalid url to map_link field and check for correct error
        form_data['map_link'] = '38927y6ifuhw 9348yrh39fuh3 908f4h98hfsrf~~'
        assert validate_hike_form(form_data) == 'invalid_url'


class TestAddRetrieveArea:
    '''Test area table utility functions'''
    DB = 'test.db'
    mock_area_name = 'Kewl Area'

    def setup(self):
        '''Set up sql database'''
        # Execute init_sql with test arg to create test database.
        runner('test')


    def test_add_area(self, db=DB, run_cleanup=True):
        '''Test adding area to areas table'''
        # Run setup
        self.setup()
        # Run add_area and check for success
        assert add_area(db, self.mock_area_name) == 0
        # Add duplicate area and check for no error
        assert add_area(db, self.mock_area_name) == 0
        # Add empty area name and check for expected error
        assert add_area(db, '') == 'Error: Required value not provided'
        if run_cleanup:
            cleanup(self)


    def test_get_area_id(self, db=DB):
        '''Test retreiving area id from areas table'''
        # Run test_add_area to setup database and add an area
        self.test_add_area(run_cleanup=False)
        # Query for area id by valid area name and check for expected value
        assert get_area_id(self.mock_area_name, db) == 1
        # Query nonexistant area name and check for expected response
        assert not get_area_id('fake area name', db)
        # Run cleanup
        cleanup(self)
