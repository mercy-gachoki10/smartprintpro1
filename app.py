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

@app.route("/vendors")
def vendors():
    return render_template("vendors.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)

