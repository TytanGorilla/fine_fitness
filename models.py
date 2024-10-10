from datetime import datetime
from extensions import db


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
    training_session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=True)  # New session relationship
    training_week_id = db.Column(db.Integer, db.ForeignKey('training_weeks.id'), nullable=True)  # Foreign key to TrainingWeek
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
    training_session = db.relationship('TrainingSession', backref=db.backref('logs', lazy=True))
    training_week = db.relationship('TrainingWeek', backref=db.backref('logs', lazy=True))  # Relationship to TrainingWeek

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
    training_sessions = db.relationship('TrainingSession', backref='training_week', lazy=True)


class TrainingSession(db.Model):
    __tablename__ = 'training_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, nullable=False)  # Name of the session (e.g., Upper Body, Lower Body)
    day_of_week = db.Column(db.Integer, nullable=False)  # Day of the week (1 for Monday, 2 for Tuesday, etc.)
    training_week_id = db.Column(db.Integer, db.ForeignKey('training_weeks.id'), nullable=False) # Foreign key to TrainingWeek
