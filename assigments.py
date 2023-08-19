# app.py
import sqlite3
from datetime import datetime, timedelta
from flask import *
import re
import math

app = Flask(__name__)
app.secret_key ='dahdjii/@h'
# Configure the SQLite database
DATABASE = 'assignments.db'



def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS borrowings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        user_type TEXT NOT NULL,
        borrowed_on DATE DEFAULT CURRENT_DATE,
        
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES teachers(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE
    )
''')

    # Create a new table for max_books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS max_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            max_quantity INTEGER NOT NULL
        )
    ''')
    # cursor.execute('SELECT COUNT(*) FROM max_books')
    # count = cursor.fetchone()[0]

    # if count == 0:
    #     cursor.execute('INSERT INTO max_books (user_type, max_quantity) VALUES (?, ?)', ('teacher', 10))
    #     cursor.execute('INSERT INTO max_books (user_type, max_quantity) VALUES (?, ?)', ('student', 5))
    #     conn.commit()
    #     print('Default maximum quantities inserted.')
    # Insert initial data into the max_books table
    

    # Create the 'students' table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY,
                        student_name TEXT NOT NULL
                    )''')
    cursor.execute('''DROP TABLE IF EXISTS assignments''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS assignments (
                            id INTEGER PRIMARY KEY,
                            assignment_name TEXT NOT NULL,
                            teacher_name TEXT NOT NULL
                        )''')                
    # Create the 'assignments' table
    

    # Create the 'questions' table
    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY,
                        assignment_id INTEGER NOT NULL,
                        question_text TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        marks INTEGER NOT NULL,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (id)
                    )''')

    # Create the 'answers' table
    cursor.execute('''CREATE TABLE IF NOT EXISTS answers (
                        id INTEGER PRIMARY KEY,
                        assignment_id INTEGER NOT NULL,
                        question_id INTEGER NOT NULL,
                        student_id INTEGER NOT NULL,
                        answer_text TEXT NOT NULL,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (id),
                        FOREIGN KEY (question_id) REFERENCES questions (id),
                        FOREIGN KEY (student_id) REFERENCES students (id)
                    )''')
    
    # Create the 'assignment_scores' table to store the marks for each student for each assignment
    cursor.execute('''CREATE TABLE IF NOT EXISTS assignment_scores (
                        id INTEGER PRIMARY KEY,
                        assignment_id INTEGER NOT NULL,
                        student_id INTEGER NOT NULL,
                        question_id INTEGER NOT NULL,
                        marks INTEGER NOT NULL,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (id),
                        FOREIGN KEY (student_id) REFERENCES students (id),
                        FOREIGN KEY (question_id) REFERENCES questions (id)
                    )''')
    # cursor.execute("""
    #                DROP TABLE IF EXISTS stu_comments""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            status TEXT DEFAULT 'unread',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)
    # cursor.execute("""
    #                DROP TABLE IF EXISTS teacher_deletions""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_deletions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            comment_id INTEGER NOT NULL,
            deleted INTEGER DEFAULT 0,
            FOREIGN KEY (teacher_id) REFERENCES students (id),
            FOREIGN KEY (comment_id) REFERENCES comments (id)
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stu_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        is_positive INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers (id),
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        description TEXT,
        quantity INTEGER DEFAULT 1,
        out_of_stock INTEGER DEFAULT 0,
        due_days INTEGER DEFAULT 7  -- Set default due days to 7 days
    )
