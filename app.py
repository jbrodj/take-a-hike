'''For rendering, routing, and accessing request properties'''
from flask import Flask, redirect, render_template, request
from content import formContent

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


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
    return render_template('index.html')

@app.route('/new-hike', methods=['GET', 'POST'])
def new_hike():
    '''Renders new hike form template on GET, or submits hike data to db on POST.'''
    if request.method == 'POST':
        hike_data = request.form
        print(hike_data)
        required_values = ['date', 'area', 'trailhead', 'trails']
        for value in hike_data:
            print(hike_data.get(value))
            if hike_data.get(value) == '' and value in required_values:
                return render_template('/error.html')
        return redirect('/')
    return render_template('new-hike.html', formContent=formContent)
