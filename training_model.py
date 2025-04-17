import spacy
from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy.training import Example
import json
from spacy.tokens import DocBin
import numpy as np
from spellchecker import SpellChecker
import wikipedia
spell = SpellChecker()
from tqdm import tqdm
import random

TRAIN_DATA_FOOD = [
    ("I love eating pizza with extra cheese", {"entities": [(14, 19, "FOOD")]}),
    ("Sushi is my favorite Japanese dish", {"entities": [(0, 5, "FOOD")]}),
    ("I had spaghetti for dinner last night", {"entities": [(6, 15, "FOOD")]}),
    ("Can you make a sandwich with turkey and cheese?", {"entities": [(15, 23, "FOOD"), (29, 35, "FOOD"), (40, 46, "FOOD")]}),
    ("Breakfast today was eggs, bacon, and toast", {"entities": [(20, 24, "FOOD"), (26, 31, "FOOD"), (37, 42, "FOOD")]}),
    ("Chocolate cake is my dessert of choice", {"entities": [(0, 14, "FOOD")]}),
    ("She made a delicious bowl of soup for lunch", {"entities": [(33, 37, "FOOD")]}),
    ("Do you prefer an apple or an orange?", {"entities": [(18, 23, "FOOD"), (31, 37, "FOOD")]}),
    ("I enjoy a cup of coffee in the morning", {"entities": [(16, 22, "FOOD")]}),
    ("Freshly baked bread smells amazing", {"entities": [(15, 20, "FOOD")]}),
    ("She had a burger and fries for dinner", {"entities": [(10, 16, "FOOD"), (21, 26, "FOOD")]}),
    ("A bowl of cereal is perfect for breakfast", {"entities": [(10, 16, "FOOD")]}),
    ("I can't wait to try the lasagna at the restaurant", {"entities": [(25, 32, "FOOD")]}),
    ("Peanut butter and jelly sandwich is a classic", {"entities": [(0, 13, "FOOD"), (18, 24, "FOOD"), (13, 30, "FOOD")]}),
    ("How about some spaghetti with meatballs?", {"entities": [(16, 25, "FOOD"), (31, 40, "FOOD")]}),
    ("We had grilled chicken with vegetables", {"entities": [(7, 22, "FOOD"), (28, 39, "FOOD")]}),
    ("I love homemade apple pie", {"entities": [(17, 26, "FOOD")]}),
    ("Pasta with marinara sauce is my comfort food", {"entities": [(0, 5, "FOOD"), (11, 25, "FOOD")]}),
    ("A slice of watermelon is refreshing on a hot day", {"entities": [(10, 20, "FOOD")]}),
    ("My mom makes the best pancakes", {"entities": [(24, 32, "FOOD")]}),
    ("Grilled salmon with garlic butter is so tasty", {"entities": [(0, 14, "FOOD"), (20, 33, "FOOD")]}),
    ("I had a slice of pizza for lunch", {"entities": [(17, 22, "FOOD")]}),
]


