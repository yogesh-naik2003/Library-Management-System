import os
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, make_response
from flask_cors import CORS
import mysql.connector
import secrets
import jwt
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
SECRET_KEY = secrets.token_hex(32)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your database password",
        database="library_db"
    )
    print("Database connection successful!")
    return conn

EVENT_IMAGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'event_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['EVENT_IMAGE_UPLOAD_FOLDER'] = EVENT_IMAGE_UPLOAD_FOLDER
os.makedirs(EVENT_IMAGE_UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Serve files from the uploads directory (including event_images)
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/')
def home():
    return "<h1>Flask is running</h1><p>The backend is operational. Navigate to <a href='/adminstudent'>Admin/Student Page</a> to access the adminstudent.html page.</p>"

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", (username, password))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    if admin:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid Admin credentials'})

@app.route('/admin-logout', methods=['POST'])
def admin_logout():
    return jsonify({'success': True, 'message': 'Admin logged out successfully'})

@app.route('/student-login', methods=['POST'])
def student_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student_users WHERE username = %s AND password = %s", (username, password))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid Student credentials'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection error.'}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
        cursor.execute(query, (username, password, role))
        user = cursor.fetchone()

        if user:
            # No need to generate JWT for simple redirect, just return role
            return jsonify({'success': True, 'message': f'Welcome, {user["full_name"]}!', 'role': role})
        else:
            return jsonify({'success': False, 'message': 'Invalid username, password, or role.'})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([{'book_id': b[0], 'book_name': b[1], 'author': b[2], 'category': b[3], 'description': b[4]} for b in books])
    
    elif request.method == 'POST':
        data = request.get_json()
        action = data.get('action')

        conn = get_db_connection()
        cursor = conn.cursor()

        if action == 'add':
            sql = 'INSERT INTO books (book_id, book_name, author, category, description) VALUES (%s, %s, %s, %s, %s)'
            val = (data['book_id'], data['book_name'], data['author'], data['category'], data['description'])
            cursor.execute(sql, val)
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Book added successfully!'})

        elif action == 'delete':
            sql = 'DELETE FROM books WHERE book_id = %s'
            val = (data['book_id'],)
            cursor.execute(sql, val)
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Book deleted successfully!'})

        elif action == 'update':
            sql = 'UPDATE books SET book_name=%s, author=%s, category=%s, description=%s WHERE book_id=%s'
            val = (data['book_name'], data['author'], data['category'], data['description'], data['book_id'])
            cursor.execute(sql, val)
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Book updated successfully!'})

        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid action'})

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')
        feedback_type = data.get('feedback_type')
        message = data.get('message')

        usn = data.get('usn') if role == 'student' else None
        branch = data.get('branch') if role == 'student' else None
        admin_id = data.get('admin_id') if role == 'admin' else None

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedbacks (name, email, role, usn, branch, admin_id, feedback_type, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, role, usn, branch, admin_id, feedback_type, message))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Feedback submitted successfully!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM feedbacks ORDER BY created_at DESC")
        feedbacks = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(feedbacks)

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    
@app.route('/feedbacks/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedbacks WHERE id = %s", (feedback_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Feedback deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/students', methods=['GET', 'POST', 'DELETE'])
def students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(students)

    elif request.method == 'POST':
        data = request.get_json()
        if data.get('action') == 'update':
            usn = data.get('usn')
            name = data.get('name')
            age = data.get('age')
            branch = data.get('branch')
            if not usn or not name or not age or not branch:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            cursor.execute(
                'UPDATE students SET name=%s, age=%s, branch=%s WHERE usn=%s',
                (name, age, branch, usn)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Student updated successfully'})

        usn = data.get('usn')
        name = data.get('name')
        age = data.get('age')
        branch = data.get('branch')

        if not usn or not name or not age or not branch:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        cursor.execute('INSERT INTO students (usn, name, age, branch) VALUES (%s, %s, %s, %s)', 
                       (usn, name, age, branch))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Student added successfully'})

    elif request.method == 'DELETE':
        data = request.get_json()
        usn = data.get('usn')

        cursor.execute('DELETE FROM students WHERE usn = %s', (usn,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Student removed successfully'})

@app.route('/adminstudent')
def adminstudent():
    return send_file('c:/Users/Yogi/OneDrive/Desktop/New folder/DBMS PROJECT/librarymanagementsystem/adminstudent.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    full_name = data.get('fullName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    phone = data.get('phone')
    user_id = data.get('userId')
    dob = data.get('dob')

    library_card = data.get('libraryCard') if role == 'student' else None
    usn = data.get('usn') if role == 'student' else None
    branch = data.get('branch') if role == 'student' else None
    admin_id = data.get('adminId') if role == 'admin' else None

    print("Received data:", data)
    print("Full Name:", full_name)
    print("Role:", role)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check for duplicate username or email
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Username or email already exists. Please choose another.'})

        cursor = conn.cursor()
        if role == 'student':
            query = """
                INSERT INTO users (full_name, username, email, password, phone, role, user_id, dob, library_card, usn, branch)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, username, email, password, phone, role, user_id, dob, library_card, usn, branch))
        elif role == 'admin':
            query = """
                INSERT INTO users (full_name, username, email, password, phone, role, user_id, dob, admin_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, username, email, password, phone, role, user_id, dob, admin_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        import traceback
        print("Error:", e)
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Registration failed. Please try again.'})

@app.route('/reviews', methods=['GET'])
def get_reviews():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
             print("Error: Failed to get database connection for fetching reviews.")
             return jsonify({"success": False, "message": "Database connection error."}), 500

        cursor = conn.cursor(dictionary=True)

        query = "SELECT book_title, author, username, usn, review_text, rating, created_at FROM book_reviews ORDER BY created_at DESC"
        cursor.execute(query)
        reviews_raw = cursor.fetchall()

        for review in reviews_raw:
            if 'created_at' in review and isinstance(review['created_at'], datetime.datetime):
                review['created_at'] = review['created_at'].isoformat()

        return jsonify(reviews_raw)

    except mysql.connector.Error as db_err:
        print(f"Database Error fetching reviews: {db_err}")
        return jsonify({"success": False, "message": "Failed to fetch reviews due to database error."}), 500
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred while fetching reviews."}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/reviews-page')
def reviews_page():
    try:
        file_path = 'c:/Users/Yogi/OneDrive/Desktop/New folder/DBMS PROJECT/librarymanagementsystem/review1.html'
        return send_file(file_path)
    except FileNotFoundError:
        print(f"Error: review1.html not found at {file_path}")
        return "Error: Review page file not found.", 404
    except Exception as e:
        print(f"Error serving review page: {e}")
        return "An internal error occurred while serving the review page.", 500

@app.route('/submit-review', methods=['POST'])
def submit_review():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received or not in JSON format."}), 400

    book_title = data.get('book_title')
    author = data.get('author')
    username = data.get('username')
    usn = data.get('usn')
    review_text = data.get('review_text')
    rating = data.get('rating')

    if not all([book_title, author, username, usn, review_text, rating]):
        return jsonify({"success": False, "message": "All fields are required!"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
             print("Error: Failed to get database connection for submitting review.")
             return jsonify({"success": False, "message": "Database connection error."}), 500
        cursor = conn.cursor()

        sql = """
            INSERT INTO book_reviews (book_title, author, username, usn, review_text, rating, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        current_time = datetime.datetime.now()
        values = (book_title, author, username, usn, review_text, rating, current_time)
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({"success": True, "message": "Review submitted successfully!"})

    except mysql.connector.Error as db_err:
        print(f"Database Error submitting review: {db_err}")
        if conn: conn.rollback()
        return jsonify({"success": False, "message": f"Failed to submit review due to a database issue."}), 500
    except Exception as e:
        print(f"Unexpected Error submitting review: {e}")
        if conn: conn.rollback()
        return jsonify({"success": False, "message": f"An unexpected error occurred."}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

@app.route('/add-event', methods=['POST'])
def add_event():
    try:
        title = request.form.get('title')
        date = request.form.get('date')
        time_ = request.form.get('time')
        location = request.form.get('location')
        category = request.form.get('category')
        description = request.form.get('description')
        image_file = request.files.get('image')

        # Debug: Print all received form data
        print("Received event data:", {
            "title": title, "date": date, "time": time_, "location": location,
            "category": category, "description": description, "image_file": image_file.filename if image_file else None
        })

        if not all([title, date, time_, location, category, description]):
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        image_path_to_store = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(EVENT_IMAGE_UPLOAD_FOLDER, filename)
            image_file.save(save_path)
            image_path_to_store = os.path.join('uploads', 'event_images', filename)
        elif image_file and not allowed_file(image_file.filename):
            return jsonify({"success": False, "message": "Invalid file type for image."}), 400

        # Debug: Print what will be inserted into DB
        print("Inserting event into DB:", (title, date, time_, location, category, description, image_path_to_store))

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO events (title, event_date, event_time, location, category, description, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (title, date, time_, location, category, description, image_path_to_store))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Event added successfully!"})
    except Exception as e:
        import traceback
        print("Error in /add-event:", traceback.format_exc())  # This will print the full error in your Flask console
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/add-event', methods=['GET'])
def add_event_get():
    return jsonify({"success": False, "message": "This endpoint is for POST requests only."}), 200

@app.route('/events', methods=['GET'])
def get_events():
    try:
        print("GET /events called")  # Debug
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events ORDER BY event_date DESC, event_time DESC")
        events_raw = cursor.fetchall()
        print("Events fetched from DB (count):", len(events_raw))  # Debug

        # Normalize keys for frontend and convert event_time to string
        events = []
        for ev in events_raw:
            event_time = ev.get("event_time") or ev.get("time") or ""
            # Convert timedelta to string (e.g., 'HH:MM:SS')
            if isinstance(event_time, datetime.timedelta):
                total_seconds = int(event_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                event_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                event_time_str = str(event_time) if event_time else ""
            events.append({
                "id": ev.get("id") or ev.get("event_id"),  # Ensure id is present for frontend
                "title": ev.get("title") or ev.get("event_title") or "",
                "event_date": str(ev.get("event_date") or ev.get("date") or ""),
                "event_time": event_time_str,
                "location": ev.get("location") or "",
                "category": ev.get("category") or "",
                "description": ev.get("description") or "",
            })
        print("Events sent to frontend:", events)  # Debug
        cursor.close()
        conn.close()
        response = make_response(jsonify(events))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        print("Error fetching events:", e)
        return jsonify([])

@app.route('/event/<int:event_id>', methods=['GET'])
def get_event_by_id(event_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        ev = cursor.fetchone()
        cursor.close()
        conn.close()
        if not ev:
            return jsonify({'success': False, 'message': 'Event not found'}), 404
        # Convert event_time to string if needed
        event_time = ev.get("event_time") or ev.get("time") or ""
        if isinstance(event_time, datetime.timedelta):
            total_seconds = int(event_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            event_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            event_time_str = str(event_time) if event_time else ""
        return jsonify({
            "id": ev.get("id") or ev.get("event_id"),
            "title": ev.get("title") or ev.get("event_title") or "",
            "event_date": str(ev.get("event_date") or ev.get("date") or ""),
            "event_time": event_time_str,
            "location": ev.get("location") or "",
            "category": ev.get("category") or "",
            "description": ev.get("description") or "",
        })
    except Exception as e:
        print("Error fetching event by id:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/update-event/<int:event_id>', methods=['POST', 'PUT'])
def update_event(event_id):
    try:
        title = request.form.get('title')
        date = request.form.get('date')
        time_ = request.form.get('time')
        location = request.form.get('location')
        category = request.form.get('category')
        description = request.form.get('description')
        image_file = request.files.get('image')

        image_path_to_store = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(EVENT_IMAGE_UPLOAD_FOLDER, filename)
            image_file.save(save_path)
            image_path_to_store = os.path.join('uploads', 'event_images', filename)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build SQL and params
        sql = """
            UPDATE events
            SET title=%s, event_date=%s, event_time=%s, location=%s, category=%s, description=%s
        """
        params = [title, date, time_, location, category, description]
        if image_path_to_store:
            sql += ", image_path=%s"
            params.append(image_path_to_store)
        sql += " WHERE id=%s"
        params.append(event_id)

        cursor.execute(sql, tuple(params))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Event updated successfully!"})
    except Exception as e:
        import traceback
        print("Error in /update-event:", traceback.format_exc())
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/adminevents')
def adminevents():
    return render_template('adminevents.html')

@app.route('/return-book', methods=['POST'])
def return_book():
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        user_id = data.get('user_id')
        # Here you would update your database to mark the book as returned/requested for return.
        # For now, just return success.
        # Optionally, you can log or print the request for debugging.
        print(f"Return request received for book_id={book_id}, user_id={user_id}")
        return jsonify({'success': True, 'message': 'Return request processed.'})
    except Exception as e:
        print("Error in /return-book:", e)
        return jsonify({'success': False, 'message': 'Server error processing return request.'}), 500

@app.route('/borrowed-books')
def borrowed_books():
    username = request.args.get('username')
    if not username:
        return jsonify([])  # Return empty if not logged in
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM borrowed_books WHERE username = %s", (username,))
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "message": "Method Not Allowed (405). Please use the correct HTTP method."}), 405

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

