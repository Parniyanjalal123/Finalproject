from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Define the Book model
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    language = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)


# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        author = request.form.get('author')
        language = request.form.get('language')
        title = request.form.get('title')

        # Define the SQL INSERT statement
        sql = text('''
            INSERT INTO books (author, language, title)
            VALUES (:author, :language, :title)
        ''')

        # Execute the SQL statement
        with db.engine.connect() as connection:
            trans = connection.begin()  # Begin a transaction
            try:
                connection.execute(sql, {
                    'author': author,
                    'language': language,
                    'title': title
                })
                trans.commit()  # Commit the transaction if successful
                print("Data committed to database successfully.")
            except Exception as e:
                trans.rollback()  # Rollback the transaction if an error occurs
                print(f"Error executing SQL statement: {e}")

        # Redirect to the same page or another page as needed
        return redirect(url_for('index'))

    # Render the index.html template
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
