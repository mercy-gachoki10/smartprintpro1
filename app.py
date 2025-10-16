from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

# Optional: PostgreSQL connection setup
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="your_db",
            user="your_user",
            password="your_password",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