TRAIN_DATA_COUNTRIES = [
    ("I am planning a trip to France this summer", {"entities": [(24, 30, "COUNTRY")]}),
    ("Germany has a rich history and beautiful landscapes", {"entities": [(0, 7, "COUNTRY")]}),
    ("Canada is known for its maple syrup and cold winters", {"entities": [(0, 6, "COUNTRY")]}),
    ("Brazil hosted the World Cup in 2014", {"entities": [(0, 6, "COUNTRY")]}),
    ("India has a diverse culture and cuisine", {"entities": [(0, 5, "COUNTRY")]}),
    ("The United States is a popular tourist destination", {"entities": [(4, 18, "COUNTRY")]}),
    ("I have relatives living in Italy", {"entities": [(27, 32, "COUNTRY")]}),
    ("Australia is famous for its wildlife and beaches", {"entities": [(0, 9, "COUNTRY")]}),
    ("The Eiffel Tower is located in Paris, France", {"entities": [(38, 44, "COUNTRY")]}),
    ("China has a long history and a large population", {"entities": [(0, 5, "COUNTRY")]}),
    ("Japan is a leader in technology and innovation", {"entities": [(0, 5, "COUNTRY")]}),
    ("South Africa is known for its wildlife and safaris", {"entities": [(0, 12, "COUNTRY")]}),
    ("Mexico is famous for its tacos and vibrant culture", {"entities": [(0, 6, "COUNTRY")]}),
    ("Argentina's capital is Buenos Aires", {"entities": [(0, 9, "COUNTRY")]}),
    ("Egypt is home to the ancient pyramids", {"entities": [(0, 5, "COUNTRY")]}),
    ("I would love to visit Greece next year", {"entities": [(22, 28, "COUNTRY")]}),
    ("The UK is famous for its royal family", {"entities": [(4, 6, "COUNTRY")]}),
    ("Russia spans across Europe and Asia", {"entities": [(0, 6, "COUNTRY")]}),
    ("Mexico is bordered by the United States to the north", {"entities": [(0, 6, "COUNTRY"), (26, 39, "COUNTRY")]}),
    ("Turkey is located between Europe and Asia", {"entities": [(0, 6, "COUNTRY")]}),
    ("Norway has stunning fjords and a rich cultural heritage", {"entities": [(0, 6, "COUNTRY")]}),
    ("Sweden is known for its high quality of life", {"entities": [(0, 6, "COUNTRY")]}),
    ("The Netherlands is famous for its tulips and windmills", {"entities": [(4, 16, "COUNTRY")]}),
]



