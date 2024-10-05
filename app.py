from flask import Flask, render_template, request, session, redirect, url_for, jsonify
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
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=True)
    mesocycle_id = db.Column(db.Integer, db.ForeignKey('meso_cycles.id'), nullable=True)  # Mesocycle
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)  # Exercise ID column
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)  # New session relationship
    load = db.Column(db.Integer, nullable=False)  # Load column
    sets = db.Column(db.Integer, nullable=False)  # Sets column
    reps = db.Column(db.String, nullable=False)  # Store reps as CSV string
    rir = db.Column(db.Integer, nullable=False)  # RIR column
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Use current timestamp

    # Relationships (not mandatory but useful for easier access)
    user = db.relationship('User', backref=db.backref('logs', lazy=True))
    program = db.relationship('Program', backref=db.backref('logs', lazy=True))  # Add relationship to Program
    mesocycle = db.relationship('MesoCycle', backref=db.backref('logs', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('logs', lazy=True))
    session = db.relationship('Session', backref=db.backref('logs', lazy=True))

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
    total_weeks = db.Column(db.Integer, nullable=False)  # New column for total weeks
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False) # Foreign key to Program

    # Relationships
    training_weeks = db.relationship('TrainingWeek', backref='meso_cycle', lazy=True)


class TrainingWeek(db.Model):
    __tablename__ = 'training_weeks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    week_number = db.Column(db.Integer, nullable=False)  # Week number in the meso cycle
    #deload_week = db.Column(db.Boolean, default=False)  # Whether this week is a deload week
    meso_cycle_id = db.Column(db.Integer, db.ForeignKey('meso_cycles.id'), nullable=False) # Foreign key to MesoCycle
    week_split = db.Column(db.String, nullable=False)

    # Relationships
    sessions = db.relationship('Session', backref='training_week', lazy=True)


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, nullable=False)  # Name of the session (e.g., Upper Body, Lower Body)
    day_of_week = db.Column(db.Integer, nullable=False)  # Day of the week (1 for Monday, 2 for Tuesday, etc.)
    training_week_id = db.Column(db.Integer, db.ForeignKey('training_weeks.id'), nullable=False) # Foreign key to TrainingWeek

    # Relationship to Logs
    #logs = db.relationship('Log', backref='session', lazy=True)



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


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # Fetch programs from the database
    programs = Program.query.all()  # Fetch all programs (adjust as needed)
    
    if request.method == 'POST':
        # Handle form submission logic here
        ...

    return render_template('create.html', programs=programs, user_id=session['user_id'])


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
    program_id = request.form.get('program_id')  # Get the selected program ID
    exercise_names = request.form.getlist('exercise_name[]')  # List of exercise names
    loads = request.form.getlist('load[]')  # List of loads
    sets = request.form.getlist('sets[]')  # List of sets
    rirs = request.form.getlist('rir[]')  # List of RIRs
    new_week_number = int(request.form.get('week_number'))  # Selected week number
    session_day = int(request.form.get('session_day'))  # Selected day for the session (from dropdown)
    session_name = request.form.get('session_name')  # Session name (optional)

    print(f"Program ID: {program_id}, Week Number: {new_week_number}")  # Debugging

    # Fetch relevant mesocycle pertaining to this log
    mesocycle = MesoCycle.query.filter_by(id=program_id).first()
    if not mesocycle:
        return "Mesocycle not found", 400

    ##############################
    # Find training weeks pertaining to this mesocycle
    training_weeks = TrainingWeek.query.filter_by(meso_cycle_id=mesocycle.id).all()
    if not training_weeks:
        return "Training weeks not found", 400
    
    base_week = next((week for week in training_weeks if week.week_number == 1), None) # Get the base week, should be present after program creation
    training_week = next((week for week in training_weeks if week.week_number == new_week_number), None)
    if not training_week:
        # Handle the case where no matching training week is found
        print("No matching training week found")
        # Create a new training week if new_week_number is not found in the database
        new_training_week = TrainingWeek(week_number=new_week_number, meso_cycle_id=mesocycle.id, week_split=base_week.week_split)
        db.session.add(new_training_week)
        db.session.commit()
        training_week_id = new_training_week.id
    else:
        training_week_id = training_week.id


    # Check if a session for this day and week already exists
    session = Session.query.filter_by(day_of_week=session_day, training_week_id=training_week_id).first()

    # If session doesn't exist, create a new one
    if not session:
        session = Session(
            name=session_name if session_name else f"Session for Day {session_day}",  # Optional session name
            day_of_week=session_day,
            training_week_id=training_week_id
        )
        db.session.add(session)
        db.session.commit()

    # Loop through each exercise entry
    for i in range(len(exercise_names)):
        ex_name = exercise_names[i].strip()
        load_value = int(loads[i]) if loads[i] else 0
        sets_value = int(sets[i]) if sets[i] else 0
        rir_value = int(rirs[i]) if rirs[i] else 0

        # Ensure required fields are not empty
        if not all([ex_name, load_value, sets_value, rir_value]):
            continue

        # Check if the exercise already exists in the Exercise table
        exercise = Exercise.query.filter_by(exercise_name=ex_name).first()

        # If the exercise doesn't exist, create a new one
        if not exercise:
            new_exercise = Exercise(exercise_name=ex_name)
            db.session.add(new_exercise)
            db.session.commit()  # Commit to get the ID for the new exercise
            db.session.flush()  # Flush to get the ID without committing
            exercise_id = new_exercise.id  # Use the ID of the newly created exercise
        else:
            exercise_id = exercise.id  # Use the existing exercise ID

        # Capture reps for each set and join them into a CSV string
        reps = request.form.getlist(f'reps[{i}][]')  # Get reps for this exercise (row i)
        reps_csv = ','.join(reps) if reps else ''

        # Create a new log entry
        log = Log(
            user_id=user_id,
            program_id=program_id,  # Save the selected program ID  # Use the retrieved or newly created exercise ID
            mesocycle_id=mesocycle.id,
            exercise_id=exercise_id,
            session_id=session.id,  # Associate the log with the session
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
    weeks = int(request.form.get('weeks')) # Get the number of weeks from the design form
    training_days = request.form.getlist('training_days[]')  # Get selected training days from checkboxes

    # Concatenate the training days into a string or process them as integers
    training_days_str = ','.join(training_days)  # Example: '1,2,4,5' for Mon, Tue, Thu, Fri

    # Convert start_date string to a Python date object
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    # Create the program
    program = Program(name=program_name)
    db.session.add(program)
    db.session.commit()

    # Create the meso cycle
    meso_cycle = MesoCycle(
        start_date=start_date,
        total_weeks=weeks,  # Pass total weeks to the meso cycle
        program_id=program.id
    )
    db.session.add(meso_cycle)
    db.session.commit()

    # Create the training week
    split = TrainingWeek(
        week_number=1, # Week 1 when you start a program.
        meso_cycle_id=meso_cycle.id,
        week_split=training_days_str
        
    )
    db.session.add(split)
    db.session.commit()

    return redirect('/')

# Utility function to convert day number to day name
def get_day_name(day_number):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[day_number - 1]  # Since day_number is 1-based

@app.route('/log/<int:program_id>', methods=['GET'])
def log_form(program_id):
    # Get the Program by its ID
    program = Program.query.get(program_id)

    # Retrieve associated training weeks (assuming one week, adjust if needed)
    training_weeks = TrainingWeek.query.filter_by(meso_cycle_id=program.id).all()

    # Extract week split from the CSV stored in the relevant TrainingWeek
    training_days = []
    for week in training_weeks:
        training_days.extend([int(day) for day in week.week_split.split(',')])

    # Generate a list of available day names for the dropdown
    available_days = [(day, get_day_name(day)) for day in set(training_days)]  # Use set to avoid duplicates

    # Render the log form, passing the available days
    return render_template('create.html', available_days=available_days)

@app.route('/get_training_days/<int:program_id>', methods=['GET'])
def get_training_days(program_id):
    # Fetch the program based on its ID
    program = Program.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found GET_TRAINING_DAYS'}), 404

    # Fetch the meso cycle and training week associated with the program
    meso_cycle = MesoCycle.query.filter_by(program_id=program_id).first()
    training_week = TrainingWeek.query.filter_by(meso_cycle_id=meso_cycle.id).first()

    # Extract training days from the CSV stored in `training_week.training_days`
    training_days = [int(day) for day in training_week.week_split.split(',')]
    available_days = [(day, get_day_name(day)) for day in training_days]

    return jsonify(available_days)

@app.route('/get_training_weeks/<int:program_id>', methods=['GET'])
def get_training_weeks(program_id):
    # Fetch the program based on its ID
    program = Program.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found GET_TRAINING_WEEKS'}), 404

    # Fetch the meso cycle and training weekS associated with the program
    meso_cycle = MesoCycle.query.filter_by(program_id=program_id).first()
    training_weeks = meso_cycle.total_weeks

    # Check if no training weeks are found
    if not training_weeks:
        print("No training weeks found for this program_id")  # Debugging line
    
    # Return the total week number
    return jsonify({'total_weeks': training_weeks})


if __name__ == '__main__':
    print("Creating database and tables if they don't exist...")
    create_db()  # Initialize the database
    app.run(debug=True)  # Start the Flask application