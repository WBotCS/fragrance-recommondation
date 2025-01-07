# Fragrance Recommendation System

## YOU NEED TO DOWNLOAD THE MODEL FOR THE RECOMMENDATION TO WORK.

Model Link ''

## Overview

This project is a content-based fragrance recommendation system that suggests perfumes to users based on their preferences for notes, scent families, and gender. The system uses machine learning (specifically, cosine similarity) to find fragrances that are similar in their composition to the user's stated preferences.

## Project Structure

fragrance_recommender/
├── app.py               # Flask web application
├── model_training.py    # Script to train and save the model
├── fragrances.csv       # Fragrance dataset
├── static/
│   └── style.css        # CSS for styling the website
│   └── script.js         # JavaScript for frontend interactions
├── templates/
│   └── index.html       # HTML template for the website
├── similarity_matrix.joblib # Saved similarity matrix
├── feature_columns.joblib  # Saved feature column names
├── fragrance_data.joblib   # Saved fragrance DataFrame (optional)
└── label_encoder.

## Getting Started

### Prerequisites

*   Python 3.x
*   Required Python packages (install using pip):

    ```bash
    pip install pandas scikit-learn flask joblib numpy
    ```

### Installation

1.  Clone this repository:

    ```bash
    git clone <repository_url>
    cd fragrance_recommender
    ```

2.  Place your fragrance dataset (`fragrances.csv`) in the `fragrance_recommender` directory. The CSV should have the following columns (with the specified delimiter if it's not a comma):

    *   `Fragrance Name`
    *   `Brand`
    *   `Gender`
    *   `Top Notes`
    *   `Middle Notes`
    *   `Base Notes`
    *   `Scent Family`

### Training the Model

1.  Run the `model_training.py` script to train the recommendation model and save the necessary data:

    ```bash
    python model_training.py
    ```

    This will generate the following files:

    *   `similarity_matrix.joblib`
    *   `feature_columns.joblib`
    *   `fragrance_data.joblib` (optional)
    *   `label_encoder.joblib` (optional)

### Running the Web Application

1.  Start the Flask development server:

    ```bash
    python app.py
    ```

2.  Open your web browser and go to `http://127.0.0.1:5000/` to access the fragrance recommender.

## Usage

1.  **Input Preferences:** On the website, select your preferences for:
    *   Gender
    *   Favorite Notes
    *   Favorite Scent Families
2.  **Get Recommendations:** Click the "Get Recommendations" button.
3.  **View Recommendations:** The recommended fragrances will be displayed on the page.

## How it Works

*   **Model Training (`model_training.py`):**
    *   Loads the fragrance dataset (`fragrances.csv`).
    *   Preprocesses the data (handles special characters, converts to lowercase, splits notes/families into lists).
    *   Performs feature engineering:
        *   Combines top, middle, and base notes into a single "All Notes" feature.
        *   One-hot encodes the "All Notes" and "Scent Family" columns using `MultiLabelBinarizer`.
        *   Encodes the "Gender" column using `LabelEncoder`.
    *   Calculates the cosine similarity between all fragrance pairs based on their features.
    *   Saves the similarity matrix, feature column names, and optionally the fragrance data and label encoder using `joblib`.

*   **Web Application (`app.py`):**
    *   Loads the saved model data (`similarity_matrix.joblib`, `feature_columns.joblib`, etc.) at startup.
    *   Handles user input from the website form.
    *   Transforms user input into a feature vector that matches the format used during model training.
    *   Uses the `get_recommendations` function to find the most similar fragrances based on the user's preferences and the pre-calculated similarity matrix.
    *   Sends the recommendations back to the frontend as a JSON response.

*   **Frontend (`index.html`, `script.js`):**
    *   Provides a user interface for inputting preferences.
    *   Sends an AJAX POST request to the Flask backend with the user's preferences.
    *   Dynamically updates the webpage to display the received recommendations.

## Customization

*   **Dataset:** Replace `fragrances.csv` with your own dataset. Make sure the column names and data format are consistent with the code.
*   **Features:** Modify the feature engineering in `model_training.py` to include or exclude features as needed.
*   **Recommendation Logic:** Adjust the `get_recommendations` function in `app.py` to change the number of recommendations, filtering criteria, or similarity calculation.
*   **Styling:** Customize the appearance of the website by editing `style.css`.
*   **Frontend Functionality:** Enhance the frontend with more interactive features using JavaScript.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.

