#cluster aesthetics
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA


# Load the Excel file
file_path = 'aesthetics_file.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# Combine key motifs and key colours into one column for analysis
df['combined'] = df['Key motifs'] + ' ' + df['Key colours']

# Create a TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['combined'])

# Calculate the cosine similarity matrix
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Generate the linkage matrix
linkage_matrix = sch.linkage(cosine_sim, method='ward')

# Plot the dendrogram
plt.figure(figsize=(15, 10))
dendrogram = sch.dendrogram(linkage_matrix, labels=df['Aesthetic'].values, leaf_rotation=90, leaf_font_size=10)
plt.title('Dendrogram for Aesthetic Clustering')
plt.xlabel('Aesthetics')
plt.ylabel('Euclidean Distances')
plt.show()

# Dimensionality reduction with PCA before clustering
pca = PCA(n_components=50)
pca_result = pca.fit_transform(tfidf_matrix.toarray())

# Perform K-means clustering with optimized number of clusters
kmeans = KMeans(n_clusters=6, random_state=42)
kmeans.fit(pca_result)
labels = kmeans.labels_

# Perform t-SNE for dimensionality reduction
tsne = TSNE(n_components=2, random_state=42, perplexity=30, learning_rate=200, n_iter=1000)
tsne_results = tsne.fit_transform(pca_result)

# Create a scatter plot
plt.figure(figsize=(15, 10))
scatter = plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=labels, cmap='tab10')

# Annotate points with aesthetic names
for i, label in enumerate(df['Aesthetic']):
    plt.annotate(label, (tsne_results[i, 0], tsne_results[i, 1]), fontsize=8, alpha=0.7)

plt.colorbar(scatter)
plt.title('t-SNE Scatter Plot with K-means Clustering')
plt.xlabel('t-SNE Dimension 1')
plt.ylabel('t-SNE Dimension 2')
plt.show()
