import json

import spacy
from difflib import SequenceMatcher
from trainset import train
import utilities as util

# DEFINE
MODEL_ADDRESS = "models/pc/model-best"
ANNOTATION_FILE = "annotations/sc-annotations.json"
TMF_FILE = "tmfs/TMF620-ProductCatalog-v4.0.0.swagger.json"

# text = "pc: in product catalog/specifications/service-resource specification, adding a new new resorce specification is giving error."
# text = "pc - post a second version of a launched category has validity period check issues"
# text = "pc - related specification page 400 error issue"
text = "pc: specification lifecycle status update issue"


#
#
# Base Definitions class for storing and comparing TMF definitions
#
#
class Definition:
    def __init__(self, name, search_name, fields):
        self.name = name
        self.search_name = search_name
        self.fields = fields


# Train Model
"""
train(ANNOTATION_FILE);
"""
# Load best model
nlp = spacy.load(MODEL_ADDRESS)

doc = nlp(text)

#
#
# Get definitions from the TMF file
#
#

f = open(TMF_FILE)
data = json.load(f)

definitions = []

# TODO: TMF 4.0 için çalışır, TMF 5.0 için farklı bir yapı geliştirilecektir.
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

# Print found definitions
for definition in definitions:
    print(definition.name)
    print(definition.search_name)
    print(definition.fields)
    print("=================================================")

# Print our text and found entities
print("\n\n\n===========================")
print("TEXT: " + text)
for ent in doc.ents:
    print(ent.text, "  ->>>>  ", ent.label_)
print("===========================")

#
#
# Match Definitions
#
#

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
            if SequenceMatcher(None, definition.search_name, search_component).ratio() > 0.66:
                matched_definitions.append(definition)

# Print component matched definitions
print("\n===========================")
print("component matched definitions")
for matched_definition in matched_definitions:
    print(matched_definition.name)

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

print("\n===========================")
print("field-wise filtered definitions")
for matched_definition in matched_definitions:
    print(matched_definition.name)
