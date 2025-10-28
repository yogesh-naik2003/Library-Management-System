CREATE DATABASE library_db;
USE library_db;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    role ENUM('student', 'admin') NOT NULL,
    user_id VARCHAR(50),
    dob DATE,
    library_card VARCHAR(50),
    usn VARCHAR(50),
    branch VARCHAR(50),
    admin_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users 
    MODIFY library_card VARCHAR(50) NULL,
    MODIFY usn VARCHAR(50) NULL,
    MODIFY branch VARCHAR(50) NULL;

select * from users;
SELECT * FROM users WHERE username = 'yogesh' AND role = 'student'; 

SELECT * FROM users WHERE role = 'student';
SELECT * FROM users WHERE role = 'admin';

USE library_db;

CREATE TABLE IF NOT EXISTS books (
    book_id VARCHAR(20) PRIMARY KEY,
    book_name VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT
);
 
select * from books;
USE library_db;
SHOW TABLES;  

DESCRIBE books; 
GRANT ALL PRIVILEGES ON library_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
SELECT * FROM books;

CREATE TABLE students (
    usn VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    branch VARCHAR(100) NOT NULL
);
USE library_db;
SELECT * FROM students;

DESCRIBE students;

USE library_db;
CREATE TABLE feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') NOT NULL,
    usn VARCHAR(50) DEFAULT NULL,
    branch VARCHAR(100) DEFAULT NULL,
    admin_id VARCHAR(100) DEFAULT NULL,
    feedback_type ENUM('general', 'issue', 'suggestion', 'other') NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE feedback;
SELECT * FROM feedbacks;

USE library_db;

CREATE TABLE book_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_title VARCHAR(255),
    author VARCHAR(255),
    username VARCHAR(100),
    usn VARCHAR(100),
    review_text TEXT,
    rating VARCHAR(10),
    created_at DATETIME
);

select * from book_reviews;
DESCRIBE book_reviews;

USE library_db;
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    image_path VARCHAR(255) NULL
);
select * from events;
DESCRIBE events;

