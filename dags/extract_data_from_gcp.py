from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base_hook import BaseHook
from datetime import datetime
import pandas as pd
import sqlalchemy

### Transform Step.....
def load_to_sql(file_path):
    conn = BaseHook.get_connection('postgres_default')  
    engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{conn.login}:{conn.password}@mlops-project-telco-custumer-church_a11a23-postgres-1:{conn.port}/{conn.schema}")
    df = pd.read_csv(file_path)
    df.to_sql(name="Telco_Customer_Churn", con=engine, if_exists="replace", index=False)

# Define the DAG
with DAG(
    dag_id="extract_telco_custome_churn_data",
    schedule_interval='0 5 * * 1',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    list_files = GCSListObjectsOperator(
        task_id="list_files",
        bucket="my_bucket_custumer_churn", 
    )

    download_file = GCSToLocalFilesystemOperator(
        task_id="download_file",
        bucket="my_bucket_custumer_churn", 
        object_name="Telco-Customer-Churn.csv", 
        filename="/tmp/Telco-Customer-Churn.csv", 
    )

    load_data = PythonOperator(
        task_id="load_to_sql",
        python_callable=load_to_sql,
        op_kwargs={"file_path": "/tmp/Telco-Customer-Churn.csv"}
    )

    list_files >> download_file >> load_data