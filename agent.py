import spacy
from spacy.tokens import Token
import numpy as np
from spellchecker import SpellChecker
import wikipedia
spell = SpellChecker()


nlp = spacy.load("custom_ner_model")

training_text = "We had coffee in Berlin yesterday.I have always dreamed of visiting Rio de Janeiro.Chicago winters are brutal.She moved from Seoul to New York.Bangkok has the best street markets.I've been playing basketball every weekend.Surfing looks so fun but also scary.Do you like to watch soccer or baseball more? They went skiing in the Alps.Fencing requires quick reflexes.Pandas are my favorite animals at the zoo.We saw a group of dolphins near the boat. Bats usually sleep during the day.Kangaroos can jump really high. The tiger stared directly at us.She learned Japanese before moving to Tokyo.Many people in Brazil speak Portuguese. I think German sounds very strong.He's studying Arabic at the university.Do you want to practice some French together? I traveled from Paris to Barcelona while practicing my Spanish.The kids learned some Korean after watching a documentary about Seoul.While in Sydney, we went surfing and saw kangaroos nearby.After playing volleyball in Dubai, we enjoyed some Arabic food. Lions are often associated with cities like Cairo in ancient myths."

text = input("create flashcards for: ")
# search wikipedia based on topic
def search(topic,topic_class):
    search_arguments=f"{topic}, ({topic_class})"
    try:
        return wikipedia.summary(search_arguments,sentences=2)
    except Exception as e:
        print(f"Error searching: {e}")
# cleans token is there are any spelling mistakes on input
# will be more useful when its on the website
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
    
    
    # create dictionatry to store words

# takes the cleaned text information and searches wikipedia
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
                    # word_dic[token.text] = information
        # so if it does not recognize theres an ent on the noun then it will also search for it. Otherwise it will skip it
        elif token.pos_ == 'NOUN' and not token.ent_type_:
            ms = nlp.vocab.vectors.most_similar(
            np.asarray([nlp.vocab.vectors[nlp.vocab.strings[token.text]]]), n=8)
            words = [nlp.vocab.strings[w] for w in ms[0][0]]
            # only allow words that are different enough so we dont get plurals
            cleaned_words = [w for w in words if token.text.lower()[:len(w)//2] not in w.lower()]
            # add to the dictionary
            word_dic[f"{token.text}"] = cleaned_words
            # search for the words
            for words in word_dic:
                words_info = search(words,words)
                card = flashcard(words_info,words)
                flashcards[f'Card-{index}'] = card
                index +=1
                information[words] = words_info
        
    print(f"flashcards from find_info\n {flashcards}")
    return word_dic, information, flashcards

# checks how accurate the training was
def check_training(text):
    doc = nlp(text)
    for token in doc:
        if token.ent_type_:
            print(f"{token.text} --> {token.ent_type_}")
        else:
            print(token.text)
            







def flashcard(text,keyword):
    card ={}
    sentences = text.split(".")
    sentences.remove("")
    card['Name'] = keyword
    for i,sentence in enumerate(sentences):
        # print(f"sentence: {sentence.lower()}, Keyword: {keyword.lower()}")   
        if keyword.lower() in sentence.lower():
            new_sentence = sentence.lower().replace(keyword,"____")
            card[f"question-{i}"] = new_sentence
            card[f"answer-{i}"] = keyword
            continue
        else:
            card[f"question-{i}"] = f"What is this about? --> {sentence}"
            card[f"answer-{i}"] = keyword
        
            continue
    
    # print(f"cards\n{card}\ncards")
    return card
    
# print(find_information(text))    

find_information(text)

# check_training(training_text)
