import unittest, time, os, sys
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase



class Simple(FunkLoadTestCase):

    def setUp(self):
        """Setting up test."""
        #self.logd("setUp")

    def _exc_info(self):
        return sys.exc_info()


    def tearDown(self):
        print("Tearing down")
        #self.logd("tearDown.\n")
        fileList = os.listdir(sys.path[0])
        for xmlFile in fileList:
            if -1 != xmlFile.find('xml'):
                os.remove(xmlFile)


    def RetrieveOnePage(self, url, assertString):
        time.sleep(0.5)
        self.get(self.server_url + url, description = 'Loading single GET for the URL ' + url)
        time.sleep(0.5)
        self.assertTrue(assertString in str(self.getBody()), 'Could not load page ' + url)
    
    
    def PostLongRunningProcess(self, inURL, inParams, inDescription, inTimeoutSeconds, inStringListForAssertions, printWebResult = False):
#        time.sleep(0.5)

        self.post(self.server_url + inURL, params=inParams, description = inDescription)
        
        time.sleep(0.5)
        
        if -1 != str(self.getBody()).find('This field is required'):
            self.assertTrue(0, 'Form is missing a required field')

        startTime = time.time()
        time.sleep(0.5)
        self.get(self.server_url + '/StatusAndResults/', description='Getting status for ' + inDescription)
        time.sleep(0.5)
        body = str(self.getBody())
        while (-1 != body.find('REDIRECT')) or (-1 != body.find('REFRESH')):
            if (time.time() - startTime) > inTimeoutSeconds:
                self.assertTrue(0, 'More than ' + str(inTimeoutSeconds) + ' seconds have passed for ' + inDescription + '\n\n' + body)
            time.sleep(3.0)
            self.get(self.server_url + '/StatusAndResults/', description='Getting status for ' + inDescription)
            time.sleep(0.5)
            body = str(self.getBody())
            
            if printWebResult == True:
                print(body)

        for testString in inStringListForAssertions:
            self.assertTrue(-1 != body.find(testString), 'Incorrect ' + inDescription + ': "' + testString + '"')
    

    def test_simple(self):
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
                    postData.append([key, postDict[key]])
        
            if line[:5] == 'path:':
                postURL = line[5:-2]

        self.server_url = self.conf_get('main', 'url')

        # this sets a session cookie
        self.RetrieveOnePage('/CharacterizeData/1/', 'Please select an option from the pull-down')
        
        # now post the file data
        self.PostLongRunningProcess(postURL,
                                    list(postData),
                                    'Test ' + postURL,
                                    240,
                                    ['script'])



unittest.main()
