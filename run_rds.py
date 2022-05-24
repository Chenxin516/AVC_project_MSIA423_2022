"""Creates and ingests data into a table of songs for the PennyLane."""
import os
import logging.config
from sqlalchemy.ext.declarative import declarative_base
from src.employee_db import create_db, EmployeeManager, Employee
from sqlalchemy.exc import ProgrammingError, OperationalError
import argparse

engine_string = os.getenv("SQLALCHEMY_DATABASE_URI")
if engine_string is None:
    raise RuntimeError("SQLALCHEMY_DATABASE_URI environment variable not set; exiting")


# set up logging config
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__file__)

Base = declarative_base()

if __name__ == "__main__":

    # Add parsers for both creating a database and adding model result data to it
    parser = argparse.ArgumentParser(description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sp_create = subparsers.add_parser("create_db", description="Create database")
    sp_create.add_argument("--engine_string", default=engine_string,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    sp_ingest = subparsers.add_parser("ingest", description="Add result data to database")
    sp_ingest.add_argument("--input_path", default="data/raw/employee_attrition_result.csv",
                           help="input file path")
    sp_ingest.add_argument("--engine_string", default=engine_string,
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name

    if sp_used == 'create_db':
        try:
            create_db(args.engine_string)
            logger.info("The employee table has been created")
        except ValueError as e:
            logger.error("Exiting. Please check database connection string.")
        except (ProgrammingError, OperationalError) as e:
            logger.error("Exiting. An error has occurred while making the database connection.")

    elif sp_used == 'ingest':
        employee = EmployeeManager(engine_string=args.engine_string)
        employee.add_result(args.input_path)
        logger.info("the result data has been ingested")
        employee.close()






