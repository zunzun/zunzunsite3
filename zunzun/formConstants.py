



import inspect
import pyeq3


udfTopText = '''
# Enter the text of your function here. Comments begin
# with a "#". Lines with no text are ignored.
'''

udfBottomText = '''
# Note that most spreadsheets use log base 10 for
# a LOG() function, here log() is the natural log.
# The site uses power() or **, not the caret '^'.
# The site uses fabs() not abs() for absolute value.
# The web site will automatically decode the
# parameter names (coefficient names) that you use.
# See the examples below for ideas on function entry.
'''

initialUserDefinedFunctionText2D = udfTopText + '# Use an upper case "X" to represent your data.' + udfBottomText

initialUserDefinedFunctionText3D = udfTopText + '# Use upper case "X" and "Y" to represent your data.' + udfBottomText

initialDataEntryText = '''
This data is provided as an example, cut and paste
as needed to model your data. All lines of text
that do not begin with a number are ignored.

'''

extendedEquationTypeChoices = [['STANDARD', 'Standard equation types'],
                               ['RECIPROCAL', 'Reciprocal extended types'],
                               ['INVERSE', 'Inverse extended types'],
                               ['LINEAR_GROWTH', 'Linear Growth extended types'],
                               ['LINEAR_DECAY', 'Linear Decay extended types'],
                               ['EXPONENTIAL_GROWTH', 'Exponential Growth extended types'],
                               ['EXPONENTIAL_DECAY', 'Exponential Decay extended types']]

graphScaleChoices = [["0.010", "Autoscale +/- 1%"],
                     ["0.025", "Autoscale +/- 2.5%"],
                     ["0.050", "Autoscale +/- 5%"],
                     ["0.100", "Autoscale +/- 10%"],
                     ["0.250", "Autoscale +/- 25%"],
                     ["0.500", "Autoscale +/- 50%"],
                     ["1.000", "Autoscale +/- 100%"],
                     ["1.500", "Autoscale +/- 150%"],
                     ["2.000", "Autoscale +/- 200%"],
                     ["99.00", "Manual Scale"]]

onOffChoices = [['ON', 'On'],
                ['OFF', 'Off']]

logLinChoices = [['LIN', 'Linear Scaling'],
                 ['LOG', 'Logarithmic Scaling']]

weightedFittingChoices = [['OFF', 'Standard Unweighted Fitting: no weights required'],
                          ['ON',  'Weighted Fitting: each data point requires a weight']]

scientificNotationChoices = [['ON', 'On'],
                             ['OFF', 'Off'],
                             ['AUTO', 'Auto']]

dataPointSize3D_Choices = [['1.0', 'Tiny'], # 1x1
                           ['9.0', 'Small'], # 3x3
                           ['25.0', 'Medium'], # 5x5
                           ['49.0', 'Large'], # 7x7
                           ['81.0', 'Extra Large'], # 9x9
                           ['0.0', 'Auto']]

commaConversionChoices = [['S','Convert commas to spaces (1,2,0,3 yields 1 2 0 3)'],
                          ['D','Use comma as decimal separator (1,203 = 1.203)'],
                          ['I','Remove commas from text (1,2,0,3 yields 1203)']]

graphSizeOptions = [["320x240", "320 x 240 (fastest)"],
                    ["500x400", "500 x 400"],
                    ["640x480", "640 x 480"],
                    ["700x500", "700 x 500"],
                    ["800x600", "800 x 600"],
                    ["900x700", "900 x 700"],
                    ["1024x768", "1024 x 768"],
                    ["1280x1024", "1280 x 1024"],
                    ["1600x1200", "1600 x 1200 (slowest)"],
                    ["2400x400", "wide ratio 2400 x 400"]]

animationSizeOptions = [["320x240", "320 x 240 (smallest)"],
                        ["500x400", "500 x 400"],
                        ["640x480", "640 x 480"],
                        ["700x500", "700 x 500"],
                        ["800x600", "800 x 600"],
                        ["900x700", "900 x 700 (largest)"],
                        ["0x0", "No Animations"]]

azimuthChoices = [["0", "0"],
                  ["15", "15"],
                  ["30", "30"],
                  ["45", "45"],
                  ["60", "60"],
                  ["75", "75"],
                  ["90", "90"],
                  ["105", "105"],
                  ["120", "120"],
                  ["135", "135"],
                  ["150", "150"],
                  ["165", "165"],
                  ["170", "170"],
                  ["180", "180"],
                  ["195", "195"],
                  ["210", "210"],
                  ["225", "225"],
                  ["240", "240"],
                  ["255", "255"],
                  ["270", "270"],
                  ["285", "285"],
                  ["300", "300"],
                  ["315", "315"],
                  ["330", "330"],
                  ["345", "345"]]