''')
    # Return a book


# def insert_dummy_data():
#     # Dummy data for the 'students' table
#     dummy_students = [
#         {
#             'student_name': 'John Doe'
#         },
#         {
#             'student_name': 'Jane Smith'
#         }
#         # Add more students as needed
#     ]

#     # Dummy data for the 'assignments' table
#     dummy_assignments = [
#         {
#             'teacher_name': 'Professor X',
#             'assignment_text': 'Geography Quiz'
#         },
#         {
#             'teacher_name': 'Dr. Y',
#             'assignment_text': 'Art History Test'
#         }
#         # Add more assignments as needed
#     ]

#     # Dummy data for the 'questions' table
#     dummy_questions = [
#         {
#             'assignment_id': 1,
#             'question_text': 'What is the capital of France?',
#             'correct_answer': 'Paris',
#             'marks': 10
#         },
#         {
#             'assignment_id': 1,
#             'question_text': 'Who painted the Mona Lisa?',
#             'correct_answer': 'Leonardo da Vinci',
#             'marks': 15
#         },
#         {
#             'assignment_id': 2,
#             'question_text': 'What is the capital of Spain?',
#             'correct_answer': 'Madrid',
#             'marks': 10
#         },
#         {
#             'assignment_id': 2,
#             'question_text': 'Which planet is known as the Red Planet?',
#             'correct_answer': 'Mars',
#             'marks': 20
#         }
#         # Add more questions as needed
#     ]

#     # Dummy data for the 'answers' table
#     dummy_answers = [
#         {
#             'assignment_id': 1,
#             'question_id': 1,
#             'student_id': 1,
#             'answer_text': 'Paris'
#         },
#         {
#             'assignment_id': 1,
#             'question_id': 2,
#             'student_id': 1,
#             'answer_text': 'Leonardo da Vinci'
#         },
#         {
#             'assignment_id': 1,
#             'question_id': 1,
#             'student_id': 2,
#             'answer_text': 'London'
#         },
#         {
#             'assignment_id': 1,
#             'question_id': 2,
#             'student_id': 2,
#             'answer_text': 'Michelangelo'
#         }
#         # Add more answers as needed
#     ]

#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()

#     # Insert data into the 'students' table
#     for student in dummy_students:
#         cursor.execute('''INSERT INTO students (student_name) VALUES (?)''', (student['student_name'],))

#     # Insert data into the 'assignments' table
#     for assignment in dummy_assignments:
#         cursor.execute('''INSERT INTO assignments (teacher_name, assignment_text) VALUES (?, ?)''',
#                        (assignment['teacher_name'], assignment['assignment_text']))

#     # Insert data into the 'questions' table
#     for question in dummy_questions:
#         cursor.execute('''INSERT INTO questions (assignment_id, question_text, correct_answer, marks)
#                           VALUES (?, ?, ?, ?)''',
#                        (question['assignment_id'], question['question_text'],
#                         question['correct_answer'], question['marks']))

#     # Insert data into the 'answers' table
#     for answer in dummy_answers:
#         cursor.execute('''INSERT INTO answers (assignment_id, question_id, student_id, answer_text)
#                           VALUES (?, ?, ?, ?)''',
#                        (answer['assignment_id'], answer['question_id'],
#                         answer['student_id'], answer['answer_text']))

#     conn.commit()
#     conn.close()
@app.route('/clear_teacher_history', methods=['POST'])
def clear_teacher_history():
    teacher_id = 1  # Replace with the actual teacher's ID

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM comments WHERE student_id = ? AND deleted = 0", (teacher_id,))
        comment_ids = [row[0] for row in cur.fetchall()]

        if not comment_ids:
            return jsonify({'error': 'No comments to clear for this teacher.'}), 400

        cur.executemany("INSERT INTO teacher_deletions (teacher_id, comment_id, deleted) VALUES (?, ?, 1)",
                        [(teacher_id, comment_id) for comment_id in comment_ids])
        con.commit()

    return redirect('/teacher_comments_history')



@app.route('/teacher_comments_history')
def teacher_comments_history():
    teacher_id = 1  # Assuming teacher's ID is 1, modify accordingly if needed

    with sqlite3.connect(DATABASE) as con:
        
        cur = con.cursor()
        

        
        cur.execute("""
            SELECT c.id, c.comment, c.timestamp
            FROM comments c
            LEFT JOIN teacher_deletions td ON c.id = td.comment_id
            WHERE c.student_id = ? AND td.deleted IS NULL AND c.deleted = 0
            ORDER BY c.timestamp DESC
        """, (teacher_id,))
                
           
        
        comments = [{'id': row[0], 'comment': row[1], 'timestamp': row[2]} for row in cur.fetchall()]
        print("comment",comments)
        
    return render_template('teacher_comments_history.html', comments=comments)

