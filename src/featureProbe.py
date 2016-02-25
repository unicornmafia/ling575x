##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# svo.py
#
# author:  tcmarsh@uw.edu
#
# description:  base class for determining the word order features for a XIGT
#               corpus of odin data
#
##############################################################################
import abc


#
# base class for determining word order for a single language.
#
class FeatureProbe:
    __metaclass__ = abc.ABCMeta

    #
    # constructor
    #
    # parameters:
    #   debug:  print dependency parse and text for each instance
    #
    def __init__(self, corpus, language_code, possibilities, label, debug):
        self.order_counts = {}
        self.order_possibilities = possibilities
        self.instance_count = 0
        self.corpus = corpus
        self.language_code = language_code
        self.debug = debug
        self.sorted_probs = []
        self.best_guess = "unk"
        self.ndo_threshold = 0.25
        self.label = label
        for possibility in self.order_possibilities:
            self.order_counts[possibility] = 0.0

    #
    # list_to_word_order()
    # parameter:
    #   list:  a list containing the WordPos objects in the correct sorted order
    # returns: a string for the most likely word order
    #
    @staticmethod
    def list_to_word_order(word_list):
        if len(word_list) == 1:
            return word_list[0].grammatical_function  # this had better be "v"
        elif len(word_list) == 2:
            return word_list[0].grammatical_function+word_list[1].grammatical_function
        else:  # len had better be 3
            return word_list[0].grammatical_function+word_list[1].grammatical_function+word_list[2].grammatical_function

    #
    # estimate_word_order_for_instance(): estimates word order for a single instance
    # note:  this only checks for non-passive constructions
    # parameters:
    #   igt - the igt
    #
    @abc.abstractmethod
    def estimate_word_order_for_instance(self, igt):
        """ must implement as child """

    #
    # log to console if debugging is turned on
    #
    def debug_log(self, string):
        if self.debug:
            print(string)

    #
    # generate a best guess of the correct word order.
    #
    def generate_best_guess(self):
        best_guess = "unk"
        sorted_probs = sorted(self.order_counts, key=self.order_counts.get, reverse=True)
        if len(sorted_probs) == 0:
            return ["unk", None]
        elif len(sorted_probs) == 1:
            if self.order_counts[sorted_probs[0]] == 0.0:
                return ["unk", None]
            best_guess = sorted_probs[0]
        elif len(sorted_probs) > 1:  # see if the top one is over the threshold from the secondmost one
            if self.order_counts[sorted_probs[0]] == 0.0:
                return ["unk", None]
            diff = self.order_counts[sorted_probs[0]] - self.order_counts[sorted_probs[1]]
            if diff > self.ndo_threshold:
                best_guess = sorted_probs[0]
            else:
                best_guess = "ndo"  # no dominate order because probabilities of first two are too similar
        self.best_guess = best_guess
        self.sorted_probs = sorted_probs

    #
    # estimate_word_order_for_each_instance() - loops through all the igt instances and calculates word order.
    #               NOTE:  there is code in here to print the dependency parse because that was a pain!
    # parameters:
    #   corpus: a single, parsed, XIGT language file
    #
    def estimate_word_order_for_each_instance(self):
        for igt in self.corpus:
            self.estimate_word_order_for_instance(igt)

        if self.instance_count > 0:
            self.generate_best_guess()

    #
    # print_language_name() - print the name of the language as stored in first instance metadata
    #
    def print_language_name(self):
        print("Language Code (from file name): " + self.language_code)
        for igt in self.corpus:
            for metadata in igt.metadata[0][0]:
                if metadata.name == 'subject':
                    print("Subject: " + metadata.text)
                    return

    #
    # print_order_estimates() - prints the list of probabilities of the word orders
    #
    def print_order_estimates(self):
        if self.instance_count > 0 and self.sorted_probs is not None:
            print(self.label + " ORDER PROBABILITIES:  " + str(self.instance_count) + " Instances")
            for order in self.sorted_probs:
                prob = self.order_counts[order] / float(self.instance_count)
                if prob > 0.0:
                    print(order + ": " + str(prob))
            print("")
        else:
            print("NO USABLE INSTANCES FOUND:  " + self.label + " order indeterminate from data\n")

