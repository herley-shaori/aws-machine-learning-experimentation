from flask import Flask, request, jsonify
import pandas as pd
import joblib
import numpy as np
import logging

# Configure logging for debugging in CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load the trained model from /opt/ml/model/
model_path = "random_forest_model.pkl"

try:
    model = joblib.load(model_path)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

def perform_inference(data):
    """
    Perform inference using the loaded model.

    Parameters:
    data: pandas DataFrame or numpy array with 10 features in the same order as training data

    Returns:
    predictions: array of predicted class labels
    """
    # Ensure input is a DataFrame
    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data, columns=[f'feature_{i}' for i in range(1, 11)])

    # Perform prediction
    predictions = model.predict(data)
    return predictions

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint for SageMaker."""
    if model is None:
        return jsonify({"status": "Unhealthy", "error": "Model not loaded"}), 500
    return jsonify({"status": "Healthy"}), 200

@app.route("/invocations", methods=["POST"])
def invocations():
    """Inference endpoint for SageMaker."""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get JSON input
        data = request.get_json()
        logger.info(f"Received input: {data}")

        # Expect input as a list of samples, e.g., [[1, 2, ..., 10], [1, 2, ..., 10]]
        if not isinstance(data, list):
            return jsonify({"error": "Input must be a list of samples"}), 400

        # Convert to numpy array and then DataFrame
        input_data = np.array(data)
        if input_data.shape[1] != 10:
            return jsonify({"error": "Each sample must have 10 features"}), 400

        input_df = pd.DataFrame(input_data, columns=[f'feature_{i}' for i in range(1, 11)])

        # Perform inference
        predictions = perform_inference(input_df)
        logger.info(f"Predictions: {predictions}")

        # Return predictions as JSON
        return jsonify({"predictions": predictions.tolist()}), 200
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)