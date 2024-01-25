import json

import spacy
from trainset import train
import utilities as util

# DEFINE
OPERATION_TARGET = "sc"

MODEL_ADDRESS, TMF_FILE = None, None
ANNOTATION_FILE = None

match OPERATION_TARGET:
    case "pc":
        MODEL_ADDRESS = "models/pc/model-best"
        TMF_FILE = "tmfs/TMF620-ProductCatalog-v4.0.0.swagger.json"
    case "sc":
        MODEL_ADDRESS = "models/sc/model-best"
        TMF_FILE = "tmfs/TMF633-Service-Catalog-v4.0.0-swagger.json"
    case "train":
        train(ANNOTATION_FILE)

if MODEL_ADDRESS is None:
    raise NotImplementedError("Configure a case for test")


# text = "pc: in product catalog/specifications/service-resource specification, adding a new new resorce specification is giving error."
# text = "pc - post a second version of a launched category has validity period check issues"
# text = "pc - related specification page 400 error issue"
# text = "DSCMS: Patch fails due to category baseType, category type and category schemaLocation"
text = "Service Catalog Mgmt: Wrong datatype for value in CharacteristicValueSpecification"

# Get definitions from the TMF file
# TODO: TMF 4.0 için çalışır, TMF 5.0 için farklı bir yapı geliştirilecektir.
f = open(TMF_FILE)
data = json.load(f)

definitions = util.getTMF_4_0_Definitions(data)


# Extract entities from the defect summary
# Load best model and feed text
nlp = spacy.load(MODEL_ADDRESS)
doc = nlp(text)

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

# By component
matched_definitions = util.matchByComponent(doc, definitions)

# If components are matched, filter by fields
# Else get the definitions that are matched by fields
matched_definitions = util.filterByFields(doc, matched_definitions) if matched_definitions else util.matchByFields(doc, definitions)

print("\n===========================")
print("Final Definitions")
for matched_definition in matched_definitions:
    print(matched_definition.name)
