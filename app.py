# /usr/bin/python2.7
import psycopg2
from configparser import ConfigParser
from flask import Flask, request, render_template, g, abort
import time
import redis
from redis_host import REDIS_HOST

cache = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=None)


def config(filename='config/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def dbfetch(sql):
    # connect to database listed in database.ini
    conn = connect()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql)

        # fetch one row
        retval = cur.fetchone()

        # close db connection
        cur.close()
        conn.close()
        print("PostgreSQL connection is now closed")

        return retval
    else:
        return None


def connect():
    """ Connect to the PostgreSQL database server and return a cursor """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)
        conn = None

    else:
        # return a conn
        return conn


app = Flask(__name__)


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.route("/")
def index():
    cached_db_result = cache.get('cached_db_result')
    cached_params = cache.get('cached_params')
    if cached_db_result and cached_params:
        print('Cached data found!')
        db_version = (str(cached_db_result, 'utf-8') + ', via AWS ElastiCache')
        db_host = (str(cached_params, 'utf-8') + ' via AWS ElastiCache')
    else:
        print('No cached data found. Querying database...')
        sql = 'SELECT slow_version();'
        db_result = dbfetch(sql)
        params = config()
        db_host = params['host']

        if db_result:
            db_version = ''.join(db_result)
            cache.set('cached_db_result', db_version)
            cache.set('cached_params', db_host)
        else:
            abort(500)

    return render_template('index.html', db_version=db_version, db_host=db_host)


if __name__ == "__main__":  # on running python app.py
    app.run()  # run the flask app
