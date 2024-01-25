"""

Base Definitions class for storing and comparing TMF definitions

"""


class Definition:
    component_match_ratio = 0.0
    fields_matched = []

    def __init__(self, name, search_name, fields):
        self.name = name
        self.search_name = search_name
        self.fields = fields

    def setComponentNameMatchRatio(self, ratio):
        self.component_match_ratio = ratio

    def addMatchedField(self, matched_field):
        if matched_field not in self.fields_matched:
            self.fields_matched.append(matched_field)
