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
from svo import SVOProbe
from sv import SVProbe
from ov import OVProbe
from nadj import NounAdjectiveProbe
from wals import WalsFeature, WalsLanguageCodes
from reporting import Reporting
import glob
import os
import errors
import argparse

wals_path = "/opt/dropbox/15-16/575x/data/WALS-data"
odin_path = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/"
data_dir = "../data"

# this loads all the odin/xigt files in the path into a list
odin_corpus = glob.glob(os.path.join(odin_path, "*.xml"))

# this is an annoying required conversion between WALS language ids and ISO language ids
wals_dictionary = WalsLanguageCodes(os.path.join(wals_path, "wals-language"))

# this is a simple list of languages and their gold-value for feature.
wals_svo = WalsFeature(os.path.join(wals_path, "wals-dataset"), "81A", wals_dictionary)
wals_sv = WalsFeature(os.path.join(wals_path, "wals-dataset"), "82A", wals_dictionary)
wals_ov = WalsFeature(os.path.join(wals_path, "wals-dataset"), "83A", wals_dictionary)
wals_nadj = WalsFeature(os.path.join(wals_path, "wals-dataset"), "87A", wals_dictionary)

# some globals
svo_feature_dictionary = {}
sv_feature_dictionary = {}
ov_feature_dictionary = {}
nadj_feature_dictionary = {}

svo_feature_num_instances_dictionary = {}
sv_feature_num_instances_dictionary = {}
ov_feature_num_instances_dictionary = {}
nadj_feature_num_instances_dictionary = {}

num_languages = len(odin_corpus)
i = 0


svo_possibilities = ["SOV", "SVO", "VSO", "VOS", "OVS", "OSV", "ndo"]  # ndo is "no dominant order"
sv_possibilities = ["SV", "VS", "ndo"]  # ndo is "no dominant order"
ov_possibilities = ["OV", "VO", "ndo"]  # ndo is "no dominant order"
nadj_possibilities = ["Noun-Adjective", "Adjective-Noun", "ndo", "other"]

nadj_errors = errors.ErrorAnalysis(wals_nadj, "Noun-Adjective")
svo_errors = errors.ErrorAnalysis(wals_nadj, "SVO")
ov_errors = errors.ErrorAnalysis(wals_nadj, "SV")
sv_errors = errors.ErrorAnalysis(wals_nadj, "OV")

try:
    os.stat(data_dir)
except:
    os.mkdir(data_dir)

do_nadj = False
do_svo = False
do_sv = False
do_ov = False

##############################################################
# get parser args and set up global variables
##############################################################
parser = argparse.ArgumentParser(description='XIGT Language Profiler.')
parser.add_argument('-n', '--nadj', help="calculate noun-adjective order", action="store_true")
parser.add_argument('-s', '--svo', help="calculate subject-object-verb order", action="store_true")
parser.add_argument('-o', '--ov', help="calculate object-verb order", action="store_true")
parser.add_argument('-v', '--sv', help="calculate subject-verb order", action="store_true")
parser.add_argument('-a', '--all', help="calculate all orders", action="store_true")
args = parser.parse_args()

if args.nadj or args.all:
    do_nadj = True
    print("Determining Noun-Adjective Order")
if args.svo or args.all:
    do_svo = True
    print("Determining Subject-Verb-Object Order")
if args.sv or args.all:
    do_sv = True
    print("Determining Subject-Verb Order")
if args.ov or args.all:
    do_ov = True
    print("Determining Object-Verb Order")


def examine(calc, feature_dictionary, feature_num_instances_dictionary, error_analyzer):
    calc.estimate_word_order_for_each_instance()
    if calc.best_guess != "unk":
        feature_dictionary[language_code] = calc.best_guess
        feature_num_instances_dictionary[language_code] = calc.instance_count
    calc.print_language_name()
    calc.print_order_estimates()
    error_analyzer.analyze_instance(calc)


def report(feature_dictionary, wals, feature_num_instances_dictionary, possibilities, label):
    reporting = Reporting(feature_dictionary, wals,
                               feature_num_instances_dictionary,
                               possibilities, data_dir,  label + " Data")
    reporting.print_order_confusion_matrix_for_feature()
    reporting.print_accuracy_vs_num_instances()
    reporting.write_accuracy_vs_num_instances_to_file()


# START REALLY DOING STUFF HERE
# loop through and determine our best guess
for language in odin_corpus:
    i += 1
    filename = os.path.basename(language)
    language_code = os.path.splitext(filename)[0]

    # DEBUG
    #language = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/yaq.xml"
    #language_code = "eng"

    wals_nadj_value = wals_nadj.get_value_from_iso_language_id(language_code)
    wals_svo_value = wals_svo.get_value_from_iso_language_id(language_code)
    wals_sv_value = wals_sv.get_value_from_iso_language_id(language_code)
    wals_ov_value = wals_ov.get_value_from_iso_language_id(language_code)
    if wals_svo_value == "No Match" \
            and wals_sv_value == "No Match" \
            and wals_ov_value == "No Match" \
            and wals_nadj_value == "No Match":
        continue  # early out if no one cares

    xc = xigtxml.load(language, mode='full')
    if wals_nadj_value != "No Match" and do_nadj:
        calc = NounAdjectiveProbe(xc, language_code)
        examine(calc, nadj_feature_dictionary, nadj_feature_num_instances_dictionary, nadj_errors)
    if wals_svo_value != "No Match" and do_svo:
        calc = SVOProbe(xc, language_code)
        examine(calc, svo_feature_dictionary, svo_feature_num_instances_dictionary, svo_errors)
    if wals_sv_value != "No Match" and do_sv:
        calc = SVProbe(xc, language_code)
        examine(calc, sv_feature_dictionary, sv_feature_num_instances_dictionary, sv_errors)
    if wals_ov_value != "No Match" and do_ov:
        calc = OVProbe(xc, language_code)
        examine(calc, ov_feature_dictionary, ov_feature_num_instances_dictionary, ov_errors)

    # DEBUG
    # if len(nadj_errors.incorrect_iso_ids) > 1:
    #    break


if do_nadj:
    report(nadj_feature_dictionary, wals_nadj, nadj_feature_num_instances_dictionary, nadj_possibilities, "Noun-Adjective")

if do_svo:
    report(svo_feature_dictionary, wals_svo, svo_feature_num_instances_dictionary, svo_possibilities, "SVO")

if do_sv:
    report(sv_feature_dictionary, wals_sv, sv_feature_num_instances_dictionary, sv_possibilities, "SV")

if do_ov:
    report(ov_feature_dictionary, wals_ov, ov_feature_num_instances_dictionary, ov_possibilities, "OV")


if do_nadj:
    nadj_errors.print_incorrect_guesses()

if do_svo:
    svo_errors.print_incorrect_guesses()

if do_sv:
    sv_errors.print_incorrect_guesses()

if do_ov:
    ov_errors.print_incorrect_guesses()



