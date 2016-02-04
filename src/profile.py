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

# this is a simple list of languages and their gold-value for feature.
wals_svo = WalsFeature(os.path.join(wals_path, "wals-dataset"), "81A")
wals_sv = WalsFeature(os.path.join(wals_path, "wals-dataset"), "82A")
wals_ov = WalsFeature(os.path.join(wals_path, "wals-dataset"), "83A")
wals_ndo = WalsFeature(os.path.join(wals_path, "wals-dataset"), "81B")

# some globals
svo_feature_dictionary = {}
sv_feature_dictionary = {}
ov_feature_dictionary = {}

num_languages = len(odin_corpus)
i = 0
num_languages_determined = 0
ndo_languages = []

svo_possibilities = ["SOV", "SVO", "VSO", "VOS", "OVS", "OSV", "ndo"]  # ndo is "no dominant order"
sv_possibilities = ["SV", "VS", "ndo"]  # ndo is "no dominant order"
ov_possibilities = ["OV", "VO", "ndo"]  # ndo is "no dominant order"


def print_order_confusion_matrix_for_feature(feature_dictionary, wals_gold_standard, possibilities, title):
    # build and print a confusion matrix for svo
    print("\nComparing results with gold standard from WALS for " + title + ":")
    confusion_matrix = ConfusionMatrix(title, possibilities)
    num_reported = 0
    for code in feature_dictionary:
        our_value = feature_dictionary[code]
        try:
            wals_code = wals_dictionary.iso_to_wals[code]
            wals_value = wals_gold_standard.feature_dictionary[wals_code]
            confusion_matrix.addLabel(wals_value, our_value)
            num_reported += 1
        except KeyError:
            print("No matching SVO WALS data for language " + code)
    print("Num Languages Compared: " + str(num_reported))
    if num_reported > 0:
        print(confusion_matrix.printMatrix())


# START REALLY DOING STUFF HERE
# loop through and determine our best guess
for language in odin_corpus:
    i += 1
    filename = os.path.basename(language)
    language_code = os.path.splitext(filename)[0]
    try:
        # todo:  this is going to change.   we will fail later when we're doing confusion matrix
        # this is just a check to see if we get an error here.
        # we're going to error out if we can't look up this language/feature in WALS.
        wals_code = wals_dictionary.iso_to_wals[language_code]
        wals_value = wals_svo.feature_dictionary[wals_code]
    except KeyError:  # it wasn't in the dictionary of languages which have reported stats for feature in WALS
        continue

    # DEBUG
    #language = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/eng.xml"
    #language_code = "eng"

    xc = xigtxml.load(language, mode='full')
    svo_calc = SVO(xc, language_code)
    svo_calc.estimate_word_order_for_each_instance()
    if svo_calc.total_instance_count > 0:
        if svo_calc.svo_sorted_probs is not None:
            svo_feature_dictionary[language_code] = svo_calc.svo_best_guess
        if svo_calc.sv_sorted_probs is not None:
            sv_feature_dictionary[language_code] = svo_calc.sv_best_guess
        if svo_calc.ov_sorted_probs is not None:
            ov_feature_dictionary[language_code] = svo_calc.ov_best_guess
        if svo_calc.svo_best_guess == "ndo":
            ndo_languages.append(language_code)
        svo_calc.print_language_name()
        svo_calc.print_order_estimates()
        num_languages_determined += 1
    # DEBUG
    #if num_languages_determined >= 10:
    #    break

print("Num Languages Determined: \n" + str(num_languages_determined))

print_order_confusion_matrix_for_feature(svo_feature_dictionary, wals_svo, svo_possibilities, "SVO Data")
print_order_confusion_matrix_for_feature(sv_feature_dictionary, wals_sv, sv_possibilities, "SV Data")
print_order_confusion_matrix_for_feature(ov_feature_dictionary, wals_ov, ov_possibilities, "OV Data")



