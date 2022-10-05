from venv import create
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib.style import context

import spacy
from yaml import load
nlp = spacy.load('en_core_web_sm')
import numpy as np
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher

import json


# Create your views here.
def index(request):
    return render(request, 'createUserPersona/index.html')

def letsGo(request):
    konten = request.POST['konten']
    
    preprocessed_konten = preprocessingWithSpacy(konten)
    created_persona = createUserPersona(preprocessed_konten)

    load_the_json = json.loads(created_persona)
    send_to_render = {'user_persona': load_the_json}


    
    # return HttpResponse(send_to_render)
    return render(request, 'createUserPersona/result.html', send_to_render)


# function untuk membuat user persona
def createUserPersona(group_of_sentences):
    matcher = Matcher(nlp.vocab)
    userPersonaCreated = []
    i = 1
    no_entities = []

    for each in group_of_sentences:
        
        go = nlp(str(each))

        token_types = [token.ent_type_ for token in go]
        
        pattern = [{'POS': 'VERB'},
            {'POS': 'ADJ'},
            {'POS': 'NOUN'}]
        matcher.add("EndResult", [pattern])
        
        matches3 = matcher(go)

        nomor_goals = 1
            
        # memilah apakah dia memiliki entitas, jika ya, akan langsung dicetak, jika tidak maka akan dimasukkan dalam array
        if('PERSON' in token_types) or ('ORG' in token_types):
            print("====== USER PERSONA ", i, "============")

            # mencari nama
            for ent in go.ents:
                if ent.label_ == "PERSON":
                    nama = ent.text
                    print('Name:' + ent.text)
                    break
                if ent.label_ == "ORG":
                    nama = ent.text
                    print('Name:' + ent.text)
                    break     
            
            # mencari organisasi
            if('PERSON' in token_types) and ('ORG' in token_types):
                for ent in go.ents:
                    if ent.label_== "ORG":
                        kerja = ent.text
                        print('Work:' + ent.text)                    
            else:
                kerja = ""
                print('Work: N/A')
            print()

            goals_found = []
            for match_id, start, end in matches3:
                string_id = nlp.vocab.strings[match_id]  # Get string representation
                span = go[start:end]  # The matched span
                goals_found.append(span.text)
                print(nomor_goals, span.text)
                nomor_goals = nomor_goals+1   
            print("===========================")

            ketemu = UserPersona(nama, kerja, goals_found)
            userPersonaCreated.append(ketemu.__dict__)
        else:
            for match_id, start, end in matches3:
                string_id = nlp.vocab.strings[match_id]  # Get string representation
                span = go[start:end]  # The matched span
                no_entities.append(span.text)
            continue
        
        i = i+1

        print()

    print("====== USER PERSONA ", i, "============")
    print('User')
    nomor_no_entities = 1
    for each in no_entities:
        print(nomor_no_entities, each)
        nomor_no_entities = nomor_no_entities+1
    ketemu = UserPersona('User', 'N/A', no_entities)
    userPersonaCreated.append(ketemu.__dict__)
    
    print("===========================")
    json_hasil = json.dumps(userPersonaCreated)


    return json_hasil

# preprocessing dengan spacy
def preprocessingWithSpacy(input):
    doc = nlp(input)

    # menggunakan lemmatized form
    # lemmatized_words = " ".join([token.lemma_ for token in doc])
    # doc = nlp(lemmatized_words)

    # mencari pattern goals
    matcher = Matcher(nlp.vocab)
    pattern = [{'POS': 'VERB'},
            {'POS': 'ADJ'},
            {'POS': 'NOUN'}]
    matcher.add("HelloWorld", [pattern])
    
    filtered_goals = []
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        print(match_id, string_id, start, end, span.text)
        filtered_goals.append(span.text)

    # mencari kalimat-kalimat yang mengandung goals
    matcher = PhraseMatcher(nlp.vocab)
    docs_for_pattern_goals = [nlp.make_doc(text) for text in filtered_goals]
    matcher.add("MencariKalimatMengandungGoals", docs_for_pattern_goals)

    filtered_sentences_containing_goals = []
    for sent in doc.sents:
        for match_id, start, end in matcher(nlp(sent.text)):
            if nlp.vocab.strings[match_id] in ["MencariKalimatMengandungGoals"]:
                filtered_sentences_containing_goals.append(sent.text)

    filtered_sentences_containing_goals = np.unique(filtered_sentences_containing_goals)
    a = 1
    for i in filtered_sentences_containing_goals:
        print(a, i)
        a=a+1
    
    return filtered_sentences_containing_goals

# kelas untuk object userpersona
class UserPersona:
    def __init__(self, name, work="", goals=[]):
        self.name = name
        self.work = work
        self.goals = goals
