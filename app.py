from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from cs50 import SQL
from functools import wraps # Comes with python so no need to install via requirements.txt
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Defined tables
class User(db.Model):
    __tablename__ = 'users'  # Define the table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    username = db.Column(db.String, nullable=False, unique=True)  # Username column
    hash = db.Column(db.String, nullable=False)  # Hash column for passwords

# Create the database and tables if they don't exist
def create_db():
    with app.app_context():
        print("Creating database and tables...")
        db.create_all()

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    #return "TYTANNNN"


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Check method used
    if request.method == "GET":
        # Hand user a registration form
        return render_template("registration.html")

    else:  # User is POSTing
        # Check inputs are correct & not void, retyped password match, no user name duplication in database
        if not request.form.get("username"):
            return "BAD APE! Please provide a username."

        # Username present, check for database duplicates
        #match = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        username = request.form.get("username")
        match = User.query.filter_by(username=username).first()

        if match != None:  # There is a username duplicate in the database
            return "BAD APE! That username already exists."

        # If there is no duplicate
        # Check if provided passwords match
        pass_1 = request.form.get("password")
        pass_2 = request.form.get("confirmation")
        if not pass_1 or not pass_2:  # If either password or has a falsy value of None or empty
            return "BAD APE! Please provide a password."
        elif pass_1 != pass_2:  # Password mismatch
            return "BAD APE! Passwords do not match."

        # Add to database
        try:
            # Hash password
            hashed_pass = generate_password_hash(pass_1, method='pbkdf2', salt_length=16)
            #db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", request.form.get("username"), hashed_pass)
            new_user = User(username=request.form.get("username"), hash=hashed_pass)
            db.session.add(new_user)
            db.session.commit()

        except ValueError as e:
            return "BAD APE! " + str(e)

        # Query database for username
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        user = User.query.filter(User.username == request.form.get("username")).first()

        # Log user in
        if user: # and not None
            # Log user in
            session["user_id"] = user.id  # Store the user's ID in the session

        # Redirect user to home page
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return "BAD APE! Please provide a username."

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "BAD APE! Please provide a password."

        # Query database for username
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        user = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user.hash, request.form.get("password")):
            return "BAD APE! Invalid username and/or password."

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == '__main__':
    print("Creating database and tables if they don't exist...")
    create_db()  # Initialize the database
    app.run(debug=True)  # Start the Flask application