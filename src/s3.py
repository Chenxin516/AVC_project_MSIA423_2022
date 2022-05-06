import argparse
import logging.config
import re
import typing

import boto3
import botocore
import pandas as pd

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger(__name__)


def parse_s3(s3path: str) -> typing.Tuple[str, str]:
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_path: str, s3path: str) -> None:
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)


def upload_to_s3_pandas(local_path: str, s3path: str, sep: str = ';') -> None:
    df = pd.read_csv(local_path, sep=sep)

    try:
        df.to_csv(s3path, sep=sep)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)


def download_file_from_s3(local_path: str, s3path: str) -> None:
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.download_file(s3_just_path, local_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data downloaded from %s to %s', s3path, local_path)


def download_from_s3_pandas(local_path: str, s3path: str, sep: str = ';'):
    try:
        df = pd.read_csv(s3path, sep=sep)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        df.to_csv(local_path, sep=sep)
        logger.info('Data uploaded from %s to %s', local_path, s3path)