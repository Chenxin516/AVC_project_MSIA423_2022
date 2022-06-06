"""Download and upload data from S3."""
import argparse
import logging.config
import yaml

from src.s3 import download_file_from_s3, upload_file_to_s3, download_from_s3_pandas, upload_to_s3_pandas

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('s3-pipeline')

if __name__ == '__main__':
    with open('config/config.yaml', "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    parser = argparse.ArgumentParser()
    parser.add_argument('--sep',
                        default=';',
                        help="CSV separator if using pandas")
    parser.add_argument('--pandas', default=False, action='store_true',
                        help="If used, will load data via pandas")
    parser.add_argument('--download', default=False, action='store_true',
                        help="If used, will load data via pandas")
    parser.add_argument('--s3path', default=config['s3'],
                        help="If used, will load data via pandas")
    parser.add_argument('--local_path', default=config['local'],
                        help="Where to load data to in S3")
    args = parser.parse_args()

    if args.download:
        if args.pandas:
            download_from_s3_pandas(args.local_path, args.s3path, args.sep)
        else:
            download_file_from_s3(args.local_path, args.s3path)
    else:
        if args.pandas:
            upload_to_s3_pandas(args.local_path, args.s3path, args.sep)
        else:
            upload_file_to_s3(args.local_path, args.s3path)
