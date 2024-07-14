from flask import Flask, request, render_template, send_from_directory, jsonify
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances

app = Flask(__name__)

# Load the aesthetics and clothing datasets
aesthetic_df = pd.read_excel('aesthetics_file.xlsx', sheet_name='Sheet1')
clothing_df = pd.read_csv('cleaned_clothing_file.csv')

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

# Perform K-means clustering
aesthetic_kmeans = KMeans(n_clusters=8, random_state=42)
aesthetic_kmeans.fit(aesthetic_embeddings)
clothing_kmeans = KMeans(n_clusters=8, random_state=42)
clothing_kmeans.fit(clothing_embeddings)

def get_items_with_min_distance(aesthetic):
    if aesthetic not in aesthetic_df['Aesthetic'].values:
        return pd.DataFrame(columns=['image', 'description'])

    aesthetic_index = aesthetic_df.loc[aesthetic_df['Aesthetic'] == aesthetic].index[0]
    clothing_distances = euclidean_distances(clothing_embeddings, aesthetic_embeddings[aesthetic_index].reshape(1, -1))
    min_distance_indices = clothing_distances.flatten().argsort()[:10]
    items_with_min_distance = clothing_df.iloc[min_distance_indices]
    return items_with_min_distance

# Define the Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results.html')
def results_page():
    return send_from_directory('templates', 'results.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return render_template('results.html', items=[])

    query_embedding = model.encode([query])
    distances = cosine_similarity(query_embedding, clothing_embeddings)
    indices = distances.argsort()[0][-5:][::-1]

    results = clothing_df.iloc[indices][['image', 'description']].to_dict(orient='records')
    return render_template('results.html', items=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
