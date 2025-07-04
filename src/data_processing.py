import os
import pandas as pd 
from utils.logger import get_logger
from utils.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml, load_data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import joblib


logger = get_logger(__name__)

class DataProcessor:

    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.config = read_yaml(config_path)
        self.config_split_data_config = self.config['split_data_config']
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.train_test_ratio = self.config_split_data_config["train_ratio"]
        self.random_state = self.config_split_data_config['random_state']
        self.target = self.config_split_data_config['target']
    
    
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

        if not os.path.exists(ENCODER_DIR):
            os.makedirs(ENCODER_DIR)    

    def split_data(self):
        try:
            logger.info("Starting the splitting process.....")
            data = pd.read_csv(RAW_DATA)

            y = data[self.target] 

            train_data, test_data = train_test_split(data, 
                                                    test_size= 1-self.train_test_ratio,
                                                    random_state=self.random_state,
                                                    stratify=y)

            train_data.to_csv(RAW_DATA_TRAIN, index=None)
            test_data.to_csv(RAW_DATA_TEST, index=None)

            logger.info(f"Train data saved to {RAW_DATA_TRAIN}")
            logger.info(f"Test data saved to {RAW_DATA_TEST}")
        
        except Exception as e:
            logger.error("Error while splitting data")
            raise CustomException("Failed to split data into training and test sets ", e)    


    def process_data(self, dataframe, dataset_name="unknown", encoders=None, save_encoder=False):
        try:
            logger.info(f"Starting Data Processing Step for [{dataset_name}] dataset...")

            dataframe.drop(columns=['customerID', 'gender'], inplace=True)
            dataframe.drop_duplicates(inplace=True)

            dataframe['TotalCharges'] = pd.to_numeric(dataframe['TotalCharges'], errors='coerce')

            dataframe['TotalCharges'].fillna(dataframe['TotalCharges'].median(), inplace=True)

            logger.info(f"Start Feature Engineering for [{dataset_name}] dataset...")

            dataframe['AvgMonthlySpend'] = dataframe['TotalCharges'] / (dataframe['tenure'] + 1)

            dataframe['NoOnlineServices'] = (
                (dataframe['OnlineSecurity'] == 'No').astype(int) +
                (dataframe['OnlineBackup'] == 'No').astype(int) +
                (dataframe['DeviceProtection'] == 'No').astype(int) +
                (dataframe['TechSupport'] == 'No').astype(int)
            )

            dataframe['NoStreaming'] = (
                (dataframe['StreamingTV'] == 'No').astype(int) +
                (dataframe['StreamingMovies'] == 'No').astype(int)
            )

            def count_services(row):
                count = 0
                service_cols = ['PhoneService', 'MultipleLines', 'InternetService','OnlineSecurity',
                                'OnlineBackup', 'DeviceProtection','TechSupport', 'StreamingTV',
                                'StreamingMovies']
                for col in service_cols:
                    if 'No internet service' in str(row[col]) or 'No phone service' in str(row[col]):
                        continue
                    if row[col] in ['Yes', 'Fiber optic', 'DSL']:
                        count += 1
                return count

            dataframe['TotalServices'] = dataframe.apply(count_services, axis=1)

            dataframe['RiskScore'] = (
                (dataframe['Contract'] == 'Month-to-month').astype(int) +
                (dataframe['OnlineSecurity'] == 'No').astype(int) +
                (dataframe['TechSupport'] == 'No').astype(int) +
                (dataframe['PaymentMethod'] == 'Electronic check').astype(int) +
                (dataframe['tenure'] < 6).astype(int)
            )

            logger.info("Applying Label Encoding")

            label_encoders = encoders or {}
            for col in dataframe.select_dtypes(include='object').columns:
                if col in label_encoders:
                    le = label_encoders[col]
                    dataframe[col] = le.transform(dataframe[col])
                    if col != self.target:
                        label_encoders[col] = le
                else:
                    le = LabelEncoder()
                    dataframe[col] = le.fit_transform(dataframe[col])
                    label_encoders[col] = le

            if save_encoder:
                joblib.dump(label_encoders, ENCODER_PATH)
                logger.info(f"Label encoders saved successfully at {ENCODER_PATH}")

            return dataframe, label_encoders

        except Exception as e:
            logger.error(f"Error during data processing: {e}")
            raise CustomException(e)
        
    
     
    def balance_data(self, dataframe, dataset_name="unknown"):
        try:
            logger.info(f"Handling Imbalanced Data for [{dataset_name}] dataset...")

            X = dataframe.drop(columns='Churn')
            y = dataframe["Churn"]

            smote = SMOTE(random_state = self.random_state)
            X_resampled, y_resampled = smote.fit_resample(X,y)

            balanced_df = pd.DataFrame(X_resampled , columns=X.columns)
            balanced_df["Churn"] = y_resampled

            logger.info("Data balanced sucesffuly")
            return balanced_df
        
        except Exception as e:
            logger.error(f"Error during balancing data step {e}")
            raise CustomException("Error while balancing data", e) 
    
    
    def save_data(self, df, file_path, dataset_name="unknown"):
        try:
            logger.info(f"Saving processed [{dataset_name}] data to {file_path}...") 

            df.to_csv(file_path, index=None)

            logger.info(f"Data saved sucessfuly to {file_path}")      

        except Exception as e:
            logger.error(f"Error during saving data step {e}")
            raise CustomException("Error while saving data", e)  

    
    def run(self):
        try:
            logger.info("Loading data from RAW directory") 

            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path) 

            train_df, label_encoders = self.process_data(train_df, dataset_name="train", save_encoder=True)
            test_df, _ = self.process_data(test_df, dataset_name="test", encoders=label_encoders, save_encoder=False)


            train_df = self.balance_data(train_df, dataset_name="train")
            test_df = self.balance_data(test_df, dataset_name="test")

            feature_columns = [col for col in train_df.columns if col != self.target]
            
            # Save as .pkl
            joblib.dump(feature_columns, FEATURES_PATH)
            logger.info(f"Feature columns saved to {FEATURES_PATH}")

            self.save_data(train_df, PROCESSED_TRAIN_DATA_PATH, dataset_name="train")
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH, dataset_name="test")

            logger.info("Data processing completed successfully")

        except Exception as e:
            logger.error(f"Error during preprocessing pipeline {e}")
            raise CustomException("Error while data preprocessing pipeline", e)


if __name__ == "__main__":

    processor = DataProcessor(train_path = RAW_DATA_TRAIN, test_path = RAW_DATA_TEST, processed_dir = PROCESS_DATA_DIR, config_path = CONFIG_PATH)
    processor.split_data()
    processor.run()            
