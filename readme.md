# AWS Machine Learning Experimentation 🚀

I leverage multiple AWS services to streamline machine learning experimentation, ensuring a robust and scalable workflow. Below is a refined overview of the process, organized into three key phases: model creation, model deployment, and the separation of training and serving logic.

## 1. Model Creation 🛠️
I developed a lightweight machine learning model and validated its performance locally. To containerize the model, I encapsulated it within a Docker image using a `Dockerfile`, followed by local testing to ensure functionality. For automated builds, I integrated AWS CodeBuild, utilizing a `buildspec.yml` configuration file. The finalized model artifacts were archived into `model_creation.zip` and securely uploaded to an Amazon S3 bucket for storage and accessibility.

## 2. Model Deployment 🌐
To support deployment, I provisioned a Virtual Private Cloud (VPC) with public subnets across two Availability Zones (AZs) for high availability, alongside an Amazon Elastic Container Registry (ECR) repository. AWS CodeBuild automates the building of the Docker image, which is then pushed to ECR. For real-time inference, I deployed an Amazon SageMaker real-time endpoint, configured to pull the containerized model from ECR. The endpoint’s functionality was rigorously tested using the `aws_endpoint_test.sh` script to ensure seamless operation.

## 3. Separate Training and Serving Scripts 📂
By isolating the training workflow in `train.py` from the inference logic in `inference.py`, we achieve clear ownership of each phase: SageMaker channels handle data ingestion and model artifacts during training, while the serving script focuses solely on model loading, input parsing, prediction, and output serialization. This separation enhances code maintainability, simplifies debugging, and allows independent updates or scaling of the training and inference components without impacting each other.
