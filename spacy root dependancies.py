import tkinter
import spacy
import web_crawling_tests
nlp = spacy.load("en_core_web_sm")
#'leading' dependancies:
#prop, agent
#'object of leading' dependancies:
#pobj

#gets every token with a subject dependancy

def get_sub(doc):
    subjlist = []
    for token in doc:
        if "subj" in token.dep_ and token.pos_ != "PRON":
            subjlist.append(token)
            if token.text == "calculus":
                print("we got calculus (:")
        #if there is no subject in the doc returns false so I know there are no facts in the doc
    if len(subjlist) == 0:
        truefalse = False
    else:
        truefalse = True
    return truefalse, subjlist
 
 
#returns every token that is dependant on the root word passed into the function
def rootdeptrue(sent,root):
    rootdeps = []
    for token in sent:
        if token.head == root:
            rootdeps.append(token)
    return rootdeps

#bubble sort for spacy token arrays
def sortspacy(tokarr):
    for f in range(len(tokarr)-1):
        for i in range(len(tokarr)-1):
            if tokarr[i].i > tokarr[i+1].i:
                add = tokarr[i]
                tokarr[i] = tokarr[i+1]
                tokarr[i+1] = add
    return tokarr
 
#advattribute check, gets the ancestor of the first word of the subject/attribute to find the root,
#then iterates through the children of the root to find complex dependancies
#then it will recur to find the children of the children of those dependancies until there are no more children with a complex dependancy.
def getroot(text):
    ancestors = []
    for token in text:
        while token.is_ancestor == False:
            token = token.ancestors
            ancestors.append(token)
    finalancestors = []
    for tok in ancestors:
        if tok not in finalancestors:
            finalancestors.append(tok)
    return ancestors
 
#takes a single token input, gets the children of that token input and iterates through those children checking if the children have a
#dependancy of either a 'leading' dependancy or an 'object' dependancy, if it is a 'leading' dependancy it just appends the recursion of the subroutine, passing in the child token
#if it is an object dependancy it appends the child token and then appends the recursion of the subroutine, passing in the child token

def complexitycheck(root):
    #variable to return
    complexpart = []
    #gets an array of children in the tree
    children = ([child for child in root.children])
    #iterates through the array of children
    for child in children:
        #checks if an attribute of the child object is == a 'leading' dependancy
        if child.dep_ in ["agent", "prep","attr", "acomp", "nmod", "dobj","oprd","ccomp"]:
            #gets the recursion of the array
            complexpartadd = (complexitycheck(child))
            #iterates through the recursion of the array and appends each item to the main array
            for item in complexpartadd:
                complexpart.append(item)
        #does the exact same thing as the previous 'if' just also appends the current child,
        # this if being true is the only way to appends items to the main array
        elif child.dep_ in ["pobj"]:
            complexpart.append(child)
            complexpartadd = complexitycheck(child)
            if len(complexpartadd) >= 1:
                for item in complexpartadd:
                    complexpart.append(complexpartadd)
 
    return complexpart
 
#checks for compounds for the subject by iterating through the doc to find compounds dependancies that are dependant on the subject
#it then uses recursion to iterate through the doc to find compounds that have compound dependancies on the compound of the subject,
#this recursion repeats until it has found every compound related to the subject in the chain and then unwinds and returns the 'full subject'
 
