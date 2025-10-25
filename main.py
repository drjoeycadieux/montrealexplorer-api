import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Needed for sessions

    app.config["NAME"] = os.getenv("NAME", "World")
    app.config["PORT"] = int(os.getenv("PORT", 3000))

    # Dummy credentials (replace with DB or environment vars later)
    USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    PASSWORD = os.getenv("ADMIN_PASSWORD", "password123")

    @app.route("/")
    def hello_world():
        name = app.config["NAME"]
        return render_template("index.html", name=name)

    @app.route("/services")
    def services():
        # Only allow access if logged in
        if not session.get("logged_in"):
            flash("Please log in to access services.")
            return redirect(url_for("login"))
        return render_template("services.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page for Montreal Explorer backend."""
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == USERNAME and password == PASSWORD:
                session["logged_in"] = True
                flash("Login successful!", "success")
                return redirect(url_for("services"))
            else:
                flash("Invalid credentials. Please try again.", "danger")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("logged_in", None)
        flash("You’ve been logged out.", "info")
        return redirect(url_for("login"))

    return app


# ✅ Required by Vercel
app = create_app()
