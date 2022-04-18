
import sys
from io import StringIO
import pandas as pd
import requests
import logging
import re
from config import config
import warnings
warnings.simplefilter("ignore")
data_url = config.data_url
local_data_path = config.local_data_path

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def download_data(local_path=local_data_path):
    """
    download static, public, data file into python using the request library, save csv to local path, and convert to pandas dataframe
    Args:
        local_path [string]: local path to download raw data to
    Returns:
        data [pandas dataframe]: raw data as a pandas dataframe
    """

    try:
        logger.debug("Attempting to download raw data from data source")
        r = requests.get(data_url)
    except requests.exceptions.RequestException:
        logger.error("Unable to download raw data from data source")
        sys.exit(1)

    text = r.text
    textIO = StringIO(text)
    data = pd.read_csv(textIO, sep=',')
    data.to_csv(local_path, sep=',', index=False)
    return data
