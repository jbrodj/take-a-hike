'''For rendering, routing, and accessing request properties'''
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from content import new_hike_form_content, error_messages
import utils


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

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
    '''Renders default template at base route.'''
    hikes_list = utils.get_hikes_for_ui(DB, session['user_id'])
    if not hikes_list:
        return render_template('no-data.html')
    return render_template('index.html', hikes_list=hikes_list)

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    '''Renders sign-up form template on GET, or submits new user to db on POST'''
    if request.method == 'POST':
        username = request.form.get('username')
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

        for existing_name in existing_usernames:
            if username == existing_name[0]:
                return utils.handle_error(request.url, 'Username is already taken', 403)
        utils.add_user(username, password_hash)
        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def log_in():
    '''Renders log-in form template on GET, or validates login data on POST'''
    session.clear()

    if request.method == 'POST':
        username = request.form.get('username')
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

        session['username'] = username
        session['user_id'] = user['id']
        return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    '''Clears user data from session, redirects user to login page.'''
    session.clear()
    return redirect('/login')

@app.route('/new-hike', methods=['GET', 'POST'])
def new_hike():
    '''Renders new hike form template on GET, or submits hike data to db on POST.'''
    if request.method == 'POST':
        form_data = request.form
        # Validate that required fields are populated
        for field in form_data:
            if form_data.get(field) == '' and new_hike_form_content[field]['required'] is True:
                return utils.handle_error(
                    request.url, error_messages['missing_values'], 403)
        # Validate that distance field is numbers and decimal chars only.
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

    return render_template('new-hike.html', form_content=new_hike_form_content)
