import json
import os
import joblib
import numpy as np
import pandas as pd


def model_fn(model_dir):
    """
    Load the model from the model directory.

    Args:
        model_dir (str): Directory where the model artifacts are stored.

    Returns:
        model: Loaded scikit-learn model.
    """
    model_path = os.path.join(model_dir, 'random_forest_model.pkl')
    model = joblib.load(model_path)
    return model


def input_fn(request_body, request_content_type):
    """
    Deserialize the input data.

    Args:
        request_body (str): The raw request data.
        request_content_type (str): The content type of the request.

    Returns:
        data: Parsed input data as a numpy array.

    Raises:
        ValueError: If the content type is not 'application/json'.
    """
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        # Expect input_data to be a list of feature vectors (e.g., [[f1, f2, ..., f10], ...])
        data = np.array(input_data)
        return data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data, model):
    """
    Perform inference using the loaded model.

    Args:
        input_data (numpy.ndarray): Input data for prediction.
        model: Loaded scikit-learn model.

    Returns:
        predictions: Array of predicted class labels.
    """
    # Convert to DataFrame to ensure correct feature order
    data_df = pd.DataFrame(input_data, columns=[f'feature_{i}' for i in range(1, 11)])
    predictions = model.predict(data_df)
    return predictions


def output_fn(prediction, accept):
    """
    Serialize the prediction output.

    Args:
        prediction (numpy.ndarray): The model predictions.
        accept (str): The desired response content type.

    Returns:
        dict: Serialized predictions in JSON format.

    Raises:
        ValueError: If the accept type is not 'application/json'.
    """
    if accept == 'application/json':
        return json.dumps(prediction.tolist())
    else:
        raise ValueError(f"Unsupported accept type: {accept}")