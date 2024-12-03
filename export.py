import sqlite3
import pandas as pd

conn = sqlite3.connect("course_data.db")

# Check if there is any data in the 'course' table
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM course")
rows_count = cursor.fetchone()[0]
print(f"Number of rows in the course table: {rows_count}")

if rows_count > 0:
    df = pd.read_sql_query('SELECT * FROM course', conn)
    df.to_excel("course_table.xlsx", index=False)
else:
    print("The course table is empty.")

conn.close()
