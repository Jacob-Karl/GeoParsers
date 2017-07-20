from lxml import html
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from pyparsing import *
import nltk
import requests
import time
#nltk.download()

web = input("Enter the web adresses seperated by ','.")
pointer = 0
adresses = []
commas = []
contents = []
locations = []
unwantedCharacters = ['\\','~','!','@','#','$','%','^','&','*','(',')','-','_','+','=','[',']','{','}',':',';','<','>',',','.','"','?','/','1','2','3','4','5','6','7','8','9','0']

#Function for finding specified strings in a larger string
def find(thing, page):
    found = False 
    pointer = len(thing)
    i=0
    while pointer < len(page):
        if page[i:pointer] == thing:
            print pointer
            found = True
            return pointer
        pointer = pointer+1
        i = i+1
    return -1

#Function removes characters specified in characterSet from the strings in array
def purify(array, characterSet):
    finalArray = []
    for item in array:
        i=0
        for letter in item:
            for character in characterSet:
                if letter == character:
                    i = i+1
        if i == 0:
            finalArray.append(item)
    return finalArray

#Determine the total number of web addresses by counting the number of commas plus one
while pointer<len(web):
    char = web[pointer: pointer+1]
    if char == ',':
        commas.append(pointer)
    pointer = pointer +1
    
commas.append(len(web))

pointer = 0
i = 0
webs = []

#Scrape the contents of each web adress and append it to contents
while i<len(commas):
    time.sleep(2)
    print web[pointer:commas[i]]
    webs.append(web[pointer:commas[i]] +'.txt')
    page = requests.get(web[pointer:commas[i]])
    data = html.fromstring(page.content)
    soup = BeautifulSoup(page.content, 'html.parser')
    newSoup = UnicodeDammit(soup)
    print newSoup
    contents.append(soup)
    print contents
    #contents_string = BeautifulSoup(str(contents),"lxml")
    #print soup.get_text(' ', strip=True)
    pointer = commas[i]+1
    i = i+1

print webs
i=0
j=0
k=-1
properNouns = []
nounLocations = []
test = []

#loop through contents
while i<len(contents):
    pointer = 0
    found = False
    page = str(contents[i]) #define page as the current character
    if find('<h2>Materials and Methods</h2>', page) > 0:
        pointer = find('<h2>Materials and Methods</h2>', page)#set pointer to the location found
        found = True
        
    if found == False:    
        if find('<h2>Methods</h2>', page) > 0:  
            pointer = find('<h2>Methods</h2>', page)
            found = True
    
    if found == False:
        if find('<h2>Study Site</h2>', page) > 0:
            pointer = find('<h2>Study Site</h2>', page)
            found = True
    print pointer
    text = page[pointer:pointer+10000] #provide a character buffer for finding the location
    text = text.decode('utf-8','ignore')
    tokenedText = nltk.word_tokenize(text) #tokenize using nltk
    print tokenedText
    taggedText = nltk.pos_tag(tokenedText) #tag using nltk
    print taggedText
    for word, tag in taggedText: #find all propper nouns and copy them to properNouns
        if tag == 'NNP':
            properNouns.append(word)
    print properNouns
    while j<len(properNouns): #for each word in properNouns encode to utf-8, and ignore all errors
        temp = properNouns[j]
        temp = temp.encode('utf-8','ignore')
        temp = str(temp)
        properNouns[j] = temp
        j = j+1
    properNouns = purify(properNouns,unwantedCharacters) #purify all properNouns
    print properNouns
    for noun in properNouns:#Fill the nounLocation array with the numerical location in text of all elements from properNouns
        if len(nounLocations) == 0:
            nounLocations.append(find(noun, text))
        else:
            nounLocations.append(find(noun,text)+nounLocations[k])
        k = k+1
    print nounLocations
    print webs[i]
    webs[i] = webs[i].replace("/",".")#reformat the file names to be read by java
    webs[i] = webs[i].replace(":","_")
    #open a file named from webs[i] and write all properNouns and all nounLocation
    file = open(webs[i], 'w')
    for item in properNouns:
        item = item.encode('utf-8','ignore')
        file.write(str(item)+' ')
    file.write('\n')
    for item in nounLocations:
        file.write(str(item)+' ')
    file.close()
    i = i+1

print webs