def checkcomp(subj,doc):
    subjarr = []
    iter = False
    for token in doc:
        if type(subj) == list:
            if iter == False:
                for subject in subj:
                    subjarr.append(subject)
                iter = True
            for subject in subj:
                try:
                    if token.head == subject and token.dep_ == "compound":
                        if token.i > subject.i:
                            token = checkcomp(token,doc)
                            if type(token) == list:
                                for tok in token:
                                    subjarr.insert(subject.i+1,tok)
                            else:
                                subjarr.insert(subject.i+1,token)
                        else:
                            token = checkcomp (token,doc)
                            if type(token) == list:
                                for tok in token:
                                    subjarr.insert(subject.i,tok)
                            else:
                                subjarr.insert(subject.i,token)
                except AttributeError:
                    for i in range(30):
                        print("error token =", token)
        else:
            if iter == False:
                subjarr.append(subj)
                iter = True
            if token.head == subj and token.dep_ in "compound":
                if token.i > subj.i:
                    token = checkcomp(token,doc)
                    if type(token) == list:
                        for tok in token:
                            subjarr.insert((subj.i)+1,tok)
                    else:
                        subjarr.insert((subj.i)+1,token)
                else:
                    token = checkcomp(token,doc)
                    if type(token) == list:
                        for tok in token:
                            subjarr.insert(subj.i,tok)
                    else:
                        subjarr.insert(subj.i,token)
    return sortspacy(subjarr)
   
 
def finddef(subjects,doc):
    finalfacts = []
    #iterates through the subjects found in the sentance/text
    for subject in subjects:
        #defines that the root word of the sentence is whatever the subject is dependant on
        root = subject.head
        #rootdeptrue returns the tokens that are dependant on the root word the same as [child for child in root.children]
        defs = [child for child in root.children]
        #creates the array for the fact
        finalfact = []
        attr = []
        subj = []
        subj.append(subject)
        #iterates through the tokens found by rootdeptrue
        for token in defs:
            #adds negatives that are dependant on the root to the array
            if token.dep_ in ["attr", "acomp", "nmod", "dobj","oprd","ccomp"]:
                #creates an array of the words that are dependant on the root (which the subject is also dependant on) that are also attributes or similar describing words
                #prep = advpartcheck(token,doc)
                #appends the 'fact' or subject - attribute relationship to the list of facts contained in the doc
                #attr.append(token)
                #if prep != token:
                attr.append(token)
                #takes the single token attribute and runs a complexity check to find all the linking attributes
                #to the main attribute
                print("root = ", root.text)
                rootchildren = [child for child in root.children]
                print("the root children = ", rootchildren)
                for child in rootchildren:
                    if child.dep_ in ["attr", "acomp", "nmod", "dobj","oprd","ccomp", "agent", "prep", "pobj"]:
                        advattr = complexitycheck(child)
                        for token in advattr:
                            attr.append(token)
            elif token.dep_ == "neg":
                attr.append(token)
        print("attribute = ", attr)
        if len(attr) == 1 and attr[0].dep_ == "neg":
            attr = False
        elif len(attr) < 1:
            attr = False
        print("subj = ", subj[0])
        if type(subj) == list:
            if len(subj) > 1:
                print("subject length error")
            else:
                subj = subj[0]
        finsubj = complexitycheck(subj)
        finsubj.append(subj)
        print("subj1 = ", subj)
        finalsubj = checkcomp(finsubj,doc)
        print("subj2 = ", subj)
        if attr != False:
            attr = checkcomp(attr,doc)
        finalfact.append(finalsubj)
        finalfact.append(attr)
        #only appends a fact if there is a definition. error due to there being a negative without a definition,
        # however if there is a negative there should be a definition so its more likely to be the code's inability to process
        # complex facts#
        try:
            if finalfact[1] != False:
                finalfacts.append(finalfact)
            else:
                finalfacts.append(False)
        except TypeError:
            finalfacts.append(finalfact)
 
        #for i in range(len(finalfacts)):
        #    if finalfacts[i] != False:
        #        finalfacts[i] = checkcompinfact(finalfacts[i],doc)
 
    return finalfacts
 
        #get the head of the subject, the dependancy of the head of the subject
        #if the definition is dependant on a prepositional modifier the object of preposition is actually the definition

 

 
with open(r"D:\Spacy files\samplefacts.txt", "r") as f:
    text = f.read()
doc = nlp(text)
sent = doc
subjects = get_sub(sent)
print(subjects[1])
finalfacts = finddef(subjects[1],sent)
 
 
x = 0
for fact in finalfacts:
    print(x, fact)
    x +=1


