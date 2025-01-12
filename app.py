import os
import boto3
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from sklearn.metrics.pairwise import cosine_similarity

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
LOCAL_MODEL_PATH = 'models/'

# Download model files from S3
def download_model_files():
    s3 = boto3.client('s3')
    os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
    
    for file_name, s3_key in MODEL_FILES.items():
        local_file_path = os.path.join(LOCAL_MODEL_PATH, f"{file_name}.joblib")
        if not os.path.exists(local_file_path):
            s3.download_file(S3_BUCKET, s3_key, local_file_path)

# Load models
download_model_files()
similarity_matrix = joblib.load(os.path.join(LOCAL_MODEL_PATH, "similarity_matrix.joblib"))
feature_columns = joblib.load(os.path.join(LOCAL_MODEL_PATH, "feature_columns.joblib"))
fragrance_features = joblib.load(os.path.join(LOCAL_MODEL_PATH, "fragrance_features.joblib"))
df = joblib.load(os.path.join(LOCAL_MODEL_PATH, "fragrance_data.joblib"))
label_encoder = joblib.load(os.path.join(LOCAL_MODEL_PATH, "label_encoder.joblib"))

@app.route('/')
def index():
    return render_template('index.html', feature_columns=feature_columns)

@app.route('/select2-data')
def select2_data():
    notes_data = [{'id': feature[5:], 'text': feature[5:]} for feature in feature_columns if feature.startswith('note_')]
    families_data = [{'id': feature[7:], 'text': feature[7:]} for feature in feature_columns if feature.startswith('family_')]
    return jsonify({'notes': notes_data, 'families': families_data})

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.get_json()
        user_preferences = np.zeros(len(feature_columns))

        # Handle gender, notes, and families
        user_preferences[feature_columns.index('Gender')] = int(user_input['gender'])
        for note in user_input['preferred_notes']:
            if f"note_{note.lower()}" in feature_columns:
                user_preferences[feature_columns.index(f"note_{note.lower()}")] = 1
        for family in user_input['preferred_families']:
            if f"family_{family.lower()}" in feature_columns:
                user_preferences[feature_columns.index(f"family_{family.lower()}")] = 1

        disliked_notes_indices = [
            feature_columns.index(f"note_{note.lower()}") 
            for note in user_input.get('disliked_notes', []) 
            if f"note_{note.lower()}" in feature_columns
        ]

        recommendations = get_recommendations(user_preferences, disliked_notes_indices)
        return jsonify(recommendations.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_recommendations(user_preferences, disliked_notes_indices, top_n=5):
    user_similarity = cosine_similarity(user_preferences.reshape(1, -1), fragrance_features)
    sorted_indices = np.argsort(user_similarity[0])[::-1]

    filtered_indices = [
        idx for idx in sorted_indices 
        if all(fragrance_features.iloc[idx][di] == 0 for di in disliked_notes_indices)
    ][:top_n]

    return df.iloc[filtered_indices][['Fragrance Name', 'Brand']]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
