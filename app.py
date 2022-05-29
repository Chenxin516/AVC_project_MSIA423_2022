import logging.config
import sqlite3
import traceback
import sqlalchemy.exc
import yaml
from flask import Flask, render_template, request, redirect, url_for
from config.flaskconfig import MaritalStatus, Gender, OverTime

# For setting up the Flask-SQLAlchemy database session
from src.employee_db import Employee, EmployeeManager
from src.predict import transform_input, prediction

# Initialize the Flask application

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Web app log')

# Initialize the database session
employee_manager = EmployeeManager(app)

# load yaml configuration file
try:
    with open('config/config.yaml', "r") as file:
        conf = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Configuration file loaded")
except FileNotFoundError:
    logger.error("Configuration file is not found")


@app.route('/')
def index():
    """Main view of the loan application that allows user input applicant information
    Create view into index page that allows users input applicant information
    Returns:
        rendered html template located at: app/templates/index.html
    """

    try:
        logger.debug("Index page accessed")
        return render_template('index.html', MaritalStatus=MaritalStatus,
                               Gender=Gender, OverTime=OverTime)
    except:
        traceback.print_exc()
        logger.warning("Not able to display Employee information, error page returned")
        return render_template('error.html')


@app.route('/result', methods=['POST', 'GET'])
def add_entry():
    """View that process a POST with new applicant input
    Add new applicant information to Applications database and get prediction results
    Returns:
        rendered html template located at: app/templates/result.html if successfully processed,
        rendered html template located at: app/templates/error.html if any error occurs
    """
    if request.method == 'GET':
        return "Visit the homepage to add applicants and get predictions"
    elif request.method == 'POST':
        try:
            # Add new applicant information to RDS for future usages
            employee_manager.add_employee(
                EmployeeNumber=int(request.form['EmployeeNumber']),
                EnvironmentSatisfaction=int(request.form['EnvironmentSatisfaction']),
                JobInvolvement=int(request.form['JobInvolvement']),
                JobLevel=int(request.form['JobLevel']),
                JobSatisfaction=int(request.form['JobSatisfaction']),
                PerformanceRating=request.form['PerformanceRating'],
                RelationshipSatisfaction=request.form['RelationshipSatisfaction'],
                YearsSinceLastPromotion=request.form['YearsSinceLastPromotion'],
                WorkLifeBalance=request.form['WorkLifeBalance'],
                MaritalStatus=request.form['MaritalStatus'],
                Gender=request.form['Gender'],
                OverTime=request.form['OverTime']
            )

            logger.info(
                "New applicant of Employee ID %s added",
                request.form['EmployeeNumber']
            )

            # Get loan delinquency prediction for the new applicant
            user_input = {'EmployeeNumber': request.form['EmployeeNumber'],
                          'EnvironmentSatisfaction': request.form['EnvironmentSatisfaction'],
                          'JobInvolvement': request.form['JobInvolvement'],
                          'JobLevel': request.form['JobLevel'],
                          'JobSatisfaction': request.form['JobSatisfaction'],
                          'PerformanceRating': request.form['PerformanceRating'],
                          'RelationshipSatisfaction': request.form['RelationshipSatisfaction'],
                          'YearsSinceLastPromotion': request.form['YearsSinceLastPromotion'],
                          'WorkLifeBalance': request.form['WorkLifeBalance'],
                          'MaritalStatus': request.form['MaritalStatus'],
                          'Gender': request.form['Gender'],
                          'OverTime': request.form['OverTime']}

            user_input_new = transform_input(user_input)
            label = prediction(user_input_new)[0]
            prob = prediction(user_input_new)[1]

            logger.info(
                "The employee's probability of attrition is: %f percent, "
                "hence %s", prob, label
            )

            logger.debug("Result page accessed")
            return render_template('result.html', user_prob=prob, user_bin=label)
        except:
            logger.warning("Not able to process your request, error page returned")
            return render_template('error.html')


@app.route('/about', methods=['GET'])
def about():
    """View of an 'About' page that has detailed information about the project
    Returns:
        rendered html template located at: app/templates/about.html
    """
    logger.debug("About page accessed")
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