altimuthChoices = [["0", "0"],
                   ["5", "5"],
                   ["10", "10"],
                   ["15", "15"],
                   ["20", "20"],
                   ["25", "25"],
                   ["30", "30"],
                   ["35", "35"],
                   ["40", "40"],
                   ["45", "45"],
                   ["50", "50"],
                   ["55", "55"],
                   ["60", "60"],
                   ["65", "65"],
                   ["70", "70"],
                   ["75", "75"],
                   ["80", "80"],
                   ["85", "85"],
                   ["90", "90"]]

opacityChoices = [['0', '0 percent'],
                  ['10', '10 percent'],
                  ['20', '20 percent'],
                  ['30', '30 percent'],
                  ['40', '40 percent'],
                  ['50', '50 percent'],
                  ['60', '60 percent'],
                  ['70', '70 percent'],
                  ['80', '80 percent'],
                  ['90', '90 percent'],
                  ['100','100 percent']]

# want this specific order
targetList = ['SSQABS', 'ODR', 'SSQREL', 'ABSABS', 'ABSREL', 'PEAKABS', 'PEAKREL', 'AIC', 'BIC']
fittingTargetChoices = []
for target in targetList:
    fittingTargetChoices.append([target, 'Lowest ' + pyeq3.IModel.IModel.fittingTargetDictionary[target]])


equationCategoryNameChoices2D = []
equationCategoryNameChoicesDefaultValues2D = []
for submodule in inspect.getmembers(pyeq3.Models_2D):
    if True == inspect.ismodule(submodule[1]):
        if submodule[0] == 'Spline':
            continue
        if submodule[0] == 'UserDefinedFunction':
            continue
        equationCategoryNameChoices2D.append([submodule[0], submodule[0].replace('Polyfunctional', 'Polyfunctional (Unweighted SSQ only)')])
        if submodule[0] != 'Rational':
            equationCategoryNameChoicesDefaultValues2D.append(submodule[0])
equationCategoryNameChoices2D.sort()

equationCategoryNameChoices3D = []
equationCategoryNameChoicesDefaultValues3D = []
for submodule in inspect.getmembers(pyeq3.Models_3D):
    if True == inspect.ismodule(submodule[1]):
        if submodule[0] == 'Spline':
            continue
        if submodule[0] == 'UserDefinedFunction':
            continue
        equationCategoryNameChoices3D.append([submodule[0], submodule[0].replace('Polyfunctional', 'Polyfunctional (Unweighted SSQ only)').replace('RomanSurfaces', 'Roman Surfaces')])
        equationCategoryNameChoicesDefaultValues3D.append(submodule[0])
equationCategoryNameChoices3D.sort()


polynomialOrder2DChoices = [['0', '0'],
                            ['1', '1'],
                            ['2', '2'],
                            ['3', '3'],
                            ['4', '4'],
                            ['5', '5'],
                            ['6', '6'],
                            ['7', '7'],
                            ['8', '8']]

polynomialOrder3DChoices = [['0', '0'],
                            ['1', '1'],
                            ['2', '2'],
                            ['3', '3'],
                            ['4', '4']]

smoothnessControl2DChoices = [['1', '1'],
                              ['2', '2'],
                              ['3', '3'],
                              ['4', '4'],
                              ['5', '5'],
                              ['6', '6'],
                              ['7', '7'],
                              ['8', '8'],
                              ['9', '9'],
                              ['10', '10'],
                              ['11', '11'],
                              ['12', '12']]

smoothnessControl3DChoices = [['1', '1'],
                              ['2', '2'],
                              ['3', '3'],
                              ['4', '4'],
                              ['5', '5'],
                              ['6', '6'],
                              ['7', '7'],
                              ['8', '8'],
                              ['9', '9'],
                              ['10', '10'],
                              ['11', '11'],
                              ['12', '12'],
                              ['13', '13'],
                              ['14', '14'],
                              ['15', '15'],
                              ['16', '16'],
                              ['17', '17'],
                              ['18', '18'],
                              ['19', '19'],
                              ['20', '20'],
                              ['21', '21'],
                              ['22', '22'],
                              ['23', '23'],
                              ['24', '24'],
                              ['25', '25']]

splineOrderChoices = [['1','1: Linear'],
                      ['2','2: Quadratic'],
                      ['3','3: Cubic'],
                      ['4','4: Quartic']]

statisticalDistributionsSortByChoices = [['NegLogLikelihood', 'Negative Log Likelihood'],
                                        ['AIC', 'Akaike Information Criterion (AIC)'],
                                        ['AICc_BA', 'AIC corrected (AICc) - Burnham and Anderson']]

