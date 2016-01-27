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
# description:  class for determining the SVO word order for a XIGT
#               corpus of odin data
#
##############################################################################
from wordpos import WordPos
import xigt.ref as ref


#
# SVO:  contains logic for determining word order (WALS feature 81A) for a single language.
#
class SVO:
    #
    # constructor
    #
    # parameters:
    #   debug:  print dependency parse and text for each instance
    #
    def __init__(self, corpus, language_code, debug=False):
        self.SVO_order_probabilities = {"SOV": 0.0, "SVO": 0.0, "VSO": 0.0, "VOS": 0.0, "OVS": 0.0, "OSV": 0.0}
        self.instance_count = 0
        self.corpus = corpus
        self.language_code = language_code
        self.debug = debug
        self.sorted_probs = []
        self.best_guess = "unk"
        self.ndo_threshold = 0.1
    #
    # list_to_word_order()
    # parameter:
    #   list:  a list containing the WordPos objects in the correct sorted order
    # returns: a string for the most likely word order
    #
    def list_to_word_order(self, list):
        #todo:  there may not be all three
        #todo:  if there are two, should we distribute them equally around the ones that they might match?
        return list[0].grammatical_function+list[1].grammatical_function+list[2].grammatical_function

    #
    # estimate_word_order_for_instance(): estimates word order for a single instance
    # parameters:
    #   igt - the igt
    #
    def estimate_word_order_for_instance(self, igt):
        function_list = []
        words = igt["w"]
        dparse = igt["w-ds"]
        for pos in dparse:
            word = words[pos.attributes["dep"]]
            segmentation = word.segmentation
            word_token = ref.resolve(igt, segmentation)
            #todo:  There may be more than one of some of these.
            #todo:  do we need to check to see if the parent is the root?
            if pos.text == "nsubj":
                function_list.append(WordPos(word_token, "S", segmentation))
            elif pos.text == "root":
                function_list.append(WordPos(word_token, "V", segmentation))
            elif pos.text == "dobj":
                function_list.append(WordPos(word_token, "O", segmentation))

        if len(function_list) == 3:
            sorted_list = sorted(function_list)
            self.instance_count += 1
            word_order = self.list_to_word_order(sorted_list)
            self.SVO_order_probabilities[word_order] += 1.0
            if self.debug:
                self.debug_log("WORD-ORDER: " + word_order)

    #
    # log to console if debugging is turned on
    #
    def debug_log(self, string):
        if self.debug:
            print(string)


    #
    # estimate_word_order_for_each_instance() - loops through all the igt instances and calculates word order.
    #               NOTE:  there is code in here to print the dependency parse because that was a pain!
    # parameters:
    #   corpus: a single, parsed, XIGT language file
    #
    def estimate_word_order_for_each_instance(self):
        for igt in self.corpus:
            try:
                # print the phrases
                phrases = igt["p"]
                # print the dependency parse of the original text
                words = igt["w"]
                dparse = igt["w-ds"]
                first_time = True
                for pos in dparse:
                    # print the igt instance name the first time
                    if first_time:
                        first_time = False
                        self.debug_log("\nIGT INSTANCE: " + igt.id)
                        self.debug_log("TEXT: ")
                        for phrase in phrases:
                            text = igt["n"][phrase.content].text
                            self.debug_log("  text: " + text)
                        self.debug_log("DEPENDENCY PARSE: ")

                    word = words[pos.attributes["dep"]]
                    segmentation = word.segmentation
                    word_token = ref.resolve(igt, segmentation)
                    self.debug_log("  " + word_token + ": " + pos.text)
                # add word order estimate
                if not first_time:
                    self.estimate_word_order_for_instance(igt)
            except:
                # just move on for now.  this will happen a lot when data is not present
                pass
        if self.instance_count > 0:
            self.sorted_probs = sorted(self.SVO_order_probabilities, key=self.SVO_order_probabilities.get, reverse=True)
            if len(self.sorted_probs) == 1:
                self.best_guess = self.sorted_probs[0]
            elif len(self.sorted_probs) > 1:  # see if the top one is over the threshold from the secondmost one
                diff = self.SVO_order_probabilities[self.sorted_probs[0]]-self.SVO_order_probabilities[self.sorted_probs[1]]
                if diff > self.ndo_threshold:
                    self.best_guess = self.sorted_probs[0]
                else:
                    self.best_guess = "ndo"  # no dominate order because probabilities of first two are too similar

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
        if self.instance_count > 0:
            print("SOV ORDER PROBABILITIES:  " + str(self.instance_count) + " Instances")
            for order in self.sorted_probs:
                prob = self.SVO_order_probabilities[order]/float(self.instance_count)
                if prob > 0.0:
                    print(order + ": " + str(prob))
            print("")
        else:
            print("NO USABLE INSTANCES FOUND:  SOV order undeterminable from data\n")
