from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps # Comes with python so no need to install via requirements.txt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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
    user_name = db.Column(db.String, nullable=False, unique=True)  # Username column
    hash = db.Column(db.String, nullable=False)  # Hash column for passwords

class Exercise(db.Model):
    __tablename__ = 'exercises'  # Define the table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    exercise_name = db.Column(db.String, nullable=False, unique=True)  # Exercise_name column
    description = db.Column(db.String) 

class Log(db.Model):
    __tablename__ = 'logs'  # Define the table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User ID column
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)  # Exercise ID column
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)  # New session relationship
    load = db.Column(db.Integer, nullable=False)  # Load column
    sets = db.Column(db.Integer, nullable=False)  # Sets column
    reps = db.Column(db.String, nullable=False)  # Store reps as CSV string
    rir = db.Column(db.Integer, nullable=False)  # RIR column
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Use current timestamp


    # Relationships (not mandatory but useful for easier access)
    user = db.relationship('User', backref=db.backref('logs', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('logs', lazy=True))

class Program(db.Model):
    __tablename__ = 'programs'  # Define the table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    name = db.Column(db.String, nullable=False)

    # Relationships
    meso_cycles = db.relationship('MesoCycle', backref='program', lazy=True)

class MesoCycle(db.Model):
    __tablename__ = 'meso_cycles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    #end_date = db.Column(db.Date, nullable=True)  # Leave null until the end is confirmed

    # Foreign key to Program
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)

    # Relationships
    training_weeks = db.relationship('TrainingWeek', backref='meso_cycle', lazy=True)

class TrainingWeek(db.Model):
    __tablename__ = 'training_weeks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    week_number = db.Column(db.Integer, nullable=False)  # Week number in the meso cycle (1, 2, 3, etc.)
    start_date = db.Column(db.Date, nullable=False)
    #end_date = db.Column(db.Date, nullable=False)
    deload_week = db.Column(db.Boolean, default=False)  # Whether this week is a deload week

    # Foreign key to MesoCycle
    meso_cycle_id = db.Column(db.Integer, db.ForeignKey('meso_cycles.id'), nullable=False)

    # Relationships
    training_days = db.relationship('TrainingDay', backref='training_week', lazy=True)

class TrainingDay(db.Model):
    __tablename__ = 'training_days'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day_number = db.Column(db.Integer, nullable=False)  # Day number in the week (1, 2, 3, etc.)
    date = db.Column(db.Date, nullable=False)

    # Foreign key to TrainingWeek
    training_week_id = db.Column(db.Integer, db.ForeignKey('training_weeks.id'), nullable=False)

    # Relationships
    sessions = db.relationship('Session', backref='training_day', lazy=True)

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)  # Name of the session (e.g., Upper Body, Lower Body)
    
    # Foreign key to TrainingDay
    training_day_id = db.Column(db.Integer, db.ForeignKey('training_days.id'), nullable=False)

    # Relationship to Logs
    logs = db.relationship('Log', backref='session', lazy=True)



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
        match = User.query.filter_by(user_name=username).first()

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
            new_user = User(user_name=request.form.get("username"), hash=hashed_pass)
            db.session.add(new_user)
            db.session.commit()

        except ValueError as e:
            return "BAD APE! " + str(e)

        # Query database for username
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        user = User.query.filter(User.user_name == request.form.get("username")).first()

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
        user = User.query.filter_by(user_name=request.form.get("username")).first()

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


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    return render_template("create.html")


@app.route("/display", methods=["GET", "POST"])
@login_required
def display():
    return render_template("display.html")


@app.route("/design", methods=["GET", "POST"])
@login_required
def design():
    return render_template("design.html")

@app.route('/submit-log', methods=['POST'])
def submit_log():
    # Get data from the form
    user_id = request.form.get('user_id')  # Ensure user_id is present
    exercise_names = request.form.getlist('exercise_name[]')  # List of exercise names
    loads = request.form.getlist('load[]')  # List of loads
    sets = request.form.getlist('sets[]')  # List of sets
    rirs = request.form.getlist('rir[]')  # List of RIRs

    # Loop through each exercise entry
    for i in range(len(exercise_names)):
        ex_name = exercise_names[i].strip()
        load_value = int(loads[i]) if loads[i] else 0
        sets_value = int(sets[i]) if sets[i] else 0
        rir_value = int(rirs[i]) if rirs[i] else 0

        # Check if the exercise already exists in the Exercise table
        exercise = Exercise.query.filter_by(exercise_name=ex_name).first()

        # If the exercise doesn't exist, create a new one
        if not exercise:
            new_exercise = Exercise(exercise_name=ex_name)
            db.session.add(new_exercise)
            db.session.commit()  # Commit to get the ID for the new exercise
            exercise_id = new_exercise.id  # Use the ID of the newly created exercise
        else:
            exercise_id = exercise.id  # Use the existing exercise ID

        # Capture reps for each set and join them into a CSV string
        reps = request.form.getlist(f'reps[{i}][]')  # Get reps for this exercise (row i)
        reps_csv = ','.join(reps)  # Store reps as CSV string

        # Create a new log entry
        log = Log(
            user_id=user_id,
            exercise_id=exercise_id,  # Use the retrieved or newly created exercise ID
            load=load_value,
            sets=sets_value,
            reps=reps_csv,  # Store CSV string of reps
            rir=rir_value,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)

    # Commit all log entries to the database
    db.session.commit()

    # Flash success message and redirect
    #flash('Log successfully saved!', 'success')
    return redirect(url_for('index'))

@app.route('/create_program', methods=['POST'])
def create_program():
    program_name = request.form.get('program_name')
    start_date_str = request.form.get('start_date')
    weeks = int(request.form.get('weeks'))
    training_days = request.form.getlist('training_days[]')  # Get selected training days from checkboxes

    # Convert start_date string to a Python date object
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    # Create the program
    program = Program(name=program_name)
    db.session.add(program)
    db.session.commit()

    # Create the meso cycle
    meso_cycle = MesoCycle(
        start_date=start_date,
        program_id=program.id
    )
    db.session.add(meso_cycle)
    db.session.commit()

    # Create the training weeks and training days (based on selected days)
    for week_num in range(1, weeks + 1):
        # You can calculate the week start date and end date here if needed
        training_week = TrainingWeek(
            week_number=week_num,
            start_date=start_date,  # Adjust start_date for each week
            #end_date=None,  # Adjust end_date if necessary
            meso_cycle_id=meso_cycle.id
        )
        db.session.add(training_week)
        db.session.commit()

        # Create training days based on selected checkboxes
        for day in training_days:
            training_day = TrainingDay(
                day_number=day,  # Save the day name (e.g., "Monday", "Tuesday", etc.)
                date=start_date,  # Adjust this for each day within the week
                training_week_id=training_week.id
            )
            db.session.add(training_day)
        db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    print("Creating database and tables if they don't exist...")
    create_db()  # Initialize the database
    app.run(debug=True)  # Start the Flask application