food_data = [
    ("Italian pizza is good.",{"entities":[(8,13,"FOOD")]}),
    ("I ate chicken with rice",{"entities":[(6,13,"FOOD"),(19,23,"FOOD")]}),
    ("I love sushi and hamburgers",{"entities":[(7,12,"FOOD"),(17,27,"FOOD")]}),
    ("I had a warm bowl of tomato soup for lunch.", {"entities": [(21, 32, "FOOD")]}),  
    ("She sprinkled cinnamon on her oatmeal this morning.", {"entities": [(14, 22, "FOOD"), (30, 37, "FOOD")]}),  
    ("They ordered a large pepperoni pizza for the party.", {"entities": [(21, 36, "FOOD")]}),  
    ("He made guacamole with ripe avocados and lime juice.", {"entities": [(8, 17, "FOOD"), (28, 36, "FOOD"), (41, 51, "FOOD")]}),  
    ("We grilled hamburgers in the backyard over charcoal.", {"entities": [(11, 21, "FOOD")]}),  
    ("I brought a bag of pretzels for the road trip.", {"entities": [(19, 27, "FOOD")]}),  
    ("She baked banana bread with walnuts and dark chocolate.", {"entities": [(10, 22, "FOOD"), (28, 35, "FOOD"), (40, 54, "FOOD")]}),  
    ("He stirred honey into his green tea for sweetness.", {"entities": [(11, 16, "FOOD"), (26, 35, "FOOD")]}),  
    ("They served fried rice with soy sauce and scallions.", {"entities": [(12, 22, "FOOD"), (28, 37, "FOOD"), (42, 51, "FOOD")]}),  
    ("She snacked on baby carrots and hummus during the movie.", {"entities": [(15, 27, "FOOD"), (32, 38, "FOOD")]}),  
    ("I made spaghetti with homemade marinara sauce.", {"entities": [(7, 16, "FOOD"), (31, 45, "FOOD")]}),  
    ("We had scrambled eggs with chives for breakfast.", {"entities": [(7, 21, "FOOD"), (27, 33, "FOOD")]}),  
    ("She dipped strawberries into melted chocolate.", {"entities": [(11, 23, "FOOD"), (29, 45, "FOOD")]}),  
    ("He roasted sweet potatoes with rosemary and olive oil.", {"entities": [(11, 25, "FOOD"), (31, 39, "FOOD"), (44, 53, "FOOD")]}),  
    ("They ordered shrimp tacos with spicy salsa.", {"entities": [(13, 25, "FOOD"), (37, 42, "FOOD")]}),  
    ("I love eating sourdough toast with almond butter.", {"entities": [(14, 29, "FOOD"), (35, 48, "FOOD")]}),  
    ("She packed a turkey sandwich and an apple for lunch.", {"entities": [(13, 28, "FOOD"), (36, 41, "FOOD")]}),  
    ("He topped his burger with lettuce, tomato, and pickles.", {"entities": [(14, 20, "FOOD"), (26, 33, "FOOD"), (35, 41, "FOOD"), (47, 54, "FOOD")]}),  
    ("We made a fruit salad with melon, berries, and grapes.", {"entities": [(10, 21, "FOOD"), (27, 32, "FOOD"), (34, 41, "FOOD"), (47, 53, "FOOD")]}),  
    ("She added sliced cucumbers to her water for a refreshing drink.", {"entities": [(17, 26, "FOOD")]}),  
    ("He made an omelet with mushrooms, spinach, and feta.", {"entities": [(11, 17, "FOOD"), (23, 32, "FOOD"), (34, 41, "FOOD"), (47, 51, "FOOD")]}),  
    ("They bought cinnamon rolls from the local bakery.", {"entities": [(12, 26, "FOOD")]}),  
    ("I made pancakes with maple syrup and blueberries.", {"entities": [(7, 15, "FOOD"), (21, 32, "FOOD"), (37, 48, "FOOD")]}),  
    ("She cooked quinoa with roasted vegetables.", {"entities": [(11, 17, "FOOD"), (31, 41, "FOOD")]}),  
    ("He brought a container of Greek yogurt and granola.", {"entities": [(26, 38, "FOOD"), (43, 50, "FOOD")]}),  
    ("They enjoyed a plate of nachos with melted cheese.", {"entities": [(24, 30, "FOOD"), (36, 49, "FOOD")]}),  
    ("She made a smoothie with kale, banana, and mango.", {"entities": [(11, 19, "FOOD"), (25, 29, "FOOD"), (31, 37, "FOOD"), (43, 48, "FOOD")]}),  
    ("He baked a chocolate chip cookie the size of a plate.", {"entities": [(10, 33, "FOOD")]}),  
    ("We made a big pot of chili with kidney beans and beef.", {"entities": [(21, 26, "FOOD"), (32, 44, "FOOD"), (49, 53, "FOOD")]}),  
    ("She bought a bag of trail mix for hiking.", {"entities": [(20, 29, "FOOD")]}),  
    ("He toasted a bagel and added cream cheese.", {"entities": [(13, 18, "FOOD"), (29, 41, "FOOD")]}),  
    ("They grilled asparagus and zucchini on skewers.", {"entities": [(13, 22, "FOOD"), (27, 35, "FOOD")]}),  
    ("She brought deviled eggs to the picnic.", {"entities": [(12, 24, "FOOD")]}),  
    ("He ate a bowl of cereal with cold milk.", {"entities": [(17, 23, "FOOD"), (34, 38, "FOOD")]}),  
    ("We shared a box of sushi rolls at lunch.", {"entities": [(19, 24, "FOOD")]}),  
    ("She picked fresh raspberries from the garden.", {"entities": [(17, 28, "FOOD")]}),  
    ("He sipped coconut water after his workout.", {"entities": [(10, 23, "FOOD")]}),  
    ("They baked a pie filled with fresh peaches.", {"entities": [(29, 42, "FOOD")]}),  
    ("I packed a thermos of chicken noodle soup.", {"entities": [(22, 41, "FOOD")]}),  
    ("She added basil and mozzarella to her caprese salad.", {"entities": [(10, 15, "FOOD"), (20, 30, "FOOD"), (38, 51, "FOOD")]}),  
    ("He enjoyed a bowl of pho with extra noodles.", {"entities": [(21, 24, "FOOD"), (36, 43, "FOOD")]}),  
    ("They made crepes with lemon and powdered sugar.", {"entities": [(10, 16, "FOOD"), (22, 27, "FOOD"), (32, 46, "FOOD")]}),  
    ("She stirred peanut butter into her smoothie.", {"entities": [(12, 25, "FOOD"), (35, 43, "FOOD")]}),  
    ("He cooked a steak with garlic butter.", {"entities": [(12, 17, "FOOD"), (23, 36, "FOOD")]}),  
    ("We had corn on the cob with our barbecue.", {"entities": [(7, 22, "FOOD")]}),  
    ("She brought chocolate-covered almonds to the game.", {"entities": [(12, 37, "FOOD")]}),  
    ("He tried falafel in a pita with tahini sauce.", {"entities": [(9, 16, "FOOD"), (32, 44, "FOOD")]}),  
    ("They shared a bowl of mac and cheese.", {"entities": [(22, 36, "FOOD")]}),  
    ("I made garlic bread to go with the pasta.", {"entities": [(7, 19, "FOOD"), (35, 40, "FOOD")]}),  
    ("She snacked on rice cakes and peanut butter.", {"entities": [(15, 25, "FOOD"), (30, 43, "FOOD")]})

]

