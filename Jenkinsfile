pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "encoded-joy-418604"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github token', url: 'https://github.com/AtharvaRai07/Hotel-Reservation-Cancellation-Prediction.git']])
                }
            }
        }

        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Install GCloud SDK'){
            steps{
                script{
                    echo 'Installing Google Cloud SDK............'
                    sh '''
                    if [ ! -d "$HOME/google-cloud-sdk" ]; then
                        curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
                        tar -xf google-cloud-cli-linux-x86_64.tar.gz -C $HOME
                        $HOME/google-cloud-sdk/install.sh --quiet --usage-reporting=false --path-update=true
                        rm google-cloud-cli-linux-x86_64.tar.gz
                    fi
                    export PATH=$HOME/google-cloud-sdk/bin:$PATH
                    gcloud version
                    '''
                }
            }
        }


        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        export PATH=$HOME/google-cloud-sdk/bin:$PATH

                        gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"

                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .

                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploying to Cloud Run.............'
                        sh '''
                        export PATH=$HOME/google-cloud-sdk/bin:$PATH

                        gcloud auth activate-service-account --key-file="${GOOGLE_APPLICATION_CREDENTIALS}"

                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ml-project \
                            --image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                            --platform=managed \
                            --region=us-central1 \
                            --allow-unauthenticated
                        '''
                    }
                }
            }
        }
    }
}

