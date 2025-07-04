#data_ingestion.py
import pandas as pd
from google.cloud import storage
from utils.logger import get_logger
from utils.custom_exception import CustomException
from utils.common_functions import read_yaml
import os
import sys
from config.paths_config import *

logger = get_logger(__name__)

class DataIngestion:

    def __init__(self, gcs_params, output_dir):
        """
       gcs_params must contain:
          - "project_id": "<your_gcp_project_id>"
          - "bucket_name": "<your_bucket_name>"
          - "file_name": "<your_file_name_in_gcs>"
        """
        self.gcs_params = gcs_params
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)        

    def extract_data(self):
        """
        Download CSV directly from GCS.
        """
        try:
            logger.info("Starting GCS Download.")
            storage_client = storage.Client(project=self.gcs_params['project_id'])

            bucket = storage_client.bucket(self.gcs_params['bucket_name'])
            blob = bucket.blob(self.gcs_params['file_name'])

            local_file = os.path.join(self.output_dir, self.gcs_params['file_name'])

            blob.download_to_filename(local_file)

            logger.info("Downloaded CSV from GCS.")
            df = pd.read_csv(local_file)
            return df

        except Exception as e:
            logger.error(f"Error while downloading from GCS {e}")
            raise CustomException(str(e), sys)

    def save_data(self, df):
        """
        Saves the CSV to a local directory.
        """
        try:
            local_file = os.path.join(self.output_dir, "Telco-Customer-Churn.csv")
            df.to_csv(local_file, index=None)

            logger.info("Data Saving Done.")
        except Exception as e:
            logger.error(f"Error while saving data {e}")
            raise CustomException(str(e), sys) 


    def run(self):
        """
        Main pipeline.
        """
        try:
            logger.info("Data Ingestion Pipeline Started....")
            df = self.extract_data()
            self.save_data(df)
            logger.info("End of Data Ingestion Pipeline....")
        except Exception as e:
            logger.error(f"Error while data Ingestion pipeline.... {e}")
            raise CustomException(str(e), sys)     
        

if __name__ == "__main__":
    config = read_yaml(file_path=CONFIG_PATH)

    gcs_params = {
        "project_id": config['project_id'],
        "bucket_name": config['gcs_config']['bucket_name'],
        "file_name": config['gcs_config']['file_name'],
    }
    data_ingestion = DataIngestion(gcs_params=gcs_params, output_dir=RAW_DATA_DIR)
    data_ingestion.run()

