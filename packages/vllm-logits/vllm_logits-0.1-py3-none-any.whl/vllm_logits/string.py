import re
import nltk
import random
import string

try:
    STOPWORDS = set(nltk.corpus.stopwords.words('english'))
except:
    nltk.download("stopwords")
    nltk.download('punkt')
    STOPWORDS = set(nltk.corpus.stopwords.words('english'))

BOOLEAN_STRINGS = ["true", "false", "yes", "no", "1", "0"]

def multi_space_to_single_space(text: str) -> str:
    return re.sub(' +', ' ', text)

def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except ValueError:
        return False
    
def is_number(string: str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def generate_random_str(size: int=6, chars=string.ascii_uppercase + string.digits)-> str:
    return ''.join(random.choice(chars) for _ in range(size))

def remove_substring(text: str, sub_str: str) -> str:
    # The thrid argument of str.maketrans is a string of characters to be removed
    return text.replace(sub_str, "")

def remove_characters(text: str, characters: str) -> str:
    return text.translate(str.maketrans('', '', characters))

def remove_punctuation(text: str) -> str:
    return remove_characters(text, string.punctuation)