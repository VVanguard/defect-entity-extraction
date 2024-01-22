import json
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import os

"""
Below is the initialization of the spacy pipeline
"""


def train(ANNOTATION_FILE):
    # Load the annotated data from a JSON file
    cv_data = json.load(open(ANNOTATION_FILE, 'r', encoding="utf8"))

    # Display the number of items in the dataset
    print(len(cv_data))

    # Display the first item in the dataset
    print(cv_data[0])

    def get_spacy_doc(file, data):
        # Create a blank spaCy pipeline
        nlp = spacy.blank('en')
        db = DocBin()

        # Iterate through the data
        for text, annot in tqdm(data):
            doc = nlp.make_doc(text)
            annot = annot['entities']

            ents = []
            entity_indices = []

            # Extract entities from the annotations
            for start, end, label in annot:
                skip_entity = False
                for idx in range(start, end):
                    if idx in entity_indices:
                        skip_entity = True
                        break
                if skip_entity:
                    continue

                entity_indices = entity_indices + list(range(start, end))
                try:
                    span = doc.char_span(start, end, label=label, alignment_mode='strict')
                except:
                    continue

                if span is None:
                    # Log errors for annotations that couldn't be processed
                    err_data = str([start, end]) + "    " + str(text) + "\n"
                    file.write(err_data)
                else:
                    ents.append(span)

            try:
                doc.ents = ents
                db.add(doc)
            except:
                pass

        return db

    # Split the annotated data into training and testing sets
    train, test = train_test_split(cv_data, test_size=0.25)

    # Display the number of items in the training and testing sets
    print(len(train))
    print(len(test))

    # Open a file to log errors during annotation processing
    file = open('sources/train_file.txt', 'w')

    # Create spaCy DocBin objects for training and testing data
    db = get_spacy_doc(file, train)
    db.to_disk('sources/train_data.spacy')

    db = get_spacy_doc(file, test)
    db.to_disk('sources/test_data.spacy')

    # Close the error log file
    file.close()
    # !python -m spacy train /sources/base_config.cfg  --output /sources/output  --paths.train /sources/train_data.spacy  --paths.dev /sources/test_data.spacy --gpu-id 0
    os.system(
        "python -m spacy train sources/config.cfg --paths.train sources/train_data.spacy --paths.dev sources/test_data.spacy --output sources/output")
