import logging.config
import traceback
import yaml
from flask import Flask, render_template, request
from config.flaskconfig import MaritalStatus, Gender, OverTime
import pandas as pd

# For setting up the Flask-SQLAlchemy database session
from src.employee_db import EmployeeManager
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
        df = pd.read_csv('data/raw/employee_results.csv')
        number = max(df['EmployeeNumber']) + 1
        try:
            logger.info(
                "New applicant of Employee ID %s added",
                number
            )

            # Get loan delinquency prediction for the new applicant
            user_input = {'EmployeeNumber': number,
                          'EnvironmentSatisfaction': int(request.form['EnvironmentSatisfaction']),
                          'JobInvolvement': int(request.form['JobInvolvement']),
                          'JobLevel': int(request.form['JobLevel']),
                          'JobSatisfaction': int(request.form['JobSatisfaction']),
                          'PerformanceRating': int(request.form['PerformanceRating']),
                          'RelationshipSatisfaction': int(request.form['RelationshipSatisfaction']),
                          'WorkLifeBalance': int(request.form['WorkLifeBalance']),
                          'YearsSinceLastPromotion': int(request.form['YearsSinceLastPromotion']),
                          'MaritalStatus': request.form['MaritalStatus'],
                          'Gender': request.form['Gender'],
                          'OverTime': request.form['OverTime']}

            # get transformed input and prediction
            user_input_new = transform_input(user_input)
            label = prediction(user_input_new)[0]
            prob = prediction(user_input_new)[1]

            logger.info(
                "The employee's probability of attrition is: %f, "
                "hence %s", prob, label
            )

            if label == "the employee is not likely to leave":
                attr = 'No'
            else:
                attr = 'Yes'

            try:
                # Add new applicant information to RDS for future usages
                employee_manager.add_employee(
                    EmployeeNumber=number,
                    EnvironmentSatisfaction=int(request.form['EnvironmentSatisfaction']),
                    JobInvolvement=int(request.form['JobInvolvement']),
                    JobLevel=int(request.form['JobLevel']),
                    JobSatisfaction=int(request.form['JobSatisfaction']),
                    PerformanceRating=int(request.form['PerformanceRating']),
                    RelationshipSatisfaction=int(request.form['RelationshipSatisfaction']),
                    WorkLifeBalance=int(request.form['WorkLifeBalance']),
                    YearsSinceLastPromotion=int(request.form['YearsSinceLastPromotion']),
                    MaritalStatus=request.form['MaritalStatus'],
                    Gender=request.form['Gender'],
                    OverTime=request.form['OverTime'],
                    Attrition=attr
                )
                logger.info('New Employee added to the database')
            except:
                logger.error('Cannot add employee added to the database, check your database connection')

            df_new = df.append(user_input, ignore_index=True)
            logger.debug('Now the company has s% employee', max(df_new['EmployeeNumber']))
            df_new.to_csv('data/raw/employee_results.csv')
            logger.info('New Employee added to the local file')

            logger.debug("Result page accessed")
            return render_template('result.html', prob=prob, label=label)
        except:
            logger.warning("Not able to process your request, error page returned")
            return render_template('error.html')


@app.route('/about', methods=['GET'])
def about():
    """'About' page with information about the project and creater
    Returns:
        rendered html template located at: app/templates/about.html
    """
    logger.debug("About page accessed")
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
