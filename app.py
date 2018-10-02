# -*- coding: utf-8 -*-
"""
    Flaskr Plus
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, category, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/filter', methods=['GET'])  # Use get method to change what entries are being displayed
def filter_entries():
    db = get_db()
    if request.args.get("filter") != "":
        cur = db.execute('select title, category, text from entries WHERE category = ?',
                     (request.args.get("filter"),))  # ? to query and request filter form where clause lets me chose
                                                     # what is shown
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries)
    else:
        db = get_db()
        cur = db.execute('select title, category, text from entries order by id desc')
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries)

@app.route('/delete', methods=['GET'])  # Use get method to change what entries are being displayed
def delete_entries():
    db = get_db()
    cur = db.execute('DELETE from entries WHERE id = ?',
                     (request.args.get("delete"),))  # ? to query and request filter form where clause lets me chose
                                                     # what is shown
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (title, category, text) values (?, ?, ?)',
               [request.form['title'], request.form['category'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