@app.route('/student_comments_history')
def student_comments_history():
    student_id = 2  # Assuming student's ID is 2, modify accordingly if needed

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id, comment, timestamp
            FROM comments
            WHERE student_id = ? AND deleted = 0
            ORDER BY timestamp DESC
        """, (student_id,))
        comments = [{'id': row[0], 'comment': row[1], 'timestamp': row[2]} for row in cur.fetchall()]
        
    return render_template('student_comments_history.html', comments=comments)

# Add a new route to handle student deletions
@app.route('/delete_comment_student', methods=['POST'])
def delete_comment_student():
    comment_id = request.form['comment_id']
    student_id = 2  # Assuming student's ID is 2, modify accordingly if needed

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        # Check if the comment belongs to the student before deleting
        cur.execute("""
            SELECT id FROM comments WHERE id = ? AND student_id = ?
        """, (comment_id, student_id))
        result = cur.fetchone()

        if not result:
            return jsonify({'error': 'Comment not found or not owned by the student.'}), 403

        cur.execute("UPDATE comments SET deleted = 1 WHERE id = ?", (comment_id,))
        con.commit()

    return redirect('/student_comments_history')
@app.route('/clear_student_history', methods=['POST'])
def clear_student_history():
    student_id = 2  # Assuming student's ID is 2, modify accordingly if needed

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM comments WHERE student_id = ? AND deleted = 0", (student_id,))
        comment_ids = [row[0] for row in cur.fetchall()]

        if not comment_ids:
            return jsonify({'error': 'No comments to clear for this student.'}), 400

        cur.executemany("UPDATE comments SET deleted = 1 WHERE id = ?", [(comment_id,) for comment_id in comment_ids])
        con.commit()

    return redirect('/student_comments_history')




# Add a new route to handle teacher deletions
@app.route('/delete_comment_teacher', methods=['POST'])
def delete_comment_teacher():
    comment_id = request.form['comment_id']

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO teacher_deletions (teacher_id, comment_id, deleted) VALUES (?, ?, 1)", (1, comment_id))
        con.commit()

    return redirect('/teacher_comments_history')
@app.route('/get_comments')
def get_comments():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM students
        """)
        students = cur.fetchall()

        comments = {}
        for student in students:
            student_id = student[0]
            cur.execute("""
                SELECT * FROM comments
                WHERE student_id = ?
            """, (student_id,))
            comments[student_id] = [{'id': row[0], 'comment': row[2], 'status': row[3]} for row in cur.fetchall()]

    return jsonify(comments)

@app.route('/get_comments_for_student', methods=['POST'])
def get_comments_for_student():
    student_id = request.form['student_id']

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM comments
            WHERE student_id = ? AND status = 'unread'
        """, (student_id,))
        comments = [{'id': row[0], 'comment': row[2]} for row in cur.fetchall()]

    return jsonify(comments)

@app.route('/mark_comment_as_read', methods=['POST'])
def mark_comment_as_read():
    comment_id = request.form['comment_id']

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("UPDATE comments SET status = 'read' WHERE id = ?", (comment_id,))
        con.commit()

    return jsonify({'success': True})



@app.route('/get_unread_comments_count')
def get_unread_comments_count():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT student_id, COUNT(*) FROM comments
            WHERE status = 'unread'
            GROUP BY student_id
        """)
        unread_counts = dict(cur.fetchall())
    return jsonify(unread_counts)


