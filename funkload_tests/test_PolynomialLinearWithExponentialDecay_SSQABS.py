import unittest, time, os, sys
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase

myImportPath = os.path.join(sys.path[0][:sys.path[0].rfind(os.sep)], 'zunzun/LongRunningProcess')
if myImportPath not in sys.path:
    sys.path.append(myImportPath)
    
import DefaultData


data2D = DefaultData.defaultData2D

testPolynomialLinearWithExponentialDecay2D_SSQABS = True
testInterfacePages = True # sets session cookie


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

        
        if testInterfacePages:
            for url in [ '/Equation/2/Polynomial/2nd%20Order%20(Quadratic)/']:
                self.RetrieveOnePage(url, 'Please select an option from the pull-down')

        
        if testPolynomialLinearWithExponentialDecay2D_SSQABS:
            self.PostLongRunningProcess('/FitEquation__1___/2/Polynomial/1st%20Order%20(Linear)%20With%20Exponential%20Decay/',
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
                        ['fittingTarget', 'SSQABS'],
                        ['textDataEditor', data2D]],
                        'Test Polynomial Linear With Exponential Decay 2D (SSQABS)',
                        30,
                        ['Minimum:             -6.740628E+00     -2.816686E+00',
                         'Maximum:              1.045474E+00      9.375602E-01'])
            
            self.post(self.server_url + '/EvaluateAtAPoint/',
                params=[['x', '8.0']],
                description = 'Test Polynomial Linear With Exponential Decay 2D (SSQABS) - Evaluate At A Point')
            self.assertTrue(-1 != str(self.getBody()).find('1.35102769596'), 'Polynomial Linear With Exponential Decay 2D (SSQABS) - Evaluate At A Point')


unittest.main()
