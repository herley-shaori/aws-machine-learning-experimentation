# Use Python 3.13 slim base image
FROM python:3.13-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
COPY random_forest_model.pkl .
COPY inference.py .

RUN pip install --no-cache-dir -r requirements.txt

# Expose SageMaker's default port
EXPOSE 8080

# Run the inference server with gunicorn
ENTRYPOINT ["python","inference.py"]