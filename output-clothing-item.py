import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances

# Load the aesthetics dataset
aesthetic_file_path = 'aesthetics_file.xlsx'
aesthetic_df = pd.read_excel(aesthetic_file_path, sheet_name='Sheet1')

# Combine key motifs and key colours into one column for analysis
aesthetic_df['combined'] = aesthetic_df['Key motifs'] + ' ' + aesthetic_df['Key colours']

# Load the clothing dataset
clothing_file_path = 'cleaned_clothing_file(1).csv'
clothing_df = pd.read_csv(clothing_file_path)

# Ensure proper formatting of the 'features' column
def preprocess_text(text):
    # Remove unwanted words
    words_to_remove = ['dress', 'top', 'trousers', 'anarkali', 'shirt', 'tee', 'pant']
    for word in words_to_remove:
        text = text.replace(word, '')
    text = ' '.join(text.split())  # Remove extra spaces created by replacements
    return text

# Apply preprocessing
clothing_df['features'] = clothing_df['features'].apply(preprocess_text)

# Initialize Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for aesthetics and clothing items
aesthetic_embeddings = model.encode(aesthetic_df['combined'].tolist())
clothing_embeddings = model.encode(clothing_df['features'].tolist())

# Perform K-means clustering for aesthetics
aesthetic_kmeans = KMeans(n_clusters=6, random_state=42)
aesthetic_kmeans.fit(aesthetic_embeddings)
aesthetic_labels = aesthetic_kmeans.labels_
aesthetic_df['cluster'] = aesthetic_labels

# Perform K-means clustering for clothing items
clothing_kmeans = KMeans(n_clusters=6, random_state=42)
clothing_kmeans.fit(clothing_embeddings)
clothing_labels = clothing_kmeans.labels_
clothing_df['cluster'] = clothing_labels

# Optional: Calculate distances and find closest clothing items for a given aesthetic
def get_items_with_min_distance(aesthetic):
    if aesthetic not in aesthetic_df['Aesthetic'].values:
        print(f"Aesthetic '{aesthetic}' not found in the dataset.")
        return pd.DataFrame(columns=['image', 'description'])

    # Find the index of the input aesthetic
    aesthetic_index = aesthetic_df.loc[aesthetic_df['Aesthetic'] == aesthetic].index[0]

    # Get the distances of all clothing items to the input aesthetic
    clothing_distances = euclidean_distances(clothing_embeddings, aesthetic_embeddings[aesthetic_index].reshape(1, -1))

    # Get the clothing items with the minimum distance to the input aesthetic
    min_distance_indices = clothing_distances.flatten().argsort()[:10]  # Adjust number as needed
    items_with_min_distance = clothing_df.iloc[min_distance_indices]

    return items_with_min_distance

# Get user input for the aesthetic
user_aesthetic = input("Enter an aesthetic: ")

# Get items with minimum distance to the input aesthetic
items_with_min_distance = get_items_with_min_distance(user_aesthetic)

# Display the items with minimum distance
print(items_with_min_distance[['image', 'description']])