def insert_sample_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Insert sample students if they don't exist
        students_data = [('John',), ('Emma',)]
        for student_data in students_data:
            cursor.execute("SELECT id FROM students WHERE student_name = ?", (student_data[0],))
            existing_student_id = cursor.fetchone()
            if not existing_student_id:
                cursor.execute("INSERT INTO students (student_name) VALUES (?)", student_data)

        # Insert sample assignments if they don't exist
        assignments_data = [('Assignment 1', 'Mr. Smith'), ('Assignment 2', 'Mrs. Johnson')]
        for assignment_data in assignments_data:
            cursor.execute("SELECT id FROM assignments WHERE assignment_name = ?", (assignment_data[0],))
            existing_assignment_id = cursor.fetchone()
            if not existing_assignment_id:
                cursor.execute("INSERT INTO assignments (assignment_name, teacher_name) VALUES (?, ?)", assignment_data)

        # Insert sample questions if they don't exist
        questions_data = [
            (1, "What is 2 + 2?", "4", 10),
            (1, "What is the capital of France?", "Paris", 5),
            (2, "What is 3 + 5?", "8", 10),
            (2, "What is the capital of Germany?", "Berlin", 5)
        ]
        for question_data in questions_data:
            cursor.execute("SELECT id FROM questions WHERE assignment_id = ? AND question_text = ?",
                           (question_data[0], question_data[1]))
            existing_question_id = cursor.fetchone()
            if not existing_question_id:
                cursor.execute("INSERT INTO questions (assignment_id, question_text, correct_answer, marks) VALUES (?, ?, ?, ?)",
                               question_data)

        # Insert sample answers if they don't exist
        answers_data = [
            (1, 1, 1, "4"),
            (1, 2, 1, "Berlin"),
            (2, 3, 2, "8"),
            (2, 4, 2, "Munich")
        ]
        for answer_data in answers_data:
            cursor.execute("SELECT id FROM answers WHERE assignment_id = ? AND question_id = ? AND student_id = ?",
                           (answer_data[0], answer_data[1], answer_data[2]))
            existing_answer_id = cursor.fetchone()
            if not existing_answer_id:
                cursor.execute("INSERT INTO answers (assignment_id, question_id, student_id, answer_text) VALUES (?, ?, ?, ?)",
                               answer_data)

        conn.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        student_name = request.form['student_name']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if teacher exists in the database, if not, add them
        cursor.execute('SELECT id FROM teachers WHERE teacher_name = ?', (teacher_name,))
        teacher_row = cursor.fetchone()
        if teacher_row is None:
            cursor.execute('INSERT INTO teachers (teacher_name) VALUES (?)', (teacher_name,))
            teacher_id = cursor.lastrowid
        else:
            teacher_id = teacher_row[0]

        # Check if student exists in the database, if not, add them
        cursor.execute('SELECT id FROM students WHERE student_name = ?', (student_name,))
        student_row = cursor.fetchone()
        if student_row is None:
            cursor.execute('INSERT INTO students (student_name) VALUES (?)', (student_name,))
            student_id = cursor.lastrowid
        else:
            student_id = student_row[0]

        conn.commit()
        conn.close()

    return render_template('index.html')

@app.route('/create_assignment', methods=['GET', 'POST'])
def create_assignment():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Fetch all assignments from the 'assignments' table
        cursor.execute('''SELECT id, assignment_name, teacher_name FROM assignments''')
        assignments = cursor.fetchall()

        if request.method == 'POST':
            assignment_name = request.form['assignment_name']
            teacher_name = request.form['teacher_name']
            questions = request.form.getlist('question')
            correct_answers = request.form.getlist('correct_answer')
            marks = request.form.getlist('marks')

            # Insert the assignment into the 'assignments' table
            cursor.execute('''INSERT INTO assignments (assignment_name, teacher_name)
                              VALUES (?, ?)''', (assignment_name, teacher_name))
            conn.commit()

            # Get the assignment_id of the newly inserted assignment
            assignment_id = cursor.lastrowid

            # Insert the questions into the 'questions' table
            for question, correct_answer, mark in zip(questions, correct_answers, marks):
                cursor.execute('''INSERT INTO questions (assignment_id, question_text, correct_answer, marks)
                                  VALUES (?, ?, ?, ?)''', (assignment_id, question, correct_answer, mark))
                conn.commit()

            return redirect(url_for('create_assignment'))  # Redirect to the page for creating assignments

    return render_template('create_assignment.html', assignments=assignments)


