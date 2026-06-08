import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )
            connection.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("Email already exists or database error.", "error")
        finally:
            cursor.close()
            connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]

        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, due_date) VALUES (%s, %s, %s, %s)",
            (session["user_id"], title, description, due_date)
        )
        connection.commit()
        flash("Task added successfully.", "success")

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("dashboard.html", tasks=tasks)


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = %s AND user_id = %s",
        (task_id, session["user_id"])
    )
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("dashboard"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]
        status = request.form["status"]

        cursor.execute(
            """
            UPDATE tasks 
            SET title = %s, description = %s, due_date = %s, status = %s
            WHERE id = %s AND user_id = %s
            """,
            (title, description, due_date, status, task_id, session["user_id"])
        )
        connection.commit()

        cursor.close()
        connection.close()

        flash("Task updated successfully.", "success")
        return redirect(url_for("dashboard"))

    cursor.execute(
        "SELECT * FROM tasks WHERE id = %s AND user_id = %s",
        (task_id, session["user_id"])
    )
    task = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template("edit_task.html", task=task)


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = %s AND user_id = %s",
        (task_id, session["user_id"])
    )
    connection.commit()

    cursor.close()
    connection.close()

    flash("Task deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)