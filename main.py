# Import required libraries and install any necessary packages
import json

import spacy
from spacy.tokens import DocBin
from tqdm import tqdm

from sklearn.model_selection import train_test_split

import os

from difflib import SequenceMatcher

import utilities as util

"""
Below is the initialization of the spacy pipeline
"""

"""
# Load the annotated data from a JSON file
cv_data = json.load(open('sources/annotations.json', 'r', encoding="utf8"))

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
#!python -m spacy train /sources/base_config.cfg  --output /sources/output  --paths.train /sources/train_data.spacy  --paths.dev /sources/test_data.spacy --gpu-id 0
os.system("python -m spacy train sources/config.cfg --paths.train sources/train_data.spacy --paths.dev sources/test_data.spacy --output sources/output")
"""


class Definition:
    def __init__(self, name, search_name, fields):
        self.name = name
        self.search_name = search_name
        self.fields = fields


nlp = spacy.load("sources/output/model-best")

text = "pc: in product catalog/specifications/service-resource specification, adding a new new resorce specification is giving error."
#text = "pc - post a second version of a launched category has validity period check issues"
#text = "pc - related specification page 400 error issue"
#text = "pc: specification lifecycle status update issue"

doc = nlp(text)

f = open("sources/TMF620-ProductCatalog-v4.0.0.swagger.json")
data = json.load(f)

definitions = []

for definition in data["definitions"]:
    name = str(definition)
    fields = []

    try:
        for field in data["definitions"][name]["properties"]:
            fields.append(str(field))

        search_name = util.get_search_name(name)

        definitions.append(Definition(name, search_name, fields))

    except:
        print("Missing properties in " + name)


for definition in definitions:
    print(definition.name)
    print(definition.search_name)
    print(definition.fields)
    print("=================================================")

print("")
print("")
print("")
print("===========================")
print("TEXT: " + text)
for ent in doc.ents:
    print(ent.text, "  ->>>>  ", ent.label_)
print("===========================")


matched_definitions = []
method_type = ""

# Get Action from the Defect Summary
for ent in doc.ents:
    if ent.label_ == "ACTION":
        method_type = util.get_method_type(ent.text)
        break

# Get Component from the Defect Summary, prepare search name with action and component
for ent in doc.ents:
    if ent.label_ == "COMPONENT":
        search_component = ent.text + str(method_type)

        for definition in definitions:
            if SequenceMatcher(None, definition.search_name, search_component).ratio() > 0.65:
                matched_definitions.append(definition)

# If components are matched, filter by fields
# Else get the definitions that are matched by fields
for ent in doc.ents:
    if ent.label_ == "FIELD":

        if len(matched_definitions) > 0:
            field_matched_definitions = []

            for definition in matched_definitions:
                for field in definition.fields:
                    if SequenceMatcher(None, ent.text, field).ratio() > 0.65:
                        field_matched_definitions.append(definition)

        else:
            for definition in definitions:
                for field in definition.fields:
                    if SequenceMatcher(None, ent.text, field).ratio() > 0.65:
                        field_matched_definitions.append(definition)
                        break

        matched_definitions = field_matched_definitions


for matched_definition in matched_definitions:
    print(matched_definition.name)