# ...
# ...
@app.route('/answers/<int:assignment_id>', methods=['GET', 'POST'])
def answers(assignment_id):
    if request.method == 'POST':
        student_id = request.form['student_id']
        answers = request.form.getlist('answer')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if student exists in the database, if not, add them
        cursor.execute('SELECT id FROM students WHERE id = ?', (student_id,))
        student_row = cursor.fetchone()
        if student_row is None:
            # If the student does not exist, handle the error or redirect to an error page
            return "Student not found in the database."

        # Add answers
        cursor.execute('SELECT id FROM questions WHERE assignment_id = ?', (assignment_id,))
        question_ids = [q[0] for q in cursor.fetchall()]

        for idx, answer in enumerate(answers):
            cursor.execute('INSERT INTO answers (assignment_id, question_id, student_id, answer_text) VALUES (?, ?, ?, ?)',
                           (assignment_id, question_ids[idx], student_id, answer))

        conn.commit()
        conn.close()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, assignment_name FROM assignments')
    assignments = cursor.fetchall()

    # Fetch questions for the selected assignment
    cursor.execute('SELECT id, question_text FROM questions WHERE assignment_id = ?', (assignment_id,))
    questions = cursor.fetchall()

    conn.close()

    return render_template('answers.html', assignments=assignments, questions=questions, assignment_id=assignment_id)
# ...

# ...
# app.py
from collections import namedtuple

