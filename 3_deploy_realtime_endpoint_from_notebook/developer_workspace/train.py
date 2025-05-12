import argparse
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import logging
import os
import json
import numpy as np
from flask import Flask, Response

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app untuk menangani /ping
app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    """
    Health check endpoint for SageMaker.
    Returns HTTP 200 if the container is healthy.
    """
    logger.info("Received /ping request")
    # Tambahan pengecekan kesehatan (opsional)
    model_path = '/opt/ml/model/model.joblib'
    if os.path.exists(model_path):
        return Response(status=200)
    else:
        logger.error("Model file not found")
        return Response(status=500)

def model_fn(model_dir):
    logger.info(f"Loading model from {model_dir}/model.joblib")
    model_path = f"{model_dir}/model.joblib"
    try:
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise Exception(f"Model loading failed: {str(e)}")

def input_fn(request_body, content_type='application/json'):
    logger.info(f"Processing input with content_type: {content_type}")
    if content_type == 'application/json':
        input_data = json.loads(request_body)
        return np.array(input_data)
    elif content_type == 'text/csv':
        return np.array(pd.read_csv(request_body, header=None))
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    logger.info("Making predictions")
    predictions = model.predict(input_data)
    return predictions

def output_fn(prediction, accept='application/json'):
    logger.info(f"Serializing output with accept: {accept}")
    if accept == 'application/json':
        return json.dumps(prediction.tolist())
    else:
        raise ValueError(f"Unsupported accept type: {accept}")

if __name__ == '__main__':
    # Cek apakah dijalankan untuk training atau serving
    sm_channels = json.loads(os.environ.get('SM_CHANNELS', '[]'))
    print('SM_CHANNELS',sm_channels)
    if 'train' not in sm_channels:
        logger.error("Channel 'train' not found in SM_CHANNELS")
        # Mode serving (inference)
        logger.info("Starting Flask server for inference")
        app.run(host='0.0.0.0', port=8080)
    else:
        # Mode training
        parser = argparse.ArgumentParser()
        parser.add_argument('--train', type=str, default='/opt/ml/input/data/train')
        parser.add_argument('--model-dir', type=str, default='/opt/ml/model')
        args = parser.parse_args()

        logger.info(f"Loading data from {args.train}/train.csv")
        data = pd.read_csv(f'{args.train}/train.csv')
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]

        logger.info("Training model...")
        model = LinearRegression()
        model.fit(X, y)

        model_path = f'{args.model_dir}/model.joblib'
        logger.info(f"Saving model to {model_path}")
        joblib.dump(model, model_path)

        if os.path.exists(model_path):
            logger.info(f"Model successfully saved at {model_path}")
        else:
            logger.error(f"Failed to save model at {model_path}")