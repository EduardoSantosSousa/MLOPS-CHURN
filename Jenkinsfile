pipeline {
    agent any

    environment{
        VENV_DIR = 'venv'
    }

    stages{
        stage("Cloning from Github......"){
            steps{
                script{
                    echo 'Cloning from Github......'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token-telco-churn', url: 'https://github.com/EduardoSantosSousa/MLOPS-CHURN.git']])
                }
            }
        }

    }

    stages{
        stage("Making a virtual enviroment......"){
            steps{
                script{
                    echo 'Making a virtual enviroment......'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install  --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                    
                }
            }
        }

        stage('DVC Pull'){
            steps{
                withCredentials([file(credentialsId: 'gco-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'DVC Pull........'
                        sh'''
                        . ${VENV_DIR}/bin/activate
                        dvc pull
                        '''
                    }
                }
            }
        }

    }
}