import joblib
import pandas as pd

# Load the saved data
feature_columns = joblib.load("feature_columns.joblib")
fragrance_features = joblib.load("fragrance_features.joblib")
df = joblib.load("fragrance_data.joblib")  # If you saved it

# Print the feature columns
print(feature_columns)

# Print the first few rows of the feature matrix
print(fragrance_features.head())

# Print the first few rows of the DataFrame (if you saved it)
print(df.head())