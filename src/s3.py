import argparse
import logging.config
import re
import typing

import boto3
import botocore
import pandas as pd

# logging.config.fileConfig('config/logging.conf')
# logger = logging.getLogger('s3.py-demo')

logger = logging.getLogger(__name__)

def parse_s3(s3path: str) -> typing.Tuple[str, str]:
    """
    Parse the s3 path to get the bucket name and the path name
    Args:
        s3path (str): the input s3 path
    Returns:
        s3bucket (str): the s3 bucket name
        s3path (str): the s3 path
    """
    regex = r"s3.py://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_path: str, s3path: str) -> None:
    """
    Upload the file in local path to s3
    Args:
        local_path (str): the path that points to the local data
        s3path (str): the s3 path that the data will be uploaded to
    Returns: None
    """

    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3.py")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    except FileNotFoundError:
        logger.error('Please check whether your local path contains the data you want to upload', exc_info=True)
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)



def download_file_from_s3(local_path: str, s3path: str) -> None:
    """
        Download a data file from s3
        Args:
            local_path (str): the path that will store the downloaded data
            s3path (str): the s3 path that the data will be downloaded from
        Returns: None
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3.py")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.download_file(s3_just_path, local_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data downloaded from %s to %s', s3path, local_path)