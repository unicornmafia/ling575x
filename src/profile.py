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
import glob
import os

odin_path = "/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/"
odin_corpus = glob.glob(os.path.join(odin_path, "*.xml"))

# begin script here
for language in odin_corpus:
    print("Parsing " + os.path.basename(language))
    xc = xigtxml.load(language, mode='full')
    svo_calc = SVO(xc)
    svo_calc.print_language_name()
    svo_calc.estimate_word_order_for_each_instance()
    svo_calc.print_order_estimates()
