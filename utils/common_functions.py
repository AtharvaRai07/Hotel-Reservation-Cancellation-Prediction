import os
import pandas
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml
import sys
import pandas as pd

logger = get_logger(__name__)


def read_yaml(file_path:str):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the given path")

        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info("Succesfully read the YAML file")
            return config
    except Exception as e:
        logger.error("Error while reading YAML file")
        raise CustomException(str(e), sys)


def load_data(file_path:str) -> pd.DataFrame:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the given path")

        logger.info(f"Reading the data from {file_path}")
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        logger.error("Error while loading the data")
        raise CustomException(str(e), sys)

