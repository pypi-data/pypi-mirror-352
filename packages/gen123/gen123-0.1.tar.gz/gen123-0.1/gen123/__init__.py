p1=''' import gensim.downloader as api
import numpy as np
from numpy.linalg import norm
word_vectors = api.load("word2vec-google-news-300")
def explore_word_relationships(word1, word2, word3):
try:
vec1 = word_vectors[word1] 
vec2 = word_vectors[word2] 
vec3 = word_vectors[word3]
result_vector = vec1 - vec2 + vec3
similar_words = word_vectors.similar_by_vector(result_vector, topn=10)
filtered_words = [(word, similarity) for word, similarity in similar_words if word not in input_words]

print(f"\nWord Relationship: {word1} - {word2} + {word3}")
print("Most similar words to the result (excluding input words):")
for word, similarity in filtered_words[:5]:
print(f"{word}: {similarity:.4f}")
except KeyError as e:
print(f"Error: {e} not found in the vocabulary.")

explore_word_relationships("king", "man", "woman")
explore_word_relationships("paris", "france", "germany")
explore_word_relationships("apple", "fruit", "carrot")
def analyze_similarity(word1, word2):
try:
similarity = word_vectors.similarity(word1, word2)
print(f"\nSimilarity between '{word1}' and '{word2}': {similarity:.4f}")
except KeyError as e:
print(f"Error: {e} not found in the vocabulary.")

analyze_similarity("cat", "dog")
analyze_similarity("computer", "keyboard")
analyze_similarity("music", "art")

def find_most_similar(word):
try:
similar_words = word_vectors.most_similar(word, topn=5) 
print(f"\nMost similar words to '{word}':")
for similar_word, similarity in similar_words: 
print(f"{similar_word}: {similarity:.4f}")
except KeyError as e:
print(f"Error: {e} not found in the vocabulary.")

find_most_similar("happy")
find_most_similar("sad")
 find_most_similar("technology")'''

