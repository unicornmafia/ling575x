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
        self.instance_ranges = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
                                (6, 10), (11, 20), (21, 30), (31, 40), (41, 50),
                                (51, 100), (101, 200), (201, 300), (301, 400), (401, 500),
                                (500, 1000000)]
        self.instance_labels = self.get_labels_from_ranges(self.instance_ranges)

    def get_labels_from_ranges(self, instance_ranges):
        longest_length = ""
        instance_labels = []
        #  warning:  I'm being too clever here.  tuple populates the string.
        #  python slickness = hard to read sometimes
        for instance_range in instance_ranges:
            instance_labels.append("%d-%d" % instance_range)
        longest_length = len(max(instance_labels, key=len)) + 2
        for i in range(0, len(instance_labels)):
            instance_labels[i] = instance_labels[i].ljust(longest_length, ".")
        return instance_labels

    #
    # find the accuracy of a feature given feature with respect to WALS data, but make sure that
    # we have at least threshold_number_of_instances instances in the data.  otherwise ignore it.
    #
    def get_single_accuracy(self, instance_range):
        num_reported = 0
        num_correct = 0
        for code in self.feature_dictionary:
            our_value = self.feature_dictionary[code]
            num_instances = self.feature_instances_dictionary[code]
            if instance_range[0] <= num_instances <= instance_range[1]:
                try:
                    wals_code = self.wals_dictionary.iso_to_wals[code]
                    wals_value = self.wals_gold_standard.feature_dictionary[wals_code]
                    num_reported += 1
                    if wals_value == our_value:
                        num_correct += 1
                except KeyError:
                    pass  # we can't find it.  don't calculate it
        if num_reported > 0:
            return num_reported, num_correct
        else:
            return num_reported, num_correct

    #
    # find the accuracy of a feature given feature with respect to WALS data, plot by limiting
    # by the number of instances contained in the language.  ignore if language does not have that
    # many instances
    #
    def print_accuracy_vs_num_instances(self):
        print("\nAccuracies vs num of instances for " + self.label)
        for i in range(0, len(self.instance_ranges)):
            instance_range = self.instance_ranges[i]
            instance_label = self.instance_labels[i]
            statistics = self.get_single_accuracy(instance_range)
            try:
                accuracy = statistics[1]/float(statistics[0])
                print(instance_label + "(" + str(statistics[0]) + " instances) : " + str(accuracy))
            except ZeroDivisionError:
                print(instance_label + "(" + str(statistics[0]) + " instances) : None")

    def write_accuracy_vs_num_instances_to_file(self):
        out_file = open(self.label + ".csv", "w")
        print("Number Of Usable Instances, Number of Languages With data, Accuracy (num correct/num languages)", file=out_file)
        for i in range(0, len(self.instance_ranges)):
            instance_range = self.instance_ranges[i]
            instance_label = self.instance_labels[i]
            statistics = self.get_single_accuracy(instance_range)
            try:
                accuracy = statistics[1]/float(statistics[0])
                print(instance_label.strip(".") + ", " + str(statistics[0]) + ", " + str(accuracy), file=out_file)
            except ZeroDivisionError:
                print(instance_label.strip(".") + ", " + str(statistics[0]) + ", 0", file=out_file)

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
