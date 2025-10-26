from flask import Flask, render_template, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Optional
import zoneinfo
import platform
import psutil
import random
import logging
import os

# ------------------------------
#  Logging Configuration
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------
#  App Configuration
# ------------------------------
def create_app(config_name: Optional[str] = None) -> Flask:
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Load configuration based on environment
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False  # Preserve JSON response order
    
    return app

app = create_app()
db = SQLAlchemy(app)

# ------------------------------
#  Models
# ------------------------------
class Post(db.Model):
    """Blog post model representing entries in the blog system."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    def to_dict(self) -> Dict:
        """Convert post to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Post':
        """Create a new Post instance from dictionary data."""
        if not all(key in data for key in ['title', 'content', 'author']):
            raise ValueError("Missing required fields")
        
        return Post(
            title=data['title'],
            content=data['content'],
            author=data['author']
        )

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
#  Create tables (app context)
# ------------------------------
with app.app_context():
    db.create_all()

# ------------------------------
#  Routes
# ------------------------------
@app.route("/")
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template(
        "index.html",
        current_time=get_montreal_time(),
        message=get_random_message(),
        system_info=get_system_info(),
        posts=posts
    )

# Blog API endpoints
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

# /api/blog This is the api endpoint.

@app.route("/api/blog", methods=["POST"])
def create_blog_post():
    data = request.get_json(force=True)
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

# Other utility APIs
@app.route("/api/time")
def api_time():
    """Get current Montreal time."""
    try:
        return jsonify({"montreal_time": get_montreal_time()})
    except Exception as e:
        logger.error(f"Error getting Montreal time: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/system")
def api_system():
    """Get system information and statistics."""
    try:
        return jsonify(get_system_info())
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    db.session.rollback()  # Roll back session in case of database errors
    return jsonify({"error": "Internal server error"}), 500

# ------------------------------
#  Run server (development only)
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
