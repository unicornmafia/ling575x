##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# profile.py
#
# author:  tcmarsh@uw.edu
#
# description:  entry point for language profile project
#
##############################################################################
from xigt.codecs import xigtxml
from svo import SVO
from wals import WalsFeature, WalsLanguageCodes
from confusionMatrix import ConfusionMatrix
import glob
import os

wals_path = "/opt/dropbox/15-16/575x/data/WALS-data"
odin_path = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/"

# this loads all the odin/xigt files in the path into a list
odin_corpus = glob.glob(os.path.join(odin_path, "*.xml"))

# this is an annoying required conversion between WALS language ids and ISO language ids
wals_dictionary = WalsLanguageCodes(os.path.join(wals_path, "wals-language"))

# this is a simple list of languages and their gold-value.
wals = WalsFeature(os.path.join(wals_path, "wals-dataset"), "81A")

# some globals
feature_dictionary = {}
num_languages = len(odin_corpus)
i = 0
num_languages_determined = 0

# START REALLY DOING STUFF HERE
# loop through and determine our best guess
for language in odin_corpus:
    i += 1
    filename = os.path.basename(language)
    language_code = os.path.splitext(filename)[0]
    try:
        wals_code = wals_dictionary.iso_to_wals[language_code]
        wals_value = wals.feature_dictionary[wals_code]
    except KeyError:  # it wasn't in the dictionary of languages which have reported stats for feature in WALS
        continue
    xc = xigtxml.load(language, mode='full')
    svo_calc = SVO(xc, language_code)
    svo_calc.estimate_word_order_for_each_instance()
    if svo_calc.instance_count > 0:
        feature_dictionary[language_code] = svo_calc.best_guess
        svo_calc.print_language_name()
        svo_calc.print_order_estimates()
        num_languages_determined += 1

    #if num_languages_determined >= 5:
    #    break

print("Num Languages Determined: \n" + str(num_languages_determined))

# build and print a confusion matrix
print("\nComparing results with gold standard from WALS:")
possibilities = ["SOV", "SVO", "VSO", "VOS", "OVS", "OSV", "ndo"]  # ndo is "no dominant order"
confusion_matrix = ConfusionMatrix("Generated and WALS", possibilities)
num_reported = 0
for code in feature_dictionary:
    our_value = feature_dictionary[code]
    try:
        wals_code = wals_dictionary.iso_to_wals[code]
        wals_value = wals.feature_dictionary[wals_code]
        confusion_matrix.addLabel(wals_value, our_value)
        num_reported += 1
    except KeyError:
        print("No matching WALS data for language " + code)

print("Num Languages Compared: " + str(num_reported))

if num_reported > 0:
    print(confusion_matrix.printMatrix())