p2=''' 
!pip install gensim scikit-learn matplotlib

# Import libraries
import gensim.downloader as api
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
 
# Load pre-trained word vectors 
print("Loading pre-trained word vectors...")
word_vectors = api.load("word2vec-google-news-300") # Load Word2Vec model

# Select 10 words from a specific domain (e.g., technology)
domain_words = ["computer", "software", "hardware", "algorithm", "data", "network", "programming", "machine", "learning", "artificial"]

# Get vectors for the selected words
domain_vectors = np.array([word_vectors[word] for word in domain_words])

# Function to visualize word embeddings using PCA or t-SNE
def visualize_word_embeddings(words, vectors, method='pca', perplexity=5): # Reduce dimensionality to 2D
    if method == 'pca':
        reducer = PCA(n_components=2) 
    elif method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42, perplexity=perplexity) 
    else:
        raise ValueError("Method must be 'pca' or 'tsne'.")

# Fit and transform the vectors
    reduced_vectors = reducer.fit_transform(vectors)

# Plot the results 
    plt.figure(figsize=(10, 8))
    for i, word in enumerate(words):
      plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1], marker='o', color='blue')
      plt.text(reduced_vectors[i, 0] + 0.02, reduced_vectors[i, 1] + 0.02, word, fontsize=12)

    plt.title(f"Word Embeddings Visualization using {method.upper()}") 
    plt.xlabel("Component 1")
    plt.ylabel("Component 2") 
    plt.grid(True)
    plt.show()

# Visualize using PCA
visualize_word_embeddings(domain_words, domain_vectors, method='pca')

# Visualize using t-SNE
visualize_word_embeddings(domain_words, domain_vectors, method='tsne', perplexity=3)

# Function to generate 5 semantically similar words 
def generate_similar_words(word):
 
    try:
        similar_words = word_vectors.most_similar(word, topn=5) 
print(f"\nTop 5 semantically similar words to '{word}':")
        for similar_word, similarity in similar_words:
print(f"{similar_word}: {similarity:.4f}")
    except KeyError as e:
print(f"Error: {e} not found in the vocabulary.")

# Example: Generate similar words for a given input 
generate_similar_words("computer")
generate_similar_words("learning")'''
p3=''' 
!pip install gensim matplotlib

# Import libraries
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
 
import numpy as np

# Sample domain-specific corpus (medical domain) 
medical_corpus = [
"The patient was diagnosed with diabetes and hypertension.", "MRI scans reveal abnormalities in the brain tissue.",
"The treatment involves antibiotics and regular monitoring.", "Symptoms include fever, fatigue, and muscle pain.",
"The vaccine is effective against several viral infections.", "Doctors recommend physical therapy for recovery.", "The clinical trial results were published in the journal.",
"The surgeon performed a minimally invasive procedure.",
"The prescription includes pain relievers and anti-inflammatory drugs.", "The diagnosis confirmed a rare genetic disorder."
]

# Preprocess corpus (tokenize sentences)
processed_corpus = [sentence.lower().split() for sentence in medical_corpus]

# Train a Word2Vec model 
print("Training Word2Vec model...")
model = Word2Vec(sentences=processed_corpus, vector_size=100, window=5, min_count=1, workers=4, epochs=50)
print("Model training complete!")

# Extract embeddings for visualization 
words = list(model.wv.index_to_key)
embeddings = np.array([model.wv[word] for word in words])

# Dimensionality reduction using t-SNE
tsne = TSNE(n_components=2, random_state=42, perplexity=5, n_iter=300) 
tsne_result = tsne.fit_transform(embeddings)

# Visualization of word embeddings 
plt.figure(figsize=(10, 8))
plt.scatter(tsne_result[:, 0], tsne_result[:, 1], color="blue") 
for i, word in enumerate(words):
    plt.text(tsne_result[i, 0] + 0.02, tsne_result[i, 1] + 0.02, word, fontsize=12) 
plt.title("Word Embeddings Visualization (Medical Domain)") 
plt.xlabel("Dimension 1")
plt.ylabel("Dimension 2") 
plt.grid(True)
plt.show()
 
# Analyze domain-specific semantics
def find_similar_words(input_word, top_n=5): 
    try:
        similar_words = model.wv.most_similar(input_word, topn=top_n) 
print(f"Words similar to '{input_word}':")
        for word, similarity in similar_words: 
print(f" {word} ({similarity:.2f})")
    except KeyError:
print(f"'{input_word}' not found in vocabulary.")

# Example: Generate semantically similar words 
find_similar_words("treatment")
find_similar_words("vaccine")
'''
p4='''
!pip install gensim transformers --quiet

import gensim.downloader as api
from transformers import pipeline
import nltk
import string
from nltk.tokenize import word_tokenize

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')

# Load pre-trained word vectors
print("🔹 Loading pre-trained word vectors...")
word_vectors = api.load("glove-wiki-gigaword-100")  # 100-dimensional GloVe vectors

# Function to replace a keyword with a similar word
def replace_keyword_in_prompt(prompt, keyword, word_vectors, topn=1):
    words = word_tokenize(prompt)
    enriched_words = []

    for word in words:
        cleaned_word = word.lower().strip(string.punctuation)
        if cleaned_word == keyword.lower():
            try:
                similar_words = word_vectors.most_similar(cleaned_word, topn=topn)
                if similar_words:
                    replacement_word = similar_words[0][0]
print(f"🔁 Replacing '{word}' → '{replacement_word}'")
                    enriched_words.append(replacement_word)
                    continue
            except KeyError:
print(f"⚠️ '{keyword}' not found in the vocabulary. Using original word.")
        enriched_words.append(word)

    enriched_prompt = " ".join(enriched_words)
print(f"\n🔹 Enriched Prompt: {enriched_prompt}")
    return enriched_prompt

# Load GPT-2 text generation model
print("\n🧠 Loading GPT-2 model...")
generator = pipeline("text-generation", model="gpt2")

# Generate a text response
def generate_response(prompt, max_length=100):
    try:
        response = generator(prompt, max_length=max_length, num_return_sequences=1)
        return response[0]['generated_text']
    except Exception as e:
print(f"Error generating response: {e}")
        return None

# Example run
original_prompt = "Who is king."
print(f"\n🔹 Original Prompt: {original_prompt}")
key_term = "king"

# Enrich and generate responses
enriched_prompt = replace_keyword_in_prompt(original_prompt, key_term, word_vectors)

print("\n💬 Generating response for original prompt...")
original_response = generate_response(original_prompt)
print("\nOriginal Response:\n", original_response)

print("\n💬 Generating response for enriched prompt...")
enriched_response = generate_response(enriched_prompt)
print("\nEnriched Response:\n", enriched_response)

# Compare
print("\n📊 Comparison:")
print("Original Length:", len(original_response))
print("Enriched Length:", len(enriched_response))
print("Original Sentences:", original_response.count("."))
print("Enriched Sentences:", enriched_response.count("."))


'''
p5=''' 
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

  try: 
    similar_words = word_vectors.most_similar(seed_word, topn=top_n)
    return [word[0] for word in similar_words] 
  except KeyError:
print(f"'{seed_word}' not found in vocabulary. Try another word.")
    return []
def generate_sentence(seed_word, similar_words):
  sentence_templates = [
    f"The {seed_word} was surrounded by {similar_words[0]} and {similar_words[1]}.",
    f"People often associate {seed_word} with {similar_words[2]} and {similar_words[3]}.",
    f"In the land of {seed_word}, {similar_words[4]} was a common sight.", 
    f"A story about {seed_word} would be incomplete without {similar_words[1]} and {similar_words[3]}.", ]
  return random.choice(sentence_templates)
def generate_paragraph(seed_word):
    """Construct a creative paragraph using the seed word and similar words."""
    similar_words = get_similar_words(seed_word, top_n=5)
    if not similar_words:
        return "Could not generate a paragraph. Try another seed word."
    paragraph = [generate_sentence(seed_word, similar_words) for _ in range(4)]
    return " ".join(paragraph)

# Example usage
seed_word = input("Enter a seed word: ")
paragraph = generate_paragraph(seed_word)
print("\nGenerated Paragraph:\n")
print(paragraph)'''

