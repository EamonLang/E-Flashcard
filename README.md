# Custom NER flashcard generator

This feature utilizes a custom trained model of SPACY NER to label user input as certain entites like "COUNTRY" or "FOOD" using that information I used the wikipedia library to search for a summary about the input. Then extracted questions from that summary.

This is a work in progress and I hope to integrate it into my website soon.

##Features
- Custom NER trained model
- Extract information from wikipedia
- Convert extracted data to flashcards

#how to run

Install dependencies in requirements.txt
Try using pip install -r requirements.txt
If that does not work I would recommend just asking AI to write the prompts for installing the dependencies.

#Notes
Please note that my trained model is ignored and not posted. You will have to create and train your own but you should be able to do that through running the training_model.py
Aditionally training the model works best if you train multiple things in one data set. Originally I tried to train individual topics like food and country except it would have a "catastrophic memory loss" where the model would label everything as food or everything as country. To resolve this I trained both topics at the same time and that seemed to provide better results.


Feel free to reach out with any questions to my email is in my bio.

Eamon,