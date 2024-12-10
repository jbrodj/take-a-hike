'''For rendering, routing, and accessing request properties'''
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from content import new_hike_form_content
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
    hikes_list = utils.get_hikes_for_ui(DB)
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
                request.url, 'A username containing only letters and numbers is required', 403)
        # Validate that password exists and is at least 4 characters
        if not len(request.form.get('password')) > 3:
            return utils.handle_error(
                request.url, 'Password with minimum of 4 characters is required', 403)
        # Validate that password confirmation matches
        if not request.form.get('password') == request.form.get('confirmation'):
            return utils.handle_error(request.url, 'Passwords must match', 403)

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
            return utils.handle_error(request.url, 'Username and password are required', 403)
        # Check for existing username
        user = utils.get_user_by_username(DB, username)
        if not bool(user):
            return utils.handle_error(request.url, 'Username not found', 403)
        # Validate password
        if not check_password_hash(user['password_hash'], request.form.get('password')):
            return utils.handle_error(request.url, 'Incorrect password', 403)

        session['username'] = username
        session['user_id'] = user['id']
        return redirect('/')

    return render_template('login.html')

@app.route('/new-hike', methods=['GET', 'POST'])
def new_hike():
    '''Renders new hike form template on GET, or submits hike data to db on POST.'''
    if request.method == 'POST':
        form_data = request.form
        for value in form_data:
            if form_data.get(value) == '' and new_hike_form_content[value]['required'] is True:
                return utils.handle_error(
                    request.url, 'Date, area, trailhead, and trails are required values.', 403)

        hike_data = utils.format_hike_form_data(form_data)
        area_name = hike_data['area_name']
        trail_list = hike_data['trails_cs']
        utils.add_area(area_name)
        area_id = utils.get_area_id(area_name, DB)
        utils.add_trail(area_id, trail_list)

        utils.add_hike(hike_data, area_id)
        return redirect('/')
    return render_template('new-hike.html', form_content=new_hike_form_content)
