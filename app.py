from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "smart-library-secret-key"

DATABASE = "library.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():

    conn = get_db()

    # ==========================================
    # USERS TABLE
    # ==========================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            college TEXT,
            branch TEXT,
            student_id TEXT,
            year TEXT,
            section TEXT,
            role TEXT DEFAULT 'student'
        )
    """)

    # ==========================================
    # ADD NEW USER COLUMNS IF DATABASE IS OLD
    # ==========================================

    existing_columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(users)").fetchall()
    ]

    columns_to_add = {
        "phone": "TEXT",
        "college": "TEXT",
        "branch": "TEXT",
        "student_id": "TEXT",
        "year": "TEXT",
        "section": "TEXT"
    }

    for column, data_type in columns_to_add.items():

        if column not in existing_columns:

            conn.execute(
                f"ALTER TABLE users ADD COLUMN {column} {data_type}"
            )

    # ==========================================
    # BOOKS TABLE
    # ==========================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1
        )
    """)

    # ==========================================
    # TRANSACTIONS TABLE
    # ==========================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrowed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            returned_at TEXT,
            status TEXT DEFAULT 'borrowed'
        )
    """)

    # ==========================================
    # WAITLIST TABLE
    # ==========================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'waiting'
        )
    """)

    # ==========================================
    # ADMIN ACCOUNT
    # ==========================================

    admin = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        ("admin@library.com",)
    ).fetchone()

    if admin is None:

        conn.execute("""
            INSERT INTO users
            (
                name,
                email,
                password,
                role
            )
            VALUES (?, ?, ?, ?)
        """, (
            "Library Admin",
            "admin@library.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    # ==========================================
    # SAMPLE BOOKS
    # ==========================================

    book_count = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    if book_count == 0:

        books = [

            (
                "Python Crash Course",
                "Eric Matthes",
                "Programming",
                3,
                3
            ),

            (
                "Clean Code",
                "Robert C. Martin",
                "Programming",
                2,
                2
            ),

            (
                "The Alchemist",
                "Paulo Coelho",
                "Fiction",
                2,
                2
            ),

            (
                "Atomic Habits",
                "James Clear",
                "Self Development",
                3,
                3
            ),

            (
                "Artificial Intelligence: A Modern Approach",
                "Stuart Russell & Peter Norvig",
                "Artificial Intelligence",
                2,
                2
            ),

            (
                "Web Development with HTML CSS JavaScript",
                "Jon Duckett",
                "Web Development",
                2,
                2
            ),

            (
                "Harry Potter and the Philosopher's Stone",
                "J.K. Rowling",
                "Fantasy",
                2,
                2
            ),

            (
                "Data Structures and Algorithms",
                "Narasimha Karumanchi",
                "Computer Science",
                2,
                2
            )
        ]

        conn.executemany("""
            INSERT INTO books
            (
                title,
                author,
                category,
                quantity,
                available
            )
            VALUES (?, ?, ?, ?, ?)
        """, books)

    conn.commit()
    conn.close()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("home.html")


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "")
        student_id = request.form.get("student_id", "").strip()
        year = request.form.get("year", "")
        section = request.form.get("section", "").strip()
        password = request.form["password"]

        # ==========================================
        # VALIDATION
        # ==========================================

        if not name:

            return render_template(
                "register.html",
                error="Full Name is required."
            )

        if not email:

            return render_template(
                "register.html",
                error="Email Address is required."
            )

        if not phone:

            return render_template(
                "register.html",
                error="Phone Number is required."
            )

        if not phone.isdigit() or len(phone) != 10:

            return render_template(
                "register.html",
                error="Phone Number must contain exactly 10 digits."
            )

        if len(password) < 6:

            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        # ==========================================
        # CHECK EMAIL
        # ==========================================

        conn = get_db()

        existing = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:

            conn.close()

            return render_template(
                "register.html",
                error="This email is already registered."
            )

        # ==========================================
        # CREATE ACCOUNT
        # ==========================================

        hashed_password = generate_password_hash(password)

        conn.execute("""
            INSERT INTO users
            (
                name,
                email,
                password,
                phone,
                college,
                branch,
                student_id,
                year,
                section,
                role
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            hashed_password,
            phone,
            college,
            branch,
            student_id,
            year,
            section,
            "student"
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":

                return redirect(url_for("admin"))

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# ==========================================
# STUDENT DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    my_books = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE user_id = ?
        AND status = 'borrowed'
    """, (
        session["user_id"],
    )).fetchone()[0]

    waitlist_count = conn.execute("""
        SELECT COUNT(*)
        FROM waitlist
        WHERE user_id = ?
        AND status = 'waiting'
    """, (
        session["user_id"],
    )).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        total_books=total_books,
        my_books=my_books,
        waitlist_count=waitlist_count
    )