COMBINED_TRAIN_DATA = [
    # Country Data
    ("I am planning a trip to France this summer", {"entities": [(24, 30, "COUNTRY")]}),
    ("Germany has a rich history and beautiful landscapes", {"entities": [(0, 7, "COUNTRY")]}),
    ("Canada is known for its maple syrup and cold winters", {"entities": [(0, 6, "COUNTRY")]}),
    ("Brazil hosted the World Cup in 2014", {"entities": [(0, 6, "COUNTRY")]}),
    ("India has a diverse culture and cuisine", {"entities": [(0, 5, "COUNTRY")]}),
    ("The United States is a popular tourist destination", {"entities": [(4, 18, "COUNTRY")]}),
    ("I have relatives living in Italy", {"entities": [(27, 32, "COUNTRY")]}),
    ("Australia is famous for its wildlife and beaches", {"entities": [(0, 9, "COUNTRY")]}),
    ("The Eiffel Tower is located in Paris, France", {"entities": [(38, 44, "COUNTRY")]}),
    ("China has a long history and a large population", {"entities": [(0, 5, "COUNTRY")]}),
    ("Japan is a leader in technology and innovation", {"entities": [(0, 5, "COUNTRY")]}),
    ("South Africa is known for its wildlife and safaris", {"entities": [(0, 12, "COUNTRY")]}),
    ("Mexico is famous for its tacos and vibrant culture", {"entities": [(0, 6, "COUNTRY")]}),
    ("Argentina's capital is Buenos Aires", {"entities": [(0, 9, "COUNTRY")]}),
    ("Egypt is home to the ancient pyramids", {"entities": [(0, 5, "COUNTRY")]}),
    ("I would love to visit Greece next year", {"entities": [(22, 28, "COUNTRY")]}),
    ("The UK is famous for its royal family", {"entities": [(4, 6, "COUNTRY")]}),
    ("Russia spans across Europe and Asia", {"entities": [(0, 6, "COUNTRY")]}),
    ("Mexico is bordered by the United States to the north", {"entities": [(0, 6, "COUNTRY"), (26, 39, "COUNTRY")]}),
    ("Turkey is located between Europe and Asia", {"entities": [(0, 6, "COUNTRY")]}),
    ("Norway has stunning fjords and a rich cultural heritage", {"entities": [(0, 6, "COUNTRY")]}),
    ("Sweden is known for its high quality of life", {"entities": [(0, 6, "COUNTRY")]}),
    ("The Netherlands is famous for its tulips and windmills", {"entities": [(4, 16, "COUNTRY")]}),
    
    # Food Data
    ("Italian pizza is good.",{"entities":[(8,13,"FOOD")]}),
    ("I ate chicken with rice",{"entities":[(6,13,"FOOD"),(19,23,"FOOD")]}),
    ("I love sushi and hamburgers",{"entities":[(7,12,"FOOD"),(17,27,"FOOD")]}),
    ("I had a warm bowl of tomato soup for lunch.", {"entities": [(21, 32, "FOOD")]}),  
    ("She sprinkled cinnamon on her oatmeal this morning.", {"entities": [(14, 22, "FOOD"), (30, 37, "FOOD")]}),  
    ("They ordered a large pepperoni pizza for the party.", {"entities": [(21, 36, "FOOD")]}),  
    ("He made guacamole with ripe avocados and lime juice.", {"entities": [(8, 17, "FOOD"), (28, 36, "FOOD"), (41, 51, "FOOD")]}),  
    ("We grilled hamburgers in the backyard over charcoal.", {"entities": [(11, 21, "FOOD")]}),  
    ("I brought a bag of pretzels for the road trip.", {"entities": [(19, 27, "FOOD")]}),  
    ("She baked banana bread with walnuts and dark chocolate.", {"entities": [(10, 22, "FOOD"), (28, 35, "FOOD"), (40, 54, "FOOD")]}),  
    ("He stirred honey into his green tea for sweetness.", {"entities": [(11, 16, "FOOD"), (26, 35, "FOOD")]}),  
    ("They served fried rice with soy sauce and scallions.", {"entities": [(12, 22, "FOOD"), (28, 37, "FOOD"), (42, 51, "FOOD")]}),  
    ("She snacked on baby carrots and hummus during the movie.", {"entities": [(15, 27, "FOOD"), (32, 38, "FOOD")]}),  
    ("I made spaghetti with homemade marinara sauce.", {"entities": [(7, 16, "FOOD"), (31, 45, "FOOD")]}),  
    ("We had scrambled eggs with chives for breakfast.", {"entities": [(7, 21, "FOOD"), (27, 33, "FOOD")]}),  
    ("She dipped strawberries into melted chocolate.", {"entities": [(11, 23, "FOOD"), (29, 45, "FOOD")]}),  
    ("He roasted sweet potatoes with rosemary and olive oil.", {"entities": [(11, 25, "FOOD"), (31, 39, "FOOD"), (44, 53, "FOOD")]}),  
    ("They ordered shrimp tacos with spicy salsa.", {"entities": [(13, 25, "FOOD"), (37, 42, "FOOD")]}),  
    ("I love eating sourdough toast with almond butter.", {"entities": [(14, 29, "FOOD"), (35, 48, "FOOD")]}),  
    ("She packed a turkey sandwich and an apple for lunch.", {"entities": [(13, 28, "FOOD"), (36, 41, "FOOD")]}),  
    ("He topped his burger with lettuce, tomato, and pickles.", {"entities": [(14, 20, "FOOD"), (26, 33, "FOOD"), (35, 41, "FOOD"), (47, 54, "FOOD")]}),  
    ("We made a fruit salad with melon, berries, and grapes.", {"entities": [(10, 21, "FOOD"), (27, 32, "FOOD"), (34, 41, "FOOD"), (47, 53, "FOOD")]}),  
    ("She added sliced cucumbers to her water for a refreshing drink.", {"entities": [(17, 26, "FOOD")]}),  
    ("He made an omelet with mushrooms, spinach, and feta.", {"entities": [(11, 17, "FOOD"), (23, 32, "FOOD"), (34, 41, "FOOD"), (47, 51, "FOOD")]}),  
    ("They bought cinnamon rolls from the local bakery.", {"entities": [(12, 26, "FOOD")]}),  
    ("I made pancakes with maple syrup and blueberries.", {"entities": [(7, 15, "FOOD"), (21, 32, "FOOD"), (37, 48, "FOOD")]}),  
    ("She cooked quinoa with roasted vegetables.", {"entities": [(11, 17, "FOOD"), (31, 41, "FOOD")]}),  
    ("He brought a container of Greek yogurt and granola.", {"entities": [(26, 38, "FOOD"), (43, 50, "FOOD")]}),  
    ("They enjoyed a plate of nachos with melted cheese.", {"entities": [(24, 30, "FOOD"), (36, 49, "FOOD")]}),  
    ("She made a smoothie with kale, banana, and mango.", {"entities": [(11, 19, "FOOD"), (25, 29, "FOOD"), (31, 37, "FOOD"), (43, 48, "FOOD")]}),  
    ("He baked a chocolate chip cookie the size of a plate.", {"entities": [(10, 33, "FOOD")]}),  
    ("We made a big pot of chili with kidney beans and beef.", {"entities": [(21, 26, "FOOD"), (32, 44, "FOOD"), (49, 53, "FOOD")]}),  
    ("She bought a bag of trail mix for hiking.", {"entities": [(20, 29, "FOOD")]}),  
    ("He toasted a bagel and added cream cheese.", {"entities": [(13, 18, "FOOD"), (29, 41, "FOOD")]}),  
    ("They grilled asparagus and zucchini on skewers.", {"entities": [(13, 22, "FOOD"), (27, 35, "FOOD")]}),  
    ("She brought deviled eggs to the picnic.", {"entities": [(12, 24, "FOOD")]}),  
    ("He ate a bowl of cereal with cold milk.", {"entities": [(17, 23, "FOOD"), (34, 38, "FOOD")]}),  
    ("We shared a box of sushi rolls at lunch.", {"entities": [(19, 24, "FOOD")]}),  
    ("She picked fresh raspberries from the garden.", {"entities": [(17, 28, "FOOD")]}),  
    ("He sipped coconut water after his workout.", {"entities": [(10, 23, "FOOD")]}),  
    ("They baked a pie filled with fresh peaches.", {"entities": [(29, 42, "FOOD")]}),  
    ("I packed a thermos of chicken noodle soup.", {"entities": [(22, 41, "FOOD")]}),  
    ("She added basil and mozzarella to her caprese salad.", {"entities": [(10, 15, "FOOD"), (20, 30, "FOOD"), (38, 51, "FOOD")]}),  
    ("He had a sandwich with bacon, lettuce, and tomato.", {"entities": [(16, 21, "FOOD"), (23, 29, "FOOD"), (31, 37, "FOOD")]}),  
    ("They ordered a vegetable stir fry with tofu and rice.", {"entities": [(22, 29, "FOOD"), (34, 38, "FOOD"), (43, 47, "FOOD")]}),  
]

