pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Testes') {
            agent {
                docker {
                    image 'python:3.14-slim'
                    args '-u root'
                }
            }
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt'
                sh 'python -m pytest'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=trampohub-api -Dsonar.sources=."
                    }
                }
            }
        }

        stage('Build da imagem Docker') {
            steps {
                sh 'docker build -t trampohub-api:homolog .'
            }
        }

        stage('Deploy Homologação') {
            steps {
                sh 'docker compose --project-name trampohub-homolog -f docker-compose.homolog.yml down'
                sh 'docker compose --project-name trampohub-homolog -f docker-compose.homolog.yml up -d'
            }
        }
    }

    post {
        success {
            echo 'Pipeline executado com sucesso! Ambiente de homologação atualizado.'
        }
        failure {
            echo 'Pipeline falhou. Verifique os logs acima.'
        }
    }
}