# ==========================================
# BOOKS
# ==========================================

@app.route("/books")
def books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("q", "").strip()

    conn = get_db()

    if search:

        books = conn.execute("""
            SELECT *
            FROM books
            WHERE title LIKE ?
               OR author LIKE ?
               OR category LIKE ?
            ORDER BY title
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        )).fetchall()

    else:

        books = conn.execute("""
            SELECT *
            FROM books
            ORDER BY title
        """).fetchall()

    conn.close()

    return render_template(
        "books.html",
        books=books,
        search=search,
        name=session["name"]
    )


# ==========================================
# BORROW BOOK
# ==========================================

@app.route("/borrow/<int:book_id>", methods=["POST"])
def borrow(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if book is None:

        conn.close()

        return redirect(url_for("books"))

    # ==========================================
    # CHECK ALREADY BORROWED
    # ==========================================

    already = conn.execute("""
        SELECT *
        FROM transactions
        WHERE user_id = ?
        AND book_id = ?
        AND status = 'borrowed'
    """, (
        session["user_id"],
        book_id
    )).fetchone()

    if already:

        conn.close()

        return redirect(url_for("books"))

    # ==========================================
    # BOOK NOT AVAILABLE
    # ==========================================

    if book["available"] <= 0:

        conn.close()

        return redirect(url_for("books"))

    # ==========================================
    # DECREASE AVAILABLE COPIES
    # ==========================================

    conn.execute("""
        UPDATE books
        SET available = available - 1
        WHERE id = ?
    """, (
        book_id,
    ))

    # ==========================================
    # CREATE TRANSACTION
    # ==========================================

    conn.execute("""
        INSERT INTO transactions
        (
            user_id,
            book_id,
            status
        )
        VALUES (?, ?, 'borrowed')
    """, (
        session["user_id"],
        book_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("my_books"))


# ==========================================
# MY BOOKS
# ==========================================

@app.route("/my-books")
def my_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    borrowed_books = conn.execute("""
        SELECT
            transactions.id AS transaction_id,
            books.title,
            books.author,
            books.category,
            transactions.borrowed_at
        FROM transactions
        JOIN books
            ON transactions.book_id = books.id
        WHERE transactions.user_id = ?
        AND transactions.status = 'borrowed'
        ORDER BY transactions.borrowed_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "my_books.html",
        books=borrowed_books,
        name=session["name"]
    )


# ==========================================
# RETURN BOOK
# ==========================================

