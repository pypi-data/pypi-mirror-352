p7 = """
# Install required libraries (only needed for first-time setup)
# !pip install transformers   # Uncomment this line if running for the first time

# Import the summarization pipeline from Hugging Face
from transformers import pipeline

# Load the BART summarization model
print("Loading Summarization Model (BART)…")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to summarize text with multiple strategies
def summarize_text(text, max_length=None, min_length=None):
    "
    Summarizes a given long text using a pre-trained BART summarization model.
    
    Args:
        text (str): The input passage to summarize.
        max_length (int, optional): Maximum length of the summary.
        min_length (int, optional): Minimum length of the summary.

    Returns:
        None: Prints different summary styles.
    "

    # Remove unnecessary line breaks
    text = " ".join(text.split())

    # Auto-adjust summary length based on input size
    if not max_length:
        max_length = min(len(text) // 3, 150)
    if not min_length:
        min_length = max(30, max_length // 3)

    # Generate summaries using different settings
    summary_1 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    summary_2 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=True, temperature=0.9)
    summary_3 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False, num_beams=5)
    summary_4 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=True, top_k=50, top_p=0.95)

    # Print all summaries
    print("\nOriginal Text:")
    print(text)
    print("\nSummarized Texts:")
    print("Default:", summary_1[0]['summary_text'])
    print("High randomness:", summary_2[0]['summary_text'])
    print("Conservative:", summary_3[0]['summary_text'])
    print("Diverse sampling:", summary_4[0]['summary_text'])


# Example long text passage
long_text = "
Artificial Intelligence (AI) is a rapidly evolving field of computer science focused on creating 
intelligent machines capable of mimicking human cognitive functions such as learning, problem-solving, 
and decision-making. In recent years, AI has significantly impacted various industries, including healthcare, 
finance, education, and entertainment. AI-powered applications, such as chatbots, self-driving cars, 
and recommendation systems, have transformed the way we interact with technology. 
Machine learning and deep learning, subsets of AI, enable systems to learn from data and improve 
over time without explicit programming. However, AI also poses ethical challenges, such as bias 
in decision-making and concerns over job displacement. As AI technology continues to advance, it is 
crucial to balance innovation with ethical considerations to ensure its responsible development and deployment.
"

# Run summarization
summarize_text(long_text)
"""