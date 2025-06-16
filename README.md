# 🔹 Telco Customer Churn Analysis 🔹

This is a **Machine Learning project aimed at analyzing Customer Churn for a Telecom Company**.
The main objective is to **understand customer behavior, uncover key drivers of churn, and develop a robust, scalable, and reliable predictive model** that can help the business proactively identify at-risk customers and implement retention strategies **before they churn**.

By applying **exploratory data analysis, statistical methods, and machine learning techniques**, this project aims not only to accurately predict which customers are likely to discontinue their service, but also to **derive actionable insights and recommendations**.
These insights can empower the company’s stakeholders — from marketing to customer service — to make data-informed decisions, optimize retention campaigns, and enhance overall customer satisfaction and loyalty.

The final pipeline comprises **end-to-end components**, from **data ingestion and transformation** to **model training, evaluation, deployment, and monitoring**, allowing the solution to be integrated smoothly into a production environment and maintained over time.

---

## 📁 Project Structure

```
MLOPS_PROJECT_TELCO_CUSTOMER_CHURN
├── .astro/
├── .dvc/
├── airflow/
├── artifacts/
├── config/
├── Custom_Jenkins/
├── dags/
├── Documentation_Review/
├── include/
├── k8s/
├── logs/
├── mlflow/
├── MLOPS_PROJECT_TELCO_CUSTOMER_CHURCH.egg-info/
├── notebook/
├── pipeline/
├── plugins/
├── src/
├── static/
├── templates/
├── tests/
├── utils/
├── venv/
├── .dockerignore
├── .dvcignore
├── .gitignore
├── .env
├── airflow_settings.yaml
├── application.py
├── Docker_Test_Poducao.md
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.dev
├── Dockerfile.mlflow
├── Jenkinsfile
├── packages.txt
├── prometheus.yml
├── README.md
```
---

## 🔍 1️⃣ Exploratory Data Analysis (Jupyter)

The project starts with **exploratory data analysis (EDA)** in a **Jupyter notebook**, following these steps:

- **1.1. Overview of the Dataset:**  
  Loading the data, inspecting dimensions, column types, and previewing first few rows.

- **1.2. Check for Null/Missing Values:**  
  Detect and handle missing or invalid values.

- **1.3. Check Unique Values per Column:**  
  Quantify unique values in each categorical column.

---

## 📊 2️⃣ Univariate Analysis

- **2.1. Numerical Variables:**  
  Distribution, summary statistics, and boxplots.

- **2.2. Categorical Variables:**  
  Counts, proportions, and bar charts.

---

## 🔄 3️⃣ Bivariate Analysis

- **3.1. Categorical vs Churn:**  
  Analyzing Churn proportions across different categories.

- **3.2. Numerical vs Churn:**  
  Boxplot, Violin,  Histogram to visualize distributions conditioned on Churn.

---

## 🔗 4️⃣ Multivariate Analysis

- **4.1. Pearson's Correlation:**  
  Heatmap to show relationships between numerical variables.

- **4.2. Pairplot:**  
  Visualize multivariate relationships in a grid format.

---

## 🧹 5️⃣ Model Preparation

- **5.1. Categorical Impact:**  
  Apply label or one-hot encoding.

- **5.2. Preprocessing:**  
  Handle missing values, scaling, and split into training and testing.

---

## ⚙ 6️⃣ Model, MLflow & Deployment

- The pipeline comprises a **modular and scalable architecture** designed to streamline the entire Machine Learning lifecycle. It includes:

  - **Data Ingestion:**  
    Responsible for retrieving raw data from a Google Cloud Platform (GCP) Bucket and loading it into a directory for further processing.  
    This component handles all operations related to accessing, validating, and preparing the raw data for subsequent steps.

  - **Data Processing:**  
    Performs extensive **preprocessing and transformation** of the raw data, including cleaning, scaling, and encoding of features.  
    It prepares both the training and testing sets in a form suitable for training a Machine Learning algorithm, addressing missing values, categorical variables, and other data issues along the way.

  - **Model Training:**  
    Initializes and fits a Machine Learning pipeline on the processed data, employing techniques to find the best hyperparameter settings and maximize performance.  
    The pipeline is designed to be **modular**, allowing for swapping in different algorithms and components without affecting the rest of the architecture.

