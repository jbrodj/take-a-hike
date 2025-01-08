'''Unit tests for all python utility functions'''
import os
from init_sql import runner
from utils import  (
        add_user,
        commit_close_conn,
        convert_to_dict,
        create_connection,
        get_all_usernames,
        get_context_string_from_referrer,
        get_similar_usernames,
        get_user_by_username,
        get_username_from_user_id,
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

    def test_add_user(
            self,
            db=DB,
            user_1=mock_users[0],
            user_2=mock_users[1]
            ):
        '''Test add_user util. Takes username string, pw hash string and db file'''
        # Run init_sql with test environment arg to create table schema in a temporary db file
        runner('test')
        # Clear users from table
        db_connection = create_connection(db)
        db_connection['cursor'].execute('DELETE FROM users')
        commit_close_conn(db_connection['connection'])
        # Add a user to table with valid args and check success (ie. 0 return value)
        assert add_user(db, user_1['username'], user_1['password_hash']) == 0
        # Add a user to table with duplicate username and check failure
        #   (ie. there is return value from sqlite error)
        assert add_user(db, user_1['username'], 'differentpasswordhash123') != 0
        # Add a second valid username to table
        assert add_user(db, user_2['username'], user_2['password_hash']) == 0


    def test_get_all_usernames(
            self,
            db = DB,
            num_of_users=len(mock_users),
            username_1=mock_users[0]['username'],
            username_2=mock_users[1]['username']
            ):
        '''Test get_all_usernames util.'''
        assert len(get_all_usernames(db)) == num_of_users
        assert (username_1,) and (username_2,) in get_all_usernames(db)
        assert (username_2,) in get_all_usernames(db)


    def test_get_user_by_username(
            self,
            db=DB,
            username=mock_users[0]['username'],
            password_hash=mock_users[0]['password_hash']
            ):
        '''Test get_user_by_username util. Takes username string, pw hash string and db file'''
        # Retrieve user by username and check dict structure and values
        expected_user_structure = {'id': 1, 'username': username, 'password_hash': password_hash}
        assert get_user_by_username(db, username) == expected_user_structure
        # Call get user by username

    def test_get_username_from_user_id(
            self,
            db=DB,
            username=mock_users[0]['username']
            ):
        '''Test get_username_from_user_id util.'''
        # Call get username from user id and assert correct username returned.
        # User ID is created sequentially by the database when a user is stored
            # - so user 0 will have an id of 1.
        expected_structure = {'id': 1, 'username': username}
        assert get_username_from_user_id(db, 1) == expected_structure
        # Maybe also assert what happens when the user isn't found in both id and username scenarios


    def test_get_similar_usernames(
            self,
            db=DB,
            username_1=mock_users[0]['username'],
            username_2=mock_users[1]['username']
            ):
        '''Test get_similar_usernames util.'''
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
        # Rm temporary db file
        db_path = f'./{db}'
        os.remove(db_path)
        assert os.path.exists(db_path) is False
