import joblib
import re
from urllib.parse import urlparse
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the trained model
# model = joblib.load(r"StressidentificationNLP")
model = joblib.load(r"D:\10_Projects\Main Projects\Decision support system (Mental Health)\My_Health_Hero\StressidentificationNLP")

# Load the vectorizer
# vectorizer = joblib.load(r"TfidfVectorizer.joblib")
vectorizer = joblib.load(r"D:\10_Projects\Main Projects\Decision support system (Mental Health)\My_Health_Hero\TfidfVectorizer.joblib")

# Define preprocessing functions
def text_process(text):
    # Remove brackets
    text = re.sub('[][)(]', ' ', text)
    # Remove URLs
    text = [word for word in text.split() if not urlparse(word).scheme]
    text = ' '.join(text)
    # Remove escape characters
    text = re.sub(r'\@\w+', '', text)
    # Remove HTML tags
    text = re.sub(re.compile("<.*?>"), '', text)
    # Keep only alphanumeric characters
    text = re.sub("[^A-Za-z0-9]", ' ', text)
    # Convert to lowercase
    text = text.lower()
    # Tokenize text
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Function to predict stress
def predictor(text):
    processed_text = text_process(text)
    # Vectorize the text
    processed_text_vectorized = vectorizer.transform([text])
    # Predict using the model
    prediction = model.predict(processed_text_vectorized)
    if prediction[0] == 1:
        return "This person is in stress."
    else:
        return "This person is not in stress."

# Example texts
text1 = """This is the worst thing that happened to me today. I got less marks in my exam, 
            so it is not going to help me in my future."""
text2 = """Hi Shashank sir, I gained a lot of knowledge from you for my future use. 
            This was a very fun journey for me. Thanks for boosting my confidence."""

# Predict stress for the example texts
print(predictor(text1))
print(predictor(text2))

# User input
user_input = input("Enter a text: ")
# Predict stress for user input
print(predictor(user_input))
