from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load model data
similarity_matrix = joblib.load("similarity_matrix.joblib")
feature_columns = joblib.load("feature_columns.joblib")
fragrance_features = joblib.load("fragrance_features.joblib")
df = joblib.load("fragrance_data.joblib")
label_encoder = joblib.load("label_encoder.joblib")

# Recommendation function
def get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features, top_n=5):
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
    return render_template('index.html', feature_columns=feature_columns)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recommend', methods=['POST'])
def recommend():
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
    recommendations = get_recommendations(user_preferences, disliked_notes_indices, df, similarity_matrix, fragrance_features, top_n=5)

    print("Recommendations:", recommendations)

    # Convert recommendations to JSON and return
    return jsonify(recommendations.to_dict(orient='records'))

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
    app.run(debug=True)