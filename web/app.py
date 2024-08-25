from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# SQLite-Database connection
def get_db_connection():
    conn = sqlite3.connect('nacl.db',check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout = 50000')  # Timeout von 30 Sekunden
    return conn

# Default page (redirect)
@app.route('/')
def index():
    return redirect(url_for('mappings'))

# Page: Display Mappings
@app.route('/mappings')
def mappings():
    conn = get_db_connection()
    mappings = conn.execute(
        'SELECT m.netgroup, m.contentgroup, n.subnet, n.comment AS ncomment, '
        'c.filter, c.type, c.comment AS ccomment '
        'FROM mapping m '
        'JOIN netgroups n ON m.netgroup = n.id '
        'JOIN contentgroups c ON m.contentgroup = c.id'
    ).fetchall()
    conn.close()
    return render_template('mappings.html', mappings=mappings)

# Page: Add Mapping
@app.route('/add_mapping', methods=('GET', 'POST'))
def add_mapping():
    conn = get_db_connection()
    netgroups = conn.execute('SELECT * FROM netgroups').fetchall()
    contentgroups = conn.execute('SELECT * FROM contentgroups').fetchall()

    if request.method == 'POST':
        netgroup = request.form['netgroup']
        contentgroup = request.form['contentgroup']

        conn.execute(
            'INSERT INTO mapping (netgroup, contentgroup) VALUES (?, ?)',
            (netgroup, contentgroup)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('mappings'))

    conn.close()
    return render_template('add_mapping.html', netgroups=netgroups, contentgroups=contentgroups)

#Page: Delete Mapping
@app.route('/delete_mapping/<int:netgroup>/<int:contentgroup>', methods=('POST',))
def delete_mapping(netgroup, contentgroup):
    conn = get_db_connection()
    conn.execute('DELETE FROM mapping WHERE netgroup = ? AND contentgroup = ?', (netgroup, contentgroup))
    conn.commit()
    conn.close()
    return redirect(url_for('mappings'))

#Page: Display Netgroups
@app.route('/netgroups')
def netgroups():
    conn = get_db_connection()
    netgroups = conn.execute('SELECT * FROM netgroups').fetchall()
    conn.close()
    return render_template('netgroups.html', netgroups=netgroups)

#Page: Create Netgroup
@app.route('/add_netgroup', methods=('GET', 'POST'))
def add_netgroup():
    if request.method == 'POST':
        subnet = request.form['subnet']
        comment = request.form.get('comment', '')

        conn = get_db_connection()
        conn.execute('INSERT INTO netgroups (subnet, comment) VALUES (?, ?)', (subnet, comment))
        conn.commit()
        conn.close()
        return redirect(url_for('netgroups'))

    return render_template('add_netgroup.html')

#Page: Delete Netgroup
@app.route('/delete_netgroup/<int:id>', methods=('POST',))
def delete_netgroup(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM netgroups WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('netgroups'))

#Page: Display Contentgroups
@app.route('/contentgroups')
def contentgroups():
    conn = get_db_connection()
    contentgroups = conn.execute('SELECT * FROM contentgroups').fetchall()
    conn.close()
    return render_template('contentgroups.html', contentgroups=contentgroups)

#Page: Add Contentgroup
@app.route('/add_contentgroup', methods=('GET', 'POST'))
def add_contentgroup():
    if request.method == 'POST':
        ctype = request.form['type']
        filter_ = request.form['filter']
        comment = request.form.get('comment', '')

        conn = get_db_connection()
        conn.execute('INSERT INTO contentgroups (type, filter, comment) VALUES (?, ?, ?)', (ctype, filter_, comment))
        conn.commit()
        conn.close()
        return redirect(url_for('contentgroups'))

    return render_template('add_contentgroup.html')

#Page: Delete Contentgroup
@app.route('/delete_contentgroup/<int:id>', methods=('POST',))
def delete_contentgroup(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM contentgroups WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('contentgroups'))

#Start app
if __name__ == '__main__':
    app.run(debug=False)
