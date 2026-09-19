pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'registry.local:5000'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint & Unit Tests') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    PYTHONPATH=. python3 -m unittest discover -s tests -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker containers...'
                // Will be activated in Phase 9
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                echo 'Scanning container images with Trivy...'
                // Will be activated in Phase 11
            }
        }

        stage('Deploy to Staging / K8s') {
            steps {
                echo 'Deploying to Kubernetes staging namespace...'
                // Will be activated in Phase 12
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please inspect logs.'
        }
    }
}