print("View function executed")
@app.route('/assignment/<int:assignment_id>/<int:student_id>', methods=['GET', 'POST'])
def assignment_details(assignment_id, student_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute('''SELECT * FROM questions WHERE assignment_id = ?''', (assignment_id,))
            questions = cursor.fetchall()
           
            # Loop through the questions to handle multiple question_id and awarded_marks pairs
            for question in questions:
                question_id_key = f'question_id_{question[0]}'
                awarded_marks_key = f'awarded_marks_{question[0]}'
                if question_id_key in request.form and awarded_marks_key in request.form:
                    question_id = int(request.form[question_id_key])
                    awarded_marks = int(request.form[awarded_marks_key])

              
                    cursor.execute('''INSERT INTO assignment_scores (assignment_id, student_id, question_id, marks)
                                        VALUES (?, ?, ?, ?)''', (assignment_id, student_id, question_id, awarded_marks))
                    conn.commit()

        cursor.execute('''SELECT * FROM assignments WHERE id = ?''', (assignment_id,))
        assignment = cursor.fetchone()

        if assignment:
            cursor.execute('''SELECT * FROM questions WHERE assignment_id = ?''', (assignment_id,))
            questions = cursor.fetchall()
            print('questions',questions)
            assignment_details = {
                'assignment_id': assignment[0],
                'assignment_name': assignment[1],
                'teacher_name': assignment[2],
                'questions': questions,
                'student_id': student_id
            }
            print("assignment_details",assignment_details)
            cursor.execute('''SELECT * FROM students WHERE id = ?''', (student_id,))
            student = cursor.fetchone()

            if student:
                # Fetch the answers for the student and assignment
                student_answers = {}
                for question in questions:
                    cursor.execute('''SELECT answer_text FROM answers
                                      WHERE assignment_id = ? AND question_id = ? AND student_id = ?''',
                                   (assignment_id, question[0], student_id))
                    answer = cursor.fetchone()
                    if answer:
                        student_answers[question[0]] = answer[0]
                print("student_answers",student_answers)
                return render_template('view_assignment.html', assignment_details=assignment_details,
                                       student=student, student_answers=student_answers,questions=questions)
            else:
                return "Student not found."

        return "Assignment not found."

# ... (previous code)
@app.route('/view_results/<int:assignment_id>/<int:student_id>')
def view_results(assignment_id, student_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Fetch the student's answers for the specific assignment
        cursor.execute('''SELECT q.question_text, q.correct_answer, q.marks,
                          a.answer_text, s.marks AS awarded_marks
                          FROM questions q
                          LEFT JOIN answers a ON q.id = a.question_id AND a.student_id = ?
                          LEFT JOIN assignment_scores s ON q.id = s.question_id AND s.student_id = ?
                          WHERE q.assignment_id = ?''',
                       (student_id, student_id, assignment_id))
        results = cursor.fetchall()

        # Fetch assignment details for displaying on the template
        cursor.execute('''SELECT assignment_name FROM assignments WHERE id = ?''', (assignment_id,))
        assignment_name = cursor.fetchone()
         # Calculate total marks and percentage
        total_marks = sum(result[4] for result in results if result[4] is not None)
        maximum_marks = sum(result[2] for result in results)
        percentage_score = (total_marks / maximum_marks) * 100 if maximum_marks != 0 else 0

        return render_template('view_results.html', assignment_name=assignment_name[0],
                               results=results, total_marks=total_marks, percentage_score=percentage_score)
        
@app.route('/comments')
def comments():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        student_id=1
        cur.execute("SELECT * FROM students WHERE id=?",(student_id,))
        students = cur.fetchall()
        cur.execute("SELECT * FROM comments WHERE student_id=?",(student_id,))
        comments = cur.fetchall()
    return render_template('comments.html', students=students, comments=comments)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    student_ids = request.form.getlist('students[]')
    comment = request.form['comment']

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        for student_id in student_ids:
            cur.execute("INSERT INTO comments (student_id, comment) VALUES (?, ?)", (student_id, comment))
        con.commit()
        
    flash(f"send success: {comment}")
    
    return redirect(url_for('student_comments'))

@app.route('/student_comments')
def student_comments():
    with sqlite3.connect(DATABASE) as con:
        student_id=1
        cur = con.cursor()
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        if not students:
            return "Student not found!", 404
        
        cur.execute("SELECT * FROM comments WHERE student_id = ?", (student_id,))
        comments = cur.fetchall()
    return render_template('student_comments.html', students=students, comments=comments)

def convert_interval_to_days(interval):
    interval = interval.strip().lower()
    if re.match(r'^\d+ days?$', interval):
        return int(interval.split()[0])
    elif re.match(r'^\d+ weeks?$', interval):
        return int(interval.split()[0]) * 7
    elif re.match(r'^\d+ months?$', interval):
        return int(interval.split()[0]) * 30
    elif re.match(r'^\d+ years?$', interval):
        return int(interval.split()[0]) * 365
    else:
        return 30  # Default to one month if the interval is not recognized

# ...
@app.route('/teacher_rates')
def teacher_rates():
    return render_template("comment_rates.html")

@app.route('/send_comments')
def send():
    return render_template('send_comments.html')
@app.route('/send_comment', methods=['POST'])
def send_comment():
    teacher_id = request.form['teacher_id']
    student_id = request.form['student_id']
    comment = request.form['comment']
    is_positive = request.form['is_positive']

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO stu_comments (teacher_id, student_id, comment, is_positive) VALUES (?, ?, ?, ?)",
                    (teacher_id, student_id, comment, is_positive))
        con.commit()

    return jsonify({'success': True})

# Route to calculate the rate of positive comments for each teacher over time
@app.route('/calculate_teacher_rates', methods=['POST', 'GET'])
def calculate_teacher_rates():
    time_interval = request.form.get('time_interval', '1 week')  # Default to 1 week if not provided
    time_interval_days = convert_interval_to_days(time_interval)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=time_interval_days)

    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        # Fetch all teacher IDs from the teachers table
        cur.execute("SELECT id FROM teachers")
        teacher_ids = [row[0] for row in cur.fetchall()]

        # Initialize the teacher_rates dictionary with default values
        teacher_rates = {teacher_id: {'positive_rate': 0, 'negative_rate': 0} for teacher_id in teacher_ids}

        cur.execute("""
            SELECT teacher_id,
                   SUM(CASE WHEN is_positive = 1 THEN 1 ELSE 0 END) as positive_comments,
                   SUM(CASE WHEN is_positive = 0 THEN 1 ELSE 0 END) as negative_comments,
                   COUNT(*) as total_comments
            FROM stu_comments
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY teacher_id
        """, (start_date, end_date))

        for row in cur.fetchall():
            teacher_id, positive_comments, negative_comments, total_comments = row
            rate = positive_comments / total_comments if total_comments > 0 else 0
            negative_rate = negative_comments / total_comments if total_comments > 0 else 0
            teacher_rates[teacher_id]['positive_rate'] = round(rate, 2)
            teacher_rates[teacher_id]['negative_rate'] = round(negative_rate, 2)

    return render_template('comment_rates.html', teacher_rates=teacher_rates)

