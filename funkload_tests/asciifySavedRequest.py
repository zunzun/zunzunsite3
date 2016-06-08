#! /usr/bin/python
import os, sys


if len(sys.argv)<2:
    print("No file name given, using 'test.req' as file name")
    fileName = 'test.req'
else:
    fileName = sys.argv[1]
    
requestFileLines = open(fileName, 'r').readlines()

# get the POST data
for line in requestFileLines:
    if line[:17] == 'POST:<QueryDict: ':
        postText = line[17:-3].replace("u'", "'")
        postDict =  eval(postText)
        postData = []
        for key in list(postDict.keys()):
            print(key, ' : ', str(postDict[key]).replace('\\r\\n', '\n').replace('\\t', '\t'))
            print()
            print()
