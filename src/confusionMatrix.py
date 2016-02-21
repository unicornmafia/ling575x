__author__ = 'thomas'
"""
  Python Source Code for ling575x
  Author: Thomas Marsh
  Date: 1/18/2015

  ConfusionMatrix:  utilities for manipulating a confusion matrix

"""


#
# DecisionTree:  trees for Decision Trees
#
class ConfusionMatrix(dict):
    #
    # constructor:  initializes the data
    #
    def __init__(self, batch_label, labels, **kwargs):
        super(ConfusionMatrix, self).__init__(**kwargs)
        self.batchLabel = batch_label
        self.labels = labels
        self.numCorrect = 0
        self.numTries = 0
        for ylabel in labels:
            self[ylabel] = {}
            for xlabel in labels:
                self[ylabel][xlabel] = 0
        self.maxlen = len(max(labels, key=len))

    def add_label(self, true_label, output_label):
        # just exit if we get something we don't expect.  don't collect stats
        try:
            self[true_label][output_label] += 1
        except KeyError:
            if true_label not in self:
                print("Confusion Matrix: Received unrecognized gold standard label.  Ignoring. true_label:" + true_label)
            elif output_label not in self[true_label]:
                print("Confusion Matrix: Received unrecognized system label.  Ignoring. output_label:" + output_label)
            return
        self.numTries += 1
        if true_label == output_label:
            self.numCorrect += 1



    def print_matrix(self):
        ret_string = "Confusion matrix for the " + self.batchLabel + " data:\n"
        ret_string += "row is the truth, column is the system output\n\n" + " " * (self.maxlen + 1)

        for label in self.labels:
            ret_string += label.ljust(self.maxlen) + " "
        ret_string += "\n"
        for ylabel in self.labels:
            ret_string += ylabel.ljust(self.maxlen)
            for xlabel in self.labels:
                ret_string += " " + str(self[ylabel][xlabel]).ljust(self.maxlen)
            ret_string += "\n"
        if self.numTries > 0:
            ret_string += "\n" + self.batchLabel + " accuracy=" + str(self.numCorrect/float(self.numTries)) + "\n\n"
        return ret_string
