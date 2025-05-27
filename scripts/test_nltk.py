import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

print("NLTK version:", nltk.__version__)

try:
    lemmatizer = WordNetLemmatizer()
    print("WordNetLemmatizer initialized successfully")
    
    try:
        result = lemmatizer.lemmatize('running')
        print(f"Lemmatized 'running' to: '{result}'")
    except Exception as e:
        print(f"Error lemmatizing: {str(e)}")
        
except Exception as e:
    print(f"Error initializing WordNetLemmatizer: {str(e)}")

# Check wordnet corpus
try:
    print("WordNet synsets for 'car':", wordnet.synsets('car')[:2])
except Exception as e:
    print(f"Error accessing WordNet: {str(e)}")
