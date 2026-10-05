// Build, test, version and publish both services, then deploy with Ansible.
// Required Jenkins config: credentials 'gcp-sa-key' (secret file), env ARTIFACT_BUCKET, GCP_PROJECT.
pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    timeout(time: 45, unit: 'MINUTES')
  }

  environment {
    ARTIFACT_BUCKET = "${env.ARTIFACT_BUCKET ?: 'order-platform-artifacts'}"
    GCP_SA_FILE     = credentials('gcp-sa-key')
  }

  stages {
    stage('Version') {
      steps {
        script {
          // Plain X.Y.Z so it is valid for Maven, PEP 440 and GCS object names.
          env.APP_VERSION = "1.0.${env.BUILD_NUMBER}"
          echo "Version: ${env.APP_VERSION} (commit ${env.GIT_COMMIT})"
        }
      }
    }

    stage('Build & test') {
      parallel {
        stage('order-service (Java)') {
          steps {
            dir('services/order-service') {
              sh "mvn -B -Drevision=${env.APP_VERSION} clean verify"
            }
          }
          post {
            always { junit 'services/order-service/target/surefire-reports/*.xml' }
          }
        }
        stage('notification-service (Python)') {
          steps {
            dir('services/notification-service') {
              sh '''
                python3 -m venv .venv
                . .venv/bin/activate
                pip install -r requirements.txt build
                pytest --junitxml=pytest-report.xml
              '''
              sh """
                . .venv/bin/activate
                sed -i 's/^version = .*/version = "${env.APP_VERSION}"/' pyproject.toml
                python -m build --wheel
              """
            }
          }
          post {
            always { junit 'services/notification-service/pytest-report.xml' }
          }
        }
      }
    }

    stage('Publish artifacts') {
      steps {
        sh '''
          gcloud auth activate-service-account --key-file="$GCP_SA_FILE"
          gcloud storage cp services/order-service/target/order-service-${APP_VERSION}.jar \
            gs://${ARTIFACT_BUCKET}/order-service/order-service-${APP_VERSION}.jar
          gcloud storage cp services/notification-service/dist/*.whl \
            gs://${ARTIFACT_BUCKET}/notification-service/
        '''
        archiveArtifacts artifacts: 'services/order-service/target/*.jar, services/notification-service/dist/*.whl',
                         fingerprint: true
      }
    }

    stage('Deploy') {
      when { branch 'main' }
      steps {
        sh '''
          cd ansible
          ansible-galaxy collection install -r requirements.yml
          ansible-playbook playbooks/deploy.yml -e app_version="${APP_VERSION}"
        '''
      }
    }
  }

  post {
    success { echo "Deployed ${env.APP_VERSION}" }
    failure { echo 'Pipeline failed; see stage logs. Failed deploys roll back automatically per host.' }
    cleanup { cleanWs() }
  }
}
