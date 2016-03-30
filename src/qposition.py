from xigt.codecs import xigtxml
from wals import WalsFeature, WalsLanguageCodes
from confusionMatrix import ConfusionMatrix
import glob
import os
import re

def max_value(dic):
    if sum(dic.values())==0:
        return "No question particle"

    max=0
    maxk=""
    for item in dic:
        if dic[item]>max:
            max=dic[item]
            maxk=item

    mult_max=[]
    for item in dic:
        if dic[item]==max:
            mult_max.append(item)
    if len(mult_max)>1:
        return "In either of two positions"
    else:
        return maxk

def clean_word(word):
    word=word.lower()
    dirt=["\"","\'","`","\.","-","*"]

    all_dirt=True
    for char in word:
        if char not in dirt:
            all_dirt=False
    if all_dirt:
        return""

    while word[0] in dirt:
        word=word[1:]

    while word[len(word)-1] in dirt:
        word=word[:(len(word)-1)]

    return word

wals_path = "C:/Users/Kenedy/Documents/CLMS/575/data/WALS-data/"
odin_path = "C:/Users/Kenedy/Documents/CLMS/575/data/xigt-enriched/"

# this loads all the odin/xigt files in the path into a list
odin_corpus = glob.glob(os.path.join(odin_path, "*.xml"))

# this is an annoying required conversion between WALS language ids and ISO language ids
wals_dictionary = WalsLanguageCodes(os.path.join(wals_path, "wals-language"))

# this is a simple list of languages and their gold-value.
wals = WalsFeature(os.path.join(wals_path, "wals-dataset"), "92A")

qc=0
pqc=0
ec=0
feature_dictionary={}
polars=[]
whWords=["who","what","where","when","why","which","whose","whom","wherever","how"]

output=open("output","w")
results=open("results","w")

for i in range(len(odin_corpus)):
    filename = os.path.basename(odin_corpus[i])
    language_code = os.path.splitext(filename)[0]
    try:
        # this is just a check to see if we get an error here.
        # we're going to error out if we can't look up this language/feature in WALS.
        wals_code = wals_dictionary.iso_to_wals[language_code]
        wals_value = wals.feature_dictionary[wals_code]
    except KeyError:  # it wasn't in the dictionary of languages which have reported stats for feature in WALS
        continue
    xc = xigtxml.load(odin_corpus[i], mode='transient')
    hasq=False
    haspq=False
    lang_count=0
    values={"Initial":0,"Second position":0,"Final":0,"In either of two positions":0,"Other position":0}
    examples=[]
    for igt in xc:
        good=True
        try:
            sentence=igt["t"][0].value()
            tw=igt["tw"]
            gw=igt["gw"]
            g=igt["g"]
            good=True
        except:
            ec+=1
            good=False
        #check if the sentence is a question by looking for a question mark
        if good:
            if "?" in sentence:
                hasq=True
                #check if the question is polar by looking for wh words
                hasWh=False
                for item in igt["tw-ps"]:
                    if item.value()=="WP" or item.value() == "WDT" or item.value() == "WP$" or item.value == "WRB":
                        hasWh=True
                for word in tw:
                    if clean_word(word.value()) in whWords:
                        hasWh=True
                for item in g:
                    if clean_word(item.value()) in whWords:
                        hasWh=True
                if not hasWh:
                    lang_count+=1
                    try:
                        new=igt["p"][0].value()+"\n"
                        for thing in igt["gw"]:
                            new+=(thing.value()+" ")
                        new+="\n"
                        new+=sentence+"\n\n"
                        examples.append(new)
                    except:
                        pass
                    haspq=True
                    pos=[]
                    for i in range(len(igt["g"])):
                        morph = igt["g"][i].value()
                        if morph == "Q" or morph == "q" or morph == "QUEST" or morph == "NEGQ" or morph=="QU" or morph=="%" or morph.lower()=="inter" or morph.lower()=="interr":
                            pos.append(i)
                    if pos == []:
                        pass
                    else:
                        for num in pos:
                            if num==0:
                                values["Initial"]+=1
                            if num==1:
                                values["Second position"]+=1
                            if num==len(igt["g"])-1:
                                values["Final"]+=1
                            if num!=0 and num!=1 and num!=len(igt["g"])-1:
                                values["Other position"]+=.1
    if haspq:
        if lang_count >= 5:
            pqc+=1
            feature_dictionary[language_code]=max_value(values)
            if feature_dictionary[language_code]!=wals_value:
                output.write(language_code+": output value is "+feature_dictionary[language_code]+" WALS value is "+wals_value+"\n")
                for ex in examples:
                    output.write(ex)

    if hasq:
        qc+=1

    hasq=False
    haspq=False

    if i%10 ==0:
        print("done with corpus "+str(i))

#find the accuracy
print("found "+str(qc)+" languages with questions")
print(str(pqc)+" of those have polar questions")

possibilities = ["Initial","Second position","Final","In either of two positions","No question particle","Other position"]
confusion_matrix = ConfusionMatrix("Generated and WALS", possibilities)
correct=0

for code in feature_dictionary:
    our_value = feature_dictionary[code]
    try:
        wals_code = wals_dictionary.iso_to_wals[code]
        wals_value = wals.feature_dictionary[wals_code]
        confusion_matrix.addLabel(wals_value, our_value)
    except KeyError:
        print("No matching WALS data for language " + code)

for q in polars:
    output.write(q)
    output.write("\n")

print(confusion_matrix.printMatrix())


output.close()
results.close()

print(ec)