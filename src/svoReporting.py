__author__ = 'thomas'
from confusionMatrix import ConfusionMatrix


#
# SVOReporting:  helper class for keeping track of and reporting statistics of our data.
#
#
class SVOReporting:
    def __init__(self, feature_dictionary,
                       wals_gold_standard,
                       wals_dictionary,
                       feature_instances_dictionary,
                       possibilities,
                       label):
        self.feature_dictionary = feature_dictionary
        self.wals_gold_standard = wals_gold_standard
        self.feature_instances_dictionary = feature_instances_dictionary
        self.wals_dictionary = wals_dictionary
        self.label = label
        self.possibilities = possibilities

    #
    # find the accuracy of a feature given feature with respect to WALS data, but make sure that
    # we have at least threshold_number_of_instances instances in the data.  otherwise ignore it.
    #
    def get_single_accuracy(self, threshold_number_of_instances):
        num_reported = 0
        num_correct = 0
        for code in self.feature_dictionary:
            our_value = self.feature_dictionary[code]
            num_instances = self.feature_instances_dictionary[code]
            if num_instances >= threshold_number_of_instances:
                try:
                    wals_code = self.wals_dictionary.iso_to_wals[code]
                    wals_value = self.wals_gold_standard.feature_dictionary[wals_code]
                    num_reported += 1
                    if wals_value == our_value:
                        num_correct += 1
                except KeyError:
                    pass  # we can't find it.  don't calculate it
        if num_reported > 0:
            return num_correct/float(num_reported)
        else:
            return 0.0

    #
    # find the accuracy of a feature given feature with respect to WALS data, plot by limiting
    # by the number of instances contained in the language.  ignore if language does not have that
    # many instances
    #
    def print_accuracy_vs_num_instances(self):
        print("\nAccuracies vs num of instances for " + self.label)
        thresholds = [1, 2, 3, 4, 5, 10, 20, 30, 50, 100]
        for threshold in thresholds:
            accuracy = self.get_single_accuracy(threshold)
            print(str(threshold) + ": " + str(accuracy))

    #
    # print the confusion matrix for the feature.
    # params:
    #  feature_dictionary:  the dictionary in which we have stored OUR best guesses
    #  wals_gold_Standard:  the wals dictionary which stores the WALS gold standard answers
    #  possibilities:  the possible values for the feature
    #  title:  what to title this confusion matrix
    #
    def print_order_confusion_matrix_for_feature(self):
        # build and print a confusion matrix for svo
        print("\nComparing results with gold standard from WALS for " + self.label + ":")
        confusion_matrix = ConfusionMatrix(self.label, self.possibilities)
        num_reported = 0
        for code in self.feature_dictionary:
            our_value = self.feature_dictionary[code]
            try:
                wals_code = self.wals_dictionary.iso_to_wals[code]
                wals_value = self.wals_gold_standard.feature_dictionary[wals_code]
                confusion_matrix.add_label(wals_value, our_value)
                num_reported += 1
            except KeyError:
                pass
                #  print("No matching SVO WALS data for language " + code)
        print("Num Languages Compared: " + str(num_reported))
        if num_reported > 0:
            print(confusion_matrix.print_matrix())
