##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# plural.py
#
#
# description:  contains an algorithm for WALS feature 33A: Coding of Nominal
# plurality. Prints a confusion matrix of the results to std output. Also creates
# an output file for IGT from all languages that were incorrectly classified.
##############################################################################
from xigt.codecs import xigtxml
from wals import WalsFeature, WalsLanguageCodes
from confusionMatrix import ConfusionMatrix
import glob
import os
import re

def find_root(igt,word):
    alignments=igt["a"]

    for a in alignments:
        target=(a.attributes["target"])
        thing = igt["g"][target]
        if re.split("\[",thing.content)[0]==word:
            return thing.id
    return "none"

def printIGT(igt,file):
    try:
        for line in igt["n"]:
            output.write(line.value())
            output.write("\n")
        output.write("\n")
    except:
        output.write("No N line \n")

wals_path = "C:/Users/Kenedy/Documents/CLMS/575/data/WALS-data/"
odin_path = "C:/Users/Kenedy/Documents/CLMS/575/data/xigt-enriched/"

# this loads all the odin/xigt files in the path into a list
odin_corpus = glob.glob(os.path.join(odin_path, "*.xml"))

# this is an annoying required conversion between WALS language ids and ISO language ids
wals_dictionary = WalsLanguageCodes(os.path.join(wals_path, "wals-language"))

# this is a simple list of languages and their gold-value.
wals = WalsFeature(os.path.join(wals_path, "wals-dataset"), "33A")


output=open("output","w")
results=open("results","w")
gloss_file=open("standard_glosses.txt")
baseline_guess="Plural suffix"
baseline_correct=0
affixes=["PL"]
feature_dictionary={}
lang_count=0

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
    prefix_count=0
    suffix_count=0
    affix_count=0
    no_affix_count=0
    word_count=0
    sentence_count=0
    hasmarker=False
    igt_list=[]
    for igt in xc:
        try:
            gloss=igt["g"]
            alignments=igt["a"]
            glosspos=igt["gw-pos"]
        except:
            continue
        sentence_count+=1
        for g in gloss:
            #check if the gloss is in the list of plural markers
            if g.value() in affixes:
                igt_list.append(igt)
                hasmarker=True
                affix=g.id
                #find the root morpheme of the word
                word=(re.split("\[",g.content)[0])
                root="none"
                for g2 in gloss:
                    if re.split("\[",g2.content)[0]==word:
                        #test if this gloss is lower case alphabetic
                        if g2.value().isalpha() and g2.value().lower()==g2.value():
                            root=g2.id
                pos=(glosspos['alignment'==word].value())
                if root!="none" and pos=="NOUN":
                    affix_count+=1
                    #check if its a suffix or prefix
                    if int(affix[1:])<int(root[1:]):
                        prefix_count+=1
                    else:
                        suffix_count+=1
                else:
                    if word==affix:
                        word_count+=1
    count = affix_count+no_affix_count
    if sentence_count>0 and count >=10:
        lang_count+=1
        if affix_count==0 and word_count==0:
            feature_dictionary[language_code]="No plural"
        else:
            if word_count > affix_count:
                feature_dictionary[language_code]="Plural word"
            else:
                ratio=suffix_count/affix_count
                if ratio>.80:
                    feature_dictionary[language_code]="Plural suffix"
                if ratio>.60 and ratio <=.80:
                    feature_dictionary[language_code]="Plural suffix"
                if ratio>.40 and ratio <=.60:
                    feature_dictionary[language_code]="Mixed morphological plural"
                if ratio>.20 and ratio <=.40:
                    feature_dictionary[language_code]="Plural prefix"
                if ratio<=.20:
                    feature_dictionary[language_code]="Plural prefix"
        if wals_value==baseline_guess:
            baseline_correct+=1
        if feature_dictionary[language_code]!=wals_value:
            output.write(language_code+"\n")
            output.write("Our value "+feature_dictionary[language_code]+" WALS "+wals_value+"\n")
            for igt in igt_list:
                printIGT(igt,output)
    print(prefix_count,suffix_count,affix_count,wals_value)

print(str(lang_count),"languages classified")
#find the accuracy

possibilities = ["Plural suffix","Plural prefix","Plural word","Mixed morphological plural","Plural clitic","No plural"]
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

print(confusion_matrix.printMatrix())

print("baseline: "+str(baseline_correct/lang_count))
output.close()
results.close()
