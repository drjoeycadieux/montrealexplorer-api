# Montreal Explorer Backend

This is a simple Flask-based backend for a blog application. It provides API endpoints to manage blog posts and exposes some utility endpoints to get server information.

## Setup and Running

1.  **Install dependencies:** 
    ```bash
    pip install -r requirements.txt
    ```
2.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```
3.  **Run the application:**
    ```bash
    ./devserver.sh
    ```

## API Endpoints

*   `GET /`: Renders the home page with a list of blog posts.
*   `GET /api/blog`: Returns a JSON list of all blog posts.
*   `POST /api/blog`: Creates a new blog post. Requires a JSON body with `title`, `content`, and `author`.
*   `GET /api/time`: Returns the current time in Montreal.
*   `GET /api/system`: Returns system information like CPU and memory usage.