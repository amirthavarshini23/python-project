from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Init DB
def init_db():
    conn = sqlite3.connect('bloodbank.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, age INTEGER, blood_group TEXT,
            contact TEXT, bp TEXT, sugar TEXT, weight REAL
        )
    ''')
    conn.commit()
    conn.close()

# Admin login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple static check (replace with DB check if needed)
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/dashboard')
        else:
            error = "Invalid credentials!"
    return render_template('login.html', error=error)

# Admin dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect('bloodbank.db')
    c = conn.cursor()
    c.execute("SELECT * FROM donors")
    donors = c.fetchall()
    conn.close()
    return render_template('dashboard.html', donors=donors)

# Add donor
@app.route('/add', methods=['POST'])
def add():
    if not session.get('admin'):
        return redirect('/')
    data = (
        request.form['name'],
        request.form['age'],
        request.form['blood_group'],
        request.form['contact'],
        request.form['bp'],
        request.form['sugar'],
        request.form['weight']
    )
    conn = sqlite3.connect('bloodbank.db')
    c = conn.cursor()
    c.execute('''INSERT INTO donors (name, age, blood_group, contact, bp, sugar, weight)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# Delete donor
@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect('bloodbank.db')
    c = conn.cursor()
    c.execute("DELETE FROM donors WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

#search donor
@app.route('/search', methods=['GET'])
def search():
    if not session.get('admin'):
        return redirect('/')

    blood_group = request.args.get('blood_group')
    donors = None

    if blood_group:
        conn = sqlite3.connect('bloodbank.db')
        c = conn.cursor()
        c.execute("SELECT * FROM donors WHERE lower(blood_group) = ?", (blood_group.lower(),))
        donors = c.fetchall()
        conn.close()

    return render_template('search.html', donors=donors)


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=True)

