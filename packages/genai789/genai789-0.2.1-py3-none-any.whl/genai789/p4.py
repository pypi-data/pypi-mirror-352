p4 = """
# Install required libraries
# Install gensim for downloading pre-trained models 
!pip install gensim
# Install Hugging Face Transformers for NLP pipelines !pip install transformers
# Install NLTK for text preprocessing and tokenization !pip install nltk 
# Import libraries
import gensim.downloader as api 
from transformers import pipeline
import nltk
import string
from nltk.tokenize import word_tokenize
# Download the 'punkt_tab' resource from NLTK nltk.download('punkt_tab') 
# Load pre-trained word vectors
print("Loading pre-trained word vectors...")
word_vectors = api.load("glove-wiki-gigaword-100") # Load Word2Vec model 
# Function to replace words in the prompt with their most similar words def replace_keyword_in_prompt(prompt, keyword, word_vectors, topn=1): 
"
Replace only the specified keyword in the prompt with its most similar word. 
Args:
prompt (str): The original input prompt.
keyword (str): The word to be replaced with a similar word.
word_vectors (gensim.models.KeyedVectors): Pre-trained word embeddings. topn (int): Number of top similar words to consider (default: 1). 
Returns:
str: The enriched prompt with the keyword replaced. 
"
words = word_tokenize(prompt) # Tokenize the prompt into words enriched_words = [] 
for word in words:
cleaned_word = word.lower().strip(string.punctuation) # Normalize word 
if cleaned_word == keyword.lower(): # Replace only if it matches the keyword try: 
# Retrieve similar word
similar_words = word_vectors.most_similar(cleaned_word, topn=topn) if similar_words: 
replacement_word = similar_words[0][0] # Choose the most similar word print(f"Replacing '{word}' → '{replacement_word}'") enriched_words.append(replacement_word)
continue # Skip appending the original word 
except KeyError:
print(f"'{keyword}' not found in the vocabulary. Using original word.") 
enriched_words.append(word) # Keep original if no replacement was made 
enriched_prompt = " ".join(enriched_words) print(f"\n🔹 Enriched Prompt: {enriched_prompt}") return enriched_prompt 
# Load an open-source Generative AI model (GPT-2) print("\nLoading GPT-2 model...")
generator = pipeline("text-generation", model="gpt2") 
# Function to generate responses using the Generative AI model 
def generate_response(prompt, max_length=100): 
try:
response = generator(prompt, max_length=max_length, num_return_sequences=1) return response[0]['generated_text'] 
except Exception as e:
print(f"Error generating response: {e}") return None 
# Example original prompt
original_prompt = "Who is king."
print(f"\n🔹 Original Prompt: {original_prompt}") 
# Retrieve similar words for key terms in the prompt key_term = "king" 
# Enrich the original prompt 
enriched_prompt = word_vectors) 
replace_keyword_in_prompt(original_prompt,key_ter m, 
# Generate responses for the original and enriched prompts print("\nGenerating response for the original prompt...") original_response = generate_response(original_prompt) print("\nOriginal Prompt Response:") print(original_response) 
print("\nGenerating response for the enriched prompt...") enriched_response = generate_response(enriched_prompt) print("\nEnriched Prompt Response:") print(enriched_response) 
# Compare the outputs
print("\nComparison of Responses:")
print("\nOriginal Prompt Response Length:", len(original_response)) print("Enriched Prompt Response Length:", len(enriched_response)) print("\nOriginal Prompt Response Detail:", original_response.count(".")) print("Enriched Prompt Response Detail:", enriched_response.count(".")) 
Output: 
[nltk_data] Downloading package punkt to /root/nltk_data... [nltk_data] Package punkt is already up-to-date!
Loading pre-trained word vectors...
Loading GPT-2 model... 
Device set to use cpu 
Truncation was not explicitly activated but `max_length` is provided a specific value, please use `truncation=True` to explicitly truncate examples to max length. Defaulting to 'longest_first' truncation strategy. If you encode pairs of sequences (GLUE-style) with the tokenizer you can select this strategy more precisely by providing a specific strategy to `truncation`. 
Setting `pad_token_id` to `eos_token_id`:50256 for open-end generation. 
🔹 Original Prompt: Who is king. Replacing 'king' → 'prince'
🔹 Enriched Prompt: Who is prince . 
Generating response for the original prompt...
Setting `pad_token_id` to `eos_token_id`:50256 for open-end generation 
Original Prompt Response: 
Who is king. Is any one of them a son of God? He is the Lord of every kingdom. (3)--But, in the case of the Son of Man there was seen: how much is it with us to know that he is the Son of God? Now I am in an immolated body so that you could look with a clear eye at the Scriptures. And I was told by a man whom I know not whom you will come out, that the Lord had his own daughter 
Generating response for the enriched prompt... 
Enriched Prompt Response: 
Who is prince ...?" 
And this prince is one of the lords of the earth and of the kings of the world? The God of his Kingdom. 
He was an uncle who was named by God and was taken away by men for the adultery of some of them who had gone before him. 
And what is a prince? 
One who is Prince of heaven and of the earth, like him who comes to me with water in one hand and his Lord with 
Comparison of Responses: 
Original Prompt Response Length: 380 Enriched Prompt Response Length: 382 
Original Prompt Response Detail: 3 Enriched Prompt Response Detail: 5 

"""