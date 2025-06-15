pipeline {
    agent any

    environment {
        VENV_DIR          = 'venv'
        GCP_PROJECT       = 'serious-cat-455501-d2'
        GCLOUD_PATH       = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
        DOCKER_BUILDKIT   = '1'
    }

    stages {
        stage("Cloning from GitHub") {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[ name: '*/main' ]],
                    userRemoteConfigs: [[
                        credentialsId: 'github-token-telco-churn',
                        url: 'https://github.com/EduardoSantosSousa/MLOPS-CHURN.git'
                    ]]
                ])
            }
        }

        stage("Setup Environment") {
            steps {
                sh """
                python -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip setuptools wheel
                pip install -e .
                pip install dvc google-cloud-storage mlflow prometheus-client
                """
            }
        }

        stage("Validate GCP Credentials") {
            steps {
                withCredentials([ file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS') ]) {
                    sh """
                    . ${VENV_DIR}/bin/activate
                    python -c "from google.cloud import storage; storage.Client()"
                    echo "✅ GCP Credentials Validated"
                    """
                }
            }
        }

        stage('DVC Pull') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    withCredentials([ file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS') ]) {
                        sh """
                        . ${VENV_DIR}/bin/activate
                        export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
                        dvc pull
                        """
                    }
                }
            }
        }

        stage('Build & Push Images') {
            steps {
                withCredentials([ file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS') ]) {
                    sh """
                    set -e
                    export DOCKER_CLI_EXPERIMENTAL=enabled
                    export DOCKER_BUILDKIT=1

                    export PATH=\$PATH:${GCLOUD_PATH}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud auth configure-docker --quiet

                    docker build -t gcr.io/${GCP_PROJECT}/ml-telco-churn:latest .
                    docker push gcr.io/${GCP_PROJECT}/ml-telco-churn:latest

                    docker build -t gcr.io/${GCP_PROJECT}/mlflow-telco -f Dockerfile.mlflow .
                    docker push gcr.io/${GCP_PROJECT}/mlflow-telco
                    """
                }
            }
        }

        stage('Deploy Kubernetes Infra') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                    set -e
                    export PATH=\$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1

                    kubectl apply -f k8s/

                    # Espera os deployments estarem disponíveis
                    sleep 10
                    
                    # Verifica e espera pelos rollouts
                    for deployment in mlflow churn-app prometheus grafana; do
                      if kubectl get deployment \$deployment > /dev/null; then
                        echo "🚀 Checking rollout status for \$deployment"
                        kubectl rollout status deployment/\$deployment --timeout=300s
                      else
                        echo "⚠️ Deployment \$deployment not found!"
                      fi
                    done
                    """
                }
            }
        }

        stage('Run Model Training') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        withCredentials([ file(credentialsId:'gcp-key', variable:'GOOGLE_APPLICATION_CREDENTIALS') ]) {
                            echo '🚀 Starting Model Training…'
                            
                            // Executa o Job de treinamento
                            sh """
                            set -e
                            export PATH=\$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}
                            gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1

                            kubectl apply -f k8s/model-training-job.yaml
                            """
                            
                            // Espera a conclusão com timeout
                            def status = sh(
                                script: "kubectl wait --for=condition=complete job/model-training-job --timeout=1800s",
                                returnStatus: true
                            )
                            
                            // Busca e exibe logs
                            def pod = sh(
                                script: "kubectl get pod -l job-name=model-training-job -o jsonpath='{.items[0].metadata.name}'",
                                returnStdout: true
                            ).trim()
                            
                            echo "=== 📝 Logs do pod ${pod} ==="
                            sh "kubectl logs ${pod} --tail=100"
                            
                            if (status != 0) {
                                error("❌ Job de treinamento falhou")
                            } else {
                                echo "✅ Training completed successfully"
                            }
                        }
                    }
                }
            }
        }

        stage('Version Model Artifacts') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    withCredentials([
                        file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                        usernamePassword(
                            credentialsId: 'github-token-telco-churn',
                            usernameVariable: 'GIT_USER',
                            passwordVariable: 'GIT_TOKEN'
                        )
                    ]) {
                        sh """
                        set -e
                        . ${VENV_DIR}/bin/activate
                        export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}

                        # Verifica se há mudanças nos artefatos
                        dvc add artifacts/model artifacts/encoders artifacts/processed artifacts/data
                        
                        if git diff --quiet -- artifacts; then
                            echo "🤷 No changes in artifacts"
                        else
                            echo "💾 Versioning new artifacts"
                            git config user.email "eduardosousa.eds@gmail.com"
                            git config user.name "Eduardo Sousa"
                            git add artifacts/*.dvc
                            git commit -m "Auto-update model artifacts [ci skip]"
                            git push https://${GIT_USER}:${GIT_TOKEN}@github.com/EduardoSantosSousa/MLOPS-CHURN.git HEAD:main
                            dvc push
                        fi
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                    set +e
                    export PATH=\$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1
                    
                    # Limpeza segura
                    kubectl delete job model-training-job --ignore-not-found
                    """
                }
            }
        }
        success {
            script {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                    export PATH=\$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ml-telco-churn-cluster --region us-central1
                    """
                    
                    // Verifica o MLflow de forma mais robusta
                    def mlflowSvc = sh(
                        script: """
                        kubectl get svc mlflow-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || 
                        kubectl get svc mlflow-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' || 
                        echo "not-available"
                        """,
                        returnStdout: true
                    ).trim()
                    
                    if (mlflowSvc != "not-available") {
                        echo "🚀 MLflow UI: http://${mlflowSvc}:5000"
                    }
                    
                    // Verifica o Grafana
                    def grafanaSvc = sh(
                        script: """
                        kubectl get svc grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || 
                        kubectl get svc grafana -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' || 
                        echo "not-available"
                        """,
                        returnStdout: true
                    ).trim()
                    
                    if (grafanaSvc != "not-available") {
                        echo "📊 Grafana Dashboard: http://${grafanaSvc}:3000"
                    }
                }
            }
        }
    }
}
