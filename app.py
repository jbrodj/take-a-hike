'''This module contains app and service configuration and all routes for the application'''
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
from flask_session import Session
from content import hike_form_content, error_messages
from constants import DB, CLOUDINARY_URL_100, CLOUDINARY_URL_900
from utils import (add_area, add_hike, add_trail, add_user, delete_hike, format_hike_form_data,
    follow, get_all_usernames, get_area_id, get_feed, get_followees, get_hikes, get_hike_img_src,
    get_similar_usernames, get_context_string_from_referrer, get_user_by_username, handle_error,
    login_required, process_img_upload, update_hike, validate_hike_form)


# Configure app and instantiate Session
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# -- cloudinary config -- for storing and serving image content
    # Source: https://cloudinary.com/documentation/python_quickstart
# Load environment variables
load_dotenv()
# Pass cloud name to config method
cloudinary.config(
    cloud_name = 'take-a-hike',
    secure = True,
)


@app.after_request
def after_request(response):
    '''Ensure responses aren't cached. Source: CS50'''
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response


# == SPLASH PAGE ==

@app.route('/')
def index():
    '''Renders default template at base route. Or redirects to user page if logged in.'''
    if session:
        return redirect(f'/users/{session["username"]}')
    return render_template('index.html')


#  == FEED ==

@app.route('/users/<username>/feed')
@login_required
def feed(username):
    '''Renders feed template'''
    hikes_list = get_feed(DB, username)
    return render_template(
        'feed.html',
        username=username,
        hikes_list=hikes_list,
        cloudinary_url=CLOUDINARY_URL_900,
        is_feed=True)


#  == USERS  ==

@app.route('/users/<username>', methods=['GET', 'POST'])
def user_route(username):
    '''Renders hikes for a given user'''
    # Check if user is valid
    user = get_user_by_username(DB, username)
    if not bool(user):
        return handle_error(request.host_url, error_messages['user_not_found'], 403)
    # Default params
    is_authorized_to_edit = False
    follow_status = False
    context_string = ''
    # Get hikes for given user
    hikes_list = get_hikes(DB, user.get('id'))
    # Set follow_status if auth user is not same as current user page
    if not session.get('username') == username:
        user_id = get_user_by_username(DB, username).get('id')
        followees_list = get_followees(DB, session.get('username'))
        if user_id in followees_list:
            follow_status = True
    # Return no data template if user's hikes list is empty
    if not hikes_list:
        return render_template(
            'feed.html', username=username, hikes_list=[], following=follow_status)
    # Check if authenticated user is same as user page (for edit/delete context menu)
    if session.get('username') == username:
        is_authorized_to_edit = True
        # If user clicks edit or delete button, get hike id from button value
        if request.method == 'POST':
            action = request.form.get('edit_hike').split('_')[0]
            hike_id = request.form.get('edit_hike').split('_')[1]
            # Check if it is a delete action
            if action == 'del':
                delete_hike(DB, hike_id, session.get('user_id'))
                path = username + '?delete' + hike_id
                return redirect(path)
            # Otherwise it is an edit action
            path = '/edit-hike/' + hike_id
            return redirect(path)
        # Otherwise check for context string
        context_string = get_context_string_from_referrer(
            request.referrer, request.query_string, session.get('username'))
    # Render user page with list of that user's hikes
    return render_template(
        'feed.html', username=username, hikes_list=hikes_list, auth=is_authorized_to_edit,
        context_string=context_string, following=follow_status, cloudinary_url=CLOUDINARY_URL_900)


#  == FOLLOW ==
@app.route('/follow/<username>')
@login_required
def follow_user(username):
    '''Performs follow operation
        Re-renders user page
    '''
    # Perform follow operation
    follow(DB, session['username'], username, 'follow')
    path = '/users/' + username
    return redirect(path)


#  == UNFOLLOW ==

@app.route('/unfollow/<username>')
@login_required
def unfollow_user(username):
    '''Performs follow operation
        Re-renders user page
    '''
    # Perform unfollow operation
    follow(DB, session['username'], username, 'unfollow')
    path = '/users/' + username
    return redirect(path)


#  == USER SEARCH ==

@app.route('/users', methods=['GET', 'POST'])
def user_search():
    '''Renders users search form, or user list template if query string is present
        Redirects to users/<username> if exact match is found.
    '''
    # If form has been submitted, query string will be present.
    if request.query_string:
        query_param = request.args.get("user_search").lower()
        # Validate that input has valid query value.
        if not query_param or not len(query_param) <15:
            return handle_error(request.base_url, error_messages['user_query_invalid'], 403)
        # Check for an exact username match.
        exact_match = get_user_by_username(DB, query_param).get('username')
        # Get similar usernames.
        similar_usernames = get_similar_usernames(DB, query_param)
        if not similar_usernames and not exact_match:
            return render_template('user-search.html', query=query_param, user_list='no_match')
        user_list = []
        for user in similar_usernames:
            is_exact_match = False
            if user == exact_match:
                is_exact_match = True
            user_id = get_user_by_username(DB, user).get('id')
            most_recent_hike_img = get_hike_img_src(DB, user_id)
        # Then create a list of dictionaries:
            user_list.append(
                {'username': user, 'img_src': most_recent_hike_img, 'exact_match': is_exact_match})
        return render_template(
            'user-search.html',
            query=query_param,
            user_list=user_list,
            cloudinary_url=CLOUDINARY_URL_100
            )
    # Route directly to blank users search page.
    return render_template('user-search.html')


