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
from collections import defaultdict

from createUserPersona.jobTitlesList import job_titles

import json


# Create your views here.
def index(request):
    return render(request, 'createUserPersona/index.html')

def letsGo(request):
    konten = request.POST['konten']
    
    preprocessed_konten = preprocessingWithSpacy(konten)
    created_persona = createUserPersona(preprocessed_konten)

    sentences_with_entities = findingSentencesWithEntities(konten)
    potential_entities = profilingEntities(sentences_with_entities)

    

    created_persona_dict = json.loads(created_persona)
    potential_entities_dict = json.loads(potential_entities)

    print(potential_entities)

    combined_user_persona = created_persona_dict + potential_entities_dict
    print(combined_user_persona)
    combined_user_persona = MergeAndSort(combined_user_persona)
    print(combined_user_persona)
    


    send_to_render = {'user_persona': combined_user_persona}


    
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

            # mencari job title
            job_matcher = PhraseMatcher(nlp.vocab)
            jabatan = job_titles

            patterns_job = [nlp.make_doc(text) for text in jabatan]
            job_matcher.add("TerminologyList", patterns_job)

            nama_jabatan = ""
            job_titles_found = job_matcher(go)
            for match_id, start, end in job_titles_found:
                nama_jabatan = go[start:end]
                print(go[start:end])

            goals_found = []
            for match_id, start, end in matches3:
                string_id = nlp.vocab.strings[match_id]  # Get string representation
                span = go[start:end]  # The matched span
                goals_found.append(span.text)
                print(nomor_goals, span.text)
                nomor_goals = nomor_goals+1   
            print("===========================")

            ketemu = UserPersona(nama, kerja, str(nama_jabatan), goals_found)
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
    ketemu = UserPersona('User', 'N/A', 'N/A', no_entities)
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

# mencari kalimat yang ber entitas
def findingSentencesWithEntities(input):
    doc = nlp(input)

    who_aspect = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "ORG":
            who_aspect.append(ent.text)

    who_aspect = np.unique(who_aspect)

    print(who_aspect)

    matcher = PhraseMatcher(nlp.vocab)
    terms = who_aspect.tolist()

    # Only run nlp.make_doc to speed things up
    patterns = [nlp.make_doc(text) for text in terms]
    matcher.add("TerminologyList", patterns)

    filtered_sentences = []
    for sent in doc.sents:
        for match_id, start, end in matcher(nlp(sent.text)):
            if nlp.vocab.strings[match_id] in ["TerminologyList"]:
                filtered_sentences.append(sent.text)

    filtered_sentences = np.unique(filtered_sentences)

    print(filtered_sentences)

    return filtered_sentences

# profiling entitas
def profilingEntities(sentences):
    list_of_user_persona = []
    list_of_names = []
    
    for each in sentences:
        go = nlp((str(each)))
        token_types = [token.ent_type_ for token in go]

        if('PERSON' in token_types) or ('ORG' in token_types):

            # mencari nama
            for ent in go.ents:
                if ent.label_ == "PERSON":
                    nama = ent.text
                    print('Person:' + ent.text)
                    break
                if ent.label_ == "ORG":
                    nama = ent.text
                    print('Organization:' + ent.text)
                    pass     
            
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

            # mencari job title
            job_matcher = PhraseMatcher(nlp.vocab)
            jabatan = job_titles

            patterns_job = [nlp.make_doc(text) for text in jabatan]
            job_matcher.add("TerminologyList", patterns_job)

            nama_jabatan = ""
            job_titles_found = job_matcher(go)
            for match_id, start, end in job_titles_found:
                nama_jabatan = go[start:end]
                print(go[start:end])

            baru = UserPersona(nama, kerja, str(nama_jabatan), [])
            list_of_user_persona.append(baru.__dict__)
        
        res_list = []
        for i in range(len(list_of_user_persona)):
            if list_of_user_persona[i] not in list_of_user_persona[i + 1:]:
                res_list.append(list_of_user_persona[i])
        print('res list', res_list)
        json_hasil = json.dumps(res_list)

    return json_hasil

def merge_dict(d1, d2):
    dd = defaultdict(list)

    for d in (d1, d2):
        for key, value in d.items():
            if isinstance(value, list):
                dd[key].extend(value)
            else:
                dd[key].append(value)
    return dict(dd)

# kelas untuk object userpersona
class UserPersona:
    def __init__(self, name, work="", job_title="", goals=[]):
        self.name = name
        self.work = work
        self.goals = goals
        self.job_title = job_title

# function untuk menggabungkan dictionary dan mensortir persona
def MergeAndSort(baca_json):
    name_sementara = []
    for each in baca_json:
        name_sementara.append(each['name'])

    name_sementara = np.unique(name_sementara)

    from operator import itemgetter
    baca_json = sorted(baca_json, key=itemgetter('name', 'goals'), reverse=True) 

    temp = []
    temp_nama = None
    temp_kerja = None
    temp_organisasi = None

    Sorted_Filtered_Persona = []

    for nama in name_sementara:
        for each in baca_json:
            if each['name'] == nama:
                if each['goals']:
                    temp.extend(each['goals'])

                if each['job_title']:
                    temp_kerja = each['job_title']

                if each['work']:
                    temp_organisasi = each['work']

                temp_nama = nama
                
            else:
                if len(temp) > 1:
                    print("hi")

                if temp_nama:
                    Sorted_Filtered_Persona.append(UserPersona(temp_nama, temp_organisasi, temp_kerja, temp).__dict__)
                    print(temp_nama, temp_kerja, temp_organisasi, temp)
                    
                temp = []
                temp_nama = [] 
                temp_kerja = []
                temp_organisasi = []


    return Sorted_Filtered_Persona
