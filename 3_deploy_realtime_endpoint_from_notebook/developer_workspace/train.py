import argparse
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, default='/opt/ml/input/data/train')
    parser.add_argument('--model-dir', type=str, default='/opt/ml/model')
    args = parser.parse_args()

    logger.info(f"Loading data from {args.train}/train.csv")
    # Load data
    data = pd.read_csv(f'{args.train}/train.csv')
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    logger.info("Training model...")
    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Save model
    model_path = f'{args.model_dir}/model.joblib'
    logger.info(f"Saving model to {model_path}")
    joblib.dump(model, model_path)

    # Verify model file exists
    if os.path.exists(model_path):
        logger.info(f"Model successfully saved at {model_path}")
    else:
        logger.error(f"Failed to save model at {model_path}")
        raise Exception("Model saving failed")