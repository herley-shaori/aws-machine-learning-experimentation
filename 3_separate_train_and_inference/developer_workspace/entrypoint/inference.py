# sagemaker_dev/entrypoint/inference.py

import os
import json
import joblib
import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def model_fn(model_dir):
    """Load the trained model from model_dir/model.joblib."""
    path = os.path.join(model_dir, 'model.joblib')
    logger.info(f"Loading model from {path}")
    model = joblib.load(path)
    return model

def input_fn(request_body, content_type='application/json'):
    """Deserialize input into a NumPy array."""
    logger.info(f"Deserializing input; Content-Type={content_type}")
    if content_type == 'application/json':
        data = np.array(json.loads(request_body))
    elif content_type == 'text/csv':
        df = pd.read_csv(request_body, header=None)
        data = df.values
    else:
        raise ValueError(f"Unsupported content type: {content_type}")
    return data

def predict_fn(input_data, model):
    """Make predictions."""
    logger.info("Running model.predict")
    return model.predict(input_data)

def output_fn(prediction, accept='application/json'):
    """Serialize prediction output."""
    logger.info(f"Serializing output; Accept={accept}")
    if accept == 'application/json':
        return json.dumps(prediction.tolist()), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")