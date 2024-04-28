from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)


# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('instance/books.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


# Route to show users
@app.route('/')
def show_users():
    # Connect to the database
    conn = get_db_connection()
    # Query to fetch all users from the `users` table
    users = conn.execute('SELECT * FROM users').fetchall()
    # Close the database connection
    conn.close()
    # Render the `user.html` template and pass the list of users
    return render_template('user.html', users=users)


# Route to handle form submission for adding new users
@app.route('/add_user', methods=['POST'])
def add_user():
    # Extract form data
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    role = request.form.get('role')
    password= request.form.get('password')

    # Connect to the database
    conn = get_db_connection()
    # Insert the new user into the `users` table
    conn.execute('INSERT INTO users (name, phone, email, role,password) VALUES (?, ?, ?, ?,?)',
                 (name, phone, email, role,password))
    # Commit the transaction
    conn.commit()
    # Close the database connection
    conn.close()

    # Redirect to the user list page
    return redirect('/')


# Route to handle form submission for editing users
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Connect to the database
    conn = get_db_connection()

    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')

        # Update the user's information in the `users` table
        conn.execute('UPDATE users SET name = ?, phone = ?, email = ?, role = ?, password = ? WHERE user_id = ?',
                     (name, phone, email, role, password, user_id))
        # Commit the transaction
        conn.commit()
        # Close the database connection
        conn.close()

        # Redirect to the user list page
        return redirect('/')

    else:
        # Fetch the user data to pre-fill the form
        user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        conn.close()

        # Render the `edit_user.html` template and pass the user data
        return render_template('edit_user.html', user=user)


# Route to handle deleting users
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Connect to the database
    conn = get_db_connection()

    # Delete the user from the `users` table
    conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    # Commit the transaction
    conn.commit()
    # Close the database connection
    conn.close()

    # Redirect to the user list page
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)


