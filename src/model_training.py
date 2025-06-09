import os
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report, confusion_matrix
from config.paths_config import *
from utils.logger import get_logger
from utils.custom_exception import CustomException
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class ModelTrainer:
    
    def __init__(self, train_path, test_path, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.config = read_yaml(config_path)

    def load_data(self):
        try:
            logger.info("Loading processed training and test datasets")
            train_df = pd.read_csv(self.train_path)
            test_df = pd.read_csv(self.test_path)

            X_train = train_df.drop(columns='Churn')
            y_train = train_df['Churn']

            X_test = test_df.drop(columns='Churn')
            y_test = test_df['Churn']

            return X_train, y_train, X_test, y_test
        
        except Exception as e:
            logger.error("Error loading data")
            raise CustomException("Failed to load processed data", e)

    def save_model(self, model):
        try:
            os.makedirs(MODEL_DIR, exist_ok=True)
            joblib.dump(model, MODEL_PATH)
            logger.info(f"Model successfully saved to: {MODEL_PATH}")
        except Exception as e:
            logger.error("Error saving model.")
            raise CustomException("Error saving model", e)

    def train_model(self, X_train, y_train, X_test, y_test):
        try:
            logger.info("Starting model training with GridSearch and MLflow")

            rf_params = self.config["model_config"]
            rf = RandomForestClassifier(**rf_params)

            grid_config = self.config["grid_search_config"] 
            param_grid = grid_config.pop("param_grid")

            param_grid["max_depth"] = [None if v is None else v for v in param_grid['max_depth']]

            grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, **grid_config)

            with mlflow.start_run(run_name="RandomForest_SMOTE_GridSearch", nested=True) as run:
                grid_search.fit(X_train, y_train)

                best_model = grid_search.best_estimator_
                y_pred = best_model.predict(X_test)

                f1 = f1_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred)
                recall = recall_score(y_test, y_pred)

                mlflow.log_params(grid_search.best_estimator_.get_params())
                mlflow.log_metric("f1_score", f1)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                
                # Salvando o modelo localmente primeiro
                self.save_model(best_model)
                
                logger.info(f"Best parameters: {grid_search.best_params_}")
                logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
                logger.info(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
                logger.info("Model Training Done....")
                
        except Exception as e:
            logger.error(f"Error while training model: {e}")
            raise CustomException("Error during model training", e)
        
if __name__ == "__main__":
    trainer = ModelTrainer(
        train_path=PROCESSED_TRAIN_DATA_PATH,
        test_path=PROCESSED_TEST_DATA_PATH,
        config_path=CONFIG_PATH
    )

    X_train, y_train, X_test, y_test = trainer.load_data()
    trainer.train_model(X_train, y_train, X_test, y_test)





