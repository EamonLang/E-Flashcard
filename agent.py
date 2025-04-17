import spacy
from spacy.tokens import Token
import numpy as np
from spellchecker import SpellChecker
import wikipedia
spell = SpellChecker()


nlp = spacy.load("custom_ner_model")

training_text = "In Italy, you can enjoy pasta, pizza, and gelato; in Japan, you can savor sushi, ramen, and tempura; in Mexico, you can eat tacos, burritos, and guacamole; in India, you can relish curry, samosas, and naan; in France, you can indulge in croissants, baguettes, and coq au vin; in Thailand, you can taste pad Thai, green curry, and mango sticky rice; in Greece, you can have souvlaki, moussaka, and baklava; in China, you can feast on dumplings, Peking duck, and sweet and sour pork; in Brazil, you can enjoy feijoada, pão de queijo, and caipirinha; in the United States, you can devour burgers, hot dogs, and apple pie; in Spain, you can savor paella, tapas, and churros."

text = "Pizza in france"
# search wikipedia based on topic
def search(topic):
    try:
        return wikipedia.summary(topic,sentences=2)
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
    for token in doc:

        if token.pos_ == 'NOUN':
            ms = nlp.vocab.vectors.most_similar(
            np.asarray([nlp.vocab.vectors[nlp.vocab.strings[token.text]]]), n=8)
            words = [nlp.vocab.strings[w] for w in ms[0][0]]
            # only allow words that are different enough so we dont get plurals
            cleaned_words = [w for w in words if token.text.lower()[:len(w)//2] not in w.lower()]
            # add to the dictionary
            word_dic[f"{token.text}"] = cleaned_words
            # search for the words
            for words in word_dic:
                information[words] = search(words)
        elif token.ent_type_ == "COUNTRY" or token.ent_type_ == "FOOD":
            summary2 = search(token.text)
            information[token.text] = summary2
            card = flashcard(summary2,token.text)
            flashcards['Card'] = card
            # word_dic[token.text] = information

    return word_dic, information, flashcards

# checks how accurate the training was
def check_training(text):
    doc = nlp(text)
    for token in doc:
        if token.ent_type_ == "COUNTRY" or token.ent_type_ == "FOOD":
            print(f"{token.text}-->{token.ent_type_}")
        else:
            print(token.text)







def flashcard(text,keyword):
    card ={}
    sentences = text.split(".")
    sentences.remove("")
    card['Name'] = keyword
    for i,sentence in enumerate(sentences):
        print(f"sentence: {sentence.lower()}, Keyword: {keyword.lower()}")   
        if keyword.lower() in sentence.lower():
            new_sentence = sentence.lower().replace(keyword,"____")
            print("replaced")
            card[f"question-{i}"] = new_sentence
            card[f"answer-{i}"] = keyword
            continue
        else:
            card[f"question-{i}"] = f"What is this about? --> {sentence}"
            card[f"answer-{i}"] = keyword
        
            continue
    
    print(f"cards\n{card}\ncards")
    
print(find_information(text))    