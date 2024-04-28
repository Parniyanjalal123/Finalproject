from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('instance/books.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def show_books():
    # Connect to the database
    conn = get_db_connection()
    # Query to fetch all books from the `books` table
    books = conn.execute('SELECT * FROM books').fetchall()
    # Close the database connection
    conn.close()

    # Render the `books.html` template and pass the list of books
    return render_template('book.html', books=books)


if __name__ == '__main__':
    app.run(debug=True)
