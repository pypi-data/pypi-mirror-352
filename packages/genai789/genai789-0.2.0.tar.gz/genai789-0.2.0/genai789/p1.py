p1 = """
# import numpy as np
# from numpy.linalg import norm

# # Load pre-trained word vectors print("Loading pre-trained word vectors...")
# word_vectors = api.load("word2vec-google-news-300")

# # Function to perform vector arithmetic and find similar words def explore_word_relationships(word1, word2, word3):
# try:
# # Get vectors for the input words vec1 = word_vectors[word1] vec2 = word_vectors[word2] vec3 = word_vectors[word3]

# # Perform vector arithmetic: word1 - word2 + word3 result_vector = vec1 - vec2 + vec3

# # Find the most similar words to the resulting vector
# similar_words = word_vectors.similar_by_vector(result_vector, topn=10)

# # Exclude input words from the results input_words = {word1, word2, word3}
# filtered_words = [(word, similarity) for word, similarity in similar_words if word not in input_words]

# print(f"\nWord Relationship: {word1} - {word2} + {word3}") print("Most similar words to the result (excluding input words):") for word, similarity in filtered_words[:5]: # Show top 5 results
# print(f"{word}: {similarity:.4f}")

# except KeyError as e:
# print(f"Error: {e} not found in the vocabulary.")

# # Example word relationships to explore explore_word_relationships("king", "man", "woman") explore_word_relationships("paris", "france", "germany") explore_word_relationships("apple", "fruit", "carrot")

# # Function to analyze the similarity between two words def analyze_similarity(word1, word2):
# try:
# similarity = word_vectors.similarity(word1, word2)
# print(f"\nSimilarity between '{word1}' and '{word2}': {similarity:.4f}") except KeyError as e:
# print(f"Error: {e} not found in the vocabulary.")

# # Example similarity analysis analyze_similarity("cat", "dog") analyze_similarity("computer", "keyboard")
 
# analyze_similarity("music", "art")

# # Function to find the most similar words to a given word def find_most_similar(word):
# try:
# similar_words = word_vectors.most_similar(word, topn=5) print(f"\nMost similar words to '{word}':")
# for similar_word, similarity in similar_words: print(f"{similar_word}: {similarity:.4f}")
# except KeyError as e:
# print(f"Error: {e} not found in the vocabulary.")

# # Example: Find most similar words find_most_similar("happy") find_most_similar("sad") find_most_similar("technology")

# Output:
# Loading pre-trained word vectors... Word Relationship: king - man + woman
# Most similar words to the result (excluding input words): queen: 0.7301
# monarch: 0.6455
# princess: 0.6156
# crown_prince: 0.5819
# prince: 0.5777

# Word Relationship: paris - france + germany
# Most similar words to the result (excluding input words): berlin: 0.4838
# german: 0.4695
# lindsay_lohan: 0.4536
# switzerland: 0.4468
# heidi: 0.4445

# Word Relationship: apple - fruit + carrot
# Most similar words to the result (excluding input words): carrots: 0.5700
# proverbial_carrot: 0.4578
# Carrot: 0.4159
# Twizzler: 0.4074
# peppermint_candy: 0.4074
 
# Similarity between 'cat' and 'dog': 0.7609

# Similarity between 'computer' and 'keyboard': 0.3964 Similarity between 'music' and 'art': 0.4010
# Most similar words to 'happy': glad: 0.7409
# pleased: 0.6632
# ecstatic: 0.6627
# overjoyed: 0.6599
# thrilled: 0.6514

# Most similar words to 'sad': saddening: 0.7273
# Sad: 0.6611
# saddened: 0.6604
# heartbreaking: 0.6574
# disheartening: 0.6507

# Most similar words to 'technology': technologies: 0.8332
# innovations: 0.6231
# technological_innovations: 0.6102
# technol: 0.6047
"""