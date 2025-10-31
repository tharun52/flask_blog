from flask import Flask, jsonify, render_template, request, redirect, url_for
import pymysql
import os
def load_env_file(path):
    try:
        with open(path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    except FileNotFoundError:
        pass

load_env_file("/home/ubuntu/flask_blog/.env")

app = Flask(__name__)

# ---------- Database connection helper ----------
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_ENDPOINT'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------- Create table if not exists ----------
def init_db():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blogs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        conn.close()
        print("✅ Table 'blogs' ready.")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

# ---------- Routes ----------
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, content, created_at FROM blogs ORDER BY created_at DESC")
            posts = cursor.fetchall()
        conn.close()
        return render_template('index.html', posts=posts)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/new')
def new_blog():
    return render_template('new.html')

@app.route('/add', methods=['POST'])
def add_blog():
    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        return "Please enter both title and content", 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO blogs (title, content) VALUES (%s, %s)", (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------- Run the app ----------
if __name__ == '__main__':
    init_db()  # create table if not exists
    app.run(host='0.0.0.0', port=80)
