#training_pipeline.py
import os
import sys
import mlflow
from utils.common_functions import read_yaml
from config.paths_config import *
from src.data_ingestion import DataIngestion
from src.data_processing import DataProcessor
from src.model_training import ModelTrainer
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

def setup_mlflow(config):
    tracking_uri = config.get("mlflow_config", {}) \
                       .get("tracking_uri", "http://mlflow-service:5000")
    mlflow.set_tracking_uri(tracking_uri)
    logger.info(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")


def main():
    try:
        #1) Reads settings
        config = read_yaml(CONFIG_PATH)

        # Configure MLflow
        setup_mlflow(config)

        # Define experiment
        experiment_name = config.get("mlflow_config", {}).get("experiment_name", "default")
        mlflow.set_experiment(experiment_name)
        logger.info(f"Set MLflow experiment: {experiment_name}")

        # Creates a main run that encompasses the entire pipeline
        with mlflow.start_run(run_name="full_training_pipeline"):
            #2) Ingestion
            logger.info("=== STEP 1: Data Ingestion ===")
            ingestion = DataIngestion(
                gcs_params={
                    "project_id": config['project_id'],
                    "bucket_name": config['gcs_config']['bucket_name'],
                    "file_name": config['gcs_config']['file_name'],
                },
                output_dir=RAW_DATA_DIR
            )
            ingestion.run()

            #3) Processing
            logger.info("=== STEP 2: Data Processing ===")
            processor = DataProcessor(
                train_path=RAW_DATA_TRAIN,
                test_path=RAW_DATA_TEST,
                processed_dir=PROCESS_DATA_DIR,
                config_path=CONFIG_PATH
            )
            processor.split_data()
            processor.run()

            #4) Training
            logger.info("=== STEP 3: Model Training ===")
            trainer = ModelTrainer(
                train_path=PROCESSED_TRAIN_DATA_PATH,
                test_path=PROCESSED_TEST_DATA_PATH,
                config_path=CONFIG_PATH
            )
            X_train, y_train, X_test, y_test = trainer.load_data()
            # Inside train_model there is already a nested run and metrics and model logs
            trainer.train_model(X_train, y_train, X_test, y_test)

        logger.info("=== PIPELINE COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise CustomException(str(e), sys)


if __name__ == "__main__":
    main()
