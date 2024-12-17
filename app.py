'''Flask for rendering, routing, and accessing request properties'''
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from content import hike_form_content, error_messages
import utils


# Configure app and instantiate Session
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)


# Constants
DB = 'hikes.db'


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
    user = utils.get_user_by_username(DB, username)
    is_authorized_to_edit = False
    if not bool(user):
        return utils.handle_error(request.host_url, error_messages['user_not_found'], 403)
    # Get hikes for given user
    hikes_list = utils.get_hikes(DB, user['id'])
    # Return no data template if user's hikes list is empty
    if not hikes_list:
        # return render_template('no-data.html')
        return render_template('user.html', username=username, hikes_list=[], auth=is_authorized_to_edit)
    # Check if authenticated user is same as user page (for edit/delete context menu)
    if session.get('username') == username:
        is_authorized_to_edit = True
        # If user clicks edit or delete button, get hike id from button value
        if request.method == 'POST':
            action = request.form.get('edit_hike').split('_')[0]
            hike_id = request.form.get('edit_hike').split('_')[1]
            # Check if it is a delete action
            if action == 'del':
                utils.delete_hike(hike_id, session.get('user_id'))
                return redirect(username)
            # Otherwise it is an edit action
            path = '/edit-hike/' + action + '/' + hike_id
            return redirect(path)
    # Render user page with list of that user's hikes
    return render_template('user.html', username=username, hikes_list=hikes_list, auth=is_authorized_to_edit)


@app.route('/users', methods=['GET', 'POST'])
def user_search():
    '''Renders users search form, or user list template if query string is present
        Redirects to users/<username> if exact match is found.
    '''
    # If form has been submitted, query string will be present.
    if request.query_string:
        query_param = request.args.get("user_search").lower()
        # Validate that input has valid query value.
        if not query_param:
            return utils.handle_error(request.base_url, error_messages['missing_values'], 403)
        # Check for an exact username match.
        exact_match = utils.get_user_by_username(DB, query_param)
        if exact_match:
            path = '/users/' + query_param
            return redirect(path)
        # Get similar usernames.
        similar_usernames = utils.get_similar_usernames(DB, query_param)
        if not similar_usernames:
            return render_template('user_search.html', query=query_param, results='no_match')
        return render_template('user_search.html', query=query_param, results=similar_usernames)
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
        existing_usernames = utils.get_all_usernames(DB)
        # Validate that username exists and is alphanumeric
        if not username.isalnum():
            return utils.handle_error(
                request.url, error_messages['username_required'], 403)
        # Validate that password exists and is at least 4 characters
        if not len(request.form.get('password')) > 3:
            return utils.handle_error(
                request.url, error_messages['password_required'], 403)
        # Validate that password confirmation matches
        if not request.form.get('password') == request.form.get('confirmation'):
            return utils.handle_error(request.url, error_messages['pw_confirm_match'], 403)
        # Check if submitted username is already taken.
        for existing_name in existing_usernames:
            if username == existing_name[0]:
                return utils.handle_error(request.url, error_messages['username_taken'], 403)
        utils.add_user(username, password_hash)
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
            return utils.handle_error(request.url, error_messages['no_username_or_pw'], 403)
        # Check for existing username
        user = utils.get_user_by_username(DB, username)
        if not bool(user):
            return utils.handle_error(request.url, error_messages['user_not_found'], 403)
        # Validate password
        if not check_password_hash(user['password_hash'], request.form.get('password')):
            return utils.handle_error(request.url, error_messages['incorrect_pw'], 403)
        # If values are valid, log in and redirect to home
        session['username'] = username
        session['user_id'] = user['id']
        return redirect('/')
    # Route to login form
    return render_template('login.html')


@app.route('/logout')
def logout():
    '''Clears user data from session, redirects user to home page.'''
    session.clear()
    return redirect('/')


@app.route('/new-hike', methods=['GET', 'POST'])
@utils.login_required
def new_hike():
    '''Renders new hike form template on GET, or submits hike data to db on POST.'''
    if request.method == 'POST':
        form_data = request.form
        # Validate that required fields are populated
        for field in form_data:
            if form_data.get(field) == '' and hike_form_content[field]['required'] is True:
                return utils.handle_error(
                    request.url, error_messages['missing_values'], 403)
        # Validate that distance field is numbers and decimal chars only
        for char in form_data.get('distance_km'):
            if not char.isnumeric() and not char == '.':
                return utils.handle_error(request.url, error_messages['invalid_number'], 403)
        # Validate that distance value is between 0 and 100
        distance = float(form_data.get('distance_km'))
        if distance < 0 or distance > 99.9:
            return utils.handle_error(request.url, error_messages['out_of_range'], 403)
        # Format form data
        hike_data = utils.format_hike_form_data(form_data)
        # Insert to areas, trails, and hikes tables
        area_name = hike_data['area_name']
        trail_list = hike_data['trails_cs']
        utils.add_area(area_name)
        area_id = utils.get_area_id(area_name, DB)
        utils.add_trail(area_id, trail_list)
        utils.add_hike(session['user_id'], area_id, hike_data)
        return redirect('/')
    # Route to new hike form
    return render_template('new-hike.html', form_content=hike_form_content)


@app.route('/edit-hike/<action>/<hike_id>', methods=['GET', 'POST'])
@utils.login_required
def edit_hike(action, hike_id):
    '''Sends update to database to edit or delete hike data'''
    username = session.get('username')
    if request.method == 'POST':
        # Check action for cancel and break out
        if action == 'cancel':
            path = '/users/' + username
            return redirect(path)
        # Format and check form data
        # TODO validate form
        existing_hike_data = utils.get_hikes(DB, session.get('user_id'), hike_id)[0]
        updated_hike_data = utils.format_hike_form_data(request.form)
        del updated_hike_data['action']
        # Insert updated data into database
        utils.update_hike(existing_hike_data, updated_hike_data)
        # Redirect to user page
        path = '/users/' + username
        return redirect(path)
    user_id = session.get('user_id')
    selected_hike_data = utils.get_hikes(DB, user_id, hike_id)[0]
    # Ensure user is authorized to edit this hike:
    # -- If hike user_id doesn't match current user id, get_hikes() will return []
    if not selected_hike_data:
        path = request.host_url + 'users/' + username
        return utils.handle_error(path, error_messages['unauthorized'], 401)
    return render_template(
        '/edit-hike.html', form_content=hike_form_content, selected_hike_data=selected_hike_data)
