from flask import Flask, abort, render_template
from pymongo import MongoClient
from datetime import datetime
import jwt
import jdate
secret = 'secret'
db_client = MongoClient()
db = db_client['days']
days = db['days']
days.drop_indexes()
days.create_index([('key', 1)])

app = Flask(__name__)


@app.route('/<key>')
def index(key):
    key = key.encode()
    now = datetime.now()
    jd = jdate.gregorian_to_jd(now.year, now.month, now.day)
    date = jdate.jd_to_persian(jd)
    user = jwt.decode(key, secret, algorithms=['HS256'])
    q = {
        'user': user['username'],
        'date': {
            'year': date[0],
            'month': date[1],
            'day': date[2],
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
    print(day)
    return day


@app.route('/<key>/<int:year>/<int:month>/<int:day>/<int:hour>:<value>')
def hour(key, year, month, day, hour, value):
    user = jwt.decode(key, secret, algorithms=['HS256'])
    q = {
        'user': user['username'],
        'date': {
            'year': year,
            'month': month,
            'day': day
        }
    }
    try:
        days.update(q, {
            '$set': {
                'hours.{hour}'.format(hour=hour): value
            }
        })
        return 'OK', 200
    except:
        abort(404)


@app.route('/<admin>$', methods=['GET'])
def admin(admin):
    admin = jwt.decode(admin, secret, algorithms=['HS256'])
    if admin['username'] == 'admin':
        return render_template('', )
    abort(403)


@app.route('/<admin>$<username>:<password>')
def new_user(admin, username, password):
    admin = jwt.decode(admin, secret, algorithms=['HS256'])
    if admin['username'] == 'admin':
        encoded_jwt = jwt.encode({'username': username, 'password': password}, secret, algorithm='HS256')
        return encoded_jwt
    abort(403)


@app.route('/<admin>$<key>', methods=['GET'])
def user(admin, key):
    admin = jwt.decode(admin, secret, algorithms=['HS256'])
    if admin['username'] == 'admin':
        user = jwt.decode(key, secret, algorithms=['HS256'])
        year = 'year'
    abort(403)


if __name__ == '__main__':
    print(jwt.encode({'username': 'admin', 'password': 'admin'}, secret, algorithm='HS256'))
    app.run()
