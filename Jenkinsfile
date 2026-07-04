pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Testes') {
            steps {
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt'
                bat 'venv\\Scripts\\python -m pytest'
            }
        }

        stage('Build da imagem Docker') {
            steps {
                bat 'docker build -t trampohub-api:homolog .'
            }
        }

        stage('Deploy Homologação') {
            steps {
                bat 'docker compose -p trampohub-homolog -f docker-compose.homolog.yml down'
                bat 'docker compose -p trampohub-homolog -f docker-compose.homolog.yml up -d'
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