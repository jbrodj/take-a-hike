'''Flask for rendering, routing, and accessing request properties'''
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from content import hike_form_content, error_messages
from constants import DB
from utils import (add_area, add_hike, add_trail, add_user, delete_hike, format_hike_form_data,
    get_all_usernames, get_area_id, get_hikes, get_similar_usernames, get_user_by_username,
    handle_error, login_required, update_hike, validate_hike_form)


# Configure app and instantiate Session
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)


@app.after_request
def after_request(response):
    '''Ensure responses aren't cached. Source: CS50'''
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/')
def index():
    '''Renders default template at base route. Or redirects to user page if logged in.'''
    if session:
        return redirect(f'/users/{session["username"]}')
    return render_template('index.html')


@app.route('/users/<username>', methods=['GET', 'POST'])
def user_route(username):
    '''Renders hikes for a given user'''
    # Check if user is valid
    user = get_user_by_username(DB, username)
    is_authorized_to_edit = False
    if not bool(user):
        return handle_error(request.host_url, error_messages['user_not_found'], 403)
    # Get hikes for given user
    hikes_list = get_hikes(DB, user.get('id'))
    # Return no data template if user's hikes list is empty
    if not hikes_list:
        # return render_template('no-data.html')
        return render_template(
            'user.html', username=username, hikes_list=[], auth=is_authorized_to_edit)
    # Check if authenticated user is same as user page (for edit/delete context menu)
    if session.get('username') == username:
        is_authorized_to_edit = True
        # If user clicks edit or delete button, get hike id from button value
        if request.method == 'POST':
            action = request.form.get('edit_hike').split('_')[0]
            hike_id = request.form.get('edit_hike').split('_')[1]
            # Check if it is a delete action
            if action == 'del':
                delete_hike(hike_id, session.get('user_id'))
                return redirect(username)
            # Otherwise it is an edit action
            path = '/edit-hike/' + action + '/' + hike_id
            return redirect(path)
    # Render user page with list of that user's hikes
    return render_template(
        'user.html', username=username, hikes_list=hikes_list, auth=is_authorized_to_edit)


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
            return render_template('user_search.html', query=query_param, results='no_match')
        # Remove exact matched username from list if present
        if exact_match in similar_usernames:
            similar_usernames.pop(exact_match)
        return render_template(
            'user_search.html',
            query=query_param,
            results=similar_usernames,
            exact_match=exact_match
            )
    # Route directly to blank users search page.
    return render_template('user_search.html')


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
        add_user(username, password_hash)
        return redirect('/login')
    # Render signup form
    return render_template('signup.html')


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


@app.route('/logout')
def logout():
    '''Clears user data from session, redirects user to home page.'''
    session.clear()
    return redirect('/')


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
        # Insert to areas, trails, and hikes tables
        area_name = hike_data.get('area_name')
        trail_list = hike_data.get('trails_cs')
        add_area(area_name)
        area_id = get_area_id(area_name, DB)
        add_trail(area_id, trail_list)
        add_hike(session.get('user_id'), area_id, hike_data)
        return redirect('/')
    # Route to new hike form
    return render_template('new-hike.html', form_content=hike_form_content)


@app.route('/edit-hike/<action>/<hike_id>', methods=['GET', 'POST'])
@login_required
def edit_hike(action, hike_id):
    '''Sends update to database to edit or delete hike data'''
    username = session.get('username')
    if request.method == 'POST':
        # Check action for cancel and break out
        if action == 'cancel':
            path = '/users/' + username
            return redirect(path)
        # Format and check form data
        existing_hike_data = get_hikes(DB, session.get('user_id'), hike_id)[0]
        updated_hike_data = format_hike_form_data(request.form)
        form_error = validate_hike_form(updated_hike_data)
        if form_error:
            return handle_error(request.url, error_messages[form_error], 403)
        del updated_hike_data['action']
        # Insert updated data into database
        update_hike(existing_hike_data, updated_hike_data)
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
        '/edit-hike.html', form_content=hike_form_content, selected_hike_data=selected_hike_data)
