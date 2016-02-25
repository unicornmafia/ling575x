__author__ = 'thomas'
##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# WALS.py
#
# author:  tcmarsh@uw.edu
#
# description:  class for reading and holding gold standard WALS data
#
##############################################################################
import os


#
# WalsFeature:  a class which reads in and holds a
#               dictionary of feature values per language
#               for a given WALS feature
#
class WalsFeature:
    def __init__(self, path, feature_id, wals_dictionary):
        self.path = path
        self.feature_id = feature_id
        self.feature_dictionary = {}
        self.load_dictionary()
        self.wals_dictionary = wals_dictionary

    #
    # load_dictionary() - loads the dictionary from the file
    #
    def load_dictionary(self):
        filename = os.path.join(self.path, "wals-" + self.feature_id + ".csv")
        first_line = True
        for line in open(filename, 'r'):
            if first_line:
                first_line = False
                continue
            entries = line.split(",")
            language_id = entries[0][4:]
            feature_value = entries[4]
            if feature_value == "No dominant order":
                feature_value = "ndo"
            self.feature_dictionary[language_id] = feature_value

    def get_value_from_iso_language_id(self, iso_id):
        try:
            wals_code = self.wals_dictionary.iso_to_wals[iso_id]
            wals_value = self.feature_dictionary[wals_code]
            return wals_value
        except KeyError:
            return "No Match"

    def is_language_present(self, iso_id):
        if self.get_value_from_iso_language_id(iso_id) == "No Match":
            return False
        else:
            return True


#
# WalsLanguageCodes
#
# UGH!  we have to build a dictionary to convert WALS codes to ISO codes (and back)
#
class WalsLanguageCodes:
    def __init__(self, path):
        self.path = path
        self.wals_to_iso = {}
        self.iso_to_wals = {}
        self.load_dictionary()

    #
    # load_dictionary() - loads the dictionary from the file
    #
    def load_dictionary(self):
        filename = os.path.join(self.path, "language.csv")
        first_line = True
        for line in open(filename, 'r'):
            if first_line:
                first_line = False
                continue
            entries = line.split(",")
            iso_code = entries[1]
            wals_code = entries[0]
            self.wals_to_iso[wals_code] = iso_code
            self.iso_to_wals[iso_code] = wals_code
            # print(iso_code + " " + wals_code)
