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
    def __init__(self, batchLabel, labels, **kwargs):
        super(ConfusionMatrix, self).__init__(**kwargs)
        self.batchLabel = batchLabel
        self.labels = labels
        self.numCorrect = 0
        self.numTries = 0
        for ylabel in labels:
            self[ylabel] = {}
            for xlabel in labels:
                self[ylabel][xlabel] = 0
        self.maxlen = len(max(labels, key=len))

    def addLabel(self, trueLabel, outputLabel):
        self.numTries += 1
        self[trueLabel][outputLabel] += 1
        if trueLabel == outputLabel:
            self.numCorrect += 1

    def printMatrix(self):
        retString = "Confusion matrix for the " + self.batchLabel + " data:\n"
        retString += "row is the truth, column is the system output\n\n" + " " * (self.maxlen + 1)


        for label in self.labels:
            retString += label.ljust(self.maxlen) + " "
        retString += "\n"
        for ylabel in self.labels:
            retString += ylabel.ljust(self.maxlen)
            for xlabel in self.labels:
                retString += " " + str(self[ylabel][xlabel]).ljust(self.maxlen)
            retString += "\n"
        if self.numTries > 0:
            retString += "\n" + self.batchLabel + " accuracy=" + str(self.numCorrect/float(self.numTries)) + "\n\n"
        return retString