p8 = """
#  Step 1: Install required libraries (Run this only once) 
!pip install langchain cohere langchain-community google-colab 
#  Step 2: Import necessary libraries  
import cohere  
import getpass 
from langchain import PromptTemplate  
from langchain.llms import Cohere 
from google.colab import auth 
from google.colab import drive 
#  Step 3: Authenticate Google Drive 
auth.authenticate_user() 
drive.mount('/content/drive') 
#  Step 4: Load the Text File from Google Drive 
file_path = "/content/drive/My Drive/Teaching.txt" # Change this to your file path 
try:  
with open(file_path, "r", encoding="utf-8") as file:  
text_content = file.read() 
print("   
File loaded successfully!")  
except Exception as e: 
print("  
Error loading file:", str(e))  
#  Step 5: Set Up Cohere API Key 
COHERE_API_KEY = getpass.getpass("  
Enter your Cohere API Key: ")  
#  Step 6: Initialize Cohere Model with LangChain  
cohere_llm = Cohere(cohere_api_key=COHERE_API_KEY, model="command") 
# Step 7: Create a Prompt Template  
template = " 
You are an AI assistant helping to summarize and analyze a text document. Here is the document 
content:  
{text} 
Summary: -  
Provide a concise summary of the document.  
Key Takeaways: - List 3 important points from the text.  
Sentiment Analysis: - Determine if the sentiment of the document is Positive, Negative, or Neutral. 
"  
prompt_template = PromptTemplate(input_variables=["text"], template=template)  
#  Step 8: Format the Prompt and Generate Output  
formatted_prompt = prompt_template.format(text=text_content)  
response = cohere_llm.predict(formatted_prompt) 
#  Step 9: Display the Generated Output 
print("\n**Formatted Output** ")  
print(response) """