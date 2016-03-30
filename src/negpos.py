##############################################################################
#
# ling575x
# language profile project
# Winter Term, 2016, Fei Xia
#
# negpos.py
#
# description:  contains an algorithm for WALS feature 143A: Position of negative
# morphem and verb. Prints a confusion matrix of the results to std output. Also creates
# an output file for IGT from all languages that were incorrectly classified.
##############################################################################

from xigt.codecs import xigtxml
from wals import WalsFeature, WalsLanguageCodes
from confusionMatrix import ConfusionMatrix
import glob
import os
import re

#Searches a Xigt Corpus for negative words and records their position relative to the
#root verb.
def findwords(xc):
    position={"before":0,"after":0}
    number={"single":0,"double":0}
    neglist=[]
    hasneg=False
    for igt in xc:
        negcount=0
        good=True
        try:
            stuff=igt["w-ds"]
        except:
            good=False
        if good:
            good=False
            root=""
            for item in igt["w-ds"]:
                attributes=item.attributes
                if item.value() == "root":
                    root=attributes["dep"]
                if "head" in attributes:
                    if item.value() == "neg" and attributes["head"]==root:
                        negcount+=1
                        hasneg=True
                        neglist.append(igt)
                        neglist.append(igt)
                        neg=attributes["dep"]
                        if int(neg[1:]) < int(root[1:]):
                            position["before"]+=1
                        else:
                            position["after"]+=1
        if negcount==1:
            number["single"]+=1
        if negcount==2:
            number["double"]+=1
        if negcount>2:
            print("YOOOOOOOO"+str(negcount))
    return(hasneg,position,neglist,number)

#Searches a Xigt corpus for negative morphemes attached to a verb and records their position.
def findmorphs(xc):
    position={"before":0,"after":0}
    hasneg=False
    neglist=[]
    number={"single":0,"double":0}
    for igt in xc:
        negcount=0
        good=True
        try:
            stuff=igt["g"]
            stuff=igt["gw-pos"]
            stuff=igt["tw-ps"]
            stuff=igt["a"]
        except:
            good=False
        if good:
            for gloss in igt["g"]:
                #check if neg is in the glosses
                if(gloss.value().lower()) == "neg":
                    neg=gloss.id
                    negcount+=1
                    #check if neg is attached to a verb
                    word=(re.split("\[",gloss.content)[0])
                    for pos in igt["gw-pos"]:
                        if pos.alignment == word:
                            tag=pos.value()
                    if tag=="VERB":
                        info=(igt["gw"][word].value())
                        #find the verb in the word
                        morphs=[]
                        for gloss in igt["g"]:
                            if (re.split("\[",gloss.content)[0])==word:
                                morphs.append(gloss.id)
                        align={}
                        for a in igt["a"]:
                            if a.attributes["target"] in morphs:
                                align[a.attributes["source"]]=a.attributes["target"]
                        verb=""
                        for ps in igt["tw-ps"]:
                            if "alignment" in ps.attributes:
                                if ps.attributes["alignment"] in align:
                                    if ps.value()[:1]=="V":
                                        verb=align[ps.attributes["alignment"]]
                        if verb!="":
                            hasneg=True
                            neglist.append(igt)
                            if int(neg[1:])<int(verb[1:]):
                                position["before"]+=1
                            else:
                                position["after"]+=1
        if negcount==1:
            number["single"]+=1
        if negcount==2:
            number["double"]+=1
    if hasneg:
        print(number)
    return(hasneg,position,neglist,number)

def max_value(dic):
    maxv=0
    max=""
    for thing in dic:
        if dic[thing]>maxv:
            maxv=dic[thing]
            max=thing
    return max

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
wals = WalsFeature(os.path.join(wals_path, "wals-dataset"), "143A")

output=open("output2","w")
negc=0
correct_position=0
incorrect_position=0
feature_dictionary={}

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
    xc = xigtxml.load(odin_corpus[i], mode='full')
    hasneg=False
    position={"VNeg":0,"NegV":0,"[V-Neg]":0,"[Neg-V]":0}
    number={"single":0,"double":0}

    result1=findwords(xc)
    hasword=result1[0]
    wordpos=result1[1]
    neglist=result1[2]
    wordnum=result1[3]
    position["NegV"]=wordpos["before"]#*(524/1059)
    position["VNeg"]=wordpos["after"]#*(171/1059)
    number["single"]+=wordnum["single"]
    number["double"]+=wordnum["double"]

    result2=findmorphs(xc)
    hasmorph=result2[0]
    morphpos=result2[1]
    neglist+=result2[2]
    morphnum=result2[3]
    position["[Neg-V]"]=morphpos["before"]#*(162/1059)
    position["[V-Neg]"]=morphpos["after"]#*(202/1059)
    number["single"]+=morphnum["single"]
    number["double"]+=morphnum["double"]

    hasneg=(hasword or hasmorph)
    if sum(position.values()) >= 1:
        if hasneg:
            if number["double"]>number["single"]:
                feature_dictionary[language_code]="ObligDoubleNeg"
            else:
                print(wals_value)
                print(position)
                feature_dictionary[language_code]=max_value(position)
            if wals_value != feature_dictionary[language_code]:
                output.write(language_code+"\n")
                output.write("WALS: "+wals_value+" Output: "+feature_dictionary[language_code]+"\n")
                output.write(str(position)+"\n")
                for igt in neglist:
                    printIGT(igt,output)


#confusion matrix
print(len(feature_dictionary))
possibilities = ["VNeg","NegV","[V-Neg]","[Neg-V]","ObligDoubleNeg","OptDoubleNeg"]
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

output.close()