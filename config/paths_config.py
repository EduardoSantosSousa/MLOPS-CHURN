import os

# ------------------------------------------------------
# Project root path
# ------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..')) 

# ------------------------------------------------------
# File and directory configuration
# ------------------------------------------------------

# Path to general configuration file
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config', 'config.yml')

# Directories and data files
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'artifacts', 'data')
RAW_DATA = os.path.join(RAW_DATA_DIR, 'telco_custumer_churn.csv')

RAW_DATA_TRAIN = os.path.join(RAW_DATA_DIR,'train.csv') 
RAW_DATA_TEST = os.path.join(RAW_DATA_DIR,'test.csv')

PROCESS_DATA_DIR = os.path.join(PROJECT_ROOT, 'artifacts','processed' )
PROCESSED_TRAIN_DATA_PATH = os.path.join(PROCESS_DATA_DIR,'processed_train.csv')
PROCESSED_TEST_DATA_PATH = os.path.join(PROCESS_DATA_DIR,'processed_test.csv')

ENCODER_DIR = os.path.join(PROJECT_ROOT, 'artifacts', 'encoders')
ENCODER_PATH = os.path.join(ENCODER_DIR, 'label_encoders.pkl')

# ------------------------------------------------------
# Model directory
# ------------------------------------------------------
MODEL_DIR = os.path.join(PROJECT_ROOT, 'artifacts', 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'best_random_forest.pkl')
FEATURES_PATH = os.path.join(MODEL_DIR, 'feature_columns.pkl')