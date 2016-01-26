from xigt.codecs import xigtxml
import xigt.ref as ref
import re
import operator

xigt_corpus = ["/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/eng.xml"]


# initialize initial word order counts for SVO
#SVO_order_counts = {"SOV": 0, "SVO": 0, "VSO": 0, "VOS": 0, "OVS": 0, "OSV": 0}
SVO_order_probabilities = {"SOV": 0.0, "SVO": 0.0, "VSO": 0.0, "VOS": 0.0, "OVS": 0.0, "OSV": 0.0}
instance_count = 0




class WordPos:
    def __init__(self, token, grammatical_function, segmentation):
        self.segmentation = segmentation
        self.grammatical_function = grammatical_function
        self.token = token
        self.paragraph = None
        self.offset = None
        self.segmentation_regex = '^[a-z]+([1-9]+)\[([0-9]+):([0-9]+)\]'
        self.parse_segmentation()

    def parse_segmentation(self):
        p = re.compile(self.segmentation_regex)
        matches = re.findall(p, self.segmentation)
        self.paragraph = int(matches[0][0])
        self.offset = int(matches[0][1])

    def __gt__(self, other):
        if self.paragraph > other.paragraph:
            return True
        elif self.offset > other.offset:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.paragraph < other.paragraph:
            return True
        elif self.offset < other.offset:
            return True
        else:
            return False


def list_to_word_order(list):
    return list[0].grammatical_function+list[1].grammatical_function+list[2].grammatical_function


def estimate_word_order_for_instance(igt, dparse):
    global instance_count
    function_list = []
    words = igt["w"]
    for pos in dparse:
        word = words[pos.attributes["dep"]]
        segmentation = word.segmentation
        word_token = ref.resolve(igt, segmentation)
        if word_token == "meokeotta":
            oi = 1
        if pos.text == "nsubj":
            function_list.append(WordPos(word_token, "S", segmentation))
        elif pos.text == "root":
            function_list.append(WordPos(word_token, "V", segmentation))
        elif pos.text == "dobj":
            function_list.append(WordPos(word_token, "O", segmentation))

    if len(function_list) == 3:
        sorted_list = sorted(function_list)
        instance_count += 1
        word_order = list_to_word_order(sorted_list)
        SVO_order_probabilities[word_order] += 1.0
        print("WORD-ORDER: " + word_order)


def estimate_word_order_for_each_instance(corpus):
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
                estimate_word_order_for_instance(igt, dparse)


        except:
            # move on
            pass


def print_order_estimates():
    sorted_probs = sorted(SVO_order_probabilities, key=SVO_order_probabilities.get, reverse=True)
    for prob in sorted_probs:
        print(prob + ": " + str(SVO_order_probabilities[prob]/float(instance_count)))

# begin script here
for language in xigt_corpus:
    xc = xigtxml.load(language, mode='full')
    estimate_word_order_for_each_instance(xc)
    print_order_estimates()
