# 📚 Smart Library Management System

A web-based library management application developed using Python, Flask, HTML, CSS, and SQLite. It helps students discover and borrow books while allowing administrators to manage library activities efficiently.

## ✨ Features

### 👨‍🎓 Student Features
- Student registration and login
- Search books by title, author, and category
- Borrow available books
- Return borrowed books
- View borrowing history
- Join waiting lists for unavailable books
- Category-based book recommendations
- Student profile management

### 👨‍💼 Admin Features
- Admin dashboard with library statistics
- Add, edit, and delete books
- Manage student records
- View borrowing transactions
- Monitor book availability

### 🚀 Smart Features
- **FIFO Waitlist:** First In, First Out waiting-list management
- **Book Recommendations:** Category-based recommendations using borrowing history
- **Book Availability Tracking:** Automatic availability updates during borrowing and returning

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| HTML | Web page structure |
| CSS | Website styling |
| SQLite | Database management |
| SQL | Database operations |
| Werkzeug | Password hashing and verification |

## 🗄️ Database Design

The application uses SQLite with the following main tables:

- `users` – Student and administrator details
- `books` – Book information and availability
- `transactions` – Borrowing and returning records
- `waitlist` – Waiting-list requests and status

## 🧠 Algorithms and Techniques

- FIFO (First In, First Out) for waitlist processing
- Category-based book recommendation
- Book availability checking
- CRUD operations (Create, Read, Update, Delete)
- Authentication and session management
- Role-based access control

## ⚙️ Installation and Setup

### Prerequisites
- Python 3
- Git
- VS Code (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/prasannabichalla-ops/Smart-Library-Management-System.git
```

### 2. Open the project folder

```bash
cd Smart-Library-Management-System
```

### 3. Install Flask

```bash
pip install flask
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in browser

```text
http://127.0.0.1:5000
```

The database is initialized by the application when it starts.

## 🔮 Future Enhancements

- Email and SMS notifications
- Book due-date reminders
- Fine calculation
- QR-code-based book issuing
- Advanced recommendation algorithms
- Detailed reports and analytics

## 👩‍💻 Project Information

**Project Name:** Smart Library Management System

**Project Type:** Web Application / Academic Project

**Developed using:** Python, Flask, HTML, CSS, SQLite

---

⭐ If you find this project useful, feel free to explore the repository.
