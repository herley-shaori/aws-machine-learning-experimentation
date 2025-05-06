import pandas as pd
import joblib
import numpy as np

# Load the trained model
model = joblib.load('random_forest_model.pkl')


# Function to perform inference
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


# Example usage
if __name__ == "__main__":
    # Create sample data for inference (replace with your actual data)
    sample_data = np.random.randn(5, 10)  # 5 samples, 10 features
    sample_df = pd.DataFrame(sample_data, columns=[f'feature_{i}' for i in range(1, 11)])

    # Perform inference
    predictions = perform_inference(sample_df)

    # Print results
    print("Sample Data:")
    print(sample_df)
    print("\nPredictions:", predictions)