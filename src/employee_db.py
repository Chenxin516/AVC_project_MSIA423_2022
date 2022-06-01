import typing
import logging

import flask
import pandas as pd
import sqlalchemy
import sqlalchemy.exc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Set up logging config
logging.basicConfig(format='%(asctime)s%(name)-12s%(levelname)-8s%(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.DEBUG)
logger = logging.getLogger(__name__)

Base = declarative_base()


# Create a db session
class Employee(Base):
    """Creates a data model for the database to be set up for employees."""

    __tablename__ = "Employee"

    EmployeeNumber = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    EnvironmentSatisfaction = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    JobInvolvement = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    JobLevel = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    JobSatisfaction = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    PerformanceRating = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    RelationshipSatisfaction = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    YearsSinceLastPromotion = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)
    WorkLifeBalance = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=True)

    MaritalStatus = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)
    Gender = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)
    OverTime = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)
    Attrition = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<Employee %d>' % self.EmployeeNumber


def create_db(engine_string: str = None) -> None:
    """
    Create database from provided engine string
    Args:
        engine_string (str): SQLAlchemy engine string specifying which database to write to
    Returns: None
    """
    if engine_string is None:
        logger.error('No ENGINE_STRING provided')
        raise ValueError("`ENGINE_STRING` must be provided")

    engine = sqlalchemy.create_engine(engine_string)
    # test database connection
    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        logger.error("Could not connect to database!")
        logger.debug("Database URI: %s", )
        raise e

    try:
        Base.metadata.create_all(engine)
        logger.info("Database successfully created")
    except sqlalchemy.exc.OperationalError:
        message = ('Connection error. Have you configured \n'
                   'SQLALCHEMY_DATABASE_URI variable correctly and connect to Northwestern VPN?')
        logger.error("Could not connect to database!")
        logger.error('%s', message)


class EmployeeManager:
    """
    Creates a SQLAlchemy connection to the Employee table.
    Args:
        app (:obj:`flask.app.Flask`): Flask app object for when connecting from
            within a Flask app. Optional.
        engine_string (str): SQLAlchemy engine string specifying which database
            to write to. Follows the format
    """

    def __init__(self, app: typing.Optional[flask.app.Flask] = None,
                 engine_string: typing.Optional[str] = None):
        """
        Args:
            app (Flask): Flask app
            engine_string (str): Engine String
        """
        if app:
            self.database = SQLAlchemy(app)
            self.session = self.database.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            session_maker = sessionmaker(bind=engine)
            self.session = session_maker()
        else:
            raise ValueError("Need either an engine string or a Flask app to initialize")

    def add_result(self, input_path: str):
        """
        Create the result table in RDS
        Args:
            input_path (string): the path of the result data
        Returns:
            None
        """

        session = self.session
        logger.info("Session has been initialized")
        result_list = []
        datas = pd.read_csv(input_path).to_dict(orient='records')
        logger.info("Result data has been read")

        for data in datas:
            result_list.append(Employee(**data))

        try:
            session.add_all(result_list)
            session.commit()
            logger.info('%s result rows were successfully added to the employee table', len(result_list))
        except sqlalchemy.exc.OperationalError:
            logger.error('You might have connection error')
            logger.error("The original error message is: ", exc_info=True)
        else:
            logger.info("There are %s records added to the table", len(result_list))

    def add_employee(self,
                     EmployeeNumber: int,
                     EnvironmentSatisfaction: int,
                     JobInvolvement: int,
                     JobLevel: int,
                     JobSatisfaction: int,
                     PerformanceRating: int,
                     RelationshipSatisfaction: int,
                     YearsSinceLastPromotion: int,
                     WorkLifeBalance: int,
                     MaritalStatus: str,
                     Gender: str,
                     OverTime: str,
                     Attrition: str) -> None:
        """Seeds an existing database with a new employee.
        Args:
            arguments with respect to employee (self-explanatory by names)
        Returns:
            None
        """

        logger.debug("trying to add employee with employee number %s", EmployeeNumber)

        session = self.session
        logger.debug("session initialized")
        employee = Employee(EmployeeNumber=EmployeeNumber, EnvironmentSatisfaction=EnvironmentSatisfaction,
                            JobInvolvement=JobInvolvement, JobLevel=JobLevel, JobSatisfaction=JobSatisfaction,
                            PerformanceRating=PerformanceRating, RelationshipSatisfaction=RelationshipSatisfaction,
                            YearsSinceLastPromotion=YearsSinceLastPromotion, WorkLifeBalance=WorkLifeBalance,
                            MaritalStatus=MaritalStatus, Gender=Gender, OverTime=OverTime, Attrition=Attrition)
        session.add(employee)
        session.commit()
        logger.info("new employee added")

    def close(self) -> None:
        """
        Closes SQLAlchemy session
        Returns: None
        """
        self.session.close()
        logger.info("Session closed")
