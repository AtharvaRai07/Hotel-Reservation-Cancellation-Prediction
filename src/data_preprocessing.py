import os
import sys
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml, load_data

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)

class DataPreprocessor:
    def __init__(self, train_file_path, test_file_path, processed_dir, config_path):
        self.train_file_path = train_file_path
        self.test_file_path = test_file_path
        self.processed_dir = processed_dir

        self.config = read_yaml(config_path)

        os.makedirs(self.processed_dir, exist_ok=True)

    def preprocess_data(self, df):
        try:
            logger.info("Starting our Data Preprocesing step")

            df.drop(columns=['Unnamed: 0','Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols = self.config["data_processing"]["categorical_columns"]
            num_cols = self.config["data_processing"]["numerical_columns"]

            logger.info("Applying Label Encoding")

            label_encoder = LabelEncoder()
            mappings = {}

            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])
                mappings[col] = {label:code for label, code in zip(label_encoder.classes_,label_encoder.transform(label_encoder.classes_))}

            logger.info(f"Label mappings are : \n {mappings}")

            logger.info("Handling Skewness")

            skew_threshold = self.config["data_processing"]["skewness_threshold"]
            skewness = df[num_cols].apply(lambda x:x.skew())
            for column in skewness[skewness > skew_threshold].index:
                df[column] = np.log1p(df[column])

            return df

        except Exception as e:
            logger.error("Error Occured during preprocessing data")
            raise CustomException(str(e), sys)

    def balanced_data(self, df):
        try:
            X = df.drop('booking_status', axis=1)
            y = df['booking_status']

            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X,y)

            balanced_df = pd.DataFrame(X_resampled, columns=X.columns)
            balanced_df['booking_status'] = y_resampled

            logger.info("Data balanced sucessfully")

            return balanced_df

        except Exception as e:
            logger.error("Error occured during balancing the data")
            raise CustomException(str(e), sys)

    def select_features(self, df):
        try:
            X = df.drop('booking_status', axis=1)
            y = df['booking_status']

            model = RandomForestClassifier(random_state=42)
            model.fit(X,y)

            feature_importance = model.feature_importances_

            feature_importance_df = pd.DataFrame({
                'feature':X.columns,
                'importance':feature_importance
            })

            top_features_importance_df = feature_importance_df.sort_values(by='importance',ascending=False).reset_index(drop=True)

            num_features_to_select = self.config["data_processing"]["no_of_features"]

            top_features = top_features_importance_df['feature'].head(num_features_to_select).values

            final_df = df[top_features.tolist() + ["booking_status"]]

            logger.info(f"Top {num_features_to_select} are : {top_features}")

            logger.info("Feature Selection Completed succesfully")

            return final_df

        except Exception as e:
            logger.info("Error occured while selection features")
            raise CustomException(str(e), sys)

    def save_data(self, df, file_path):
        try:
            logger.info("Saving our data in processed folder")

            df.to_csv(file_path, index=False)

            logger.info("Data Saved succesfully to the given file path")

        except Exception as e:
            logger.error("Error occured during saving the data")
            raise CustomException(str(e), sys)

    def process(self):
        try:
            logger.info("Loading data from RAM Directory")

            train_df = load_data(self.train_file_path)
            test_df = load_data(self.test_file_path)

            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            train_df = self.balanced_data(train_df)
            test_df = self.balanced_data(test_df)

            train_df = self.select_features(train_df)
            test_df = test_df[train_df.columns]

            self.save_data(train_df, PROCESSED_TRAIN_FILE_PATH)
            self.save_data(test_df, PROCESSED_TEST_FILE_PATH)

            logger.info("Data Processing completed sucessfully")

        except Exception as e:
            logger.error("Error occured during preprocessing pipeline")
            raise CustomException(str(e), sys)

if __name__ == "__main__":

    data_preprocessing = DataPreprocessor(TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_DIR, CONFIG_PATH)
    data_preprocessing.process()
