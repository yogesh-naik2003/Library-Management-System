from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os
app = Flask(__name__, static_folder='newfolder', template_folder='.')

app.secret_key = os.urandom(24)

print("Template folder:", os.path.abspath(app.template_folder))

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'Yogi@2511' 
app.config['MYSQL_DB'] = 'library_db'  

mysql = MySQL(app)

@app.route('/')
def index():
    return "<h1>Welcome to the Library Management System</h1><p><a href='/register'>Go to Registration Page</a></p>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # Handle form submission
        full_name = request.form['fullName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        phone = request.form['phone']
        role = request.form['role']
        user_id = request.form['userId']
        dob = request.form['dob']
        terms = 'terms' in request.form

        # Validate password match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # Connect to the database and insert data
        cur = mysql.connection.cursor()

        if role == 'student':
            library_card = request.form['libraryCard']
            usn = request.form['usn']
            branch = request.form['branch']
            query = "INSERT INTO users (full_name, username, email, password, phone, role, user_id, dob, library_card, usn, branch) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query, (full_name, username, email, password, phone, role, user_id, dob, library_card, usn, branch))
        elif role == 'admin':
            admin_id = request.form['adminId']
            query = "INSERT INTO users (full_name, username, email, password, phone, role, user_id, dob, admin_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query, (full_name, username, email, password, phone, role, user_id, dob, admin_id))

        # Commit the transaction and close the cursor
        mysql.connection.commit()
        cur.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
