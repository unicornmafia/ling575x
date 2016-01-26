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
    def __init__(self):
        self.SVO_order_probabilities = {"SOV": 0.0, "SVO": 0.0, "VSO": 0.0, "VOS": 0.0, "OVS": 0.0, "OSV": 0.0}
        self.instance_count = 0

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
            print("WORD-ORDER: " + word_order)

    #
    # estimate_word_order_for_each_instance() - loops through all the igt instances and calculates word order.
    #               NOTE:  there is code in here to print the dependency parse because that was a pain!
    # parameters:
    #   corpus: a single, parsed, XIGT language file
    #
    def estimate_word_order_for_each_instance(self, corpus):
        for igt in corpus:
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
                        print("\nIGT INSTANCE: " + igt.id)
                        print("TEXT: ")
                        for phrase in phrases:
                            text = igt["n"][phrase.content].text
                            print("  text: " + text)
                        print("DEPENDENCY PARSE: ")

                    word = words[pos.attributes["dep"]]
                    segmentation = word.segmentation
                    word_token = ref.resolve(igt, segmentation)
                    print("  " + word_token + ": " + pos.text)
                # add word order estimate
                if not first_time:
                    self.estimate_word_order_for_instance(igt)
            except:
                # just move on for now.  this will happen a lot when data is not present
                pass

    #
    # print_order_estimates() - prints the list of probabilities of the word orders
    #
    def print_order_estimates(self):
        sorted_probs = sorted(self.SVO_order_probabilities, key=self.SVO_order_probabilities.get, reverse=True)
        print("\nSOV ORDER PROBABILITIES:  " + str(self.instance_count) + " Instances")
        for order in sorted_probs:
            prob = self.SVO_order_probabilities[order]/float(self.instance_count)
            if prob > 0.0:
                print(order + ": " + str(prob))
