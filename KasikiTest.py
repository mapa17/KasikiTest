'''
Created on May 7, 2012

@author: Pasieka Manuel , mapa17@posgrado.upv.es
'''

import math
import sys
import operator
import os

def primefactors(n):
    '''lists prime factors, from greatest to smallest'''  
    i = 2
    while i<=math.sqrt(n):
        if n%i==0:
            l = primefactors(n/i)
            l.append(i)
            return l
        i+=1
    return [int(n)]      # n is prime


divTable = {}

#Method from http://www.math.mtu.edu/mathlab/COURSES/holt/dnt/divis2.html
#Returns a list of dividers of the number <n>
def dividers(n):
    
    if( n in divTable ):
        return divTable[n]
    
    d = set() #Dividers
    nR = int( math.sqrt(n) )
    if( (nR*nR) == n ):
        d.add(nR)
    
    #Calculate all dividers up to sqrt(n)
    for i in range(1,nR):
        if( (n%i) == 0):
            d.add(i)
    
    #find all elements k, for which k = n / m
    dt = set()
    for k in d:
        dt.add(int(n/k))
        
    d = d | dt
    
    l = list(d)
    l.sort()
    
    divTable[n] = l
    return l

#Returns a list of positions <pattern> appears in <text>
def patternRep(text, pattern):
    reps = []
    
    pos = str.find(text, pattern, 0)
    while(pos >= 0):
        reps.append(pos)
        pos = str.find(text, pattern, pos+1)
    
    return reps

#Returns a list of distances between the appearers of <pattern> in <text>
def repDistance(text, pattern):
    reps = patternRep(text, pattern)
    dist = []
    nReps = len(reps)
    if(nReps < 2):
        return []
    
    prev = reps[0]
    for idx in range(1,nReps):
        nxt = reps[idx]
        dist.append(nxt - prev)
        prev = nxt
    
    return dist   

def getDistanceForWindow(text, windowLength, debug=False):
    pD = {} #Hash of pattern and their distances
    wl = windowLength
    pattern = text[:wl]
    #text = text[wl:]
    
    if debug : print("Search for [{}] in [{}]".format(pattern, text))
    pD[pattern] = repDistance(text, pattern)
    while(len(text) > wl):
        #Shift pattern and shorten text
        pattern = pattern[1:]
        pattern += text[wl:wl+1]
        text = text[1:]
        
        if pattern not in pD:
            if debug : print("Search for [{}] in [{}]".format(pattern, text))
            pD[pattern] = repDistance(text, pattern)
        else:
            if debug : print("Search for [{}] in [{}] --- Skipp".format(pattern, text))
    
    return pD

#Returns a list of words and their distance in <text> , the word length ranges from <maxWindowLength> to 3
#The elements of the list are tuples with the world length and a list of dictionaries with words and their distances
def buildDistanceTable(text, maxWindowLength):
    dT = []
    
    wl = maxWindowLength
    while(wl >= 3):
        wD = {}
        d = getDistanceForWindow(text, wl)
        #Strip of empty substrings
        for k,v in d.items():
            if len(v) > 0:
                wD[k] = v
        
        dT.append((wl, wD))
        wl-=1
    return dT


#Calculate the dividers of all distances provided in <distanceTable>
#Returns a list of dividers organized by world length, using <distanceTable>
def getDividersForDT(distanceTable, debug=False):
    wDiv = []
    #For each word category (defined by word length only) calculate the dividers of all distances and than create a histogram of them
    for c in distanceTable:
        #c ... is a tuple containing the world length and a dictionary of words and their distances in the text
        wl = c[0]
        dT = c[1]
        div = [] #Dividers for this word length category
        for k, v in dT.items():
            if debug : print("Distances for the word {} are {}".format(k, v))
            for dist in v:
                div.extend( dividers(dist) )
                
        if debug : print("Dividers for words of length {} are {}".format(wl, div))
        wDiv.append((wl,div))
    
    return wDiv

import operator
#Creates a histogram of dividers found
#Returns a list of tuples, containing the word length and the divider with its number of occurrences in the category

#e.g [(6, [(8, 1), (16, 1)]), (5, [(8, 2), (16, 2)]), (4, [(8, 3), (16, 3)]), (3, [(8, 4), (16, 4)])]
# meaning words with length 6, have one 8 divider and one 16 divider
# word of length 4 have the divider 8 occurring thre times and the divider 16 occurring three times as well
def createDividersHistogram(dividerTable, debug=False):
    dH = [] #Divider Histogram
    for c in dividerTable:
        #c ... a tuple containing a world length and all dividers for this length
        wl = c[0]
        divs = c[1]
        udivs = set(divs) #unique dividers
        hdivs = []
        for d in udivs:
            if(d < 4):
                continue #Key length is likely higher than 3
            hdivs.append((d, divs.count(d)))
        
        #Sort on the second tupple argument
        hdivs.sort(key=operator.itemgetter(1), reverse=True)
        
        dH.append( (wl, hdivs) )
        if debug : print("Divider Histogram of word length {} is {}".format(wl, hdivs))
        
    return dH

#Returns a list of distance histograms for patterns of different length
#See description of function createDividersHistogram

#It takes a cipher text and the maximum length of patterns to find repeating in the text
def KasikiTest(text, maxWorldLength):
    mWL = maxWorldLength
    dT = buildDistanceTable(text, mWL)
    diT = getDividersForDT(dT)
    dH = createDividersHistogram(diT)
    return dH

def usage():
    return "{} CipherFile maxPatternLength".format(sys.argv[0])

#Prints out a histogram of Divider occurrence in the text provided
def main():
    if( len(sys.argv) < 3):
        print("Error in Arguments!\nUsage {}".format(usage()))
        sys.exit(1)
    
    cipherFile = str(sys.argv[1])
    os.path.abspath(cipherFile);
    if( os.path.isfile(cipherFile) == False ):
        print("Error! {} does not appear to be a file!".format(cipherFile))
        sys.exit(1)
    mWL = int(sys.argv[2])
    if(mWL <= 0):
        print("Error! {} is not a valid pattern length!".format(mWL))
        sys.exit(1)
    
    cipherText = open(cipherFile,"r").read()
    
    dH = KasikiTest(cipherText, mWL)
    
    print("Distance Histogram for [{}]".format(cipherFile))
    for i in dH:
        print("\n\nwl[{}]\n{}".format(i[0],i[1]))
    
    sys.exit(0)

if __name__ == '__main__':
    main()
