import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib

# --- Data Loading and Preprocessing ---
df = pd.read_csv("modified_fra_cleaned.csv", delimiter=";")  # Update with your CSV filename and delimiter
df.columns = ['Fragrance Name', 'Brand', 'Gender', 'Top Notes', 'Middle Notes', 'Base Notes', 'Scent Family']

# Convert to lowercase
for col in ['Brand', 'Top Notes', 'Middle Notes', 'Base Notes', 'Scent Family']:
    df[col] = df[col].str.lower()

# Split notes and scent families into lists
for col in ['Top Notes', 'Middle Notes', 'Base Notes', 'Scent Family']:
    df[col] = df[col].str.split(',')

# Combine notes into 'All Notes'
df['All Notes'] = df['Top Notes'] + df['Middle Notes'] + df['Base Notes']

# --- Feature Engineering ---
# One-hot encode All Notes
mlb = MultiLabelBinarizer()
all_notes_encoded = pd.DataFrame(mlb.fit_transform(df['All Notes']), columns=["note_" + c for c in mlb.classes_], index=df.index)
df = df.join(all_notes_encoded)

# One-hot encode Scent Family
scent_family_encoded = pd.DataFrame(mlb.fit_transform(df['Scent Family']), columns=["family_" + c for c in mlb.classes_], index=df.index)
df = df.join(scent_family_encoded)

# Encode Gender
label_encoder = LabelEncoder()
df['Gender'] = label_encoder.fit_transform(df['Gender'])

# Drop unnecessary columns
df = df.drop(['Top Notes', 'Middle Notes', 'Base Notes', 'All Notes', 'Scent Family'], axis=1)

# --- Create Feature Matrix ---
feature_columns = [col for col in df.columns if col not in ['Fragrance Name', 'Brand']]
fragrance_features = df[feature_columns]

# --- Calculate Similarity Matrix ---
similarity_matrix = cosine_similarity(fragrance_features)

# --- Save Model Data ---
joblib.dump(similarity_matrix, "similarity_matrix.joblib")
joblib.dump(feature_columns, "feature_columns.joblib")
joblib.dump(fragrance_features, "fragrance_features.joblib")
joblib.dump(df, "fragrance_data.joblib")  # Optional
joblib.dump(label_encoder, "label_encoder.joblib")  # Optional

print("Model training complete. Data saved.")