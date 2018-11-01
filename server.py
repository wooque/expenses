import json
import sqlite3
from calendar import monthrange
from datetime import datetime

from flask import Flask, g, render_template, request
from dateutil.relativedelta import relativedelta


DATABASE = '/mnt/PODACI/Dropbox/personal/troskovi.db'
app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db.cursor()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    if 'insert' in query or 'delete' in query:
        cur.connection.commit()
        rv = None
    else:
        if one:
            rv = cur.fetchone()
            rv = rv[0] if rv else None
        else:
            rv = cur.fetchall()
    cur.close()
    return rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def monthly(dt):
    mntly = query_db(
        "select sum(amount) from expenses where date like ?",
        (dt.strftime("%Y-%m-%%"),),
        one=True,
    )
    return mntly or 0


def daily(dt, fill_missing=True):
    data = query_db(
        """select strftime('%d', date), sum(amount)
            from expenses
            where date like ?
            group by strftime('%d', date)
            order by date""",
        (dt.strftime("%Y-%m-%%"),),
    )
    data = dict([(int(e[0]), e[1]) for e in data])
    for day in range(1, monthrange(dt.year, dt.month)[1] + 1):
        if not fill_missing and day > dt.day:
            break

        if day not in data:
            data[day] = 0

    return data


def values_to_str(dict_):
    values = []
    for day in sorted(dict_.keys()):
        values.append(str(dict_[day]))

    return ','.join(values)


def expense_types():
    types = query_db("select distinct type from expenses")
    return [t[0] for t in types]


def by_type(dt):
    data = query_db(
        """select type, sum(amount)
            from expenses
            where date like ?
            group by type""",
        (dt.strftime("%Y-%m-%%"),),
    )
    data = dict(data)
    for t in expense_types():
        if t not in data:
            data[t] = 0
    return data


def estimates_by_type(previous_data, current_data, today):
    days = monthrange(today.year, today.month)[1]

    estimates = {}
    for t in previous_data.keys():
        prev = previous_data[t]
        curr = current_data[t]

        e = int(curr / today.day * days)
        if e < 0.8 * prev:
            e = prev
        if e > 1.2 * prev:
            e = curr
        estimates[t] = e

    return estimates


@app.route("/")
def stats():
    today = datetime.today()

    current = monthly(today)

    current_daily = daily(today, fill_missing=False)
    current_by_type_data = by_type(today)

    previous_month = today.replace(day=1) - relativedelta(months=1)
    previous = monthly(previous_month)

    previous_daily = daily(previous_month)
    previous_by_type_data = by_type(previous_month)

    estimates_by_type_data = estimates_by_type(
        previous_by_type_data, current_by_type_data, today,
    )
    estimate = sum(estimates_by_type_data.values())

    types = ','.join([t.title() for t in sorted(expense_types())])

    return render_template(
        "stats.html",
        current=int(current),
        estimate=int(estimate),
        previous=int(previous),
        current_daily=values_to_str(current_daily),
        previous_daily=values_to_str(previous_daily),
        types=types,
        previous_by_type=values_to_str(previous_by_type_data),
        current_by_type=values_to_str(current_by_type_data),
        estimates_by_type=values_to_str(estimates_by_type_data),
    )


@app.route("/types")
def types():
    sql = "select distinct type from expenses"
    params = ()
    query = request.args.get('q')
    if query:
        sql += " where type like ?"
        params = (query + '%',)

    data = query_db(sql, params)
    data = [dict(value=d[0], tokens=d[:1]) for d in data]
    return json.dumps(data)


@app.route("/names")
def names():
    sql = "select distinct name from expenses"
    params = ()
    query = request.args.get('q')
    if query:
        sql += " where name like ?"
        params = (query + '%',)

    data = query_db(sql, params)
    data = [dict(value=d[0], tokens=[d[0].split()]) for d in data]
    return json.dumps(data)


def render_table():
    today = datetime.today()
    month = request.args.get('month')
    if month == 'prev':
        today = today.replace(day=1) - relativedelta(months=1)

    table = query_db(
        "select * from expenses where date like ? order by id desc",
        (today.strftime('%Y-%m-%%'),),
    )
    return render_template(
        'table.html',
        today=today.strftime('%Y-%m-%d'),
        table=table,
    )


@app.route("/table", methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        query_db(
            "insert into expenses(date, type, name, amount) values (?, ?, ?, ?)",
            (
                request.form['date'], request.form['type'],
                request.form['name'], request.form['price'],
            )
        )
    return render_table()


@app.route("/delete")
def delete():
    query_db("delete from expenses where id=?", (request.args['id'],))
    return render_table()

if __name__ == "__main__":
    app.run()
