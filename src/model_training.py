import os
import sys
import joblib
import pandas as pd

from scipy.stats import randint
from lightgbm import LGBMClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from config.model_params import *
from utils.common_functions import read_yaml, load_data

import mlflow
import mlflow.sklearn

logger = get_logger(__name__)

class ModelTrainer:
    def __init__(self, train_file_path, test_file_path, model_output_dir):
        self.train_file_path = train_file_path
        self.test_file_path = test_file_path
        self.model_output_dir = model_output_dir

        self.params_dict = LIGHTGBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS

        os.makedirs(os.path.dirname(self.model_output_dir),exist_ok=True)

    def load_and_split_data(self):
        try:
            logger.info(f"Loding data from {self.train_file_path}")
            train_df = load_data(self.train_file_path)

            logger.info(f"Loding data from {self.test_file_path}")
            test_df = load_data(self.test_file_path)

            X_train = train_df.drop(columns='booking_status')
            y_train = train_df['booking_status']

            X_test = test_df.drop(columns='booking_status')
            y_test = test_df['booking_status']

            logger.info("Data Splitted Succesfully for Model Training")

            return X_train, y_train, X_test, y_test

        except Exception as e:
            logger.error("Error Occured while loading and spliting the data")
            raise CustomException(str(e), sys)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Initializing our model")

            lgbm = LGBMClassifier(random_state=42)

            logger.info("Starting our Hyperparameter Tuning")

            random_search = RandomizedSearchCV(
                estimator=lgbm,
                param_distributions=self.params_dict,
                n_iter=self.random_search_params["n_iter"],
                cv=self.random_search_params["cv"],
                n_jobs=self.random_search_params["n_jobs"],
                verbose=self.random_search_params["verbose"],
                scoring=self.random_search_params["scoring"],
                random_state=42

            )

            logger.info("Fitting our model with RandomizedSearchCV")

            random_search.fit(X_train, y_train)

            logger.info("RandomizedSearchCV fitting completed")

            best_params = random_search.best_params_

            logger.info(f"Best Hyperparameters found: {best_params}")

            best_model = random_search.best_estimator_

            return best_model
        except Exception as e:
            logger.error("Error Occured while training the model")
            raise CustomException(str(e), sys)

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Starting model evaluation")

            y_pred = model.predict(X_test)

            accuray = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            logger.info(f"Model Evaluation Completed with Accuracy: {accuray}, Precision: {precision}, Recall: {recall}, F1 Score: {f1}")

            return {
                "accuracy": accuray,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }

        except Exception as e:
            logger.error("Error Occured while evaluating the model")
            raise CustomException(str(e), sys)

    def save_model(self, model):
        try:
            logger.info(f"Saving the model to {self.model_output_dir}")

            joblib.dump(model, self.model_output_dir)

            logger.info("Model saved successfully")

        except Exception as e:
            logger.error("Error Occured while saving the model")
            raise CustomException(str(e), sys)

    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Starting Model Training Pipeline")

                logger.info("Starting our MLFLOW Experiment")

                logger.info("Logging the training ans testing dataset to MLFLOW")

                mlflow.log_artifact(self.train_file_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_file_path, artifact_path="datasets")

                X_train, y_train, X_test, y_test = self.load_and_split_data()

                best_model = self.train_lgbm(X_train, y_train)

                evaluation_metrics = self.evaluate_model(best_model, X_test, y_test)

                logger.info("Logging the params and the evaluation metrics")

                mlflow.log_params(best_model.get_params())
                mlflow.log_metrics(evaluation_metrics)

                self.save_model(best_model)

                logger.info("Logging the model into MLFLOW")

                mlflow.log_artifact(self.model_output_dir)

            logger.info("Model Training Successfully completed")
        except Exception as e:
            logger.error("Error Occured during Model Training Pipeline")
            raise CustomException(str(e), sys)


if __name__ == "__main__":
    model_trainer = ModelTrainer(PROCESSED_TRAIN_FILE_PATH,PROCESSED_TEST_FILE_PATH,MODEL_OUTPUT_PATH)
    model_trainer.run()
