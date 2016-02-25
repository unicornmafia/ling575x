##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# nadj.py
#
# author:  tcmarsh@uw.edu
#
# description:  class for determining the noun-adjective word order for a XIGT
#               corpus of odin data
#
##############################################################################
from wordpos import WordPos
import xigt.ref as ref
from featureProbe import FeatureProbe


#
# NounAdjectiveProbe:  contains logic for determining word order (WALS feature 87A) for a single language.
#
class NounAdjectiveProbe(FeatureProbe):
    #
    # constructor
    #
    # parameters:
    #   debug:  print dependency parse and text for each instance
    #
    def __init__(self, corpus, language_code, debug=False):
        super(NounAdjectiveProbe, self).__init__(corpus,
                                                 language_code,
                                                 ["Adjective-Noun", "Noun-Adjective"],
                                                 "Adjective-Noun",
                                                 debug)
        self.noun_list = ["nsubj", "dobj", "nn", "nsubjpass"]

    def is_head_noun(self, adj_pos, igt, dparse):
        head_word_tag = adj_pos.attributes["head"]
        for pos in dparse:
            try:
                pos_tag = pos.attributes["dep"]
                if pos_tag == head_word_tag:
                    if pos.text in self.noun_list:
                        # we found the head word and it's a noun
                        return True
                    else:
                        # we found the head word, but it's not a noun
                        return False
            except KeyError:  # something didn't have attributes we expected.   we're ok with this.
                continue
        # weird.  we didn't find the word.
        return False

    def estimate_word_order_for_instance(self, igt):
        try:
            words = igt["w"]
            dparse = igt["w-ds"]
        except KeyError:
            return

        if len(dparse) < 0:
            return  # early exit.  wtf.

        # loop looking for all adjectives
        for pos in dparse:
            if pos.text == "amod":
                word = words[pos.attributes["dep"]]
                word_segmentation = word.segmentation
                word_token = ref.resolve(igt, word_segmentation)
                try:
                    if not self.is_head_noun(pos, igt, dparse):
                        continue
                    head_word = words[pos.attributes["head"]]
                    head_word_segmentation = head_word.segmentation
                    adj = WordPos(word_token, "adj", word_segmentation)
                    noun = WordPos(head_word, "noun", head_word_segmentation)
                    if adj > noun:
                        self.order_counts["Noun-Adjective"] += 1.0
                    else:  # assume noun>adj
                        self.order_counts["Adjective-Noun"] += 1.0
                    self.instance_count += 1
                except KeyError:
                    continue

    #
    # generate a best guess of the correct word order.
    #
    def generate_best_guess(self):
        adj_noun_p = self.order_counts["Adjective-Noun"] / float(self.instance_count)
        noun_adj_p = self.order_counts["Noun-Adjective"] / float(self.instance_count)
        if abs(adj_noun_p - noun_adj_p) < self.ndo_threshold:
            self.best_guess = "ndo"
        elif adj_noun_p > noun_adj_p:
            self.best_guess = "Adjective-Noun"
            self.sorted_probs = ["Adjective-Noun", "Noun-Adjective"]
        else:  # presumably noun_adj_p > adj_noun_p
            self.best_guess = "Noun-Adjective"
            self.sorted_probs = ["Noun-Adjective", "Adjective-Noun"]