p6=''' !pip install transformers 

# Import the sentiment analysis pipeline from Hugging Face 
from transformers import pipeline

# Load the sentiment analysis pipeline 
print("Loading Sentiment Analysis Model…")
sentiment_analyzer = pipeline("sentiment-analysis") 

# Function to analyze sentiment 
def analyze_sentiment(text): 
    result = sentiment_analyzer(text)[0]  # Get the first result 
    label = result['label']  # Sentiment label (POSITIVE/NEGATIVE) 
    score = result['score']  # Confidence score 
print(f"\n📝 Input Text: {text}")
print(f"📝 Sentiment: {label} (Confidence: {score:.4f})\n")
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
print("\nCustomer Sentiment Analysis Results:")
for review in customer_reviews: 
    analyze_sentiment(review)'''

p7=''' # Install required libraries (only needed for first-time setup) 
!pip install transformers 

# Import the summarization pipeline from Hugging Face 
from transformers import pipeline
 
# Load a more accurate pre-trained summarization model 
print("Loading Summarization Model (BART)…")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn") 
 
# Function to summarize text with improved accuracy 
def summarize_text(text, max_length=None, min_length=None): 
    """ 
    Summarizes a given long text using a pre-trained BART summarization model. 
    Args: 
        text (str): The input passage to summarize. 
        max_length (int): Maximum length of the summary (default: auto-calculated). 
        min_length (int): Minimum length of the summary (default: auto-calculated). 
    Returns: 
        str: The summarized text. 
    """ 
    # Remove unnecessary line breaks 
    text = " ".join(text.split()) 
 
    # Auto-adjust summary length based on text size 
    if not max_length: 
        max_length = min(len(text) // 3, 150)  # Summary should be ~1/3rd of input 
    if not min_length: 
        min_length = max(30, max_length // 3)  # Minimum length should be at least 30 
 
    # Generate the summary with different approaches 
    summary_1 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)  # Default Settings 
    summary_2 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=True, temperature=0.9)  # High randomness (Creative output) 
    summary_3 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False, num_beams=5)  # Conservative approach (More structured) 
    summary_4 = summarizer(text, max_length=max_length, min_length=min_length, do_sample=True, top_k=50, top_p=0.95)  # Diverse sampling using top-k and top-p 
 
print("\nOriginal Text:")
print(text)
print("\nSummarized Text:")
print("Default:", summary_1[0]['summary_text'])
print("High randomness:", summary_2[0]['summary_text'])
print("Conservative:", summary_3[0]['summary_text'])
    print("Diverse sampling:", summary_4[0]['summary_text']) '''

