import psycopg2
import pandas as pd
from utils.logger import get_logger
from utils.custom_exception import CustomException
from utils.common_functions import read_yaml
import os
import sys
from config.paths_config import *

logger = get_logger(__name__)

class DataIngestion:

    def __init__(self, db_params, output_dir):
        self.db_params= db_params
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                host = self.db_params['host'],
                port = self.db_params['port'],
                dbname = self.db_params['dbname'],
                user = self.db_params['user'],
                password = self.db_params['password']
            )    

            logger.info("Database connection established........")
            return conn
        except Exception as e:
            logger.error(f"Error while establishing connection {e}")
            raise CustomException(str(e), sys)

    def extract_data(self):
        try:
            conn = self.connect_to_db()
            query = 'SELECT * FROM public."Telco_Customer_Churn"';
            df = pd.read_sql_query(query, conn)
            conn.close()
            logger.info("Data Exctracted from DB...")
            return df
        except Exception as e:
            logger.error(f"Error while extracting data {e}")
            raise CustomException(str(e), sys)

    def save_date(self, df):
        try:
            df.to_csv(RAW_DATA, index = None)

            logger.info("Data Saving Done.....")

        except Exception as e:
            logger.error(f"Error while saving data {e}")
            raise CustomException(str(e), sys) 

    def run(self):
        try:
            logger.info("Data Ingestion Pipeline Started....")
            df = self.extract_data()
            self.save_date(df)
            logger.info("End of Data Ingestion Pipeline....")

        except Exception as e:
            logger.error(f"Error while data Ingestion Pipelin.... {e}")
            raise CustomException(str(e), sys)     
        

if __name__ =="__main__":
    config_db = read_yaml(file_path=CONFIG_PATH)
    db_params = config_db['db_config']
    data_ingestion = DataIngestion(db_params=db_params, output_dir=RAW_DATA_DIR)
    data_ingestion.run()
