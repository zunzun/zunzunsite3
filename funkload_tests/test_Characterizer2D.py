import unittest, time, os, sys
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase

myImportPath = os.path.join(sys.path[0][:sys.path[0].rfind(os.sep)], 'zunzun/LongRunningProcess')
if myImportPath not in sys.path:
    sys.path.append(myImportPath)
    
import DefaultData


data1D = DefaultData.defaultData1D
data2D = DefaultData.defaultData2D
data3D = DefaultData.defaultData3D

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
        self.server_url = self.conf_get('main', 'url')

        # interface page sets cookie
        self.RetrieveOnePage('//CharacterizeData/2/', 'Please select an option from the pull-down')
        
        self.PostLongRunningProcess('/CharacterizeData/2/',
                               [['commaConversion', 'I'],
                ['graphSize', '320x240'],
                ['animationSize', '0x0'],
                ['scientificNotationX', 'AUTO'],
                 ['scientificNotationY', 'AUTO'],
                 ['dataNameX', 'X Data'],
                 ['dataNameY', 'Y Data'],
                 ['graphScaleRadioButtonX', '0.050'],
                 ['graphScaleRadioButtonY', '0.050'],
                 ['logLinX', 'LIN'],
                 ['logLinY', 'LIN'],
                 ['textDataEditor', data2D]],
                'Test Characterizer 2D',
                240,
            ['Minimum:              5.357000E+00      3.760000E-01',
                 'Maximum:              9.861000E+00      7.104000E+00',
                 'Mean:                 6.998455E+00      2.663636E+00',
                 'Std. Error of Mean:   4.909206E-01      7.507210E-01',
                 'Median:               6.697000E+00      2.054000E+00 ',
                 'Variance:             2.410031E+00      5.635820E+00',
                 'Standard Deviation:   1.552427E+00      2.373988E+00',
                 'Skew:                 8.763577E-01      9.976853E-01',
                 'Kurtosis:            -6.964188E-01     -5.553957E-01'])

unittest.main()
