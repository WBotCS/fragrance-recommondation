import os
import boto3
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from sklearn.metrics.pairwise import cosine_similarity
import threading

app = Flask(__name__)

# S3 Configuration
S3_BUCKET = 'mymodelfragbucket'
MODEL_FILES = {
    'feature_columns': 'feature_columns.joblib',
    'fragrance_data': 'fragrance_data.joblib',
    'fragrance_features': 'fragrance_features.joblib',
    'label_encoder': 'label_encoder.joblib',
    'similarity_matrix': 'similarity_matrix.joblib'
}
LOCAL_MODEL_PATH = 'models/'  # Local directory to save the model files

# Initialize model variables
similarity_matrix = None
feature_columns = None
fragrance_features = None
df = None
label_encoder = None

def download_and_load_models():
    """Downloads and loads models asynchronously."""
    global similarity_matrix, feature_columns, fragrance_features, df, label_encoder

    s3 = boto3.client('s3')
    if not os.path.exists(LOCAL_MODEL_PATH):
        os.makedirs(LOCAL_MODEL_PATH)

    # Download model files from S3 if they don't already exist locally
    for file_name, s3_key in MODEL_FILES.items():
        local_file_path = os.path.join(LOCAL_MODEL_PATH, f"{file_name}.joblib")
        if not os.path.exists(local_file_path):
            print(f"Downloading {file_name} from S3...")
            s3.download_file(S3_BUCKET, s3_key, local_file_path)
            print(f"{file_name} downloaded successfully.")
    
    # Load models after download
    similarity_matrix = joblib.load(os.path.join(LOCAL_MODEL_PATH, "similarity_matrix.joblib"))
    feature_columns = joblib.load(os.path.join(LOCAL_MODEL_PATH, "feature_columns.joblib"))
    fragrance_features = joblib.load(os.path.join(LOCAL_MODEL_PATH, "fragrance_features.joblib"))
    df = joblib.load(os.path.join(LOCAL_MODEL_PATH, "fragrance_data.joblib"))
    label_encoder = joblib.load(os.path.join(LOCAL_MODEL_PATH, "label_encoder.joblib"))
    print("Models loaded successfully.")

# Start background model loading
threading.Thread(target=download_and_load_models).start()

def get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features, top_n=5):
    """Generates fragrance recommendations based on user preferences."""
    user_similarity = cosine_similarity(user_preferences.reshape(1, -1), fragrance_features)
    sorted_indices = np.argsort(user_similarity[0])[::-1]
    
    filtered_indices = [index for index in sorted_indices 
                        if disliked_notes_indices is None or 
                        not any(fragrance_features.iloc[index][note] for note in disliked_notes_indices)]

    if not filtered_indices:
        return pd.DataFrame(columns=['Fragrance Name', 'Brand'])

    return df.iloc[filtered_indices[:top_n]][['Fragrance Name', 'Brand']]

@app.route('/')
def index():
    return render_template('index.html', feature_columns=feature_columns)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.get_json()
    user_preferences = np.zeros(len(feature_columns))

    # Handle Gender
    user_preferences[feature_columns.index('Gender')] = int(user_input['gender'])

    # Handle preferred notes and families
    for note in user_input.get('preferred_notes', []):
        note_with_prefix = "note_" + note.lower()
        if note_with_prefix in feature_columns:
            user_preferences[feature_columns.index(note_with_prefix)] = 1

    for family in user_input.get('preferred_families', []):
        family_with_prefix = "family_" + family.lower()
        if family_with_prefix in feature_columns:
            user_preferences[feature_columns.index(family_with_prefix)] = 1

    # Handle disliked notes
    disliked_notes_indices = [feature_columns.index("note_" + note.lower()) 
                              for note in user_input.get('disliked_notes', []) 
                              if "note_" + note.lower() in feature_columns]

    # Get recommendations
    recommendations = get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features)
    return jsonify(recommendations.to_dict(orient='records'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