nlp = spacy.load("en_core_web_lg")



# used to see how accurate the data set slicing is and if any changes are need
def clean_data(data):
    for text,annot in data:
        doc = nlp.make_doc(text)
        for start,end,label in annot['entities']:
            span = doc.char_span(start,end,label=label,alignment_mode="contract")
            print(f"{text}-->{span}")
clean_data(COMBINED_TRAIN_DATA)

# used to train the module on a specific data set
def train(data,name):
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner,last=True)
    else:
        ner = nlp.get_pipe("ner")
    for names in name:
        if names not in nlp.pipe_labels:
            ner.add_label(names)

    train_examples = []
    for text,annot in data:
        
        doc = nlp.make_doc(text)
        for start,end,Label in annot['entities']:
            spacy.training.offsets_to_biluo_tags(nlp.make_doc(text), annot['entities'])
            span = doc.char_span(start,end,label=Label,alignment_mode="contract")
            span_text = text[start:end]
            spans = []
            if span is None:
                print("skipping entity")
                print(f"Span:{span_text}")
            else:  
                spans.append(span)
            doc.ents = spans
            example = Example.from_dict(doc,annot)
            train_examples.append(example)
    optimizer = nlp.resume_training()

    for epoch in range(20):
        random.shuffle(train_examples)
        losses = {}
        for example in spacy.util.minibatch(train_examples,size=4):
            nlp.update(example,drop=0.5,losses=losses)
        print(f"Epoch {epoch+1}, Losses: {losses}")
    nlp.to_disk("custom_ner_model")
    print("Trained")

nlp = spacy.load("en_core_web_lg")
ner = nlp.get_pipe("ner")

for text, annot in food_data:
    for _, _, label in annot['entities']:
        if label not in ner.labels:
            ner.add_label(label)
train(COMBINED_TRAIN_DATA,["FOOD","COUNTRY"])


# next train countries