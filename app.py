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
LOCAL_MODEL_PATH = 'models/'  # Local directory to save the model files

def download_model_files_from_s3():
    s3 = boto3.client('s3')
    if not os.path.exists(LOCAL_MODEL_PATH):
        os.makedirs(LOCAL_MODEL_PATH)
    
    for file_name, s3_key in MODEL_FILES.items():
        local_file_path = os.path.join(LOCAL_MODEL_PATH, f"{file_name}.joblib")
        if not os.path.exists(local_file_path):
            print(f"Downloading {file_name} from S3...")
            s3.download_file(S3_BUCKET, s3_key, local_file_path)
            print(f"{file_name} downloaded successfully.")
        else:
            print(f"{file_name} already exists locally.")

# Download model files from S3
download_model_files_from_s3()

# Initialize model variables as None
similarity_matrix = None
feature_columns = None
fragrance_features = None
df = None
label_encoder = None

def load_models():
    """Loads models only when needed."""
    global similarity_matrix, feature_columns, fragrance_features, df, label_encoder
    try:
        similarity_matrix = joblib.load(os.path.join(LOCAL_MODEL_PATH, "similarity_matrix.joblib"))
        feature_columns = joblib.load(os.path.join(LOCAL_MODEL_PATH, "feature_columns.joblib"))
        fragrance_features = joblib.load(os.path.join(LOCAL_MODEL_PATH, "fragrance_features.joblib"))
        df = joblib.load(os.path.join(LOCAL_MODEL_PATH, "fragrance_data.joblib"))
        label_encoder = joblib.load(os.path.join(LOCAL_MODEL_PATH, "label_encoder.joblib"))
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")

# Recommendation function
def get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features, top_n=5):

    # Load models if not already loaded
    if similarity_matrix is None: 
        load_models()

    print("----- Inside get_recommendations -----")
    print("User Preferences:", user_preferences)

    user_similarity = cosine_similarity(user_preferences.reshape(1, -1), fragrance_features)
    print("User Similarity:", user_similarity)

    sorted_indices = np.argsort(user_similarity[0])[::-1]
    print("Sorted Indices:", sorted_indices)

    filtered_indices = []
    for index in sorted_indices:
        fragrance_vector = fragrance_features.iloc[index].values
        print(f"Checking fragrance at index {index}:", fragrance_vector)

        if disliked_notes_indices is None or not disliked_notes_indices:
            filtered_indices.append(index)
        elif not any(fragrance_vector[note_index] == 1 for note_index in disliked_notes_indices):
            filtered_indices.append(index)

        if len(filtered_indices) == top_n:
            break

    print("Filtered Indices:", filtered_indices)

    if not filtered_indices:
        print("No fragrances found after filtering.")
        return pd.DataFrame(columns=['Fragrance Name', 'Brand'])

    recommendations = df.iloc[filtered_indices][['Fragrance Name', 'Brand']]
    print("Recommendations DataFrame:", recommendations)
    print("----- Exiting get_recommendations -----")
    return recommendations

@app.route('/')
def index():
    # Load models if not already loaded (for initial page load)
    if feature_columns is None:
        load_models()
    return render_template('index.html', feature_columns=feature_columns)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.get_json()
        print("User Input:", user_input)

        # Transform user input into feature vector
        user_preferences = np.zeros(len(feature_columns))
        print("Initialized User Preferences:", user_preferences)

        # Handle Gender
        gender_index = feature_columns.index('Gender')
        user_preferences[gender_index] = int(user_input['gender'])
        print("User Preferences after Gender:", user_preferences)

    # Handle preferred notes and families
        print("User Input Notes:", user_input['preferred_notes'])
        print("User Input Families:", user_input['preferred_families'])
    
        for note in user_input['preferred_notes']:
            note_with_prefix = "note_" + note.lower()
            if note_with_prefix in feature_columns:
                print("Adding note:", note_with_prefix)
                user_preferences[feature_columns.index(note_with_prefix)] = 1
            else:
                print(f"Warning: Note '{note}' not found in feature columns.")
    
        for family in user_input['preferred_families']:
            family_with_prefix = "family_" + family.lower()
            if family_with_prefix in feature_columns:
                print("Adding family:", family_with_prefix)
                user_preferences[feature_columns.index(family_with_prefix)] = 1
            else:
                print(f"Warning: Family '{family}' not found in feature columns.")
    
        print("User Preferences after Notes/Families:", user_preferences)
    
        # Handle disliked notes
        disliked_notes_indices = []
        if 'disliked_notes' in user_input and user_input['disliked_notes']:
            for note in user_input['disliked_notes']:
                note_with_prefix = "note_" + note.lower()
                if note_with_prefix in feature_columns:
                    print("Adding disliked note:", note_with_prefix)
                    disliked_notes_indices.append(feature_columns.index(note_with_prefix))
                else:
                    print(f"Warning: Disliked note '{note}' not found in feature columns.")
        else:
            disliked_notes_indices = None
            print("No disliked notes provided.")
    
        print("User Preferences after Disliked Notes:", user_preferences)
        print("Disliked Notes Indices:", disliked_notes_indices)

    # Get recommendations

        recommendations = get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features)

        return jsonify(recommendations.to_dict(orient='records'))
    except Exception as e:
        print(f"Error in recommend route: {e}")
        return jsonify({"error": "An error occurred"}), 500

@app.route('/select2-data')
def select2_data():
    notes_data = []
    for feature in feature_columns:
        if feature.startswith('note_'):
            notes_data.append({'id': feature[5:], 'text': feature[5:]})

    families_data = []
    for feature in feature_columns:
        if feature.startswith('family_'):
            families_data.append({'id': feature[7:], 'text': feature[7:]})

    return jsonify({'notes': notes_data, 'families': families_data})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the port provided by Railway
    app.run(host='0.0.0.0', port=port)
