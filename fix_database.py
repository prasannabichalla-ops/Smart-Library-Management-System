import sqlite3

DATABASE = "library.db"

conn = sqlite3.connect(DATABASE)

columns = [
    ("phone", "TEXT"),
    ("college", "TEXT"),
    ("branch", "TEXT"),
    ("student_id", "TEXT"),
    ("year", "TEXT"),
    ("section", "TEXT")
]

existing_columns = [
    row[1]
    for row in conn.execute("PRAGMA table_info(users)").fetchall()
]

for column_name, column_type in columns:

    if column_name not in existing_columns:

        conn.execute(
            f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
        )

        print(f"Added column: {column_name}")

    else:

        print(f"Already exists: {column_name}")

conn.commit()
conn.close()

print()
print("Database update completed successfully!")