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
# description:  class for determining the if a future tense is present
#
##############################################################################
from wordpos import WordPos
import xigt.ref as ref
from featureProbe import FeatureProbe


#
# FutureTenseProbe:  contains logic for determining if a future tense is present
#
class FutureTenseProbe(FeatureProbe):
    #
    # constructor
    #
    # parameters:
    #   debug:  print dependency parse and text for each instance
    #
    def __init__(self, corpus, language_code, debug=False, ndo_threshold=0.25):
        super(FutureTenseProbe, self).__init__(corpus,
                                             language_code,
                                             ["marked", "unmarked"],
                                             "Future Tense",
                                             debug,
                                             ndo_threshold)

    #
    # determine_feature_value_for_instance(): estimates word order for a single instance
    # note:  this only checks for non-passive constructions
    # parameters:
    #   igt - the igt
    #  (LOOK FOR "FUT")
    def determine_feature_value_for_instance(self, igt):
        try:
            normalized_gloss_line = igt["n"]["n2"].value

        except KeyError:
            return

        if "future" in normalized_gloss_line or "fut" in normalized_gloss_line:
            self.instance_count += 1
            self.order_counts["marked"] += 1.0
        else:
            self.instance_count += 1
            self.order_counts["unmarked"] += 1.0
