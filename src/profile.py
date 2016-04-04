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
from past import PastTenseProbe
from future import FutureTenseProbe
from nadj import NounAdjectiveProbe
from wals import WalsFeature, WalsLanguageCodes, WalsFeatureTranslatedValues
from reporting import Reporting
import glob
import os
import errors
import argparse

wals_path = "/opt/dropbox/15-16/575x/data/WALS-data"
odin_path = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/"
data_dir = "./data"

# this loads all the odin/xigt files in the path into a list
odin_corpus = glob.glob(os.path.join(odin_path, "*.xml"))

# this is an annoying required conversion between WALS language ids and ISO language ids
wals_dictionary = WalsLanguageCodes(os.path.join(wals_path, "wals-language"))

# this is a simple list of languages and their gold-value for feature.
wals_svo = WalsFeature(os.path.join(wals_path, "wals-dataset"), "81A", wals_dictionary)
wals_sv = WalsFeature(os.path.join(wals_path, "wals-dataset"), "82A", wals_dictionary)
wals_ov = WalsFeature(os.path.join(wals_path, "wals-dataset"), "83A", wals_dictionary)
wals_nadj = WalsFeature(os.path.join(wals_path, "wals-dataset"), "87A", wals_dictionary)
wals_translation_map_past = {"Present, 2-3 remoteness distinctions": "marked",
                             "Present, no remoteness distinctions": "marked",
                             "Present, 4 or more remoteness distinctions": "marked",
                             "No past tense": "unmarked"}
wals_translation_map_future = {"Inflectional future exists": "marked",
                               "No inflectional future": "unmarked"}

wals_past_tense = WalsFeatureTranslatedValues(os.path.join(wals_path, "wals-dataset"),
                                              "66A", wals_dictionary, wals_translation_map_past)
wals_future_tense = WalsFeatureTranslatedValues(os.path.join(wals_path, "wals-dataset"),
                                                "67A", wals_dictionary, wals_translation_map_future)

# some globals
svo_feature_dictionary = {}
sv_feature_dictionary = {}
ov_feature_dictionary = {}
nadj_feature_dictionary = {}
past_tense_feature_dictionary = {}
future_tense_feature_dictionary = {}

svo_feature_num_instances_dictionary = {}
sv_feature_num_instances_dictionary = {}
ov_feature_num_instances_dictionary = {}
nadj_feature_num_instances_dictionary = {}
past_tense_feature_num_instances_dictionary = {}
future_tense_feature_num_instances_dictionary = {}

num_languages = len(odin_corpus)
i = 0

svo_possibilities = ["SOV", "SVO", "VSO", "VOS", "OVS", "OSV", "ndo"]  # ndo is "no dominant order"
sv_possibilities = ["SV", "VS", "ndo"]  # ndo is "no dominant order"
ov_possibilities = ["OV", "VO", "ndo"]  # ndo is "no dominant order"
nadj_possibilities = ["Noun-Adjective", "Adjective-Noun", "ndo"]
past_tense_possibilities = ["marked", "unmarked", "ndo"]
future_tense_possibilities = ["marked", "unmarked", "ndo"]

nadj_errors = errors.ErrorAnalysis(wals_nadj, "Noun-Adjective")
svo_errors = errors.ErrorAnalysis(wals_svo, "SVO")
ov_errors = errors.ErrorAnalysis(wals_ov, "SV")
sv_errors = errors.ErrorAnalysis(wals_sv, "OV")
past_tense_errors = errors.ErrorAnalysis(wals_sv, "Past Tense")
future_tense_errors = errors.ErrorAnalysis(wals_sv, "Future Tense")

try:
    os.stat(data_dir)
except:
    os.mkdir(data_dir)

do_nadj = False
do_svo = False
do_sv = False
do_ov = False
do_past_tense = False
do_future_tense = False

##############################################################
# get parser args and set up global variables
##############################################################
parser = argparse.ArgumentParser(description='XIGT Language Profiler.')
parser.add_argument('-n', '--nadj', help="calculate noun-adjective order", action="store_true")
parser.add_argument('-s', '--svo', help="calculate subject-object-verb order", action="store_true")
parser.add_argument('-o', '--ov', help="calculate object-verb order", action="store_true")
parser.add_argument('-v', '--sv', help="calculate subject-verb order", action="store_true")
parser.add_argument('-a', '--all', help="calculate all orders", action="store_true")
parser.add_argument('-p', '--past', help="analyze for past tense", action="store_true")
parser.add_argument('-f', '--future', help="analyze for future tense", action="store_true")
parser.add_argument('-i', '--minIinstances', type=int, default=6,
                    help="Instances Threshold:  Number of instances to require before accepting data")
parser.add_argument('-d', '--ndo', type=float, default=0.25,
                    help="NDO Threshold:  How close the top two probabilities are required to be for a clear determination.  Items inside this range are marked as NDO")
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
if args.past or args.all:
    do_past_tense = True
    print("Determining Past Tense Inclusion")
if args.future or args.all:
    do_future_tense = True
    print("Determining Future Tense Inclusion")


