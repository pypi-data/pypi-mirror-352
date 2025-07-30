p5 = """
import gensim.downloader as api
import random
import nltk
from nltk.tokenize import sent_tokenize
# Ensure required resources are downloaded
nltk.download('punkt')
# Load pre-trained word vectors print("Loading pre-trained word vectors...")
 word_vectors = api.load("glove-wiki-gigaword-100") # 100D GloVe word embeddings 
print("Word vectors loaded successfully!")
def get_similar_words(seed_word, top_n=5): 
"Retrieve top-N similar words for a given seed word."
 try: 
similar_words = word_vectors.most_similar(seed_word, topn=top_n)
 return [word[0] for word in similar_words] 
except KeyError:
 print(f"'{seed_word}' not found in vocabulary. Try another word.") 
return []
def generate_sentence(seed_word, similar_words):
"Create a meaningful sentence using the seed word and its similar words."
sentence_templates = [
f"The {seed_word} was surrounded by {similar_words[0]} and {similar_words[1]}.",
f"People often associate {seed_word} with {similar_words[2]} and {similar_words[3]}.",
f"In the land of {seed_word}, {similar_words[4]} was a common sight.", 
f"A story about {seed_word} would be incomplete without {similar_words[1]} and {similar_words[3]}.", ]
return random.choice(sentence_templates)
def generate_paragraph(seed_word):
 "Construct a creative paragraph using the seed word and similar words."
similar_words = get_similar_words(seed_word, top_n=5)
if not similar_words: 
return "Could not generate a paragraph. Try another seed word."
paragraph = [generate_sentence(seed_word, similar_words) for _ in range(4)] 
return " ".join(paragraph)
# Example usage 
seed_word = input("Enter a seed word: ") 
paragraph = generate_paragraph(seed_word) 
print("\nGenerated Paragraph:\n") 
print(paragraph)
"""