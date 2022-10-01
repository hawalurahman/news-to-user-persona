from html import entities
from itertools import count
from lib2to3.pgen2 import token
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import json
import string
import re
from nltk.tag import pos_tag


file = open('items.json')
data = json.load(file)

for each in data:
    sentence = each["konten"]

    # turn to lower case
    lowercase_sentence = sentence.lower()
    print(lowercase_sentence)
    print()

    # remove number
    lowercase_sentence = re.sub(r"\d+", "", lowercase_sentence)

    # remove punctuation
    lowercase_sentence = lowercase_sentence.replace("."," ")
    lowercase_sentence = lowercase_sentence.translate(str.maketrans("","",string.punctuation))

    # remove whitespace
    lowercase_sentence = lowercase_sentence.strip()

    # remove double whitespace
    lowercase_sentence = re.sub('\s+',' ',lowercase_sentence)

    # tokenizing
    tokens = nltk.tokenize.word_tokenize(lowercase_sentence)
    print(tokens)
    print()
    print('count of tokenized words: '+ str(len(tokens)))
    print()

    # stopword
    stop_words = set(stopwords.words('english'))
    word_tokens_no_stopwords = [w for w in tokens if not w in stop_words]
    print(word_tokens_no_stopwords)
    print()
    print('count of stopword removed words: '+ str(len(word_tokens_no_stopwords)))
    print()

    # lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized = []
    for kata in word_tokens_no_stopwords:
        hasil = lemmatizer.lemmatize(kata)
        lemmatized.append(hasil)
        print(kata, hasil)
    print(lemmatized)

    # pos tagging
    pos_tagged = pos_tag(lemmatized)
    print()
    print(pos_tagged)

    # add to json
    each['preprocessed'] = tokens
    
    # print()
    # print('Tokenizing Result : \n') 
    # print(tokens)
    # print(each)



