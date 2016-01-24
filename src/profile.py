from xigt.codecs import xigtxml
import xigt.ref as ref


xigt_corpus = ["/opt/dropbox/15-16/575x/data/odin2.1/data/by-lang/xigt-enriched/eng.xml"]


xc = xigtxml.load(xigt_corpus[0], mode='full')

for igt in xc:
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
            print("  " + word_token + ": " + pos.text )
    except:
        # move on
        pass





