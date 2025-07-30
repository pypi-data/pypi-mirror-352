p2 = """
# Install required libraries
!pip install gensim scikit-learn matplotlib

# Import libraries
import gensim.downloader as api import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA from sklearn.manifold import TSNE
 
# Load pre-trained word vectors print("Loading pre-trained word vectors...")
word_vectors = api.load("word2vec-google-news-300") # Load Word2Vec model

# Select 10 words from a specific domain (e.g., technology)
domain_words = ["computer", "software", "hardware", "algorithm", "data", "network", "programming", "machine", "learning", "artificial"]

# Get vectors for the selected words
domain_vectors = np.array([word_vectors[word] for word in domain_words])

# Function to visualize word embeddings using PCA or t-SNE
def visualize_word_embeddings(words, vectors, method='pca', perplexity=5): # Reduce dimensionality to 2D
if method == 'pca':
reducer = PCA(n_components=2) elif method == 'tsne':
reducer = TSNE(n_components=2, random_state=42, perplexity=perplexity) else:
raise ValueError("Method must be 'pca' or 'tsne'.")

# Fit and transform the vectors
reduced_vectors = reducer.fit_transform(vectors)

# Plot the results plt.figure(figsize=(10, 8))
for i, word in enumerate(words):
plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1], marker='o', color='blue')
plt.text(reduced_vectors[i, 0] + 0.02, reduced_vectors[i, 1] + 0.02, word, fontsize=12)

plt.title(f"Word Embeddings Visualization using {method.upper()}") plt.xlabel("Component 1")
plt.ylabel("Component 2") plt.grid(True)
plt.show()

# Visualize using PCA
visualize_word_embeddings(domain_words, domain_vectors, method='pca')

# Visualize using t-SNE
visualize_word_embeddings(domain_words, domain_vectors, method='tsne', perplexity=3)

# Function to generate 5 semantically similar words def generate_similar_words(word):
 
try:
similar_words = word_vectors.most_similar(word, topn=5) print(f"\nTop 5 semantically similar words to '{word}':") for similar_word, similarity in similar_words:
print(f"{similar_word}: {similarity:.4f}") except KeyError as e:
print(f"Error: {e} not found in the vocabulary.")

# Example: Generate similar words for a given input generate_similar_words("computer") generate_similar_words("learning")
"""