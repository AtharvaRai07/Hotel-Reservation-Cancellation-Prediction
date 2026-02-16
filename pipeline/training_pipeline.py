from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataPreprocessor
from src.model_training import ModelTrainer
from config.paths_config import *

if __name__ == "__main__":

    ### 1. Data Ingestion
    data_ingestion = DataIngestion(CONFIG_PATH)
    data_ingestion.run()

    ### 2. Data Preprocessing
    data_preprocessor = DataPreprocessor(TRAIN_FILE_PATH,TEST_FILE_PATH,PROCESSED_DIR,CONFIG_PATH)
    data_preprocessor.process()

    ### 3. Model Training
    trainer = ModelTrainer(PROCESSED_TRAIN_FILE_PATH,PROCESSED_TEST_FILE_PATH,MODEL_OUTPUT_PATH)
    trainer.run()
