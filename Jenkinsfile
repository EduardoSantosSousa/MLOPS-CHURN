pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'serious-cat-455501-d2'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
    }

    stages {
        stage("Cloning from GitHub") {
            steps {
                script {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token-telco-churn',
                            url: 'https://github.com/EduardoSantosSousa/MLOPS-CHURN.git'
                        ]]
                    ])
                }
            }
        }

        stage("Setup Environment") {
            steps {
                script {
                    echo 'Setting up environment...'
                    sh """
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -e .
                    pip install dvc google-cloud-storage mlflow prometheus-client
                    """
                }
            }
        }

        stage("Validate Credentials") {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    usernamePassword(
                        credentialsId: 'mlflow-credentials',
                        usernameVariable: 'MLFLOW_USERNAME',
                        passwordVariable: 'MLFLOW_PASSWORD'
                    )
                ]) {
                    sh """
                    . ${VENV_DIR}/bin/activate
                    python -c "from google.cloud import storage; storage.Client()"
                    echo "MLflow Credentials Validated"
                    """
                }
            }
        }

        stage('DVC Pull') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                    . ${VENV_DIR}/bin/activate
                    export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
                    dvc pull
                    """
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                    export DOCKER_CLI_TIMEOUT=1000
                    export COMPOSE_HTTP_TIMEOUT=1000

                    export PATH=\$PATH:${GCLOUD_PATH}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud auth configure-docker --quiet

                    # Build and Push main image
                    docker build -t gcr.io/${GCP_PROJECT}/ml-telco-churn:latest .
                    docker push gcr.io/${GCP_PROJECT}/ml-telco-churn:latest

                    # Build and Push MLflow image
                    docker build -t gcr.io/${GCP_PROJECT}/mlflow-telco -f Dockerfile.mlflow .
                    docker push gcr.io/${GCP_PROJECT}/mlflow-telco
                    """
                }
            }
        }

        stage('Deploy Kubernetes Infrastructure') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    usernamePassword(
                        credentialsId: 'mlflow-credentials',
                        usernameVariable: 'MLFLOW_USERNAME',
                        passwordVariable: 'MLFLOW_PASSWORD'
                    )
                ]) {
                    sh """
                    export PATH=\$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1

                    # Create secrets
                    kubectl create secret generic gcp-key \
                        --from-file=credentials.json=${GOOGLE_APPLICATION_CREDENTIALS} \
                        --dry-run=client -o yaml | kubectl apply -f -

                    kubectl create secret generic mlflow-secrets \
                        --from-literal=username=${MLFLOW_USERNAME} \
                        --from-literal=password=${MLFLOW_PASSWORD} \
                        --dry-run=client -o yaml | kubectl apply -f -

                    # Apply manifests
                    kubectl apply -f k8s/

                    # Wait for MLflow to be available
                    kubectl wait --for=condition=available deployment/mlflow --timeout=300s
                    """
                }
            }
        }

        stage('Run Model Training') {
            steps {
                withCredentials([
                    file(credentialsId:'gcp-key', variable:'GOOGLE_APPLICATION_CREDENTIALS'),
                    usernamePassword(
                        credentialsId:'mlflow-credentials',
                        usernameVariable:'MLFLOW_USERNAME',
                        passwordVariable:'MLFLOW_PASSWORD'
                    )
                ]) {
                    echo 'Running Model Training...'
                    sh """
                    export PATH=\$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1

                    kubectl apply -f k8s/model-training-job.yaml
                    kubectl wait --for=condition=complete job/model-training-job --timeout=2800s
                    TRAINING_POD=\$(kubectl get pod -l job-name=model-training-job -o jsonpath='{.items[0].metadata.name}')
                    kubectl logs \${TRAINING_POD}
                    """
                }
            }
        }

        stage('Version Model Artifacts') {
            steps {
                withCredentials([
                    file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                    usernamePassword(
                        credentialsId: 'github-token-telco-churn',
                        usernameVariable:'GIT_USER',
                        passwordVariable:'GIT_TOKEN'
                    )
                ]) {
                    sh """
                    . ${VENV_DIR}/bin/activate
                    export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}

                    dvc add artifacts/model
                    dvc add artifacts/encoders
                    dvc add artifacts/processed
                    dvc add artifacts/data

                    git config user.email "eduardosousa.eds@gmail.com"
                    git config user.name "Eduardo Sousa"

                    git add artifacts/*.dvc
                    git commit -m "Atualização automática do modelo via Jenkins"
                    git push https://${GIT_USER}:${GIT_TOKEN}@github.com/EduardoSantosSousa/MLOPS-CHURN.git HEAD:main

                    dvc push
                    """
                }
            }
        }
    }

    post {
        always {
            sh "kubectl delete job model-training-job --ignore-not-found"
        }
        success {
            script {
                def mlflow_ip = sh(
                    script: "kubectl get svc mlflow-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'",
                    returnStdout: true
                ).trim()

                echo """
                ==============================================
                🚀 DEPLOYMENT SUCCESSFUL
                ==============================================
                MLflow Dashboard: http://${mlflow_ip}:5000
                ==============================================
                """
            }
        }
    }
}