def rate_to_angle(rate):
    return round(rate * 360 )

def rate_to_x(rate):
    return round(50 + 50 * math.cos(2 * math.pi * rate))


def calculate_teacher_rate(year=None, teacher_id=None):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        # If the year is provided, calculate rates for all teachers for that year
        if year:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)

            cur.execute("""
                SELECT teacher_id, 
                       SUM(CASE WHEN is_positive = 1 THEN 1 ELSE 0 END) as positive_comments,
                       SUM(CASE WHEN is_positive = 0 THEN 1 ELSE 0 END) as negative_comments,
                       COUNT(*) as total_comments
                FROM stu_comments
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY teacher_id
            """, (start_date, end_date))

            teacher_rates = {}
            for row in cur.fetchall():
                teacher_id, positive_comments, negative_comments, total_comments = row
                rate = positive_comments / total_comments if total_comments > 0 else 0
                negative_rate = negative_comments / total_comments if total_comments > 0 else 0
                teacher_rates[teacher_id] = {'positive_rate': round(rate, 2), 'negative_rate': round(negative_rate, 2)}

        # If the teacher ID is provided, calculate rates for that teacher for all years
        elif teacher_id:
            cur.execute("""
                SELECT strftime('%Y', timestamp) as year,
                       SUM(CASE WHEN is_positive = 1 THEN 1 ELSE 0 END) as positive_comments,
                       SUM(CASE WHEN is_positive = 0 THEN 1 ELSE 0 END) as negative_comments,
                       COUNT(*) as total_comments
                FROM stu_comments
                WHERE teacher_id = ?
                GROUP BY year
            """, (teacher_id,))

            teacher_rates = {}
            for row in cur.fetchall():
                year, positive_comments, negative_comments, total_comments = row
                rate = positive_comments / total_comments if total_comments > 0 else 0
                negative_rate = negative_comments / total_comments if total_comments > 0 else 0
                teacher_rates[year] = {'positive_rate': round(rate, 2), 'negative_rate': round(negative_rate, 2)}

    return teacher_rates

@app.route('/calculate_rates', methods=['GET', 'POST'])
def calculate_rates():
    if request.method == 'POST':
        year = request.form.get('year')
        teacher_id = request.form.get('teacher_id')

        if year:
            year = int(year)

        teacher_rates = calculate_teacher_rate(year, teacher_id)

    else:
        teacher_rates = calculate_teacher_rate()

    return render_template('teacher_rates.html', teacher_rates=teacher_rates)

def create_teachers_table():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        # Create the teachers table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

def insert_dummy_teachers():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        # Check if the teachers table is empty
        cur.execute("SELECT COUNT(*) FROM teachers")
        count = cur.fetchone()[0]

        if count == 0:
            # Insert 6 dummy records if the table is empty
            dummy_teachers = [("Teacher 1",), ("Teacher 2",), ("Teacher 3",), ("Teacher 4",), ("Teacher 5",), ("Teacher 6",)]
            cur.executemany("INSERT INTO teachers (name) VALUES (?)", dummy_teachers)
            
