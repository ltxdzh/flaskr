'''
Created on 2015-09-02

@author: zeng
'''

# all the imports
import sqlite3
import flaskr_conf
from contextlib import closing
from flask_bootstrap import Bootstrap
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash



# create our little application :)
app = Flask(__name__)
app.config.from_object(flaskr_conf)
bootstrap = Bootstrap(app)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    
    if db is not None:
        db.close()
        
    g.db.close()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/show_entries')
def show_entries():
    cur = g.db.execute('select id, title, text from entries order by id desc')
    entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    
    return render_template('show_entries.html', entries=entries)


@app.route('/add_table')
def show_add_table():
    
    return render_template('add_entries.html')


@app.route('/show_alter', methods=['POST'])
def show_alter():
    
    cur = g.db.execute('select * from entries where id = (?)', [request.form['id']])
    entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    
    if entries:
        return render_template('alter_entry.html', entry=entries[0])
    else:
        abort(401)


@app.route('/add_entry', methods=['POST'])
def add_entry():
        
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    
    flash('New entry was successfully posted')
    
    return redirect(url_for('show_entries'))


@app.route('/alter_entry', methods=['POST'])
def alter_entry():
    
    print [request.form['title'], request.form['text'], request.form['id']]
    
    g.db.execute('update entries set title = (?), text = (?) where id = (?)',
                 [request.form['title'], request.form['text'], request.form['id']])
    g.db.commit()
    
    return redirect(url_for('show_entries'))


@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    
    if not session.get('logged_in'):
        abort(401)
    
    g.db.execute('delete from entries where id = (?)', [request.form['id']])
    g.db.commit()
    
    flash('Entry deleted')
    
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    error = None
    
    if request.method == 'POST':
        
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
            
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
            
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('%s has logged in' % request.form['username'])
            
            return redirect(url_for('show_entries'))
        
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    user = session.pop('logged_in', None)
    flash('%s has logged out' % user)
    return redirect(url_for('index'))



if __name__ == '__main__':
    
#     init_db()
    app.run(host = '0.0.0.0')