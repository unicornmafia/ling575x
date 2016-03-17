##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# ov.py
#
# author:  tcmarsh@uw.edu
#
# description:  class for determining the if a past tense is present
#
##############################################################################
from wordpos import WordPos
import xigt.ref as ref
from featureProbe import FeatureProbe


#
# PastTenseProbe:  contains logic for determining if a past tense is present
#
class PastTenseProbe(FeatureProbe):
    #
    # constructor
    #
    # parameters:
    #   debug:  print dependency parse and text for each instance
    #
    def __init__(self, corpus, language_code, debug=False, ndo_threshold=0.25):
        super(PastTenseProbe, self).__init__(corpus,
                                             language_code,
                                             ["marked", "unmarked"],
                                             "Past Tense",
                                             debug,
                                             ndo_threshold)

    #
    # determine_feature_value_for_instance(): estimates word order for a single instance
    # note:  this only checks for non-passive constructions
    # parameters:
    #   igt - the igt
    # look at n, n2, find PAST, PST
    def determine_feature_value_for_instance(self, igt):
        try:
            normalized_gloss_line = igt["n"]["n2"].value.lower()

        except KeyError:
            return

        if "past" in normalized_gloss_line or "pst" in normalized_gloss_line:
            self.instance_count += 1
            self.order_counts["marked"] += 1.0
        else:
            self.instance_count += 1
            self.order_counts["unmarked"] += 1.0