p8=''' 
!pip install langchain cohere langchain-community google-colab 

# Step 2: Import necessary libraries  
import cohere
import getpass
from langchain import PromptTemplate
from langchain.llms import Cohere
from google.colab import auth
from google.colab import drive

# Step 3: Authenticate Google Drive 
auth.authenticate_user() 
drive.mount('/content/drive') 

# Step 4: Load the Text File from Google Drive 
file_path = "/content/drive/My Drive/Teaching.txt"  # Change this to your file path 
try:  
    with open(file_path, "r", encoding="utf-8") as file:  
        text_content = file.read() 
print("File loaded successfully!")
except Exception as e: 
print("Error loading file:", str(e))

# Step 5: Set Up Cohere API Key 
COHERE_API_KEY = getpass.getpass("Enter your Cohere API Key: ")  

# Step 6: Initialize Cohere Model with LangChain  
cohere_llm = Cohere(cohere_api_key=COHERE_API_KEY, model="command") 

# Step 7: Create a Prompt Template  
template = """  
You are an AI assistant helping to summarize and analyze a text document. Here is the document 
content:  
{text} 
Summary: -  
Provide a concise summary of the document.  
Key Takeaways: - List 3 important points from the text.  
Sentiment Analysis: - Determine if the sentiment of the document is Positive, Negative, or Neutral. 
"""  
prompt_template = PromptTemplate(input_variables=["text"], template=template)  

# Step 8: Format the Prompt and Generate Output  
formatted_prompt = prompt_template.format(text=text_content)  
response = cohere_llm.predict(formatted_prompt) 

# Step 9: Display the Generated Output 
print("\n**Formatted Output**")
print(response)'''

p9=''' 
!pip install wikipedia-api pydantic  

from pydantic import BaseModel
from typing import List, Optional
import wikipediaapi

class InstitutionDetails(BaseModel): 
    founder: Optional[str] 
    founded: Optional[str] 
    branches: Optional[List[str]] 
    number_of_employees: Optional[int]  
    summary: Optional[str] 

def fetch_institution_details(institution_name: str) -> InstitutionDetails: 
    # Define a user-agent as per Wikipedia's policy  
    user_agent = "MyJupyterNotebook/1.0 (contact: myemail@example.com)"  
    wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')  
    page = wiki_wiki.page(institution_name) 

    if not page.exists(): 
        raise ValueError(f"The page for '{institution_name}' does not exist on Wikipedia.")  

    # Initialize variables 
    founder = None 
    founded = None  
    branches = [] 
    number_of_employees = None 

    # Extract summary  
    summary = page.summary[:500]  # Limiting summary to 500 characters 

    # Extract information from the infobox 
    infobox = page.text.split('\n')  
    for line in infobox: 
        if 'Founder' in line:  
            founder = line.split(':')[-1].strip()  
        elif 'Founded' in line: 
            founded = line.split(':')[-1].strip() 
        elif 'Branches' in line: 
            branches = [branch.strip() for branch in line.split(':')[-1].split(',')] 
        elif 'Number of employees' in line:  
            try: 
                number_of_employees = int(line.split(':')[-1].strip().replace(',', '')) 
            except ValueError: 
                number_of_employees = None 

    return InstitutionDetails( 
        founder=founder, 
        founded=founded, 
        branches=branches if branches else None, 
        number_of_employees=number_of_employees, 
        summary=summary 
    )  

# Import necessary libraries from IPython.display 
from IPython.display import display
import ipywidgets as widgets

# Function to display institution details  
def display_institution_details(details: InstitutionDetails):  
print(f"Founder: {details.founder or 'N/A'}")
print(f"Founded: {details.founded or 'N/A'}")
print(f"Branches: {', '.join(details.branches) if details.branches else 'N/A'}")
print(f"Number of Employees: {details.number_of_employees or 'N/A'}")
print(f"Summary: {details.summary or 'N/A'}")

# Function to handle button click 
def on_button_click(b):  
    institution_name = text_box.value 
    try: 
        details = fetch_institution_details(institution_name)  
        display_institution_details(details) 
    except ValueError as e:  
print(e)

# Create input box and button  
text_box = widgets.Text( 
    value='', 
    placeholder='Enter the institution name', 
    description='Institution:', 
    disabled=False 
) 

button = widgets.Button( 
    description='Fetch Details', 
    disabled=False, 
    button_style='', 
    tooltip='Click to fetch institution details', 
    icon='search' 
) 

# Set up button click event 
button.on_click(on_button_click)  

# Display input box and button  
display(text_box, button)'''

