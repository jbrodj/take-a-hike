'''For rendering, routing, and accessing request properties'''
from flask import Flask, redirect, render_template, request
from content import form_content
import utils

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/new-hike', methods=['GET', 'POST'])
def new_hike():
    '''Renders new hike form template on GET, or submits hike data to db on POST.'''
    if request.method == 'POST':
        form_data = request.form
        for value in form_data:
            if form_data.get(value) == '' and form_content[value]['required'] is True:
                return render_template('/error.html')

        hike_data = utils.format_form_data(form_data)
        area_name = hike_data['area_name']
        trail_list = hike_data['trails_cs']
        utils.add_area(area_name)
        area_id = utils.get_area_id(area_name, DB)
        utils.add_trail(area_id, trail_list)

        utils.add_hike(hike_data, area_id)
        return redirect('/')
    return render_template('new-hike.html', form_content=form_content)
