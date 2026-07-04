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
                sh 'python3 -m venv venv'
                sh './venv/bin/pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt'
                sh './venv/bin/python -m pytest'
            }
        }

        stage('Build da imagem Docker') {
            steps {
                sh 'docker build -t trampohub-api:homolog .'
            }
        }

        stage('Deploy Homologação') {
            steps {
                sh 'docker compose -p trampohub-homolog -f docker-compose.homolog.yml down'
                sh 'docker compose -p trampohub-homolog -f docker-compose.homolog.yml up -d'
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