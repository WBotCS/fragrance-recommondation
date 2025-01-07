from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load model data (Corrected paths)
similarity_matrix = joblib.load("similarity_matrix.joblib")
feature_columns = joblib.load("feature_columns.joblib")
fragrance_features = joblib.load("fragrance_features.joblib")  # Load fragrance_features
df = joblib.load("fragrance_data.joblib")
label_encoder = joblib.load("label_encoder.joblib")

# Recommendation function (Corrected to take fragrance_features as argument)
def get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features, top_n=5):
    user_similarity = cosine_similarity(user_preferences.reshape(1, -1), fragrance_features)
    print("User Similarity:", user_similarity)

    sorted_indices = np.argsort(user_similarity[0])[::-1]
    print("Sorted Indices:", sorted_indices)

    filtered_indices = []
    for index in sorted_indices:
        fragrance_vector = fragrance_features.iloc[index].values

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
    return recommendations

@app.route('/')
def index():
    return render_template('index.html', feature_columns=feature_columns)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.get_json()
    print("User Input:", user_input)

    # Transform user input into feature vector
    user_preferences = np.zeros(len(feature_columns))

    # Handle Gender
    gender_index = feature_columns.index('Gender')
    user_preferences[gender_index] = int(user_input['gender'])

    # Handle preferred notes and families
    print("User Input Notes:", user_input['preferred_notes'])
    print("User Input Families:", user_input['preferred_families'])
    for note in user_input['preferred_notes']:
        # Convert to lowercase and add "note_" prefix to match feature column names
        note_lower = "note_" + note.lower()
        if note_lower in feature_columns:
            print("note", note_lower)
            user_preferences[feature_columns.index(note_lower)] = 1
        else:
            print(f"Warning: Note '{note}' not found in feature columns.")

    for family in user_input['preferred_families']:
        # Convert to lowercase and add "family_" prefix to match feature column names
        family_lower = "family_" + family.lower()
        if family_lower in feature_columns:
            print("family", family_lower)
            user_preferences[feature_columns.index(family_lower)] = 1
        else:
            print(f"Warning: Family '{family}' not found in feature columns.")

    # Handle disliked notes (if applicable)
    disliked_notes_indices = []
    if 'disliked_notes' in user_input:
        for note in user_input['disliked_notes']:
            # Convert to lowercase and add "note_" prefix to match feature column names
            note_lower = "note_" + note.lower()
            if note_lower in feature_columns:
                disliked_notes_indices.append(feature_columns.index(note_lower))
            else:
                print(f"Warning: Disliked note '{note}' not found in feature columns.")

    # Get recommendations (pass fragrance_features as an argument)
    recommendations = get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features, top_n=5)

    print("Recommendations:", recommendations)

    # Convert recommendations to JSON and return
    return jsonify(recommendations.to_dict(orient='records'))

@app.route('/select2-data')
def select2_data():
    notes_data = []
    for feature in feature_columns:
        if feature.startswith('note_'):
            notes_data.append({'id': feature, 'text': feature[5:]})

    families_data = []
    for feature in feature_columns:
        if feature.startswith('family_'):
            families_data.append({'id': feature, 'text': feature[7:]})

    return jsonify({'notes': notes_data, 'families': families_data})

if __name__ == '__main__':
    app.run(debug=True)