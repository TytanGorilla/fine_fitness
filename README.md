# Fine Fitness
#### Video Demo:  <https://youtu.be/mxf_gm-Ef2M>
#### Description: A web based application that allows users to log, retrieve & view their training over time from a built in database.


### Features
    - Simple Ui that dynamically responds to certain input.
    - Light weight database using sqlite.
    - Simple user authentication allowing user to login to gain access to application features.
    - Meaningful visual feedback displayed on graphs.
    - Self contained code providing consistent functioning & performance using docker.


### Overview
This final project was made as a learning experience to much more ambitious commercial project.
It consists of a variety of technologies bundled together, and attempt to solve my real world problem of logging training sessions.


### Tech Stack
Below is a non ordered list of the technologies I deployed with mixed success, and their use within the project generally.

    - HTML, CSS & JavaScript for the responsive frontend.
    - Bootstrap for quick & reliable page structure + styling.
    - Python for the backend logic & bedrock of the main application.
    - Werkzueg for basic password hashing for secure password storage.
    - Sqlite for a light weight, simple to integrate database.
    - Jinja empowered templates to render each route, pass relevant data & embed scripts.
    - Dash, Plotly & Pandas for enabling graph visualizations on the queried database.
    - Flask to provide a server on which the application serves various routes & templates.
    - Docker to contain & consistently serve said application.
    - Git, to version control the entire project as its built.


### Root Folder Contents
Below is a list of each part/file of the project, the contents within each file/folder & a brief description of their use.

As the project grew in complexity on each iteration, I was forced to separate certain parts of code that resided in one file, into dedicated files.

#### Static folder
    - style.css -> Styling for the entire application via boot strapped classes, and custom ids + classes.

#### js folder
    - form.js -> contains the various scripts accessed via the jinja script block that brings dynamism to the application.

#### Templates folder

    - layout.html
        - Contains a flexible viewport.
        - Necessary scripts & links for bootstrap & style sheet.
        - Navigation bar for traversing the application & for user logging.
        - Embedded Jinja blocks for child templates to insert content & scripts from elsewhere.

    - index.html
        - Extends from layout.html
        - Contains buttons leading to other routes if the user is logged in.
        - The navigation bar dynamically serves routes.
            - (Home, Register & login) if the user is NOT logged in.
            - (Home, Train, Program Design, Trianing Logs & logout) if the user IS logged in.
        - Routes
            - Home (/)
            - Register (/register)
            - Login (/login)
            - Train (/create)
            - Program Design (/design)
            - Training Logs (/display)

    - create.html
        - Extends from layout.html
        - Provides two buttons: Session & Design Program

            - Session when clicked hides the buttons and dynamically reveals a complex training logging form via "showForm()" method.
            Allowing a user to select a pre-created program from the "Select Program" drop down list.

            Other drop down lists "Select Week" & "Select Day" pertain to aspects of the pre-created program, 
            and assist in creating meaningful data logs.

            The following fields are for logging each exercise:
                - Exercise
                - Load
                - Sets
                - Reps -> A dynamically populating series of fields according to the "Sets" field's input, by invoking "addExerciseRow()" from form.js via the jinja script block.
                - RIR -> Reps In Reserve -> A training concept defining proximity to training failure.

            Buttons:
                - "Add Exercise" -> Adds a new exercise set of fields below, by invoking "updateRepsFields()" from form.js via the jinja script block.
                - "Remove" -> Removes the exercise set of fields, by invoking "confirmRemoveRow()" from form.js via the jinja script block.
                - "Submit" -> POSTs all lists & fields in that form to the database via the (/submit-log) route.

            - Design Program when clicked serves the (/design) route rendering design.html.

    - design.html
        - Extends from layout.html
        - Provides a form with various fields & a series of check boxes.
            - "Program Name" -> Self explanatory.
            - "Start Date" -> Time stamp for when the user intends to start the program.
            - "Number of Weeks" -> The duration of the program.
            - "Training Days" -> Check boxes for the days a user intends to train.
        - "Create Program" -> a submit button POSTing to the (/create_program) route.

    - registration.html
        - Extends from layout.html
        - Provides a very basic registration form consisting of 3 fields and a button:
            - A field for Username -> which gets checked after POSTING to the (/register) route.
            - A field for Password.
            - A field for the re-typed Password -> which also gets checked for it matching.

    - login.html
        - Extends from layout.html
        - Provides a basic login page at the (/login) route.
        - Redirects user to the index (/) route.

    - display.html
        - Extends from layout.html
        - Also accessible from the navigation bar by clicking "Training Logs"
        - Provides an embedded iframe to a (/dashboard) route provided by the initialized dash_app that allows graph displays within the (/display) route.
        - The following drop downs are filters applied to the dash_app callbacks which perform various queries to filter the data fed into the dash_app (/dashboard) route for the visualizations.

#### app.py
    - Contains all necessary dependencies.
    - Initializes the Flask app required for serving all Flask routes with the above templates.
    - Initializes the the Dash app required for serving all Dash callbacks needed to bring the visualization to life.

#### extension.py
    - I had a bit of a chicken and egg problem with initializing the database.
    - The solution was to initialize SQLAlchemy first, and then importing it, then initialize my app via Flask.
    - Then initialize my Flask app with the SQL db.
    - I'm not sure if this was the best practice, but it did offer me a functional solution.

#### models.py
    - Contains the database schema for the entire project, detailing each table & their relationships.

#### requirements.txt
    - Contains a list of dependencies required for the application to run and is required by the Dockerfile for installing said dependencies.

#### Dockerfile
    - Since docker is so wide spread I made an effort to use it for this project.
    - I also took inspiration from the online code space which CS50 hosts, and that too uses Docker.
    - It contains necessary instructions to build the environment that the application runs in and exposes ports for the web server.

#### docker-compose.yml
    - The Flask application is a web application and can run within a container just fine.
    - However when adding in a database to the mix its best practice to contain the database as well.
    - When working with more containers, you need docker-compose to coordinate those containers.
    - Sqlite didn't require a separate container, but in order to have data persistence, I needed a docker volume, and in order to integrate that, I needed docker-compose to tie it all together.

