import os
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "db"),
            user=os.getenv("MYSQL_USER", "task_user"),
            password=os.getenv("MYSQL_PASSWORD", "task_password"),
            database=os.getenv("MYSQL_DATABASE", "student_tasks")
        )
        return connection
    except Error as error:
        print(f"Database connection error: {error}")
        return None