p10='''
!pip install langchain cohere wikipedia-api pydantic  
!pip install langchain_community  

# Import necessary libraries 
from langchain import PromptTemplate, LLMChain
from langchain.llms import Cohere
from pydantic import BaseModel
from typing import Optional
import wikipediaapi

# Step 1: Set up the Cohere API 
import getpass
COHERE_API_KEY = getpass.getpass('Enter your Cohere API Key: ')  
cohere_llm = Cohere(cohere_api_key=COHERE_API_KEY, model="command")  

# Step 2: Download Indian Penal Code (IPC) summary from Wikipedia  
def fetch_ipc_summary():  
    user_agent = "IPCChatbot/1.0 (contact: myemail@example.com)" 
    wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')  
    page = wiki_wiki.page("Indian Penal Code")  
    if not page.exists(): 
        raise ValueError("The Indian Penal Code page does not exist on Wikipedia.") 
    return page.text[:5000]  # Limiting to first 5000 characters for brevity 

ipc_content = fetch_ipc_summary() 

# Step 3: Define a Pydantic model for structured responses 
class IPCResponse(BaseModel):  
    section: Optional[str] 
    explanation: Optional[str]  

# Step 4: Create a prompt template for the chatbot 
prompt_template = PromptTemplate( 
    input_variables=["question"],  
    template=""" You are a legal assistant chatbot specialized in the Indian Penal Code (IPC). Refer to the 
following IPC document content to answer the user's query: 
{ipc_content} 
User Question: {question}  
Provide a detailed answer, mentioning the relevant section if applicable. """ 
)  

# Step 5: Function to interact with the chatbot 
def get_ipc_response(question: str) -> IPCResponse:  
    formatted_prompt = prompt_template.format(ipc_content=ipc_content, question=question) 
    response = cohere_llm.predict(formatted_prompt)  
    
    # Extracting and structuring the response 
    if "Section" in response:  
        section = response.split('Section')[1].split(':')[0].strip() 
        explanation = response.split(':', 1)[-1].strip()  
    else: 
        section = None 
        explanation = response.strip() 
    
    return IPCResponse(section=section, explanation=explanation) 

# Step 6: Set up interactive chatbot in Jupyter  
from IPython.display import display
import ipywidgets as widgets

# Function to display chatbot responses  
def display_response(response: IPCResponse): 
print(f"Section: {response.section if response.section else 'N/A'}")
print(f"Explanation: {response.explanation}")

# Function to handle user input  
def on_button_click(b): 
    user_question = text_box.value 
    try:  
        response = get_ipc_response(user_question) 
        display_response(response)  
    except Exception as e: 
print(f"Error: {e}")

# Create text box and button for user input  
text_box = widgets.Text( 
    value='', 
    placeholder='Ask about the Indian Penal Code', 
    description='You:', 
    disabled=False 
) 

button = widgets.Button( 
    description='Ask', 
    disabled=False, 
    button_style='', 
    tooltip='Click to ask a question about IPC', 
    icon='legal' 
)  

button.on_click(on_button_click) 

# Display the chatbot interface  
display(text_box, button)'''
