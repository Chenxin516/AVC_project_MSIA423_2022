# MSiA423 Employee Attrition Prediction Poroject

# Table of Contents
* [Directory structure ](#Directory-structure)
* [Running the app ](#Running-the-app)
	* [1. Initialize the database ](#1.-Initialize-the-database)
	* [2. Configure Flask app ](#2.-Configure-Flask-app)
	* [3. Run the Flask app ](#3.-Run-the-Flask-app)
* [Testing](#Testing)
* [Mypy](#Mypy)
* [Pylint](#Pylint)

# Project charter

## Vision
Every year a lot of companies invest time and money in training both new and existing employees. Those companies aim to increase the effectiveness of their employees. However, every year many employees leave the companies because of various reasons like voluntary resignations, layoffs, illness, etc. It would be a waste of time and money if companies spend effort to hire and train those employees who would later leave the companies. Therefore, it would be important if companies can predict employee attrition in order to better allocate their resources.

## Mission
This project creates an app that can predict employees' attrition for a company. Employers will input a set of features of their employees to the app, then the app will predict the probability that their employees would attrite in the near future. The data of the project is from [Kaggle](https://www.kaggle.com/datasets/colearninglounge/employee-attrition).

Theoretical example: An employer has some potential candidates to hire and wants to decide which one to hire. The employer decides to make hiring decision based on their attritions. The employer could use the app and input features related to their attritions like Satisfaction level, Education, Salary, etc. Then the app will tell the employer how likely each one of them would leave the company, and the employer could come up with corresponding hiring strategies based on the information.

## Success Criteria
1. Machine Learning performance metrics: Precision, Recall, F-1 Score, AUC. Those four metrics are typical evaluation metrics for binary classification tasks. While a value of one for all four metrics is ideal, a typical minimum value of success is 0.8.

2. Business metrics:

   	Number of inputs per user (employer): This metric measures the engagement of user, higher value would indicate better engagement.

   	Number of days of login per month: This metric measures the user retention, higher value would indicate better retention.




## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs│    
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project.
|
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
│   ├── Dockerfile.run                <- Dockerfile for building image to execute run.py  
│   ├── Dockerfile.test               <- Dockerfile for building image to run unit tests
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. No executable Python files should live in this folder.  
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app 
Note: For Windows operating system, you might need to add winpty before the Docker Bash command.

### 1. Download/upload the data 
Build the Docker image for AWS_S3 (for raw data):

```bash
docker build -t project -f dockerfiles/Dockerfile.run_s3 .    
```

Upload to s3
```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY project 
```
Download from s3

```bash
docker run --mount type=bind,source="$(pwd)/data/raw/",target=/app/data/raw/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY project --download
```

###2 Run model pipeline (process data + train & save model):
Build the Docker image for running the entire pipeline
```bash
docker build -f dockerfiles/Dockerfile.pipeline -t project .
```
Run the model pipeline 

```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ project pipeline.sh
```

###3 Create the AWS_RDS database (upload processed data/add employee)
To Build the Docker image for creating database and adding records in RDS
```bash
docker build -t project -f dockerfiles/Dockerfile.run_rds .
```
Create the database in RDS
```bash
docker run -it --env SQLALCHEMY_DATABASE_URI project create_db
```
Adding processed data
```bash
docker run -it --env SQLALCHEMY_DATABASE_URI project ingest
```
#### Adding songs 
To add songs to the database:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ pennylanedb ingest --engine_string=sqlite:///data/tracks.db --artist=Emancipator --title="Minor Cause" --album="Dusk to Dawn"
```

#### Defining your engine string 
A SQLAlchemy database connection is defeind by `config/flaskconfig.py` . It includes the following configurations:
```python
# Engine string
import os
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('MYSQL_DATABASE')
DB_DIALECT = 'mysql+pymysql'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    SQLALCHEMY_DATABASE_URI = f'{DB_DIALECT}://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DATABASE}'


```
The user will need his or her AWS credentials to access S3 or RDS.



### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "Employee-Attrition-Prediction"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100
```


### 3. Run the Flask app 

#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f dockerfiles/Dockerfile.app -t pennylaneapp .
```

This command builds the Docker image, with the tag `pennylaneapp`, based on the instructions in `dockerfiles/Dockerfile.app` and the files existing in this directory.

#### Running the app

To run the Flask app, run: 

```bash
docker run --name test-app --mount type=bind,source="$(pwd)",target=/app/ -p 5000:5000 project

```
You should be able to access the app at http://127.0.0.1:5000/ in your browser (Mac/Linux should also be able to access the app at http://127.0.0.1:5000/ or localhost:5000/) .

The arguments in the above command do the following: 

* The `--name test-app` argument names the container "test". This name can be used to kill the container once finished with it.
* The `--mount` argument allows the app to access your local `data/` folder so it can read from the SQLlite database created in the prior section. 
* The `-p 5000:5000` argument maps your computer's local port 5000 to the Docker container's port 5000 so that you can view the app in your browser. If your port 5000 is already being used for someone, you can use `-p 5001:5000` (or another value in place of 5001) which maps the Docker container's port 5000 to your local port 5001.

Note: If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `dockerfiles/Dockerfile.app`)


#### Kill the container 

Once finished with the app, you will need to kill the container. 

First run "ctrl"+"\" and "ctrl"+"Z" to stop the process. If you named the container, you can execute the following: 

```bash
docker kill test-app
```
where `test-app` is the name given in the `docker run` command.

If you did not name the container, you can look up its name by running the following:

```bash 
docker container ls
```

The name will be provided in the right most column. 

## 4 Testing

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.test -t pennylanetest .
```

To run the tests, run: 

```bash
 docker run pennylanetest
```

The following command will be executed within the container to run the provided unit tests under `test/`:  

```bash
python -m pytest
``` 

## Mypy

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.mypy -t pennymypy .
```

To run mypy over all files in the repo, run: 

```bash
 docker run pennymypy .
```
To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennymypy .
```

To run mypy for a single file, run: 

```bash
 docker run pennymypy run.py
```

## Pylint

Run the following:

```bash
 docker build -f dockerfiles/Dockerfile.pylint -t pennylint .
```

To run pylint for a file, run:

```bash
 docker run pennylint run.py 
```

(or any other file name, with its path relative to where you are executing the command from)

To allow for quick iteration, mount your entire repo so changes in Python files are detected:


```bash
 docker run --mount type=bind,source="$(pwd)"/,target=/app/ pennylint run.py
```
