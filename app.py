from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def parse_int(value):
    return int(value) if value and value.strip() != '' else None


def parse_float(value):
    return float(value) if value and value.strip() != '' else None


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

    # default categories
    categories = [
        (1, 'Action'),
        (2, 'Adventure'),
        (3, 'RPG'),
        (4, 'Strategy'),
        (5, 'Sports')
    ]

    for cat in categories:
        cur.execute(
            "INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)",
            cat
        )

    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db()

    games = conn.execute('''
        SELECT games.*, categories.name AS category_name
        FROM games
        LEFT JOIN categories
        ON games.category_id = categories.id
    ''').fetchall()

    conn.close()
    return render_template('index.html', games=games)


@app.route('/append', methods=['GET', 'POST'])
def append():
    conn = get_db()
    categories = conn.execute(
        'SELECT * FROM categories'
    ).fetchall()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = parse_float(request.form.get('price', ''))
        image = request.form.get('image', '').strip()
        stock = parse_int(request.form.get('stock', ''))
        category_id = parse_int(request.form.get('category_id', ''))

        conn.execute('''
            INSERT INTO games
            (name, price, image, stock, category_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, price, image, stock, category_id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('append.html', categories=categories)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = parse_float(request.form.get('price', ''))
        image = request.form.get('image', '').strip()
        stock = parse_int(request.form.get('stock', ''))
        category_id = parse_int(request.form.get('category_id', ''))

        conn.execute('''
            UPDATE games
            SET name=?, price=?, image=?, stock=?, category_id=?
            WHERE id=?
        ''', (name, price, image, stock, category_id, id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    game = conn.execute(
        'SELECT * FROM games WHERE id=?',
        (id,)
    ).fetchone()

    categories = conn.execute(
        'SELECT * FROM categories'
    ).fetchall()

    conn.close()

    if game is None:
        return redirect(url_for('index'))

    return render_template(
        'edit.html',
        game=game,
        categories=categories
    )


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute(
        'DELETE FROM games WHERE id=?',
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)