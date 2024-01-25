from difflib import SequenceMatcher
import constants
from definition import Definition


def getTMF_4_0_Definitions(data, print_definitions=True):

    definitions = []

    for definition in data["definitions"]:
        name = str(definition)
        fields = []

        try:
            for field in data["definitions"][name]["properties"]:
                fields.append(str(field))

            search_name = getSearchName(name)

            definitions.append(Definition(name, search_name, fields))

        except:
            print("Missing properties in " + name)

    if print_definitions:
        # Print found definitions
        for definition in definitions:
            print(definition.name)
            print(definition.search_name)
            print(definition.fields)
            print("=================================================")

    return definitions


def getMethodType(action):
    # Update
    if SequenceMatcher(None, "update", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Update"

    if SequenceMatcher(None, "patch", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Update"

    if SequenceMatcher(None, "change", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Update"

    # Create
    if SequenceMatcher(None, "create", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Create"

    if SequenceMatcher(None, "add", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Create"

    if SequenceMatcher(None, "generate", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Create"

    # Delete
    if SequenceMatcher(None, "remove", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Delete"

    if SequenceMatcher(None, "delete", action).ratio() > constants.METHOD_TYPE_SEQ_MATCHER_MIN_RATIO:
        return "Delete"


def getSearchName(name):
    search_name = name

    if "Update" in name:
        search_name = name.replace("Update", "") + "Update"

    if "Create" in name:
        search_name = name.replace("Create", "") + "Create"

    if "Delete" in name:
        search_name = name.replace("Delete", "") + "Delete"

    return search_name


def matchByComponent(doc, definitions, matched_definitions=[], print_matches=True):
    _matched_definitions = matched_definitions

    method_type = ""

    # Get Action from the Defect Summary
    for ent in doc.ents:
        if ent.label_ == "ACTION":
            method_type = getMethodType(ent.text)
            break

    # Get Component from the Defect Summary, prepare search name with action and component
    for ent in doc.ents:
        if ent.label_ == "COMPONENT":
            search_component = ent.text + str(method_type)
            for definition in definitions:
                match_ratio = SequenceMatcher(None, definition.search_name, search_component).ratio()
                if match_ratio > constants.COMPONENT_NAME_SEQ_MATCHER_MIN_RATIO:
                    definition.setComponentNameMatchRatio(max(definition.component_match_ratio, match_ratio))
                    if definition not in _matched_definitions:
                        _matched_definitions.append(definition)

    _matched_definitions = sorted(_matched_definitions, key=lambda x: x.component_match_ratio, reverse=True)

    # Print component matched definitions
    if print_matches:
        print("\n===========================")
        print("component matched definitions")
        for matched_definition in _matched_definitions:
            print(matched_definition.name + ":  " + str(matched_definition.component_match_ratio))

    return _matched_definitions


def filterByFields(doc, matched_definitions, print_matches=True):
    # Filter by fields
    for ent in doc.ents:
        if ent.label_ == "FIELD":

            field_matched_definitions = []

            for definition in matched_definitions:
                for field in definition.fields:
                    if SequenceMatcher(None, ent.text, field).ratio() > constants.FIELD_NAME_SEQ_MATCHER_MIN_RATIO:
                        definition.addMatchedField(field)
                        if definition not in field_matched_definitions:
                            field_matched_definitions.append(definition)
                            break

            if print_matches:
                print("\n===========================")
                print("field-wise filtered definitions")
                for matched_definition in field_matched_definitions:
                    print(matched_definition.name + ", Fields Matched: " + str(matched_definition.fields_matched))

            return field_matched_definitions

    return matched_definitions


def matchByFields(doc, all_definitions, print_matches=True):
    # Get the definitions that are matched by fields
    for ent in doc.ents:
        if ent.label_ == "FIELD":

            field_matched_definitions = []

            for definition in all_definitions:
                for field in definition.fields:
                    if SequenceMatcher(None, ent.text, field).ratio() > constants.FIELD_NAME_SEQ_MATCHER_MIN_RATIO:
                        definition.addMatchedField(field)
                        if definition not in field_matched_definitions:
                            field_matched_definitions.append(definition)
                            break

        if print_matches:
            print("\n===========================")
            print("field-wise matched definitions")
            for matched_definition in field_matched_definitions:
                print(matched_definition.name + ", Fields Matched: " + str(matched_definition.fields_matched))

    return field_matched_definitions
