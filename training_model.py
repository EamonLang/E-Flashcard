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


NEW_DATA_SET = [
    # animals
    ("The lion is known as the king of the jungle.", {"entities": [(4, 8, "ANIMAL")]}),
    ("Pandas primarily eat bamboo and live in China.", {"entities": [(0, 6, "ANIMAL")]}),
    ("I saw a kangaroo hopping across the field.", {"entities": [(8, 16, "ANIMAL")]}),
    ("Whales are the largest animals on Earth.", {"entities": [(0, 6, "ANIMAL")]}),
    ("The cheetah can run faster than any other land animal.", {"entities": [(4, 11, "ANIMAL")]}),
    ("Elephants have incredible memories.", {"entities": [(0, 9, "ANIMAL")]}),
    ("The bald eagle is a symbol of the United States.", {"entities": [(4, 14, "ANIMAL")]}),
    ("I watched a documentary about wolves in Alaska.", {"entities": [(30, 35, "ANIMAL")]}),
    ("Octopuses are known for their intelligence.", {"entities": [(0, 9, "ANIMAL")]}),
    ("The giant panda is a national treasure in China.", {"entities": [(4, 15, "ANIMAL")]}),

    # Language Data
    ("I am learning Spanish to travel to South America.", {"entities": [(16, 23, "LANGUAGE")]}),
    ("French is a beautiful language spoken in many countries.", {"entities": [(0, 6, "LANGUAGE")]}),
    ("He can speak fluent Japanese after living in Tokyo.", {"entities": [(19, 27, "LANGUAGE")]}),
    ("Mandarin is the most spoken language in the world.", {"entities": [(0, 8, "LANGUAGE")]}),
    ("They offered German classes at the university.", {"entities": [(13, 19, "LANGUAGE")]}),
    ("Italian cuisine is loved worldwide.", {"entities": [(0, 7, "LANGUAGE")]}),
    ("I took a beginner course in Russian last year.", {"entities": [(26, 33, "LANGUAGE")]}),
    ("She learned Portuguese before moving to Brazil.", {"entities": [(13, 23, "LANGUAGE")]}),
    ("Arabic is the official language of many countries.", {"entities": [(0, 6, "LANGUAGE")]}),
    ("They are studying Korean for a work opportunity.", {"entities": [(19, 25, "LANGUAGE")]}),
    # Country Data
    ("Spain is famous for its beautiful beaches and vibrant festivals.", {"entities": [(0, 5, "COUNTRY")]}),
    ("I want to explore the temples of Thailand.", {"entities": [(30, 38, "COUNTRY")]}),
    ("Kenya offers some of the best safaris in the world.", {"entities": [(0, 5, "COUNTRY")]}),
    ("My dream is to visit New Zealand and see the landscapes.", {"entities": [(21, 32, "COUNTRY")]}),
    ("Switzerland is known for chocolate and stunning mountains.", {"entities": [(0, 11, "COUNTRY")]}),
    ("I studied abroad in South Korea last year.", {"entities": [(19, 30, "COUNTRY")]}),
    ("Portugal has amazing coastlines and rich history.", {"entities": [(0, 8, "COUNTRY")]}),
    ("Morocco has colorful markets and desert adventures.", {"entities": [(0, 7, "COUNTRY")]}),
    ("Iceland has dramatic volcanoes and glaciers.", {"entities": [(0, 7, "COUNTRY")]}),
    ("Peru is home to Machu Picchu.", {"entities": [(0, 4, "COUNTRY")]}),
    ("I went hiking in the mountains of Chile.", {"entities": [(32, 37, "COUNTRY")]}),
    ("The cultural heritage of Iran is fascinating.", {"entities": [(24, 28, "COUNTRY")]}),
    ("Poland has charming towns and delicious food.", {"entities": [(0, 6, "COUNTRY")]}),
    ("I would love to backpack across Vietnam.", {"entities": [(30, 37, "COUNTRY")]}),
    ("Indonesia is made up of thousands of islands.", {"entities": [(0, 9, "COUNTRY")]}),
    ("New York City is bustling, but upstate New York is very peaceful.", {"entities": [(0, 13, "COUNTRY"), (39, 48, "COUNTRY")]}),
    ("Nepal is the perfect place for mountain lovers.", {"entities": [(0, 5, "COUNTRY")]}),
    ("Ireland has beautiful green landscapes.", {"entities": [(0, 7, "COUNTRY")]}),
    ("I hope to travel to Belgium this spring.", {"entities": [(21, 28, "COUNTRY")]}),
    ("Scotland is known for its historic castles.", {"entities": [(0, 8, "COUNTRY")]}),
    ("Croatia has stunning beaches along the Adriatic Sea.", {"entities": [(0, 7, "COUNTRY")]}),
    ("I spent a semester studying in Denmark.", {"entities": [(32, 39, "COUNTRY")]}),
    ("The wildlife of Madagascar is truly unique.", {"entities": [(15, 25, "COUNTRY")]}),
    ("The streets of Havana, Cuba, are full of life.", {"entities": [(18, 22, "COUNTRY")]}),
    ("Many tourists visit the pyramids of Sudan.", {"entities": [(31, 36, "COUNTRY")]}),
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

    # city data

    ("Paris is beautiful in the spring.", {"entities": [(0, 5, "CITY")]}),
    ("I spent a week in Tokyo last summer.", {"entities": [(16, 21, "CITY")]}),
    ("New York is known for its skyline.", {"entities": [(0, 8, "CITY")]}),
    ("We visited Rome during our trip.", {"entities": [(11, 15, "CITY")]}),
    ("Barcelona has incredible architecture.", {"entities": [(0, 9, "CITY")]}),
    ("Los Angeles is famous for Hollywood.", {"entities": [(0, 11, "CITY")]}),
    ("Istanbul connects Europe and Asia.", {"entities": [(0, 8, "CITY")]}),
    ("Cairo has amazing historical sites.", {"entities": [(0, 5, "CITY")]}),
    ("London is rainy in the winter.", {"entities": [(0, 6, "CITY")]}),
    ("I want to move to Sydney someday.", {"entities": [(17, 23, "CITY")]}),
    ("Berlin is full of history and culture.", {"entities": [(0, 6, "CITY")]}),
    ("San Francisco has a famous bridge.", {"entities": [(0, 13, "CITY")]}),
    ("Mumbai is a bustling city in India.", {"entities": [(0, 6, "CITY")]}),
    ("Rio de Janeiro has vibrant festivals.", {"entities": [(0, 15, "CITY")]}),
    ("Chicago is known for its deep-dish pizza.", {"entities": [(0, 7, "CITY")]}),
    ("Beijing hosted the Olympics.", {"entities": [(0, 7, "CITY")]}),
    ("Dubai has the tallest building in the world.", {"entities": [(0, 5, "CITY")]}),
    ("Seoul is a tech hub.", {"entities": [(0, 5, "CITY")]}),
    ("Toronto is a diverse city.", {"entities": [(0, 7, "CITY")]}),
    ("Bangkok is known for its street food.", {"entities": [(0, 7, "CITY")]}),

    # sport daTA
    ("Soccer is the most popular sport worldwide.", {"entities": [(0, 6, "SPORT")]}),
    ("I love playing basketball with my friends.", {"entities": [(15, 25, "SPORT")]}),
    ("Tennis matches can be intense.", {"entities": [(0, 6, "SPORT")]}),
    ("Swimming is great for your health.", {"entities": [(0, 8, "SPORT")]}),
    ("Many people watch American football.", {"entities": [(18, 35, "SPORT")]}),
    ("Baseball is a classic American pastime.", {"entities": [(0, 8, "SPORT")]}),
    ("I started learning how to box.", {"entities": [(25, 28, "SPORT")]}),
    ("Cycling is very popular in Europe.", {"entities": [(0, 7, "SPORT")]}),
    ("Hockey is Canada's national sport.", {"entities": [(0, 6, "SPORT")]}),
    ("They went skiing during the winter holidays.", {"entities": [(10, 17, "SPORT")]}),
    ("Golf requires a lot of precision.", {"entities": [(0, 4, "SPORT")]}),
    ("We watched the wrestling championship.", {"entities": [(16, 25, "SPORT")]}),
    ("Volleyball is fun at the beach.", {"entities": [(0, 9, "SPORT")]}),
    ("Surfing in Hawaii is amazing.", {"entities": [(0, 7, "SPORT")]}),
    ("I tried archery last summer.", {"entities": [(7, 14, "SPORT")]}),
    ("Karate teaches discipline and focus.", {"entities": [(0, 6, "SPORT")]}),
    ("Snowboarding is thrilling.", {"entities": [(0, 11, "SPORT")]}),
    ("I practiced fencing for two years.", {"entities": [(11, 18, "SPORT")]}),
    ("Wrestling requires strength and technique.", {"entities": [(0, 9, "SPORT")]}),
    ("Rowing is a tough sport.", {"entities": [(0, 6, "SPORT")]}),

    # animal data
    ("Lions live in the African savannah.", {"entities": [(0, 5, "ANIMAL")]}),
    ("I saw an elephant at the zoo.", {"entities": [(9, 17, "ANIMAL")]}),
    ("Dolphins are highly intelligent creatures.", {"entities": [(0, 8, "ANIMAL")]}),
    ("Pandas mainly eat bamboo.", {"entities": [(0, 6, "ANIMAL")]}),
    ("Bears hibernate during the winter.", {"entities": [(0, 5, "ANIMAL")]}),
    ("Snakes can be venomous.", {"entities": [(0, 6, "ANIMAL")]}),
    ("Tigers are majestic big cats.", {"entities": [(0, 6, "ANIMAL")]}),
    ("Owls hunt at night.", {"entities": [(0, 4, "ANIMAL")]}),
    ("Wolves live and hunt in packs.", {"entities": [(0, 6, "ANIMAL")]}),
    ("Kangaroos carry their babies in pouches.", {"entities": [(0, 9, "ANIMAL")]}),
    ("Cheetahs are the fastest land animals.", {"entities": [(0, 8, "ANIMAL")]}),
    ("I love my pet dog.", {"entities": [(13, 16, "ANIMAL")]}),
    ("The cat slept all day.", {"entities": [(4, 7, "ANIMAL")]}),
    ("Eagles have incredible vision.", {"entities": [(0, 6, "ANIMAL")]}),
    ("Flamingos are pink birds.", {"entities": [(0, 9, "ANIMAL")]}),
    ("Octopuses are very smart.", {"entities": [(0, 9, "ANIMAL")]}),
    ("Penguins can't fly but swim very well.", {"entities": [(0, 8, "ANIMAL")]}),
    ("Bats use echolocation to navigate.", {"entities": [(0, 4, "ANIMAL")]}),
    ("Sharks are apex predators.", {"entities": [(0, 6, "ANIMAL")]}),
    ("Foxes are clever animals.", {"entities": [(0, 5, "ANIMAL")]}),

    # language data

    ("Spanish is spoken widely across the globe.", {"entities": [(0, 7, "LANGUAGE")]}),
    ("I studied French in school.", {"entities": [(10, 16, "LANGUAGE")]}),
    ("She is fluent in German.", {"entities": [(17, 23, "LANGUAGE")]}),
    ("They taught us Japanese basics.", {"entities": [(16, 24, "LANGUAGE")]}),
    ("Chinese is one of the oldest languages.", {"entities": [(0, 7, "LANGUAGE")]}),
    ("Many people in India speak Hindi.", {"entities": [(25, 30, "LANGUAGE")]}),
    ("Arabic is written from right to left.", {"entities": [(0, 6, "LANGUAGE")]}),
    ("Portuguese is spoken in Brazil.", {"entities": [(0, 10, "LANGUAGE")]}),
    ("I want to learn Korean next year.", {"entities": [(15, 21, "LANGUAGE")]}),
    ("Russian has a different alphabet.", {"entities": [(0, 7, "LANGUAGE")]}),
    ("Italian sounds musical.", {"entities": [(0, 7, "LANGUAGE")]}),
    ("Greek myths are fascinating.", {"entities": [(0, 5, "LANGUAGE")]}),
    ("He speaks fluent Turkish.", {"entities": [(17, 24, "LANGUAGE")]}),
    ("They offer Swahili classes here.", {"entities": [(11, 18, "LANGUAGE")]}),
    ("Dutch is relatively easy to learn.", {"entities": [(0, 5, "LANGUAGE")]}),
    ("Persian poetry is beautiful.", {"entities": [(0, 7, "LANGUAGE")]}),
    ("Hebrew is the language of Israel.", {"entities": [(0, 6, "LANGUAGE")]}),
    ("Learning Polish can be challenging.", {"entities": [(9, 15, "LANGUAGE")]}),
    ("We practiced Urdu during class.", {"entities": [(13, 17, "LANGUAGE")]}),
    ("They sang songs in Bengali.", {"entities": [(18, 25, "LANGUAGE")]}),

    # DATE examples
    ("I have a meeting on January 5th", {"entities": [(21, 32, "DATE")]}),
    ("Let's plan something for next Friday", {"entities": [(25, 36, "DATE")]}),
    ("Her birthday is July 14", {"entities": [(16, 23, "DATE")]}),
    ("The event is scheduled for tomorrow", {"entities": [(25, 33, "DATE")]}),
    ("He is visiting on the 10th of December", {"entities": [(23, 38, "DATE")]}),
    ("The deadline is next Monday", {"entities": [(17, 28, "DATE")]}),
    ("We will meet on the 15th of August", {"entities": [(17, 34, "DATE")]}),
    ("My appointment is on November 3rd", {"entities": [(17, 28, "DATE")]}),
    ("The wedding is set for June 18th", {"entities": [(21, 32, "DATE")]}),
    ("They are arriving on the 22nd of February", {"entities": [(23, 42, "DATE")]}),
    ("The meeting will take place on April 7", {"entities": [(26, 32, "DATE")]}),
    ("Her anniversary is on December 12", {"entities": [(16, 28, "DATE")]}),
    ("We are traveling on the 25th of July", {"entities": [(19, 35, "DATE")]}),
    ("The event is next weekend", {"entities": [(14, 25, "DATE")]}),
    ("The conference starts in two days", {"entities": [(21, 32, "DATE")]}),
    ("We are visiting in the fall", {"entities": [(17, 22, "DATE")]}),
    ("The holiday season is coming soon", {"entities": [(19, 28, "DATE")]}),
    ("The report is due in September", {"entities": [(17, 26, "DATE")]}),
    ("I need to submit this by next Tuesday", {"entities": [(28, 41, "DATE")]}),
    ("He is coming back on March 5", {"entities": [(22, 30, "DATE")]}),

    # TIME examples
    ("The appointment is at 3 PM", {"entities": [(22, 26, "TIME")]}),
    ("We should meet around noon", {"entities": [(21, 25, "TIME")]}),
    ("The movie starts at 8:30 p.m.", {"entities": [(20, 29, "TIME")]}),
    ("The store opens at 9 AM", {"entities": [(17, 21, "TIME")]}),
    ("I'll call you at 6:15", {"entities": [(14, 19, "TIME")]}),
    ("The train departs at 7:00 a.m.", {"entities": [(20, 26, "TIME")]}),
    ("The party starts at midnight", {"entities": [(20, 28, "TIME")]}),
    ("The event starts at 10 PM", {"entities": [(19, 23, "TIME")]}),
    ("We'll be there by 5:30", {"entities": [(16, 21, "TIME")]}),
    ("I need the report by 8 AM", {"entities": [(22, 26, "TIME")]}),
    ("The movie runs for 2 hours", {"entities": [(18, 22, "TIME")]}),
    ("The class ends at 2:30 PM", {"entities": [(17, 22, "TIME")]}),
    ("The game will begin at 4 o'clock", {"entities": [(22, 31, "TIME")]}),
    ("I need to wake up at 7 AM", {"entities": [(16, 20, "TIME")]}),
    ("The store closes at 10 PM", {"entities": [(19, 23, "TIME")]}),
    ("We'll meet at 11:15 in the morning", {"entities": [(14, 32, "TIME")]}),
    ("The concert starts at 6:45 PM", {"entities": [(20, 29, "TIME")]}),
    ("I'll be ready by 4 PM", {"entities": [(17, 21, "TIME")]}),
    ("We have a meeting at noon", {"entities": [(18, 22, "TIME")]}),
    ("The movie is at 9:15", {"entities": [(16, 21, "TIME")]}),

    # EVENT examples
    ("I'm going to the World Cup next year", {"entities": [(18, 27, "EVENT")]}),
    ("Did you watch the Oscars?", {"entities": [(20, 26, "EVENT")]}),
    ("Comic-Con is happening this weekend", {"entities": [(0, 9, "EVENT")]}),
    ("We attended the Met Gala last night", {"entities": [(16, 24, "EVENT")]}),
    ("The Super Bowl is in February", {"entities": [(4, 15, "EVENT")]}),
    ("The Grammy Awards are on Sunday", {"entities": [(4, 20, "EVENT")]}),
    ("The concert is tomorrow evening", {"entities": [(15, 29, "EVENT")]}),
    ("I'm planning to go to the Sundance Festival", {"entities": [(30, 48, "EVENT")]}),
    ("We saw a great play last night", {"entities": [(10, 14, "EVENT")]}),
    ("The concert was amazing", {"entities": [(4, 12, "EVENT")]}),
    ("I attended a fantastic art exhibit", {"entities": [(15, 32, "EVENT")]}),
    ("He performed at the Billboard Music Awards", {"entities": [(28, 56, "EVENT")]}),
    ("The marathon is next Sunday", {"entities": [(4, 13, "EVENT")]}),
    ("I watched a documentary on Netflix", {"entities": [(22, 32, "EVENT")]}),
    ("The museum exhibit opens this weekend", {"entities": [(18, 41, "EVENT")]}),
    ("They are going to a charity gala next month", {"entities": [(24, 33, "EVENT")]}),
    ("The World Cup will be exciting", {"entities": [(0, 9, "EVENT")]}),
    ("I'm attending a wedding this summer", {"entities": [(23, 32, "EVENT")]}),
    ("Did you hear about the Nobel Prize Ceremony?", {"entities": [(25, 41, "EVENT")]}),

    # ORG (companies) examples
    ("I got a job offer from Microsoft", {"entities": [(24, 33, "ORG")]}),
    ("She interned at Google last summer", {"entities": [(16, 22, "ORG")]}),
    ("Amazon is launching a new service", {"entities": [(0, 6, "ORG")]}),
    ("Tesla has introduced a new model", {"entities": [(0, 5, "ORG")]}),
    ("Apple unveiled a new product", {"entities": [(0, 5, "ORG")]}),
    ("Facebook has changed its name to Meta", {"entities": [(0, 8, "ORG")]}),
    ("He works for a startup called Square", {"entities": [(26, 32, "ORG")]}),
    ("Uber announced a new partnership", {"entities": [(0, 4, "ORG")]}),
    ("Spotify launched a new playlist feature", {"entities": [(0, 7, "ORG")]}),
    ("Intel released new processors", {"entities": [(0, 5, "ORG")]}),
    ("I joined a company called LinkedIn", {"entities": [(24, 32, "ORG")]}),
    ("Samsung is releasing new phones", {"entities": [(0, 7, "ORG")]}),
    ("Microsoft has acquired LinkedIn", {"entities": [(0, 9, "ORG")]}),
    ("I am working for a startup called Square", {"entities": [(24, 32, "ORG")]}),
    ("Amazon Prime is expanding its services", {"entities": [(0, 6, "ORG")]}),
    ("She got a promotion at PayPal", {"entities": [(23, 29, "ORG")]}),
    ("Google launched a new phone", {"entities": [(0, 6, "ORG")]}),
    ("They are investing in a startup called Stripe", {"entities": [(38, 44, "ORG")]}),
    ("Microsoft's headquarters is in Redmond", {"entities": [(0, 9, "ORG")]}),
    ("Tesla is investing in autonomous driving", {"entities": [(0, 5, "ORG")]}),

    # WORK_OF_ART examples
    ("I just finished reading The Great Gatsby", {"entities": [(24, 41, "WORK_OF_ART")]}),
    ("Have you seen Inception?", {"entities": [(14, 23, "WORK_OF_ART")]}),
    ("Yesterday I watched The Godfather", {"entities": [(20, 33, "WORK_OF_ART")]}),
    ("I love the book 1984 by George Orwell", {"entities": [(15, 19, "WORK_OF_ART")]}),
    ("The movie Jaws was a classic", {"entities": [(4, 8, "WORK_OF_ART")]}),
    ("I'm re-reading The Catcher in the Rye", {"entities": [(17, 40, "WORK_OF_ART")]}),
    ("Have you listened to Bohemian Rhapsody?", {"entities": [(25, 42, "WORK_OF_ART")]}),
    ("The painting Starry Night is famous", {"entities": [(10, 23, "WORK_OF_ART")]}),
    ("The book To Kill a Mockingbird is a classic", {"entities": [(9, 30, "WORK_OF_ART")]}),
    ("I watched The Matrix for the first time", {"entities": [(10, 22, "WORK_OF_ART")]}),
    ("The song Imagine by John Lennon is timeless", {"entities": [(4, 11, "WORK_OF_ART")]}),
    ("I read Moby-Dick over the summer", {"entities": [(2, 11, "WORK_OF_ART")]}),
    ("The Mona Lisa is on display in Paris", {"entities": [(4, 14, "WORK_OF_ART")]}),
    ("The novel The Hobbit is a great adventure", {"entities": [(9, 19, "WORK_OF_ART")]}),
    ("Have you seen The Shawshank Redemption?", {"entities": [(14, 38, "WORK_OF_ART")]}),
    ("I listened to Bohemian Rhapsody by Queen", {"entities": [(11, 29, "WORK_OF_ART")]}),
    ("The painting Girl with a Pearl Earring is famous", {"entities": [(10, 35, "WORK_OF_ART")]}),
    ("I enjoy the musical Hamilton", {"entities": [(14, 23, "WORK_OF_ART")]}),
    ("Have you read Harry Potter?", {"entities": [(12, 24, "WORK_OF_ART")]})
]
nlp = spacy.load("custom_ner_model")



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

    for epoch in range(30):
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
train(NEW_DATA_SET,["FOOD","COUNTRY","CITY","SPORT","ANIMAL","LANGUAGE","WORK_OF_ART","ORG","EVENT","TIME","DATE"])
# clean_data(NEW_DATA_SET)

# next train countries