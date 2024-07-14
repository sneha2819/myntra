from google.colab import drive
drive.mount('/content/drive')

import os
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Extract the dataset
zip_path = '/content/drive/My Drive/archive (1).zip'
extract_path = '/content/extracted_files'
if not os.path.exists(extract_path):
    os.makedirs(extract_path)

import zipfile
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Define the path to the subdirectory containing images
image_dir = os.path.join(extract_path, 'women fashion')
image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

if not image_files:
    print("No image files found in the directory.")
else:
    print(f"Found {len(image_files)} image files.")
    data_for_csv = pd.DataFrame({
        'image': [os.path.join(image_dir, img) for img in image_files],
        'description': ['Description for ' + img for img in image_files]
    })
    csv_file_path = '/content/fashion_images.csv'
    data_for_csv.to_csv(csv_file_path, index=False)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\b(?:jpeg|jpg|png|image|file|photo)\b', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    words = nltk.word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

data_for_csv = pd.read_csv(csv_file_path)
data_for_csv['description'] = data_for_csv['description'].apply(preprocess_text)

# Vectorize the descriptions
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_tfidf = tfidf_vectorizer.fit_transform(data_for_csv['description'])

# Determine the optimal number of clusters using the Elbow Method
inertia = []
k_values = range(1, 11)
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_tfidf)
    inertia.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(k_values, inertia, marker='o')
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal K')
plt.show()

# Fit K-Means
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
clusters = kmeans.fit_predict(X_tfidf)
data_for_csv['cluster'] = clusters

# Display the top terms for each cluster
feature_names = tfidf_vectorizer.get_feature_names_out()
for i in range(num_clusters):
    cluster_center = kmeans.cluster_centers_[i]
    top_terms_idx = cluster_center.argsort()[-10:][::-1]
    top_terms = [feature_names[idx] for idx in top_terms_idx]
    print(f"Cluster {i}: {', '.join(top_terms)}")

# Save the DataFrame with cluster labels
output_csv_file_path = '/content/fashion_images_with_clusters.csv'
data_for_csv.to_csv(output_csv_file_path, index=False)

# Verify the DataFrame
print(data_for_csv)
print(data_for_csv.columns)

# PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_tfidf.toarray())
pca_df = pd.DataFrame(data=X_pca, columns=['PC1', 'PC2'])
pca_df['cluster'] = clusters

plt.figure(figsize=(10, 8))
for i in range(num_clusters):
    cluster_data = pca_df[pca_df['cluster'] == i]
    plt.scatter(cluster_data['PC1'], cluster_data['PC2'], label=f'Cluster {i}')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA of TF-IDF Features with K-Means Clusters')
plt.legend()
plt.show()

Download the CSV file
from google.colab import files
files.download(output_csv_file_path)