@app.route('/undelivered_services', methods=['GET', 'POST'])
def undelivered_services():
    if request.method == 'POST':
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()

            # Get the list of all form keys that start with 'service_status_'
            service_status_keys = [key for key in request.form.keys() if key.startswith('service_status_')]
            
            # Loop through the keys and update the status for each service
            for key in service_status_keys:
                service_id = int(key.split('_')[-1])  # Extract the service_id from the key
                new_status = request.form[key]  # Get the new status from the form
                
                # Update the status of the service
                cur.execute("UPDATE services SET status = ? WHERE id = ?", (new_status, service_id))
                con.commit()

    # Fetch undelivered services
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM services WHERE status = 'undelivered'")
        undelivered_services = cur.fetchall()

    return render_template('services.html', undelivered_services=undelivered_services)





@app.route('/offer_service', methods=['GET', 'POST'])
def offer_service():
    if request.method == 'POST':
        service = request.form['service']
        status = request.form.get('status', 'undelivered')  # Default to "undelivered" if not provided

        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO services (service, status) VALUES (?, ?)", (service, status))
            con.commit()

    return render_template('admin/services/services.html')          
@app.route('/service_delivery_rate', methods=['POST', 'GET'])
def service_delivery_rate():
    time_interval = request.form.get('time_interval', '1 month')  # Default to 1 week if not provided
    time_interval_days = convert_interval_to_days(time_interval)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=time_interval_days)

    # Calculate the service delivery rate within the specified time interval
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        cur.execute("""
            SELECT status, COUNT(*) as total_count
            FROM services
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))

        service_counts = dict(cur.fetchall())
        total_delivered = service_counts.get('delivered', 0)
        total_undelivered = service_counts.get('undelivered', 0)
        total_services = total_delivered + total_undelivered

        delivery_rate = total_delivered / total_services if total_services > 0 else 0

    return render_template('services.html', delivery_rate=delivery_rate, total_delivered=total_delivered, total_undelivered=total_undelivered, undelivered_services=[])





@app.route('/delivery_rates_by_year', methods=['GET'])
def delivery_rates_by_year():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()

        # Fetch all unique years from the database
        cur.execute("SELECT DISTINCT strftime('%Y', timestamp) FROM services")
        years = [row[0] for row in cur.fetchall()]

        # Calculate delivery rates for each year
        delivery_rates = {}
        for year in years:
            start_date = year + "-01-01"
            end_date = year + "-12-31"
            cur.execute("""
                SELECT COUNT(*) as total_services,
                       SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_services
                FROM services
                WHERE timestamp BETWEEN ? AND ?
            """, (start_date, end_date))
            result = cur.fetchone()
            total_services = result[0]
            delivered_services = result[1]
            rate = delivered_services / total_services if total_services > 0 else 0
            delivery_rates[year] = rate

    return render_template('delivery_rate.html', delivery_rates=delivery_rates)



# Add or Update book form

    # if not is_logged_in():
    #     return redirect(url_for('login'))

    if request.method == 'POST':
        book_id = request.form['book_id']
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        quantity = request.form['quantity']
        due_days = request.form['due_days']

        if not book_id:  # If book_id is empty, it's a new book, so add it
            cursor=conn.cursor()
            conn=sqlite3.connect(DATABASE)
            cursor.execute('INSERT INTO books (title, author, description, quantity, due_days) VALUES (?, ?, ?, ?, ?)',
                           (title, author, description, quantity, due_days))
        else:  # If book_id is provided, it's an existing book, so update its details
            cursor.execute('UPDATE books SET title = ?, author = ?, description = ?, quantity = ?, due_days = ? WHERE id = ?',
                           (title, author, description, quantity, due_days, book_id))

        conn.commit()
        return redirect(url_for('home'))

    book_id = request.args.get('book_id')
    book_data = None
    if book_id:
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book_data = cursor.fetchone()

    return render_template('book_form.html', book_data=book_data)



    if not is_logged_in():
        return redirect(url_for('login'))

    # Delete the book from the books table
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()

    # Notify the client about the book deletion
    flash(f'{book_id},book deleted successfully')

    return jsonify({'status': 'success'})
if __name__ == '__main__':
    create_table()
    insert_sample_data()
    create_teachers_table()
    insert_dummy_teachers()
    app.run(debug=True)
     # Insert dummy data after creating tables (for demonstration purposes)
   

