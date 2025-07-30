p6 = """
# Install required libraries (only needed for first-time setup)
# !pip install transformers  # Uncomment if running for the first time

# Import the sentiment analysis pipeline from Hugging Face
from transformers import pipeline

# Load the sentiment analysis pipeline
print("🔄 Loading Sentiment Analysis Model…")
sentiment_analyzer = pipeline("sentiment-analysis")

# Function to analyze sentiment
def analyze_sentiment(text):
    "
    Analyze the sentiment of a given text input.
    
    Args:
        text (str): Input sentence or paragraph.
        
    Returns:
        dict: Sentiment label and confidence score.
    "
    result = sentiment_analyzer(text)[0]  # Get the first result
    label = result['label']               # Sentiment label (POSITIVE/NEGATIVE)
    score = result['score']               # Confidence score

    print(f"\n📝 Input Text: {text}")
    print(f"📊 Sentiment: {label} (Confidence: {score:.4f})\n")
    return result

# Example real-world application: Customer feedback analysis
customer_reviews = [
    "The product is amazing! I love it so much.",
    "I'm very disappointed. The service was terrible.",
    "It was an average experience, nothing special.",
    "Absolutely fantastic quality! Highly recommended.",
    "Not great, but not the worst either."
]

# Analyze sentiment for multiple reviews
print("\n🔍 Customer Sentiment Analysis Results:")
for review in customer_reviews:
    analyze_sentiment(review)

"""