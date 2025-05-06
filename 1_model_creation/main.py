# Synthetic Data Generation, EDA, and Classification
# This script is designed to run in a Jupyter Notebook environment

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Set random seed for reproducibility
np.random.seed(42)

# --- Data Generation ---
# We use sklearn's make_classification to create a synthetic dataset with 3 classes,
# 10 features (8 informative), and 5000 samples. This ensures a complex but learnable dataset.
X, y = make_classification(n_samples=5000, n_features=10, n_informative=8, n_redundant=2,
                          n_classes=3, n_clusters_per_class=2, random_state=42)

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(1, 11)])
df['target'] = y

# Display first few rows
print("First 5 rows of the dataset:")
print(df.head())

# --- Exploratory Data Analysis (EDA) ---
# 1. Check dataset shape and basic info
print("\nDataset Shape:", df.shape)
print("\nDataset Info:")
print(df.info())

# 2. Check for missing values
print("\nMissing Values:")
print(df.isnull().sum())

# 3. Class distribution
plt.figure(figsize=(8, 6))
sns.countplot(x='target', data=df)
plt.title('Class Distribution')
plt.xlabel('Target Class')
plt.ylabel('Count')
plt.savefig('class_distribution.png')
plt.close()

# 4. Feature distributions
plt.figure(figsize=(15, 10))
for i, col in enumerate(df.columns[:-1], 1):
    plt.subplot(4, 3, i)
    sns.histplot(df[col], kde=True)
    plt.title(f'Distribution of {col}')
plt.tight_layout()
plt.savefig('feature_distributions.png')
plt.close()

# 5. Correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix')
plt.savefig('correlation_matrix.png')
plt.close()

# --- Data Preprocessing ---
# Split features and target
X = df.drop('target', axis=1)
y = df['target']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# --- Model Training ---
# Random Forest Classifier is chosen for its robustness and ability to handle complex data
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- Model Evaluation ---
# Predictions
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("\nModel Accuracy:", accuracy)

# Classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.savefig('confusion_matrix.png')
plt.close()

# --- Save the Model ---
# Save the trained model to a .pkl file
joblib.dump(model, 'random_forest_model.pkl')
print("\nModel saved as 'random_forest_model.pkl'")

# --- Explanation ---
# 1. Data Generation: We created a synthetic dataset with 5000 samples, 10 features, and 3 classes.
#    The data is complex but designed to be learnable, ensuring good model performance.
# 2. EDA: We checked the dataset's structure, confirmed no missing values, visualized class balance,
#    feature distributions, and correlations to understand the data.
# 3. Preprocessing: Split the data into training (80%) and testing (20%) sets, maintaining class proportions.
# 4. Model: A Random Forest Classifier was trained, which typically yields high accuracy on such data.
# 5. Evaluation: The model achieves high accuracy (expected >90%) due to the synthetic data's structure.
#    The classification report and confusion matrix provide detailed performance insights.
# 6. Model Saving: The trained model is saved as a .pkl file for future use.

# To load and use the model later:
# loaded_model = joblib.load('random_forest_model.pkl')
# predictions = loaded_model.predict(new_data)