

from assigments import DATABASE# Borrow a book (for both users and admin)
import sqlite3

from flask import *

app = Flask(__name__)
app.secret_key ='dahdjii/@h'
@app.route('/search-users', methods=['POST'])
def search_users():
    user_type = request.form.get('user_type')
    search_term = request.form.get('search_term')

    if user_type == 'student':
        query = '''
        SELECT student_name
        FROM students
        WHERE student_name LIKE ? LIMIT 5
        '''
    elif user_type == 'teacher':
        query = '''
        SELECT name
        FROM teachers
        WHERE name LIKE ? LIMIT 5
        '''

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, ('%' + search_term + '%',))
    results = cursor.fetchall()
    print('results',results)
    
    return jsonify(results)

@app.route('/delete-user', methods=['POST'])
def delete_user():
    user_type = request.form['user_type']
    user_name = request.form['user_name']
    
    if user_type == 'student':
        query = 'DELETE FROM students WHERE student_name = ?'
    elif user_type == 'teacher':
        query = 'DELETE FROM teachers WHERE name = ?'
    else:
        return "Invalid user type"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, (user_name,))
    conn.commit()
    conn.close()
   

    flash(f'Successfully deleted {user_name} from {user_type}s', 'success')
    return redirect(url_for('home'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        
        if user_type == 'student':
            add_student(name)
        elif user_type == 'teacher':
            add_teacher(name)
        flash(f"successfully added {name,user_type}")
        return redirect(url_for('home'))
    
    return render_template('books/books.html')

def add_student(student_name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (student_name) VALUES (?)", (student_name,))
    conn.commit()
    conn.close()

def add_teacher(teacher_name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO teachers (name) VALUES (?)", (teacher_name,))
    conn.commit()
    conn.close()
def get_borrowing_users():
    query = '''
    SELECT
        b.user_type,
        CASE
            WHEN b.user_type = 'student' THEN s.student_name
            WHEN b.user_type = 'teacher' THEN t.name
        END AS user_name,
        b.borrowed_on,
        bb.title AS book_title
    FROM borrowings AS b
    LEFT JOIN students AS s ON b.user_id = s.id AND b.user_type = 'student'
    LEFT JOIN teachers AS t ON b.user_id = t.id AND b.user_type = 'teacher'
    LEFT JOIN books AS bb ON b.book_id = bb.id
    '''
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, ())
    result = cursor.fetchall()
    
    return result

@app.route('/borrowing-users')
def get_borrowing_users():
    query_students = '''
    SELECT
        s.student_name,
        b.book_id,
        bb.title,
        b.borrowed_on
    FROM borrowings AS b
    INNER JOIN students AS s ON b.user_id = s.id AND b.user_type = 'student'
    INNER JOIN books AS bb ON b.book_id = bb.id
    ORDER BY s.student_name DESC
    '''
    
    query_teachers = '''
    SELECT
        t.name,
        b.book_id,
        bb.title,
        b.borrowed_on
    FROM borrowings AS b
    INNER JOIN teachers AS t ON b.user_id = t.id AND b.user_type = 'teacher'
    INNER JOIN books AS bb ON b.book_id = bb.id
    ORDER BY t.name DESC
    '''
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query_students)
    students_result = cursor.fetchall()
    
    cursor.execute(query_teachers)
    teachers_result = cursor.fetchall()
   
    # Group students and books by name
    grouped_students = {}
    for student in students_result:
        student_name = student[0]
        if student_name not in grouped_students:
            grouped_students[student_name] = []
        grouped_students[student_name].append((student[2], student[3]))
    
    conn.close()
    return render_template('books/borrowing_users.html', students=grouped_students, teachers=teachers_result)



@app.route('/get-borrowing-users', methods=['GET'])
def get_borrowing_users_route():
    borrowing_users = get_borrowing_users()
    return render_template('books/borrowing_users.html', borrowing_users=borrowing_users)

@app.route('/books')
def home():
    # if not is_logged_in():
    #     return redirect(url_for('login'))

    
    conn=sqlite3.connect(DATABASE)
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM books LIMIT 6')
    books = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM borrowings', ())
    current_borrowed = cursor.fetchone()[0]
    borrowing_users = get_borrowing_users()

    
    return render_template('books/books.html', books=books ,current_borrowed=current_borrowed,borrowing_users=borrowing_users)

@app.route('/search', methods=['POST'])
def search_book():
    # if not is_logged_in():
    #     return redirect(url_for('login'))
    
    conn=sqlite3.connect(DATABASE)
    cursor=conn.cursor()
    keyword = request.form['keyword']
    if keyword:
        cursor.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? LIMIT 6', (f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute('SELECT * FROM books LIMIT 6')

    books = cursor.fetchall()
    return render_template('/books/books.html', books=books)

@app.route('/filter_books')
def filter_books():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    search_query = request.args.get('search_query', '')

    query = f"SELECT * FROM books WHERE title LIKE ? OR author LIKE ? LIMIT 6"
    cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
    books = cursor.fetchall()

    return render_template('books/books.html', books=books)


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        quantity = request.form['quantity']
        due_days = request.form['due_days']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('INSERT INTO books (title, author, description, quantity, due_days) VALUES (?, ?, ?, ?, ?)',
                       (title, author, description, quantity, due_days))

        conn.commit()
        return redirect(url_for('home'))
    else:
        return render_template('books/add_book.html')
# Display and update maximum quantities for users (admin only)
@app.route('/max_quantities', methods=['GET', 'POST'])
def max_quantities():
    # if not is_logged_in():
    #     return redirect(url_for('login'))

    # if session.get('user_type') != 'admin':
    #     flash('You do not have permission to access this page.', 'warning')
    #     return redirect(url_for('home'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if request.method == 'POST':
        teacher_quantity = int(request.form.get('teacher_quantity'))
        student_quantity = int(request.form.get('student_quantity'))

        cursor.execute('UPDATE max_books SET max_quantity = ? WHERE user_type = ?', (teacher_quantity, 'teacher'))
        cursor.execute('UPDATE max_books SET max_quantity = ? WHERE user_type = ?', (student_quantity, 'student'))
        conn.commit()
        flash('Maximum quantities updated successfully!', 'success')

    cursor.execute('SELECT * FROM max_books')
    max_books_data = cursor.fetchall()

    return render_template('books/max_quantities.html', max_books_data=max_books_data)

@app.route('/update-book', methods=['GET', 'POST'])
def update_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        quantity = request.form['quantity']
        out_of_stock=request.form['out_of_stock']
        due_days = request.form['due_days']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('UPDATE books SET title = ?, author = ?, description = ?, quantity = ?,out_of_stock=? , due_days = ? WHERE id = ?',
                       (title, author, description, quantity,out_of_stock, due_days, book_id))

        conn.commit()
        return redirect(url_for('home'))
    else:
        book_id = request.args.get('book_id')
        book_data = None
        if book_id:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book= cursor.fetchone()

        return render_template('books/update_book.html', book=book)
@app.route('/check-out-of-stock', methods=['GET'])
def check_out_of_stock():
    query = '''
    SELECT title
    FROM books
    WHERE out_of_stock >= quantity
    '''
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    out_of_stock_books = [row[0] for row in result]
    return jsonify(out_of_stock_books)
@app.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(book_id):
    # if not is_logged_in():
    #     return redirect(url_for('login'))
    conn=sqlite3.connect(DATABASE)
    cursor=conn.cursor()
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if request.method == 'POST':
        # If the user type and username are not found in the session,
        # it means the admin is assisting in the borrowing process.
        if not user_id or not user_type:
            user_type = request.form['user_type']
            username = request.form['username']

            # Check if the user exists in the respective table (teachers or students)
            if user_type == 'teacher':
                conn=sqlite3.connect(DATABASE)
                cursor=conn.cursor()
                cursor.execute('SELECT id FROM teachers WHERE name = ?', (username,))
            elif user_type == 'student':
                cursor.execute('SELECT id FROM students WHERE student_name = ?', (username,))
                print('username',username)
            else:
                flash('Invalid user type.', 'error')
                return redirect(url_for('home'))

            user = cursor.fetchone()
            print('user',user)
            if user:
                user_id = user[0]
            else:
                flash(f'User with username "{username}" not found.', 'error')
                return redirect(url_for('home'))

        # Continue with the borrowing process for the user (student or teacher)
        conn=sqlite3.connect(DATABASE)
        cursor=conn.cursor()
        # Check if the book is out of stock
        cursor.execute('SELECT out_of_stock FROM books WHERE id = ?', (book_id,))
        out_of_stock = cursor.fetchone()[0]

        if out_of_stock:
            flash('Book is out of stock!', 'warning')
            return redirect(url_for('home'))

        # Check if the user can borrow the book based on quantity and max_books limit
        cursor.execute('SELECT quantity FROM books WHERE id = ?', (book_id,))
        book_info = cursor.fetchone()
        if not book_info:
            flash('Book not found.', 'error')
            return redirect(url_for('home'))

        quantity = book_info[0]

        cursor.execute('SELECT max_quantity FROM max_books WHERE user_type = ?', (user_type,))
        max_books_info = cursor.fetchone()
        if not max_books_info:
            flash('Maximum quantity not set for user type.', 'error')
            return redirect(url_for('home'))

        max_quantity = max_books_info[0]

        cursor.execute('SELECT COUNT(*) FROM borrowings WHERE user_id = ? AND user_type = ?', (user_id, user_type))
        current_borrowed = cursor.fetchone()[0]

        if quantity <= 0 or current_borrowed >= max_quantity:
            flash('Cannot borrow more books!', 'warning')
            return redirect(url_for('home'))

        # Get the due_days for the book
        cursor.execute('SELECT due_days FROM books WHERE id = ?', (book_id,))
        due_days = cursor.fetchone()[0]

        # Calculate the due date
        from datetime import datetime, timedelta
        borrowed_on = datetime.now().date()
        # due_date = borrowed_on + timedelta(days=due_days)

        # Update book quantity
        cursor.execute('UPDATE books SET quantity = ? WHERE id = ?', (quantity - 1, book_id))

        # Add a new entry to the borrowings table
        cursor.execute('INSERT INTO borrowings (book_id, user_id, user_type, borrowed_on) VALUES (?, ?, ?, ?)',
                       (book_id, user_id, user_type, borrowed_on))

        conn.commit()
        flash('Book borrowed successfully!', 'success')
        return redirect(url_for('home'))

    # If the method is GET, it means the admin is assisting in the borrowing process,
    # so we prompt the admin to enter the user details.
    return render_template('books/borrow_book.html', book_id=book_id)

@app.route('/get-unreturned-books', methods=['POST'])
def get_unreturned_books():
    username = request.form.get('username')
    user_type = request.form.get('user_type')
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Step 1: Obtain student ID using username
    cursor.execute('SELECT id FROM students WHERE student_name = ?', (username,))
    student_id = cursor.fetchone()
    
    # If student not found, try fetching teacher ID
    if not student_id:
        cursor.execute('SELECT id FROM teachers WHERE name = ?', (username,))
        teacher_id = cursor.fetchone()
        
        if not teacher_id:
            return "User not found"
        
        user_id = teacher_id[0]
    else:
        student_id = student_id[0]
        
        # Step 2: Fetch user ID based on student ID and user type
        if user_type == 'student':
            cursor.execute('SELECT id FROM students WHERE id = ?', (student_id,))
        else:
            cursor.execute('SELECT id FROM teachers WHERE id = ?', (teacher_id,))
        
        user_id = cursor.fetchone()
        
        if not user_id:
            return "User not found"
        
        user_id = user_id[0]
    
    # Step 3: Fetch list of unreturned books for the specified user
    # Step 3: Fetch list of unreturned books for the specified user
        query = '''
            SELECT books.title ,books.id ,borrowings.borrowed_on
            FROM borrowings
            INNER JOIN books ON borrowings.book_id = books.id
            WHERE borrowings.user_id = ?
            AND borrowings.user_type = ?
        '''

        cursor.execute(query, (user_id, user_type))
        unreturned_books = cursor.fetchall()
    
        conn.close()
        print(user_type,user_id)
       
    
    return render_template('books/return_book.html', unreturned_books=unreturned_books, user_type=user_type, user_id=user_id)



# Return a book (for both users and admin)
@app.route('/return/<int:book_id>', methods=['GET', 'POST'])
def return_book(book_id):
    # if not is_logged_in():
    #     return redirect(url_for('login'))

    user_id = session.get('user_id')
    user_type = session.get('user_type')
    print(user_id,user_type)
    print('return')
    if request.method == 'POST':
        # If the user ID and user type are not found in the session,
        # it means the admin is assisting in the return process.
        if not user_id or not user_type:
            user_type = request.form['user_type']
            username = request.form['username']
            conn=sqlite3.connect(DATABASE)
            cursor=conn.cursor()

            # Check if the user exists in the respective table (teachers or students)
            if user_type == 'teacher':
                cursor.execute('SELECT id FROM teachers WHERE username = ?', (username,))
            elif user_type == 'student':
                cursor.execute('SELECT id FROM students WHERE student_name = ?', (username,))
            else:
                flash('Invalid user type.', 'error')
                return redirect(url_for('home'))

            user = cursor.fetchone()
            if user:
                user_id = user[0]
            else:
                flash(f'User with username "{username}" not found.', 'error')
                return redirect(url_for('home'))

        # Continue with the book return process for the user (student or teacher)
        cursor.execute('SELECT COUNT(*) FROM borrowings WHERE user_id = ? AND user_type = ? AND book_id = ?',
                       (user_id, user_type, book_id))
        has_borrowed = cursor.fetchone()[0]

        if not has_borrowed:
            flash('You did not borrow this book.', 'warning')
            return redirect(url_for('home'))

        # Update book quantity
        cursor.execute('SELECT quantity FROM books WHERE id = ?', (book_id,))
        book_info = cursor.fetchone()
        if not book_info:
            flash('Book not found.', 'error')
            return redirect(url_for('home'))

        quantity = book_info[0]

        cursor.execute('UPDATE books SET quantity = ? WHERE id = ?', (quantity + 1, book_id))

        # Remove the corresponding entry from the borrowings table
        cursor.execute('DELETE FROM borrowings WHERE book_id = ? AND user_id = ? AND user_type = ?', (book_id, user_id, user_type))

        conn.commit()
        flash('Book returned successfully!', 'success')
        return redirect(url_for('home'))
    print(book_id,'book id')
    conn=sqlite3.connect(DATABASE)
    cursor=conn.cursor()
    cursor.execute("SELECT title from books WHERE id=?",(book_id,))
    title=cursor.fetchone()[0]

    # If the method is GET, it means the admin is assisting in the return process,
    # so we prompt the admin to enter the user details.
    return render_template('books/return_book.html', book_id=book_id,title=title)


if __name__ == '__main__':
   
    app.run(debug=True)