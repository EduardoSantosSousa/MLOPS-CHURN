pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'serious-cat-455501-d2'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "usr/lib/google-cloud-sdk/bin"
        DOCKER_CLI_EXPERIMENTAL = 'enabled'
        DOCKER_BUILDKIT = '1'
        DOCKER_TIMEOUT = '800'  // 10 minutos

    }

    stages {
        stage("Cloning from Github......") {
            steps {
                script {
                    echo 'Cloning from Github......'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'github-token-telco-churn',
                            url: 'https://github.com/EduardoSantosSousa/MLOPS-CHURN.git'
                        ]]
                    )
                }
            }
        }

        stage("Making a virtual enviroment......") {
            steps {
                script {
                    echo 'Making a virtual enviroment......'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                }
            }
        }

        stage('DVC Pull') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'DVC Pull........'
                         sh """
                            # ativa o virtualenv
                            . ${VENV_DIR}/bin/activate
                            dvc pull
                        """
                    }
                }
            }
        }

        stage('Build and Push Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Build and Push Image to GCR............'
                        sh """
                        export DOCKER_CLI_EXPERIMENTAL=enabled
                        export DOCKER_BUILDKIT=1

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker  --quiet
                       
                        docker build -t gcr.io/${GCP_PROJECT}/ml-telco-churn:latest .
                        docker push gcr.io/${GCP_PROJECT}/ml-telco-churn:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to GKE') {
            steps {withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                script {
                      echo 'Deploy to GKE'
                      sh """
                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1

                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        
                       
                        kubectl apply -f k8s/prometheus-configmap.yaml
                        kubectl apply -f k8s/prometheus-deployment.yaml
                        kubectl apply -f k8s/prometheus-service.yaml

                        kubectl apply -f k8s/grafana-deployment.yaml
                        kubectl apply -f k8s/grafana-service.yaml
                        """
                    }
                }
            }
        }

       stage('Run Training Job') {
            steps {withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                script {
                    echo 'Starting Model Training...'
                    sh '''#!/bin/bash
                        export PATH=$PATH:'${GCLOUD_PATH}':'${KUBECTL_AUTH_PLUGIN}'
                        gcloud auth activate-service-account --key-file='${GOOGLE_APPLICATION_CREDENTIALS}'
                        gcloud config set project '${GCP_PROJECT}'
                        gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1
                    
                        # Aplica os manifestos do PostgreSQL
                        kubectl apply -f k8s/postgres.yaml
                    
                        # Espera o PostgreSQL ficar pronto
                        kubectl rollout status deployment/postgres --timeout=300s
                    
                        # Executa o job de treinamento
                        kubectl delete job ml-training-job --ignore-not-found
                        kubectl apply -f k8s/training-job.yaml
                    
                        # Monitora o completion do job
                        kubectl wait --for=condition=complete --timeout=1800s job/ml-training-job
                    
                        # Captura logs para debug
                        kubectl logs job/ml-training-job --all-containers=true --tail=50
                    '''
            }
        }
    }
}


        
    }
}