##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# wordpos.py
#
# author:  tcmarsh@uw.edu
#
# description:  contains WordPos class, a class for storing word positions
#
##############################################################################
import re
segmentation_regex = re.compile('^[a-z]+([1-9]+)\[([0-9]+):([0-9]+)\]')

#
# WordPos:  a class for storing and comparing word positions.
#
class WordPos:
    #
    # constructor
    #
    # parameters:
    #   token - the token for the word
    #   grammatical_function - this is one of ['S', 'V', 'O']
    #   segmentation - the word's segmentation.
    #           e.g. p1[43:99] meaning paragraph 1, beginning at offset 43 and ending at offset 99
    #
    def __init__(self, token, grammatical_function, segmentation):
        self.segmentation = segmentation
        self.grammatical_function = grammatical_function
        self.token = token
        self.paragraph = None
        self.offset = None
        self.parse_segmentation()

    #
    # parse out the paragraph and offset from the XIGT word segmentation
    # this is so that I can compare order based on paragraph and offset
    #
    def parse_segmentation(self):
        matches = re.findall(segmentation_regex, self.segmentation)
        self.paragraph = int(matches[0][0])
        self.offset = int(matches[0][1])

    #
    # overriding the greater-than so I can compare based on paragraph and offset
    #
    def __gt__(self, other):
        if self.paragraph > other.paragraph:
            return True
        elif self.offset > other.offset:
            return True
        else:
            return False

    #
    # overriding the less-than so I can compare based on paragraph and offset
    #
    def __lt__(self, other):
        if self.paragraph < other.paragraph:
            return True
        elif self.offset < other.offset:
            return True
        else:
            return False