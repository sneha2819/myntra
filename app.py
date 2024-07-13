import os
from flask import Flask, request, render_template, send_from_directory
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import euclidean_distances

app = Flask(__name__)

# Load datasets
try:
    aesthetic_file_path = 'aesthetics_file.xlsx'
    aesthetic_df = pd.read_excel("aesthetics_file.xlsx", sheet_name='Sheet1')
except Exception as e:
    print(f"Error loading aesthetics dataset: {e}")
    aesthetic_df = pd.DataFrame()  # Default empty DataFrame

try:
    clothing_file_path = 'cleaned_clothing_file.csv'
    clothing_df = pd.read_csv("cleaned_clothing_file.csv", encoding='ISO-8859-1')
except Exception as e:
    print(f"Error loading clothing dataset: {e}")
    clothing_df = pd.DataFrame()  # Default empty DataFrame

# Ensure proper formatting of the 'features' column
def preprocess_text(text):
    words_to_remove = ['dress', 'top', 'trousers', 'anarkali', 'shirt', 'tee', 'pant']
    for word in words_to_remove:
        text = text.replace(word, '')
    text = ' '.join(text.split())  # Remove extra spaces created by replacements
    return text

# Apply preprocessing if dataframe is not empty
if not clothing_df.empty:
    clothing_df['features'] = clothing_df['features'].apply(preprocess_text)

# Combine key motifs and key colours into one column for analysis
if not aesthetic_df.empty:
    aesthetic_df['combined'] = aesthetic_df['Key motifs'] + ' ' + aesthetic_df['Key colours']

# Initialize Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for aesthetics and clothing items if dataframes are not empty
if not aesthetic_df.empty:
    aesthetic_embeddings = model.encode(aesthetic_df['combined'].tolist())

if not clothing_df.empty:
    clothing_embeddings = model.encode(clothing_df['features'].tolist())

# Function to get items with minimum distance
def get_items_with_min_distance(aesthetic):
    if aesthetic not in clothing_df['features'].values:
        print(f"Aesthetic '{aesthetic}' not found in the dataset.")
        return pd.DataFrame(columns=['image', 'description'])

    # Get the distances of all clothing items to the input aesthetic
    clothing_distances = euclidean_distances(clothing_embeddings, clothing_embeddings[clothing_df['features'] == aesthetic].reshape(1, -1))

    # Get the clothing items with the minimum distance to the input aesthetic
    min_distance_indices = clothing_distances.flatten().argsort()[:10]  # Adjust number as needed
    items_with_min_distance = clothing_df.iloc[min_distance_indices]

    return items_with_min_distance

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    results = get_items_with_min_distance(query)
    return render_template('results.html', query=query, items=results)

@app.route('/women_fashion/<path:filename>')
def women_fashion(filename):
    return send_from_directory('women_fashion', filename)

if __name__ == '__main__':
    app.run(debug=True)
