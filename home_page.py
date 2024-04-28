

from flask import Flask, render_template, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('instance/books.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home_page():
    return render_template('home_page.html')


@app.route('/user')
def user_page():
    return render_template('user.html')


@app.route('/books')
def books_list():
    return render_template('book.html')


@app.route('/index')
def index_page():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