- **MLflow Integration:**  
  To enable **experiment tracking and reproducibility**, MLflow is integrated into the pipeline.  
  MLflow efficiently **logs all key parameters**, **metrics**, **model versions**, and **artifacts**, making it easy to compare different runs, revert back to previous versions, and collaborate with teammates.

- The pipeline is designed to be **automated, reusable, and adaptable**, allowing for smooth future improvements and scaling as the data evolves or business requirements change.


---

## 🌐 7️⃣ Web Application, Alibi-detect, Grafana, and Prometheus

- The trained model is deployed as a **Flask application with a UI (HTML + CSS)**.

- The application comprises:
  
  - **A lightweight UI:**  
    Built with **Flask**, **Jinja2**, and **HTML + CSS**, allowing business users to:
    - Provide customer details through a form.
    - Receive real-time churn risk predictions alongside a summary of key factors contributing to the score.

  - **API endpoint (/dashboard):**  
    The application performs **feature transformation**, **encoding**, and **model scoring** directly from form submissions.  
    It converts raw inputs into the required format for the trained pipeline, performs a prediction, and then displays the result back to the UI.

- **Alibi-detect (KSDrift)**  
  To **detect data drift** and track whether the distribution of incoming samples diverges from the training distribution.  
  If **drift is detected**, a warning is raised, and a counter is incremented.  
  Drift signals may be used to determine when the model might need **retraining or intervention**.

- **Grafana + Prometheus:**  
  To **observe and visualize API usage, latency, and drift events in real time**, the application exposes custom Prometheus metrics:

  - `prediction_total_count`: total number of predictions made by the API.
  - `ks_drift_detected_columns`: number of columns where a data drift was identified by the Kolmogorov-Smirnov (KS) test.
  - `drift_events_total`: total number of drift events raised by the detector.

  Grafana can connect directly to Prometheus to produce **dashboards and alerts**.  
  Operations, data science, and ML engineers can visualize these signals to track service health and respond proactively when abnormalities arise.

- **Docker Deployment:**  
  The application is containerized using **Docker**, employing a lightweight `python:3.11-slim` base image.  
  All necessary components — code, trained models, and libraries — are bundled into a single container.

---

## 🐳 8️⃣ Deployment (Docker, Kubernetes, CI/CD)

- The application is containerized with **Docker**, deployed on **Kubernetes**, and **Jenkins** is used for CI/CD.

- **DVC** is employed for **dataset and code version control** alongside Git.

🔹 Workflow Overview:

- This pipeline performs a full CI and CD flow:

    - Clone code from Git

    - Create and activate a Python virtual environment

    - Validate GCP credentials

    - Pull data and models from DVC

    - Build and Push Docker images to Container Registry

    - Apply manifests to Kubernetes

    - Launch a Model Training Job in the Cluster

    - Save trained Model to DVC and Git

    - Clean-up resources afterwards


🔹 Jenkinsfile Highlights:

The pipeline performs the following key steps:

```
stage('Clone') { … }
stage('Environment') { … }
stage('DVC Pull') { … }
stage('Docker Build and Push') { … }
stage('Kubernetes Deployment') { … }
stage('Model Training') { … }
stage('Version Model Artifacts') { … }
```

🔹 Grafana Dashboard (Metrics):

Grafana is deployed alongside the application to visualize key metrics and track API usage, latency, and training events in real time.

🔹 Flask Application (API):

Flask UI lets you manually submit customer data and view Churn predictions immediately.

🔹 MLflow UI (Model Experiment)

The MLflow UI displays a rich view of your experiments — including run IDs, parameters, metrics, and trained models — to aid in comparison and reproducibility.

---

## 🛠 Tech Stack

- **Python (Flask, scikit-learn, MLflow, Alibi-detect)**
- **Docker, Kubernetes, Grafana, Prometheus**
- **Jenkins, DVC, Git**
- **Jupyter notebook for Exploratory Analysis**
- **HTML, CSS (Front-end)**

---

## 🚀 How to Run Locally

```bash
git clone https://github.com/EduardoSantosSousa/MLOPS-CHURN.git
cd telco-churn

# (optional) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install requirements
pip install -r packages.txt

# run application
export FLASK_APP=application.py
flask run