def examine_language(calc, feature_dictionary, feature_num_instances_dictionary, error_analyzer):
    calc.estimate_word_order_for_each_instance()
    if calc.best_guess != "unk":
        feature_dictionary[language_code] = calc.best_guess
        feature_num_instances_dictionary[language_code] = calc.instance_count
    calc.print_language_name()
    calc.print_order_estimates()
    error_analyzer.analyze_instance(calc)


def final_report(feature_dictionary, wals, feature_num_instances_dictionary, possibilities, errors, label):
    reporting = Reporting(feature_dictionary, wals,
                          feature_num_instances_dictionary,
                          possibilities, label, args.minIinstances)
    # write reports to stdout
    reporting.print_order_confusion_matrix_for_feature()
    reporting.print_accuracy_vs_num_instances()

    # now write reports to file
    base_file_name = os.path.join(data_dir, label.lower().replace(" ", "_"))
    report_file_name = base_file_name + "_report.txt"
    csv_file_name = base_file_name + "_accuracy_data.txt"
    report_file = open(report_file_name, mode='w')
    csv_file = open(csv_file_name, mode='w')
    reporting.print_order_confusion_matrix_for_feature(report_file)
    reporting.print_accuracy_vs_num_instances(report_file)

    # make a csv (maybe not useful?)
    reporting.write_accuracy_vs_num_instances_to_as_csv(csv_file)

    # print the errors to a file
    errors.print_incorrect_guesses(report_file)
    report_file.close()
    csv_file.close()


# START REALLY DOING STUFF HERE
# loop through all the languages and determine our best guesses
for language in odin_corpus:
    i += 1
    filename = os.path.basename(language)
    language_code = os.path.splitext(filename)[0]

    # DEBUG
    # language = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/yaq.xml"
    # language_code = "eng"

    wals_nadj_present = wals_nadj.is_language_present(language_code)
    wals_svo_present = wals_svo.is_language_present(language_code)
    wals_sv_present = wals_sv.is_language_present(language_code)
    wals_ov_present = wals_ov.is_language_present(language_code)
    wals_past_tense_present = wals_past_tense.is_language_present(language_code)
    wals_future_tense_present = wals_future_tense.is_language_present(language_code)
    # check to see if we should bother loading the language
    if (wals_svo_present and do_svo) \
            or (wals_sv_present and do_sv) \
            or (wals_ov_present and do_ov) \
            or (wals_nadj_present and do_nadj) \
            or (wals_past_tense_present and do_past_tense) \
            or (wals_future_tense_present and do_future_tense):

        xc = xigtxml.load(language, mode='full')
        if wals_nadj_present and do_nadj:
            calc = NounAdjectiveProbe(xc, language_code, False, args.ndo)
            examine_language(calc, nadj_feature_dictionary, nadj_feature_num_instances_dictionary, nadj_errors)
        if wals_svo_present and do_svo:
            calc = SVOProbe(xc, language_code, False, args.ndo)
            examine_language(calc, svo_feature_dictionary, svo_feature_num_instances_dictionary, svo_errors)
        if wals_sv_present and do_sv:
            calc = SVProbe(xc, language_code, False, args.ndo)
            examine_language(calc, sv_feature_dictionary, sv_feature_num_instances_dictionary, sv_errors)
        if wals_ov_present and do_ov:
            calc = OVProbe(xc, language_code, False, args.ndo)
            examine_language(calc, ov_feature_dictionary, ov_feature_num_instances_dictionary, ov_errors)
        if wals_past_tense_present and do_past_tense:
            calc = PastTenseProbe(xc, language_code, False, args.ndo)
            examine_language(calc, past_tense_feature_dictionary, past_tense_feature_num_instances_dictionary,
                             past_tense_errors)
        if wals_future_tense_present and do_future_tense:
            calc = FutureTenseProbe(xc, language_code, False, args.ndo)
            examine_language(calc, future_tense_feature_dictionary, future_tense_feature_num_instances_dictionary,
                             future_tense_errors)

            # DEBUG
            # if len(nadj_errors.incorrect_iso_ids) > 1:
            #     break

if do_nadj:
    final_report(nadj_feature_dictionary, wals_nadj, nadj_feature_num_instances_dictionary, nadj_possibilities,
                 nadj_errors,
                 "Noun-Adjective")

if do_svo:
    final_report(svo_feature_dictionary, wals_svo, svo_feature_num_instances_dictionary, svo_possibilities, svo_errors,
                 "SVO")

if do_sv:
    final_report(sv_feature_dictionary, wals_sv, sv_feature_num_instances_dictionary, sv_possibilities, sv_errors, "SV")

if do_ov:
    final_report(ov_feature_dictionary, wals_ov, ov_feature_num_instances_dictionary, ov_possibilities, ov_errors, "OV")

if do_past_tense:
    final_report(past_tense_feature_dictionary, wals_past_tense, past_tense_feature_num_instances_dictionary,
                 past_tense_possibilities, past_tense_errors, "Past Tense")

if do_future_tense:
    final_report(future_tense_feature_dictionary, wals_future_tense, future_tense_feature_num_instances_dictionary,
                 future_tense_possibilities, future_tense_errors, "Future Tense")
