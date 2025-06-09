# pipeline.py
import sys
from utils.common_functions import read_yaml
from config.paths_config import *
from src.data_ingestion import DataIngestion
from src.data_processing import DataProcessor
from src.model_training import ModelTrainer
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

def main():
    try:
        # 1) Lê configurações
        config = read_yaml(CONFIG_PATH)
        db_params = config["db_config"]

        # 2) Ingestão
        logger.info("=== STEP 1: Data Ingestion ===")
        ingestion = DataIngestion(db_params=db_params, output_dir=RAW_DATA_DIR)
        ingestion.run()

        # 3) Processamento
        logger.info("=== STEP 2: Data Processing ===")
        processor = DataProcessor(
            train_path=RAW_DATA_TRAIN,
            test_path=RAW_DATA_TEST,
            processed_dir=PROCESS_DATA_DIR,
            config_path=CONFIG_PATH
        )
        processor.split_data()
        processor.run()

        # 4) Treinamento
        logger.info("=== STEP 3: Model Training ===")
        trainer = ModelTrainer(
            train_path=PROCESSED_TRAIN_DATA_PATH,
            test_path=PROCESSED_TEST_DATA_PATH,
            config_path=CONFIG_PATH
        )
        X_train, y_train, X_test, y_test = trainer.load_data()
        trainer.train_model(X_train, y_train, X_test, y_test)

        logger.info("=== PIPELINE COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise CustomException(str(e), sys)

if __name__ == "__main__":
    main()