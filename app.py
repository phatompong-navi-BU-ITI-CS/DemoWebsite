from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# สร้าง DB ครั้งแรก
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL,
        image TEXT,
        stock INTEGER,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    games = conn.execute('''
        SELECT games.*, categories.name AS category_name
        FROM games
        LEFT JOIN categories ON games.category_id = categories.id
    ''').fetchall()

    return render_template('index.html', games=games)

@app.route('/append', methods=['GET', 'POST'])
def append():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        price = request.form["price"]
        image = request.form["image"]
        stock = request.form["stock"]
        category_id = request.form["category_id"]

        # Handle empty category_id (if no category is selected)
        if not category_id:
            category_id = None

        # Insert the new game into the database
        conn.execute("""
            INSERT INTO games (name, price, image, stock, category_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, price, image, stock, category_id))
        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("append.html", categories=categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        stock = request.form['stock']
        category_id = request.form['category_id']

        conn.execute('''
            UPDATE games
            SET name=?, price=?, image=?, stock=?, category_id=?
            WHERE id=?
        ''', (name, price, image, stock, category_id, id))
        conn.commit()

        return redirect(url_for('index'))

    game = conn.execute('SELECT * FROM games WHERE id=?', (id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()

    return render_template('edit.html', game=game, categories=categories)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM games WHERE id=?', (id,))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)