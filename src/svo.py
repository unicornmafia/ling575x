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
        self.SVO_to_SV = {"SOV": "SV", "SVO": "SV", "VSO": "VS", "VOS": "VS", "OVS": "VS", "OSV": "SV"}
        self.SVO_to_OV = {"SOV": "OV", "SVO": "VO", "VSO": "VO", "VOS": "VO", "OVS": "OV", "OSV": "OV"}
        self.SV_order_probabilities = {"SV": 0.0, "VS": 0.0}
        self.SV_possibilities = {"SV": ["SOV", "SVO", "OSV"], "VS": ["VSO", "VOS", "OVS"]}
        self.OV_order_probabilities = {"OV": 0.0, "VO": 0.0}
        self.OV_possibilities = {"OV": ["SOV", "OVS", "OSV"], "VO": ["SVO", "VSO", "VOS"]}
        self.total_instance_count = 0
        self.svo_instance_count = 0
        self.sv_instance_count = 0
        self.ov_instance_count = 0
        self.corpus = corpus
        self.language_code = language_code
        self.debug = debug
        self.svo_sorted_probs = []
        self.sv_sorted_probs = []
        self.ov_sorted_probs = []
        self.svo_best_guess = "unk"
        self.ov_best_guess = "unk"
        self.sv_best_guess = "unk"
        self.ndo_threshold = 0.15
        self.distribute_unknown_probabilities = False

    #
    # list_to_word_order()
    # parameter:
    #   list:  a list containing the WordPos objects in the correct sorted order
    # returns: a string for the most likely word order
    #
    def list_to_word_order(self, word_list):
        #todo:  there may not be all three
        #todo:  if there are two, should we distribute them equally around the ones that they might match?
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
                if pos.text == "nsubj" and not found_subj and head_word == root_word:
                    function_list.append(WordPos(word_token, "S", segmentation))
                    found_subj = True
                    if found_obj:
                        break  # break out of the loop.   we have everything we need
                elif pos.text == "dobj" and not found_obj and head_word == root_word:
                    function_list.append(WordPos(word_token, "O", segmentation))
                    found_obj = True
                    if found_subj:
                        break  # break out of the loop.   we have everything we need

        # if we've found something, let's add some probabilities
        if found_root and len(function_list) > 1:
            self.total_instance_count += 1
            sorted_list = sorted(function_list)
            word_order = self.list_to_word_order(sorted_list)
            if found_subj and found_obj:
                self.svo_instance_count += 1
                self.sv_instance_count += 1
                self.ov_instance_count += 1
                self.SVO_order_probabilities[word_order] += 1.0
                self.SV_order_probabilities[self.SVO_to_SV[word_order]] += 1.0
                self.OV_order_probabilities[self.SVO_to_OV[word_order]] += 1.0
                if self.debug:
                    self.debug_log("WORD-ORDER: " + word_order)
            elif found_subj:
                self.sv_instance_count += 1
                self.SV_order_probabilities[word_order] += 1.0
                # if we don't know obj, but we know sv, let's distribute evenly
                if not found_obj and self.distribute_unknown_probabilities:
                    for order in self.SV_possibilities[word_order]:  # word_order is either "SV" or "VS"
                        self.SVO_order_probabilities[order] += 1.0/len(self.SV_possibilities[word_order])
            elif found_obj:
                self.ov_instance_count += 1
                self.OV_order_probabilities[word_order] += 1.0
                # if we don't know subj, but we know sv, let's distribute evenly
                if not found_subj and self.distribute_unknown_probabilities:
                    for order in self.OV_possibilities[word_order]:  # word_order is either "OV" or "VO"
                        self.SVO_order_probabilities[order] += 1.0/len(self.OV_possibilities[word_order])

    #
    # log to console if debugging is turned on
    #
    def debug_log(self, string):
        if self.debug:
            print(string)

    def generate_best_guess(self, probabilities):
        best_guess = "unk"
        sorted_probs = sorted(probabilities, key=probabilities.get, reverse=True)
        if len(sorted_probs) == 0:
            return ["unk", None]
        elif len(sorted_probs) == 1:
            if probabilities[sorted_probs[0]] == 0.0:
                return ["unk", None]
            best_guess = sorted_probs[0]
        elif len(sorted_probs) > 1:  # see if the top one is over the threshold from the secondmost one
            if probabilities[sorted_probs[0]] == 0.0:
                return ["unk", None]
            diff = probabilities[sorted_probs[0]]-probabilities[sorted_probs[1]]
            if diff > self.ndo_threshold:
                best_guess = sorted_probs[0]
            else:
                best_guess = "ndo"  # no dominate order because probabilities of first two are too similar
        return [best_guess, sorted_probs]

    #
    # estimate_word_order_for_each_instance() - loops through all the igt instances and calculates word order.
    #               NOTE:  there is code in here to print the dependency parse because that was a pain!
    # parameters:
    #   corpus: a single, parsed, XIGT language file
    #
    def estimate_word_order_for_each_instance(self):
        for igt in self.corpus:
           self.estimate_word_order_for_instance(igt)

        if self.svo_instance_count > 0:
            # todo: UGLY!  will fix
            retval = self.generate_best_guess(self.SVO_order_probabilities)
            self.svo_best_guess = retval[0]
            self.svo_sorted_probs = retval[1]

        if self.sv_instance_count > 0:
            retval = self.generate_best_guess(self.SV_order_probabilities)
            self.sv_best_guess = retval[0]
            self.sv_sorted_probs = retval[1]

        if self.ov_instance_count > 0:
            retval = self.generate_best_guess(self.OV_order_probabilities)
            self.ov_best_guess = retval[0]
            self.ov_sorted_probs = retval[1]

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
        if self.svo_instance_count > 0 and self.svo_sorted_probs is not None:
            print("SOV ORDER PROBABILITIES:  " + str(self.svo_instance_count) + " Instances")
            for order in self.svo_sorted_probs:
                prob = self.SVO_order_probabilities[order]/float(self.svo_instance_count)
                if prob > 0.0:
                    print(order + ": " + str(prob))
            print("")
        else:
            print("NO USABLE INSTANCES FOUND:  SOV order undeterminable from data\n")

