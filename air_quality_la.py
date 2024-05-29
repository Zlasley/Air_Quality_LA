"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
import openaq
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbaq.sqlite3'
DB = SQLAlchemy(APP)
api = openaq.OpenAQ()


class Record(DB.Model):
    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String(25))
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Time {} --- Value {}>'.format(self.datetime, self.value)


def get_results():
    api = openaq.OpenAQ()
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    results_tup = []
    for data in body['results']:
        tup = (data['date']['utc'], data['value'])
        results_tup.append(tup)
    return results_tup


@APP.route('/')
def root():
    """Base view."""
    api = openaq.OpenAQ()
    status, body = api.measurements(city='Los Angeles', parameter='pm25')

    results = body['results'][:2]
    time_value = []

    for result in results:
        time_value.append(str((result['date']['utc'], result['value'])))

    filtered = Record.query.filter(Record.value >= 18).all()

    return str(filtered)


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    data = get_results()
    for datetime, value in data:
        record = Record(datetime=datetime, value=value)
        DB.session.add(record)
    DB.session.commit()
    return 'Data is refreshed!'
