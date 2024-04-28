from flask import Flask, request, render_template, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import date
from sqlalchemy import text
from booklist import get_db_connection

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

app.secret_key = 'secret_key'


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


with app.app_context():
    db.create_all()


@app.route('/')
def welcome():
    # Render the 'welcome.html' template for the main page
    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # If email already exists, display error message
            flash('Account with this email already exists. Please try a different email.', 'error')
            return render_template('register.html')

        # Create a new user if email is not already in use
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to login page after successful registration
        return redirect('/login')

    # Render the registration form
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            session['name'] = user.name
            session['email'] = user.email
            session['password'] = user.password
            return redirect('home')
        else:
            # If login credentials are invalid, flash an error message
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/home')
def home_page():
    if session['name']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('home_page.html', user=user)
    return redirect('/login')


@app.route('/books')
def book_list():
    conn = get_db_connection()
    # Query to fetch all books from the `books` table
    books = conn.execute('SELECT * FROM books').fetchall()
    # Close the database connection
    conn.close()

    # Render the `books.html` template and pass the list of books
    return render_template('book.html', books=books)


# Route for book list
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    language = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)


# Route for the index page
@app.route('/addbook', methods=['GET', 'POST'])
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
        return redirect(url_for('book_added'))

    # Render the index.html template
    return render_template('index.html')


@app.route('/book_added')
def book_added():
    # Render the HTML content showing that the book was added successfully
    return render_template('book_added.html')


@app.route('/searchbooks', methods=['GET'])
def search_books():
    # Get query parameters from the request
    author = request.args.get('author')
    language = request.args.get('language')
    title = request.args.get('title')

    # Start with an initial query for Books
    query = Books.query

    # Apply filters based on the provided parameters
    if author:
        query = query.filter(Books.author.ilike(f'%{author}%'))
    if language:
        query = query.filter(Books.language.ilike(f'%{language}%'))
    if title:
        query = query.filter(Books.title.ilike(f'%{title}%'))

    # Execute the query and get the results
    results = query.all()

    # Render the search results using the search_results.html template
    return render_template('search_results.html', results=results)


# Delete user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        flash('You must be logged in to perform this action.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('show_users'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use. Please try a different email.', 'error')
            return redirect(url_for('add_user'))

        # Create a new user if email is not already in use
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully.', 'success')
        return redirect(url_for('show_users'))

    return render_template('add_user.html')


# Route to show all users
@app.route('/user')
def show_users():
    users = User.query.all()
    return render_template('user.html', users=users)


# Route to handle user updates
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('show_users'))

    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        password = request.form['password']

        if password:
            user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('show_users'))

    return render_template('edit_user.html', user=user)


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page or home page
    return redirect(url_for('login'))


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
