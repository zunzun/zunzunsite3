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

testInterfacePages = 1 # sets session cookie
testCharacterizers = True
testStatisticalDistributions = True
testPolynomialQuadratic2D_SSQABS = True
testPolynomialQuadratic2D_SSQREL = True
testSpline2D = True
testUserDefinedFunction2D = True
testFunctionFinder2D = True
testPolynomialLinearWithExponentialDecay2D_SSQABS = True


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
            for url in ['/CharacterizeData/1/',
                         '/CharacterizeData/2/',
                         '/CharacterizeData/3/',
                         '/StatisticalDistributions/1/',
                         '/Equation/2/Exponential/Hoerl/',
                         '/Equation/2/Polynomial/2nd%20Order%20(Quadratic)/',
                         '/Equation/2/Spline/Spline/',
                         '/Equation/2/UserDefinedFunction/UserDefinedFunction/',
                         '/FunctionFinder__1___/2/',
                         '/Equation/2/Polynomial/1st%20Order%20(Linear)%20With%20Exponential%20Decay/'
                         ]:
                self.RetrieveOnePage(url, 'Please select an option from the pull-down')

        
        if testCharacterizers:
            self.PostLongRunningProcess( '/CharacterizeData/1/',
                                         [['commaConversion', 'I'],
                                          ['graphSize', '320x240'],
                                          ['animationSize', '0x0'],
                                          ['scientificNotationX', 'AUTO'],
                                          ['dataNameX', 'X Data'],
                                          ['graphScaleRadioButtonX', '0.050'],
                                          ['logLinX', 'LIN'],
                                          ['textDataEditor', data1D]],
                                         'Test Characterizer 1D',
                                         240,
                                         ['Minimum:              5.084392E+00',
                                          'Maximum:              1.184693E+01',
                                          'Mean:                 7.582947E+00',
                                          'Std. Error of Mean:   1.165556E-01',
                                          'Median:               7.332564E+00',
                                          'Variance:             2.024195E+00',
                                          'Standard Deviation:   1.422742E+00',
                                          'Skew:                 5.742671E-01',
                                          'Kurtosis:            -1.943474E-01'])

        
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
 
            self.PostLongRunningProcess('/CharacterizeData/3/',
                [['commaConversion', 'I'],
                        ['rotationAnglesAzimuth', '165'],
                        ['rotationAnglesAltimuth', '20'],
                        ['graphSize', '320x240'],
                        ['animationSize', '0x0'],
                        ['scientificNotationX', 'AUTO'],
                        ['scientificNotationY', 'AUTO'],
                        ['scientificNotationZ', 'AUTO'],
                        ['dataNameX', 'X Data'],
                        ['dataNameY', 'Y Data'],
                        ['dataNameZ', 'Z Data'],
                        ['graphScaleRadioButtonX', '0.050'],
                        ['graphScaleRadioButtonY', '0.050'],
                        ['graphScaleRadioButtonZ', '0.050'],
                        ['logLinX', 'LIN'],
                        ['logLinY', 'LIN'],
                        ['logLinZ', 'LIN'],
                        ['textDataEditor', data3D]],
                'Test Characterizer 3D',
                240,
                ['Minimum:              6.070000E-01      1.984000E+00      3.130000E-01',
                                  'Maximum:              3.017000E+00      3.153000E+00      2.753000E+00',
                                  'Mean:                 1.971778E+00      2.712815E+00      1.640593E+00',
                                  'Std. Error of Mean:   1.268530E-01      6.327280E-02      1.579631E-01',
                                  'Median:               1.969000E+00      2.721000E+00      1.758000E+00',
                                  'Variance:             4.183838E-01      1.040896E-01      6.487610E-01',
                                  'Standard Deviation:   6.468259E-01      3.226292E-01      8.054570E-01',
                                  'Skew:                -2.371903E-01     -4.974109E-01     -2.651424E-01',
                                  'Kurtosis:            -6.569929E-01     -6.268616E-01     -1.233354E+00'])
        
        if testPolynomialQuadratic2D_SSQABS:
            self.PostLongRunningProcess('/FitEquation__1___/2/Polynomial/2nd%20Order%20(Quadratic)/',
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
                                        'Test Polynomial Quadratic 2D (SSQABS)',
                                        240,
                                        [' Minimum:             -5.824100E-02     -5.610455E-02',
                                         ' Maximum:              7.692989E-02      1.154094E-02'])

       
        if testPolynomialQuadratic2D_SSQREL:
            self.PostLongRunningProcess('/FitEquation__1___/2/Polynomial/2nd%20Order%20(Quadratic)/',
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
                        ['fittingTarget', 'SSQREL'],
                        ['textDataEditor', data2D]],
                                        'Test Polynomial Quadratic 2D (SSQREL)',
                                        240,
                                        ['Minimum:             -7.338700E-02     -1.546943E-02',
                                         'Maximum:              1.122424E-01      1.579988E-02'])
            self.post(self.server_url + '/EvaluateAtAPoint/',
                params=[['x', '8.0']],
                description = 'Test Polynomial Quadratic 2D (SSQREL) - Evaluate At A Point')
            self.assertTrue(-1 != str(self.getBody()).find('3.9510208'), 'Polynomial Quadratic 2D (SSQREL) - Evaluate At A Point')

        if testSpline2D:
            self.PostLongRunningProcess( '/FitEquation__1___/2/Spline/Spline/',
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
                        ['splineSmoothness', '1.0'],
                        ['splineOrderX', '3'],
                        ['textDataEditor', data2D]],
                                         'Test Spline 2D',
                                         240,
                                         ['Minimum:             -6.367555E-02     -9.008992E-03',
                                          'Maximum:              5.762379E-02      1.853725E-02'])

            self.post(self.server_url + '/EvaluateAtAPoint/',
                params=[['x', '8.0']],
                description = 'Test Spline 2D - Evaluate At A Point')
            self.assertTrue(-1 != str(self.getBody()).find('4.02361487093'), 'Spline 2D - Evaluate At A Point')


        if testUserDefinedFunction2D:
            self.PostLongRunningProcess('/FitEquation__1___/2/UserDefinedFunction/UserDefinedFunction/',
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
                        ['udfEditor', 'Scale * X + offset'],
                        ['textDataEditor', data2D]],
                                        'Test User Defined Function 2D (SSQABS)',
                                        240,
                                        ['Minimum:             -2.179575E-01     -5.796742E-01',
                                         'Maximum:              1.845448E-01      8.631655E-02'])

            self.post(self.server_url + '/EvaluateAtAPoint/',
                params=[['x', '8.0']],
                description = 'Test User Defined Function 2D (SSQABS) - Evaluate At A Point')
            self.assertTrue(-1 != str(self.getBody()).find('4.1924427'), 'User Defined Function 2D (SSQABS) - Evaluate At A Point')

        if testFunctionFinder2D:
            self.PostLongRunningProcess('/FunctionFinder__1___/2/',
                                        [['commaConversion', 'I'],
                        ['dataNameX', 'X Data'],
                        ['dataNameY', 'Y Data'],
                        ['smoothnessControl2D', '2'],
                        ['equationFamilyInclusion', 'BioScience'],
                        ['extendedEquationTypes', 'STANDARD'],
                        ['fittingTarget', 'SSQABS'],
                        ['textDataEditor', data2D]],
                                        'Test Function Finder 2D',
                                        240,
                                        ['SSQABS: 0.906322030501',
                                         'RMSE: 0.287041655276'])

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
                        240,
                        ['Minimum:             -6.740628E+00     -2.816686E+00',
                         'Maximum:              1.045474E+00      9.375602E-01'])
            
            self.post(self.server_url + '/EvaluateAtAPoint/',
                params=[['x', '8.0']],
                description = 'Test Polynomial Linear With Exponential Decay 2D (SSQABS) - Evaluate At A Point')
            self.assertTrue(-1 != str(self.getBody()).find('1.351027'), 'Polynomial Linear With Exponential Decay 2D (SSQABS) - Evaluate At A Point')

        if testStatisticalDistributions:
            self.PostLongRunningProcess('/StatisticalDistributions/1/',
                                        [['commaConversion', 'I'],
                        ['graphSize', '320x240'],
                        ['animationSize', '0x0'],
                        ['scientificNotationX', 'AUTO'],
                        ['dataNameX', 'X Data'],
                        ['graphScaleRadioButtonX', '0.050'],
                        ['logLinX', 'LIN'],
                        ['statisticalDistributionsSortBy', 'AIC'],
                        ['textDataEditor', data1D]],
            'Test Statistical Distributions',
            20 * 240,
            ['Top 79 Statistical Distributions'])



unittest.main()
