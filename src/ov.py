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
# description:  class for determining the OV word order for a XIGT
#               corpus of odin data
#
##############################################################################
from wordpos import WordPos
import xigt.ref as ref
from featureProbe import FeatureProbe


#
# OVProbe:  contains logic for determining OV word order for a language
#
class OVProbe(FeatureProbe):
    #
    # constructor
    #
    # parameters:
    #   debug:  print dependency parse and text for each instance
    #
    def __init__(self, corpus, language_code, debug=False):
        super(OVProbe, self).__init__(corpus,
                                      language_code,
                                      ["OV", "VO"],
                                      "OV",
                                      debug)

    #
    # estimate_word_order_for_instance(): estimates word order for a single instance
    # note:  this only checks for non-passive constructions
    # parameters:
    #   igt - the igt
    #
    def estimate_word_order_for_instance(self, igt):
        function_list = []
        try:
            words = igt["w"]
            dparse = igt["w-ds"]
        except KeyError:
            return

        found_root = False
        found_subj = False
        found_obj = False
        root_word = ""

        if len(dparse) > 0 and dparse[0].text != "root":
            return  # early exit if it doesn't have a root.  unusable
        else:
            found_root = True
            pos = dparse[0]
            root_word = pos.attributes["dep"]
            word = words[pos.attributes["dep"]]
            segmentation = word.segmentation
            word_token = ref.resolve(igt, segmentation)
            function_list.append(WordPos(word_token, "V", segmentation))

        # loop looking for subject and object of that root
        for pos in dparse:
            if pos.text != "root":
                word = words[pos.attributes["dep"]]
                segmentation = word.segmentation
                word_token = ref.resolve(igt, segmentation)
                head_word = pos.attributes["head"]
                if pos.text == "dobj" and not found_obj and head_word == root_word:
                    function_list.append(WordPos(word_token, "O", segmentation))
                    found_obj = True
                    break  # break out of the loop.   we have everything we need

        # if we've found something, let's add some probabilities
        if found_root and len(function_list) > 1:
            sorted_list = sorted(function_list)
            word_order = FeatureProbe.list_to_word_order(sorted_list)
            if found_obj:
                self.instance_count += 1
                self.order_counts[word_order] += 1.0



