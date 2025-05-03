import spacy
from spacy.tokens import Token
import numpy as np
from spellchecker import SpellChecker
import wikipedia
spell = SpellChecker()


nlp = spacy.load("custom_ner_model")


def search(topic,topic_class):
    search_arguments=f"{topic}, ({topic_class})"
    try:
        return wikipedia.summary(search_arguments,sentences=2)
    except Exception as e:
        print(f"Error searching: {e}")

def clean_tokens(text):
    doc = nlp(text)
    tokens =[]
    for token in doc:
        if token.text not in spell:
            correction = spell.correction(token.text)
            print(f"Correction:{correction}")
            tokens.append(f" {correction}")
        else:
            tokens.append(f" {token.text}")
    return "".join(tokens)

def find_information(text):
    clean_text = clean_tokens(text)
    doc = nlp(clean_text)
    word_dic = {}
    information = {}
    flashcards = {}
    
    # index makes sure each flashcard has a unique number so old card does not get over written. Each time a card is created the index in incremented allowing a new unique index for the next card
    index = 1

    # searches for sentence that user inputted and creates general flashcards
    general_search = search(text,"general information")
    card = flashcard(general_search,"GENERAL")
    flashcards[f"Card-{index}"] = card

    # then breaks down word for word and tries to find entities to search and create aditional flashcards
    for token in doc:
        
        if token.ent_type_:
                    print(f"{token.text} --> {token.ent_type_}")
                    summary2 = search(token.text,token.ent_type_)
                    information[token.text] = summary2
                    card = flashcard(summary2,token.text)
                    flashcards[f'Card-{index}'] = card
                    index +=1
        
    print(f"flashcards from find_info\n {flashcards}")
    return word_dic, information, flashcards

def flashcard(text,keyword):
    card ={}
    try:
        sentences = text.split(".")
        sentences.remove("")
    except Exception as e:
        print(f"there has been an error is slicing")
        sentences = text
        
    # card['Name'] = keyword
    for i,sentence in enumerate(sentences):
        # print(f"sentence: {sentence.lower()}, Keyword: {keyword.lower()}")   
        if keyword.lower() in sentence.lower():
            new_sentence = sentence.lower().replace(keyword,"____")
            card[f"question-{i}"] = new_sentence
            card[f"answer-{i}"] = keyword
        else:
            card[f"question-{i}"] = f"What is this about? --> {sentence}"
            card[f"answer-{i}"] = keyword
        
    
    # print(f"cards\n{card}\ncards")
    return card

# cards = find_information("pizza")[2]
# # print(cards.values())
# i = 1
# for x in cards.values():
#     for j in x.values():
#         if i%2==0:
#             print(f"question: {j}")
#             i+=1
#         else:
#             print(f"answer:{j}")
#             i+=1
# # print(cards['Card-1']['Name'])