import os
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    app.config["NAME"] = os.getenv("NAME", "World")
    app.config["PORT"] = int(os.getenv("PORT", 3000))

    @app.route("/")
    def hello_world():
        name = app.config["NAME"]
        return render_template("index.html", name=name)

    @app.route("/services")
    def services():
        return render_template("services.html")

    @app.route("/login")
    def login():
        """Login page for Montreal Explorer backend."""
        return render_template("login.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=app.config["PORT"])
