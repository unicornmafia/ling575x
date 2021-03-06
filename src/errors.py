##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# errors.py
#
# author:  tcmarsh@uw.edu
#
# description:  class for error analysis between determinations
#               from XIGT data vs WALS data.
#
##############################################################################
import sys


class ErrorAnalysis:
    def __init__(self, wals_gold_standard, label):
        self.wals_gold_standard = wals_gold_standard
        self.incorrect_iso_ids = []
        self.label = label

    def get_correct_answer(self, calc):
        wals_feature_answer = self.wals_gold_standard.get_value_from_iso_language_id(calc.language_code)
        return wals_feature_answer

    @staticmethod
    def print_stats_for_incorrect_instance(out_file,
                                           iso_code,
                                           correct_answer,
                                           our_answer,
                                           instance_count,
                                           probabilities):
        print("Incorrect Determination for: " + iso_code, file=out_file)
        print("Correct Answer: {}, Our Answer: {}".format(correct_answer, our_answer), file=out_file)
        print("Num Instances: {}".format(instance_count), file=out_file)
        for order, prob in probabilities.items():
            print("Num {}: {}".format(order, prob), file=out_file)
        print("", file=out_file)

    def analyze_instance(self, calc):
        num_instances = calc.instance_count
        our_answer = calc.best_guess
        correct_answer = self.get_correct_answer(calc)
        iso_code = calc.language_code
        probabilities = calc.order_counts
        if our_answer == correct_answer or num_instances == 0:
            return  # this one is correct, we aren't going to rock the boat

        self.incorrect_iso_ids.append((iso_code,
                                       correct_answer,
                                       our_answer,
                                       num_instances,
                                       probabilities))

    def print_incorrect_guesses(self, out_file=sys.stdout):
        print("\nError Analysis for {}".format(self.label), file=out_file)
        for iso_code, correct_answer, our_answer, instance_count, probabilities in self.incorrect_iso_ids:
            ErrorAnalysis.print_stats_for_incorrect_instance(out_file,
                                                             iso_code,
                                                             correct_answer,
                                                             our_answer,
                                                             instance_count,
                                                             probabilities)
