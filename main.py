from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import zoneinfo
import platform
import psutil
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------------------
#  Models
# ------------------------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------------------
#  Utility functions
# ------------------------------
def get_montreal_time():
    montreal_tz = zoneinfo.ZoneInfo("America/Toronto")
    return datetime.now(montreal_tz).strftime("%Y-%m-%d %H:%M:%S")

def get_random_message():
    messages = [
        "Bienvenue to the Montreal Explorer backend 👋",
        "Exploring the city one API at a time 🗺️",
        "Backend running smoothly in Eastern Time ⚙️",
        "Data loves structure — Flask delivers it! 🧠",
        "Keep your endpoints clean and your coffee strong ☕",
    ]
    return random.choice(messages)

def get_system_info():
    return {
        "Python Version": platform.python_version(),
        "Operating System": platform.system(),
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "Memory Usage": f"{psutil.virtual_memory().percent}%",
        "Server Uptime (seconds)": int(datetime.now().timestamp() - psutil.boot_time())
    }

# ------------------------------
#  Create tables (app context required)
# ------------------------------
with app.app_context():
    db.create_all()

# ------------------------------
#  Routes
# ------------------------------
@app.route("/")
def home():
    """Render main backend page with dynamic info."""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template(
        "index.html",
        current_time=get_montreal_time(),
        message=get_random_message(),
        system_info=get_system_info(),
        posts=posts
    )

# Blog API
@app.route("/api/blog", methods=["GET"])
def get_blog_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "content": p.content,
        "author": p.author,
        "created_at": p.created_at.isoformat()
    } for p in posts])

@app.route("/api/blog", methods=["POST"])
def create_blog_post():
    data = request.json
    if not data.get("title") or not data.get("content") or not data.get("author"):
        return jsonify({"error": "Missing fields"}), 400

    new_post = Post(
        title=data["title"],
        content=data["content"],
        author=data["author"]
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({
        "id": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "author": new_post.author,
        "created_at": new_post.created_at.isoformat()
    }), 201

# Other APIs (system info, time) can stay the same
@app.route("/api/time")
def api_time():
    return jsonify({"montreal_time": get_montreal_time()})

@app.route("/api/system")
def api_system():
    return jsonify(get_system_info())

# ------------------------------
#  Run server
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
