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


odin_corpus = ["/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/eng.xml"]

# begin script here
for language in odin_corpus:
    xc = xigtxml.load(language, mode='full')
    svo_calc = SVO()
    svo_calc.estimate_word_order_for_each_instance(xc)
    svo_calc.print_order_estimates()