@app.route("/return/<int:transaction_id>", methods=["POST"])
def return_book(transaction_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    transaction = conn.execute("""
        SELECT *
        FROM transactions
        WHERE id = ?
        AND user_id = ?
        AND status = 'borrowed'
    """, (
        transaction_id,
        session["user_id"]
    )).fetchone()

    if transaction:

        book_id = transaction["book_id"]

        # ==========================================
        # MARK TRANSACTION RETURNED
        # ==========================================

        conn.execute("""
            UPDATE transactions
            SET
                status = 'returned',
                returned_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            transaction_id,
        ))

        # ==========================================
        # FIND NEXT WAITLIST STUDENT
        # ==========================================

        next_student = conn.execute("""
            SELECT *
            FROM waitlist
            WHERE book_id = ?
            AND status = 'waiting'
            ORDER BY id ASC
            LIMIT 1
        """, (
            book_id,
        )).fetchone()

        # ==========================================
        # GIVE BOOK TO WAITLIST
        # ==========================================

        if next_student:

            conn.execute("""
                UPDATE waitlist
                SET status = 'ready'
                WHERE id = ?
            """, (
                next_student["id"],
            ))

        # ==========================================
        # OTHERWISE BOOK BECOMES AVAILABLE
        # ==========================================

        else:

            conn.execute("""
                UPDATE books
                SET available = available + 1
                WHERE id = ?
            """, (
                book_id,
            ))

        conn.commit()

    conn.close()

    return redirect(url_for("my_books"))


# ==========================================
# JOIN WAITLIST
# ==========================================

@app.route("/join-waitlist/<int:book_id>", methods=["POST"])
def join_waitlist(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if book is None:

        conn.close()

        return redirect(url_for("books"))

    # ==========================================
    # BOOK AVAILABLE
    # ==========================================

    if book["available"] > 0:

        conn.close()

        return redirect(url_for("books"))

    # ==========================================
    # CHECK EXISTING WAITLIST REQUEST
    # ==========================================

    existing = conn.execute("""
        SELECT *
        FROM waitlist
        WHERE user_id = ?
        AND book_id = ?
        AND status = 'waiting'
    """, (
        session["user_id"],
        book_id
    )).fetchone()

    if existing:

        conn.close()

        return redirect(url_for("waitlist"))

    # ==========================================
    # ADD TO WAITLIST
    # ==========================================

    conn.execute("""
        INSERT INTO waitlist
        (
            user_id,
            book_id,
            status
        )
        VALUES (?, ?, 'waiting')
    """, (
        session["user_id"],
        book_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("waitlist"))


# ==========================================
# WAITLIST
# ==========================================

@app.route("/waitlist")
def waitlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    waiting = conn.execute("""
        SELECT
            waitlist.id,
            books.title,
            books.author,
            waitlist.created_at,
            waitlist.status,

            (
                SELECT COUNT(*)
                FROM waitlist AS w2
                WHERE w2.book_id = waitlist.book_id
                AND w2.status = 'waiting'
                AND w2.id <= waitlist.id
            ) AS position

        FROM waitlist

        JOIN books
            ON waitlist.book_id = books.id

        WHERE waitlist.user_id = ?

        ORDER BY waitlist.id
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "waitlist.html",
        waiting=waiting,
        name=session["name"]
    )


# ==========================================
# CLAIM WAITLIST BOOK
# ==========================================

@app.route("/claim-waitlist/<int:waitlist_id>", methods=["POST"])
def claim_waitlist(waitlist_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    waitlist_item = conn.execute("""
        SELECT *
        FROM waitlist
        WHERE id = ?
        AND user_id = ?
        AND status = 'ready'
    """, (
        waitlist_id,
        session["user_id"]
    )).fetchone()

    if waitlist_item is None:

        conn.close()

        return redirect(url_for("waitlist"))

    book_id = waitlist_item["book_id"]

    book = conn.execute("""
        SELECT *
        FROM books
        WHERE id = ?
    """, (
        book_id,
    )).fetchone()

    if book is None:

        conn.close()

        return redirect(url_for("waitlist"))

    # ==========================================
    # CREATE BORROW TRANSACTION
    # ==========================================

    conn.execute("""
        INSERT INTO transactions
        (
            user_id,
            book_id,
            status
        )
        VALUES (?, ?, 'borrowed')
    """, (
        session["user_id"],
        book_id
    ))

    # ==========================================
    # MARK WAITLIST FULFILLED
    # ==========================================

    conn.execute("""
        UPDATE waitlist
        SET status = 'fulfilled'
        WHERE id = ?
    """, (
        waitlist_id,
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("my_books"))


# ==========================================
# CANCEL WAITLIST
# ==========================================

@app.route("/cancel-waitlist/<int:waitlist_id>", methods=["POST"])
def cancel_waitlist(waitlist_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    waitlist_item = conn.execute("""
        SELECT *
        FROM waitlist
        WHERE id = ?
        AND user_id = ?
        AND status = 'waiting'
    """, (
        waitlist_id,
        session["user_id"]
    )).fetchone()

    if waitlist_item is None:

        conn.close()

        return redirect(url_for("waitlist"))

    conn.execute("""
        UPDATE waitlist
        SET status = 'cancelled'
        WHERE id = ?
    """, (
        waitlist_id,
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("waitlist"))


# ==========================================
# SMART RECOMMENDATIONS
# ==========================================

@app.route("/recommendations")
def recommendations():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    interests = conn.execute("""
        SELECT DISTINCT books.category
        FROM transactions
        JOIN books
            ON transactions.book_id = books.id
        WHERE transactions.user_id = ?
        ORDER BY transactions.id DESC
    """, (
        session["user_id"],
    )).fetchall()

    # ==========================================
    # STUDENT HAS BORROWING HISTORY
    # ==========================================

    if interests:

        categories = [
            row["category"]
            for row in interests
        ]

        placeholders = ",".join(
            ["?"] * len(categories)
        )

        recommendations = conn.execute(
            f"""
            SELECT *
            FROM books
            WHERE category IN ({placeholders})

            AND id NOT IN (
                SELECT book_id
                FROM transactions
                WHERE user_id = ?
                AND status = 'borrowed'
            )

            ORDER BY
                CASE
                    WHEN category = ? THEN 0
                    ELSE 1
                END,
                title

            LIMIT 8
            """,
            (
                *categories,
                session["user_id"],
                categories[0]
            )
        ).fetchall()

    # ==========================================
    # NEW STUDENT
    # ==========================================

    else:

        recommendations = conn.execute("""
            SELECT *
            FROM books
            ORDER BY title
            LIMIT 8
        """).fetchall()

    conn.close()

    return render_template(
        "recommendations.html",
        books=recommendations,
        name=session["name"]
    )


# ==========================================
# PROFILE
# ==========================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    total_users = conn.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'student'
    """).fetchone()[0]

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    issued_books = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status = 'borrowed'
    """).fetchone()[0]

    waitlist_count = conn.execute("""
        SELECT COUNT(*)
        FROM waitlist
        WHERE status = 'waiting'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_books=total_books,
        issued_books=issued_books,
        waitlist_count=waitlist_count
    )


# ==========================================
# ADMIN - MANAGE BOOKS
# ==========================================

@app.route("/admin/books")
def admin_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    books = conn.execute("""
        SELECT *
        FROM books
        ORDER BY title
    """).fetchall()

    conn.close()

    return render_template(
        "admin_books.html",
        books=books
    )


# ==========================================
# ADMIN - ADD BOOK
# ==========================================

@app.route("/admin/add-book", methods=["GET", "POST"])
def add_book():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        title = request.form["title"].strip()
        author = request.form["author"].strip()
        category = request.form["category"].strip()

        try:
            quantity = int(request.form["quantity"])
        except ValueError:
            return render_template(
                "add_book.html",
                error="Quantity must be a number."
            )

        if quantity < 1:

            return render_template(
                "add_book.html",
                error="Quantity must be at least 1."
            )

        conn = get_db()

        conn.execute("""
            INSERT INTO books
            (
                title,
                author,
                category,
                quantity,
                available
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            title,
            author,
            category,
            quantity,
            quantity
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin_books"))

    return render_template("add_book.html")


# ==========================================
# ADMIN - EDIT BOOK
# ==========================================

@app.route("/admin/edit-book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if book is None:

        conn.close()

        return redirect(url_for("admin_books"))

    if request.method == "POST":

        title = request.form["title"].strip()
        author = request.form["author"].strip()
        category = request.form["category"].strip()

        try:
            quantity = int(request.form["quantity"])
        except ValueError:

            conn.close()

            return render_template(
                "edit_book.html",
                book=book,
                error="Quantity must be a number."
            )

        borrowed = book["quantity"] - book["available"]

        if quantity < borrowed:

            conn.close()

            return render_template(
                "edit_book.html",
                book=book,
                error=(
                    f"Quantity cannot be less than {borrowed}, "
                    f"because {borrowed} copy/copies are currently issued."
                )
            )

        if quantity < 1:

            conn.close()

            return render_template(
                "edit_book.html",
                book=book,
                error="Quantity must be at least 1."
            )

        available = quantity - borrowed

        conn.execute("""
            UPDATE books
            SET
                title = ?,
                author = ?,
                category = ?,
                quantity = ?,
                available = ?
            WHERE id = ?
        """, (
            title,
            author,
            category,
            quantity,
            available,
            book_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin_books"))

    conn.close()

    return render_template(
        "edit_book.html",
        book=book
    )


# ==========================================
# ADMIN - DELETE BOOK
# ==========================================

@app.route("/admin/delete-book/<int:book_id>", methods=["POST"])
def delete_book(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if book is None:

        conn.close()

        return redirect(url_for("admin_books"))

    # Do not delete an issued book

    if book["available"] < book["quantity"]:

        conn.close()

        return redirect(url_for("admin_books"))

    # Remove related waitlist records

    conn.execute("""
        DELETE FROM waitlist
        WHERE book_id = ?
    """, (
        book_id,
    ))

    # Delete the book

    conn.execute("""
        DELETE FROM books
        WHERE id = ?
    """, (
        book_id,
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_books"))


# ==========================================
# ADMIN - MEMBERS
# ==========================================

@app.route("/admin/members")
def admin_members():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    members = conn.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            college,
            branch,
            student_id,
            year,
            section
        FROM users
        WHERE role = 'student'
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "admin_members.html",
        members=members
    )


# ==========================================
# ADMIN - DELETE MEMBER
# ==========================================

@app.route("/admin/delete-member/<int:user_id>", methods=["POST"])
def delete_member(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    # Admin cannot delete their own account

    if user_id == session["user_id"]:
        return redirect(url_for("admin_members"))

    conn = get_db()

    member = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
        AND role = 'student'
    """, (
        user_id,
    )).fetchone()

    if member is None:

        conn.close()

        return redirect(url_for("admin_members"))

    # ==========================================
    # CHECK ACTIVE BORROWED BOOKS
    # ==========================================

    active_transaction = conn.execute("""
        SELECT *
        FROM transactions
        WHERE user_id = ?
        AND status = 'borrowed'
    """, (
        user_id,
    )).fetchone()

    if active_transaction:

        conn.close()

        return redirect(url_for("admin_members"))

    # ==========================================
    # DELETE WAITLIST RECORDS
    # ==========================================

    conn.execute("""
        DELETE FROM waitlist
        WHERE user_id = ?
    """, (
        user_id,
    ))

    # ==========================================
    # DELETE TRANSACTION HISTORY
    # ==========================================

    conn.execute("""
        DELETE FROM transactions
        WHERE user_id = ?
    """, (
        user_id,
    ))

    # ==========================================
    # DELETE MEMBER
    # ==========================================

    conn.execute("""
        DELETE FROM users
        WHERE id = ?
        AND role = 'student'
    """, (
        user_id,
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_members"))


# ==========================================
# ADMIN - TRANSACTIONS
# ==========================================

@app.route("/admin/transactions")
def admin_transactions():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()

    transactions = conn.execute("""
        SELECT
            transactions.id,
            users.name,
            users.student_id,
            books.title,
            transactions.borrowed_at,
            transactions.returned_at,
            transactions.status

        FROM transactions

        JOIN users
            ON transactions.user_id = users.id

        JOIN books
            ON transactions.book_id = books.id

        ORDER BY transactions.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_transactions.html",
        transactions=transactions
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    response = redirect(url_for("login"))

    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )