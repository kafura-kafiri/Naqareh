from datetime import datetime

import jwt
from flask import Flask, abort, render_template, url_for, redirect, jsonify
from flask_cors import CORS
from pymongo import MongoClient

import jdate

secret = 'secret'
admin_password = 'admin'
admin_username = 'admin'
db_client = MongoClient()
db = db_client['naqareh']
days = db['days']
days.drop_indexes()
# days.delete_many({})
days.create_index([('key', 1)])

app = Flask(__name__)
CORS(app)


@app.route('/$/<username>:<password>')
def _admin_key(username, password):
    if username != admin_username or password != admin_password:
        abort(403)
    return jwt.encode({'u': username, 'p': password}, secret, algorithm='HS256')


@app.route('/$/<admin_key>/<username>:<password>')
def new_user(admin_key, username, password):
    admin_key = admin_key.encode()
    admin = jwt.decode(admin_key, secret, algorithms=['HS256'])
    if admin['u'] != admin_username or admin['p'] != admin_password:
        abort(403)
    encoded_jwt = jwt.encode({'u': username, 'p': password}, secret, algorithm='HS256')
    q = {'key': encoded_jwt}
    day = days.find_one(q)
    if not day:
        days.insert_one(q)
    return encoded_jwt


@app.route('/<username>:<password>')
def get_key(username, password):
    encoded_jwt = jwt.encode({'u': username, 'p': password}, secret, algorithm='HS256')
    day = days.find_one({'key': encoded_jwt})
    if day:
        return encoded_jwt
    abort(403)


@app.route('/<key>')
def index(key):
    key = key.encode()
    now = datetime.now()
    jd = jdate.gregorian_to_jd(now.year, now.month, now.day)
    date = jdate.jd_to_persian(jd)
    q = {
        'key': key,
        'date': {
            'year': date[0],
            'month': date[1],
            'day': int(date[2]),
        }
    }
    day = days.find_one(q)
    if not day:
        day = q
        day['hours'] = [
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
        ]
        days.insert(day)
    del day['_id']
    day['key'] = day['key'].decode()
    return jsonify(day)


@app.route('/<key>/<int:year>/<int:month>/<int:day>/<int:hour>:<int:value>', methods=['POST', 'GET'])
def set_hour(key, year, month, day, hour, value):
    key = key.encode()
    q = {
        'key': key,
        'date': {
            'year': year,
            'month': month,
            'day': day
        }
    }

    result = days.update(q, {
        '$set': {
            'hours.{hour}'.format(hour=hour): value
        }
    })
    if result['updatedExisting']:
        return 'OK', 200
    abort(404)


@app.route('/$/<admin_key>', methods=['GET'])
def admin_index(admin_key):
    admin_key = admin_key.encode()
    admin = jwt.decode(admin_key, secret, algorithms=['HS256'])
    if admin['username'] == 'admin':
        return render_template('', )
    abort(403)


@app.route('/$/<admin_key>/<key>', methods=['GET'])
def get_user(admin_key, key):
    admin_key = admin_key.encode()
    key = key.encode()
    admin = jwt.decode(admin_key, secret, algorithms=['HS256'])
    if admin['username'] == 'admin':
        user = jwt.decode(key, secret, algorithms=['HS256'])
        year = 'year'
    abort(403)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


if __name__ == '__main__':
    app.run(debug=True)
