import os, datetime
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify, g, current_app
from werkzeug.utils import secure_filename
import pandas as pd, sqlite3
import json, operator, numpy
from datetime import datetime as dt
from pymongo import MongoClient
from collections import OrderedDict
from flask_paginate import Pagination, get_page_args
from flask_sqlalchemy import SQLAlchemy


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
# Sqlite db setting
app.config.from_pyfile('app.cfg')
db_path = os.path.join(APP_ROOT, 'jobDB.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_path

# Upload file setting

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

@app.before_request
def before_request():
    g.conn = sqlite3.connect('jobDB.db')
    g.conn.row_factory = sqlite3.Row
    g.cur = g.conn.cursor()


@app.teardown_request
def teardown(error):
    if hasattr(g, 'conn'):
        g.conn.close()


app.config.from_pyfile('app.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobDB.db'
db = SQLAlchemy(app)


class Job(db.Model):
    Job_ID = db.Column(db.Integer, primary_key=True)
    Date_Added = db.Column(db.String(20))
    Country_Code = db.Column(db.String(10))
    Job_Board = db.Column(db.String(20))
    Job_Description = db.Column(db.String(254))
    Job_Title = db.Column(db.String(254))
    Job_Type = db.Column(db.String(254))
    City = db.Column(db.String(50))
    State = db.Column(db.String(10))
    Location = db.Column(db.String(50))
    Organization = db.Column(db.String(254))
    Page_URL = db.Column(db.String(254))
    Sector = db.Column(db.String(254))

    def __repr__(self):
        return '<Job %r>' % self.Job_ID


@app.route("/")
def template_test():
    return render_template('dboard.html')


@app.route("/dashboard")
def dashboard():
    return render_template('dboard.html')


# @app.route("/about")
# def about():
#     return render_template('template.html', my_string="Bar",
#         my_list=[12,13,14,15,16,17], title="About", current_time=datetime.datetime.now())
#

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


def default(o):
    if isinstance(o, numpy.int64): return int(o)
    raise TypeError

# endpoints
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
        val.append(numpy.int64(v))

    result ={'dates': key,
             'jobs_available': val}

    return json.dumps(result, default=default)
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
    total = Job.query.count()

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    sql = 'select * from job order by Job_ID limit {}, {}'\
        .format(offset, per_page)
    g.cur.execute(sql)
    jobs = g.cur.fetchall()

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='jobs',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('table.html',
                           jobs=jobs,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )


@app.route('/jobs/', defaults={'page': 1})
@app.route('/jobs', defaults={'page': 1})
@app.route('/jobs/page/<int:page>/')
@app.route('/jobs/page/<int:page>')
def jobs(page):
    g.cur.execute('select * from job')
    total = g.cur.fetchone()[0]
    page, per_page, offset = get_page_args()
    sql = 'select * from job order by Job_ID limit {}, {}'\
        .format(offset, per_page)
    g.cur.execute(sql)
    jobs = g.cur.fetchall()
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=total,
                                record_name='jobs',
                                format_total=True,
                                format_number=True,
                                )
    return render_template('table.html', jobs=jobs,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           active_url='users-page-url',
                           )


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap4')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def get_alignment():
    return current_app.config.get('LINK_ALIGNMENT', '')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      alignment=get_alignment(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )


if __name__ == '__main__':
    app.run(debug=True,port=5001)
