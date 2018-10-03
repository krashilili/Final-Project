import os, datetime
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import json, operator
from datetime import datetime as dt
from pymongo import MongoClient
from collections import OrderedDict
from flask_paginate import Pagination, get_page_parameter

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'])

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

file_name = 'Dice_US_jobs.csv'
file = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

DATA_FOLDER = os.path.join(APP_ROOT, 'data')
geojson_name = 'city_jobs.geojson'
geojson_file =  os.path.join(DATA_FOLDER, geojson_name)


df = pd.read_csv(file, encoding="ISO-8859-1")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

app.jinja_env.filters['datetimefilter'] = datetimefilter


@app.route("/")
def template_test():
    return render_template('template.html', my_string="Wheeeee!",
        my_list=[0,1,2,3,4,5], title="Index", current_time=datetime.datetime.now())

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('template.html', my_string="Foo",
        my_list=[6,7,8,9,10,11], title="Home", current_time=datetime.datetime.now())


@app.route("/about")
def about():
    return render_template('template.html', my_string="Bar",
        my_list=[12,13,14,15,16,17], title="About", current_time=datetime.datetime.now())


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file_directory = app.config['UPLOAD_FOLDER']
    files = [f for f in os.listdir(file_directory)]


    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload',
                                    filename=filename))


    return """
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
              <input type=file name=file>
              <input type=submit value=Upload>
            </form>
            </html>
            """


@app.route('/save2db/<filename>')
def save_to_mongodb(filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file, encoding="ISO-8859-1")

    records = df.to_dict('records')

    conn = MongoClient('localhost')
    db = conn['jobdb']
    coll = db['jobs']

    cursor = coll.find({})
    num_docs = cursor.count()

    if num_docs > 21000:
        return "The data exists in the database."

    else:
        coll.insert_many(records)
        return "The data has been inserted into the database."


@app.route('/job_type')
def job_type():
    full_time = 0
    contract = 0
    # file = os.path.join(app.config['UPLOAD_FOLDER'], )
    for job_type in df['job_type']:

        try:
            job = job_type.lower()
            if 'full' in job:
                full_time += 1

            if 'contract' in job or 'c2h' in job:
                contract += 1
        except:
            pass

    result= jsonify({'full_time': full_time,
                    'contract': contract})
    return result


@app.route('/organization')
def org():
    company = df.groupby('organization')
    org = company.count()['job_type'].sort_values(ascending=False)[:25].to_dict()
    org['Nigel Frank International Inc'] = org['Nigel Frank International'] + org['Nigel Frank International Inc.']

    org.pop('Nigel Frank International')
    org.pop('Nigel Frank International Inc.')

    return jsonify(org)


@app.route('/date_added')
def date_added():
    dates = df.groupby('date_added')
    dcts = dates.count()['job_title'].to_dict()
    dcts2 = {dt.strptime(k, '%m/%d/%Y'): v for k, v in dcts.items()}

    ordered = OrderedDict(sorted(dcts2.items(), key=operator.itemgetter(0)))

    key, val = list(), list()
    for k, v in ordered.items():
        date = dt.strftime(k, '%m/%d/%Y')
        key.append(date)
        val.append(v)

    result ={'dates': key,
             'jobs_available': val}

    return jsonify(result)
    # return "DOne"


@app.route('/geojson')
def map():
    # df.read(geojson_file)
    geojson = dict()
    df = pd.read_json(geojson_file)

    geojson['features'] = list(df['features'])
    geojson['type'] = 'FeatureCollection'

    return jsonify(geojson)


@app.route('/table')
def table():
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    # users = User.find(...)
    # pagination = Pagination(page=page, total=users.count(), search=search, record_name='users')

    # 'page' is the default name of the page parameter, it can be customized
    # e.g. Pagination(page_parameter='p', ...)
    # or set PAGE_PARAMETER in config file
    # also likes page_parameter, you can customize for per_page_parameter
    # you can set PER_PAGE_PARAMETER in config file
    # e.g. Pagination(per_page_parameter='pp')

    # return render_template('table.html',
    #                        users=users,
    #                        pagination=pagination,
    #                        )

    return "Done!"


if __name__ == '__main__':
    app.run(debug=True, port=5001)
