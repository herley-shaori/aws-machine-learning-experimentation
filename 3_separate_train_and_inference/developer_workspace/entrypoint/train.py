# sagemaker_dev/entrypoint/train.py

import os
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train(train_dir, model_dir):
    csv_path = os.path.join(train_dir, 'train.csv')
    logger.info(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    logger.info("Training LinearRegression model")
    model = LinearRegression()
    model.fit(X, y)

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")

if __name__ == "__main__":
    # SageMaker mounts channel 'train' at /opt/ml/input/data/train
    train_dir = os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train')
    model_dir = os.environ.get('SM_MODEL_DIR',     '/opt/ml/model')
    train(train_dir, model_dir)
