# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables to ensure Python outputs are sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED=1

# Install system dependencies for SQLite
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

# Install any needed packages specified in requirements.txt
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 4000 available to the world outside this container
EXPOSE 4000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]
