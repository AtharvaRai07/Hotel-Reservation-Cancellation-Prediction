pipeline{
    agent any

    enviroment{
        VENV_DIR = "venv"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github token', url: 'https://github.com/AtharvaRai07/Hotel-Reservation-Cancellation-Prediction.git']])
                }
            }
        }
    }

    stages{
        stage('Setting up our Virtual Enviroment and Installing dependencies'){
            steps{
                script{
                    echo 'Setting up our Virtual Enviroment and Installing dependencies...'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
            }
        }
    }
}