# == SIGN UP ==

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    '''Renders sign-up form template on GET, or submits new user to db on POST'''
    if request.method == 'POST':
        username = request.form.get('username').lower()
        # Default method for generate_password_hash (scrypt) doesn't work on macOS,
        # so switching to 'pbdkf2' for development
        password_hash = generate_password_hash(request.form.get('password'), method='pbkdf2')
        existing_usernames = get_all_usernames(DB)
        # Validate that username exists and is alphanumeric amd has correct length
        if not username.isalnum() or not len(username) >3 or not len(username) <15:
            return handle_error(
                request.url, error_messages['username_invalid'], 403)
        # Validate that password exists and is at least 4 characters
        if not len(request.form.get('password')) > 3 or not len(request.form.get('password')) <65:
            return handle_error(
                request.url, error_messages['password_invalid'], 403)
        # Validate that password confirmation matches
        if not request.form.get('password') == request.form.get('confirmation'):
            return handle_error(request.url, error_messages['pw_confirm_match'], 403)
        # Check if submitted username is already taken.
        for existing_name in existing_usernames:
            if username == existing_name[0]:
                return handle_error(request.url, error_messages['username_taken'], 403)
        add_user(DB, username, password_hash)
        return redirect('/login')
    # Render signup form
    return render_template('signup.html')


# == LOG IN ==

@app.route('/login', methods=['GET', 'POST'])
def log_in():
    '''Renders log-in form template on GET, or validates login data on POST'''
    session.clear()

    if request.method == 'POST':
        username = request.form.get('username').lower()
        # Check for valid form field values
        if not username or not request.form.get('password'):
            return handle_error(request.url, error_messages['no_username_or_pw'], 403)
        # Check for existing username
        user = get_user_by_username(DB, username)
        if not bool(user):
            return handle_error(request.url, error_messages['user_not_found'], 403)
        # Validate password
        if not check_password_hash(user.get('password_hash'), request.form.get('password')):
            return handle_error(request.url, error_messages['incorrect_pw'], 403)
        # If values are valid, log in and redirect to home
        session['username'] = username
        session['user_id'] = user.get('id')
        return redirect('/')
    # Route to login form
    return render_template('login.html')


# == LOG OUT ==

@app.route('/logout')
def logout():
    '''Clears user data from session, redirects user to home page.'''
    session.clear()
    return redirect('/')


# == NEW HIKE FORM ==

@app.route('/new-hike', methods=['GET', 'POST'])
@login_required
def new_hike():
    '''Renders new hike form template on GET, or submits hike data to db on POST.'''
    if request.method == 'POST':
        form_data = request.form
        # Validate that required fields are populated
        form_error = validate_hike_form(form_data)
        if form_error:
            return handle_error(request.url, error_messages[form_error], 403)
        # Format form data
        hike_data = format_hike_form_data(form_data)
        # Upload image file and set source as cloudinary public_id
        image_id = process_img_upload(request.files.get('image_url'))

        # Replace img url with cloudinary id
        # hike_data['image_url'] = src_url
        hike_data['image_url'] = image_id

        # Insert to areas, trails, and hikes tables
        area_name = hike_data.get('area_name')
        trail_list = hike_data.get('trails_cs')
        add_area(DB, area_name)
        area_id = get_area_id(area_name, DB)
        add_trail(DB, area_id, trail_list)
        add_hike(DB, session.get('user_id'), area_id, hike_data)
        return redirect('/')
    # Route to new hike form
    return render_template('hike-form.html', form_content=hike_form_content, selected_hike_data={})


#  == EDIT HIKE FORM ==

@app.route('/edit-hike/<hike_id>', methods=['GET', 'POST'])
@login_required
def edit_hike(hike_id):
    '''Sends update to database to edit or delete hike data'''
    username = session.get('username')
    if request.method == 'POST':
        # Check form for cancel action and break out
        if request.form.get('action') == 'cancel':
            path = '/users/' + username + '?cancel'
            return redirect(path)
        # Format and check form data
        existing_hike_data = get_hikes(DB, session.get('user_id'), hike_id)[0]
        updated_hike_data = format_hike_form_data(request.form)
        form_error = validate_hike_form(updated_hike_data)
        if form_error:
            return handle_error(request.url, error_messages[form_error], 403)
        del updated_hike_data['action']
        # Upload image file and set source as cloudinary public_id
        image_id = process_img_upload(
            request.files.get('image_url'), existing_hike_data.get('image_url'))
        # Set image url with either existing or updated value
        updated_hike_data['image_url'] = image_id
        # Insert updated data into database
        update_hike(DB, existing_hike_data, updated_hike_data)
        # Redirect to user page
        path = '/users/' + username
        return redirect(path)
    user_id = session.get('user_id')
    selected_hike_data = get_hikes(DB, user_id, hike_id)[0]
    # Ensure user is authorized to edit this hike:
    # -- If hike user_id doesn't match current user id, get_hikes() will return []
    if not selected_hike_data:
        path = request.host_url + 'users/' + username
        return handle_error(path, error_messages['unauthorized'], 401)
    return render_template(
        '/hike-form.html', form_content=hike_form_content, selected_hike_data=selected_hike_data)
