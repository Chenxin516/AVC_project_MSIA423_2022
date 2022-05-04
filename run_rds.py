"""Creates and ingests data into a table of songs for the PennyLane."""
import os
import logging
import sqlalchemy as sql
import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData

engine_string = os.getenv("SQLALCHEMY_DATABASE_URI")
if engine_string is None:
    raise RuntimeError("SQLALCHEMY_DATABASE_URI environment variable not set; exiting")
#engine_string = "mysql+pymysql://chenxin:clarinet516@nu-msia423-chenxin.cbyjmaal6ssg.us-east-1.rds.amazonaws.com:3306/msia423_db"


# set up looging config
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__file__)

Base = declarative_base()


class Employee(Base):
    """Creates a data model for the database to be set up for employees."""

    __tablename__ = "employee"

    EmployeeNumber = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    Age = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    HourlyRate = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    DistanceFromHome = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    Education = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    EnvironmentSatisfaction = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    JobInvolvement = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    JobLevel = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    JobSatisfaction = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    NumCompaniesWorked = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    PerformanceRating = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    TotalWorkingYears = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)
    WorkLifeBalance = sqlalchemy.Column(sqlalchemy.Integer, unique=False, nullable=False)

    BusinessTravel = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    DailyRate = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    Gender = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=False)
    OverTime = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)
    Attrition = sqlalchemy.Column(sqlalchemy.String(100), unique=False, nullable=True)




if __name__ == "__main__":
    # set up mysql connection
    engine = sql.create_engine(engine_string)

    # test database connection
    try:
        engine.connect()
    except sqlalchemy.exc.OperationalError as e:
        logger.error("Could not connect to database!")
        logger.debug("Database URI: %s", )
        raise e

    # create the tracks table
    Base.metadata.create_all(engine)

    # create a db session
    Session = sessionmaker(bind=engine)
    session = Session()

    # add a record/track
    # employee1 = Employee(artist="Britney Spears", album="Circus", title="Radar")
    # session.add(employee1)
    # session.commit()
    #
    # logger.info(
    #     "Database created with song added: Radar by Britney spears from the album, Circus"
    # )
    # To add multiple rows
    # session.add_all([track1, track2])

    session.close()
