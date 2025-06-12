pipeline {
    agent any

    stages{
        stage("Cloning from Github......"){
            steps{
                scripts{
                    echo 'Cloning from Github......'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token-telco-churn', url: 'https://github.com/EduardoSantosSousa/MLOPS-CHURN.git']])
                }
            }
        }

    }
}