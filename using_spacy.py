import spacy
nlp = spacy.load('en_core_web_sm')
import json
import string
import re
from spacy.matcher import PhraseMatcher

def preprocessing(paragraph):
    sentence = paragraph

    # remove number
    sentence = re.sub(r"\d+", "", sentence)

    # remove punctuation
    sentence = sentence.replace("."," ")
    sentence = sentence.translate(str.maketrans("","",string.punctuation))

    # remove whitespace
    sentence = sentence.strip()

    # remove double whitespace
    sentence = re.sub('\s+',' ',sentence)

    return sentence

def pre_process_spacy(paragraph):
    doc = nlp(paragraph)
    
    return doc

file = open('items.json')
source = json.load(file)

for konten in source:
    konten['konten'] = preprocessing(konten['konten'])

print(konten)




