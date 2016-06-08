import os, sys, inspect
import settings
from django.template.loader import render_to_string

from . import ReportsAndGraphs
from . import StatusMonitoredLongRunningProcessPage

import zunzun.forms
import zunzun.formConstants

import numpy

import pyeq3



class FittingBaseClass(StatusMonitoredLongRunningProcessPage.StatusMonitoredLongRunningProcessPage):

    extraExampleDataTextForWeightedFitting = '''Weighted fitting requires an additional number to
be used as a weight when fitting. The site does
not calculate any weights, which are used as:
error = weight * (predicted - actual)
You must provide any weights you wish to use.
'''

    rank = None

            

    def CheckDataForZeroAndPositiveAndNegative(self):
        # check for zero
        if self.boundForm.equation.independentData1CannotContainZeroFlag and self.boundForm.equation.dataCache.independentData1ContainsZeroFlag:
            return 'This equation requires that "' + self.boundForm.cleaned_data['dataNameX'] + '" contain no zero values, but it contains at least one zero value.'
        if self.boundForm.equation.independentData2CannotContainZeroFlag and self.boundForm.equation.dataCache.independentData2ContainsZeroFlag:
            return 'This equation requires that "' + self.boundForm.cleaned_data['dataNameY'] + '" contain no zero values, but it contains at least one zero value.'
        
        # check for positive
        if self.boundForm.equation.independentData1CannotContainPositiveFlag and self.boundForm.equation.dataCache.independentData1ContainsPositiveFlag:
            return 'This equation requires that "' + self.boundForm.cleaned_data['dataNameX'] + '" contain no positive values, but it contains at least one positive value.'
        if self.boundForm.equation.independentData2CannotContainPositiveFlag and self.boundForm.equation.dataCache.independentData2ContainsPositiveFlag:
            return 'This equation requires that "' + self.boundForm.cleaned_data['dataNameY'] + '" contain no positive values, but it contains at least one positive value.'
            
        # check for negative
        if self.boundForm.equation.independentData1CannotContainNegativeFlag and self.boundForm.equation.dataCache.independentData1ContainsNegativeFlag:
            return 'This equation requires that "' + self.boundForm.cleaned_data['dataNameX'] + '" contain no negative values, but it contains at least one negative value.'
        if self.boundForm.equation.independentData2CannotContainNegativeFlag and self.boundForm.equation.dataCache.independentData2ContainsNegativeFlag:
            return 'This equation requires that "' + self.boundForm.cleaned_data['dataNameY'] + '" contain no negative values, but it contains at least one negative value.'
        
        # all good
        return ''


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)
        self.CommonCreateAndInitializeDataObject(False)
        self.dataObject.textDataEditor = self.boundForm.cleaned_data["textDataEditor"]

        self.webFormName = self.boundForm.equation.GetDisplayName() + ' ' + str(self.dimensionality) + 'D<br>' + self.boundForm.equation.GetDisplayHTML() # requires the above call to Initalize()

        self.pdfTitleHTML = 'Equation Family: ' + self.boundForm.equation.__module__.split('.')[-1] + '<br><br>'
        self.pdfTitleHTML += self.boundForm.equation.GetDisplayHTML() # requires the above webFormName which needs Initialize()
        
        self.boundForm.equation.dataCache = self.boundForm.equationBase.dataCache
        
        self.boundForm.equation.upperCoefficientBounds = self.boundForm.cleaned_data['upperCoefficientBoundsList']
        self.boundForm.equation.lowerCoefficientBounds = self.boundForm.cleaned_data['lowerCoefficientBoundsList']
        
        self.boundForm.equation.fixedCoefficients = self.boundForm.cleaned_data['fixedCoefficientList']
        
        self.boundForm.equation.estimatedCoefficients = numpy.array(self.boundForm.cleaned_data['estimatedCoefficientList'])
        try:
            if len(self.boundForm.equation.estimatedCoefficients) > len(self.boundForm.equation.GetCoefficientDesignators()):
                self.boundForm.equation.estimatedCoefficients = self.boundForm.equation.estimatedCoefficients[:len(self.boundForm.equation.GetCoefficientDesignators())]
        except:
            self.boundForm.equation.estimatedCoefficients = numpy.array([])
            
        # estimates for each coefficients were not supplied
        for i in range(len(self.boundForm.equation.estimatedCoefficients)):
            if self.boundForm.equation.estimatedCoefficients[i] is None:
                return 'Estimates for each parameter were not supplied. Please go back and check esimated parameters.'
        
        self.dataObject.equation = self.boundForm.equation

        return ''

            
    def CreateUnboundInterfaceForm(self, request):
 
        self.dictionaryToReturn = {}
        self.dictionaryToReturn['dimensionality'] = str(self.dimensionality)
        
        # make a dimensionality-based unbound Django form
        self.unboundForm = eval('zunzun.forms.Equation_' + str(self.dimensionality) + 'D()')
            
        # FF - set "rank" variable if coming from the function finders, else set "rank" to None
        if 'RANK' in list(request.GET.keys()):
            try:
                self.rank = int(request.GET['RANK'])
            except:
                raise Exception('Incorrect call to equation interface.')
            if self.rank < 1 or self.rank > 10000000: # must be between 1 and 10 million
                 raise Exception('Bad call to equation interface.')

            # bounds check
            self.functionFinderResultsList = self.LoadItemFromSessionStore('functionfinder', 'functionFinderResultsList')
            if self.functionFinderResultsList == None:
                 raise Exception("Your browser's session cookie appears to have expired, please run the function finder again.")
            if len(self.functionFinderResultsList) < self.rank:
                self.rank = len(self.functionFinderResultsList)

            if self.dimensionality == 2:
                self.unboundForm.fields['dataNameX'].initial = self.LoadItemFromSessionStore('data', 'IndependentDataName1')
                self.unboundForm.fields['dataNameY'].initial = self.LoadItemFromSessionStore('data', 'DependentDataName')
            else:
                self.unboundForm.fields['dataNameX'].initial = self.LoadItemFromSessionStore('data', 'IndependentDataName1')
                self.unboundForm.fields['dataNameY'].initial = self.LoadItemFromSessionStore('data', 'IndependentDataName2')
                self.unboundForm.fields['dataNameZ'].initial = self.LoadItemFromSessionStore('data', 'DependentDataName')
                
            self.unboundForm.fields['fittingTarget'].initial = self.LoadItemFromSessionStore('data', 'fittingTarget')
            
        self.dictionaryToReturn['quotedEquationFamilyName'] = self.inEquationFamilyName
        self.dictionaryToReturn['quotedEquationName'] = self.inEquationName

        self.equation = self.GetEquationFromNameAndFamily(self.inEquationName, self.inEquationFamilyName, checkForSplinesAndUserDefinedFunctionsFlag = 1)
        if not self.equation: # could not find a matching equation or spline
            raise Exception ('Could not find the equation ' + self.inEquationName + " in the equation family " + self.inEquationFamilyName + ".")
        
        self.SpecificEquationUnboundInterfaceCode(request)
            
        self.dictionaryToReturn['equationInstance'] = self.equation
        
        # set the form to have either default or session text data
        temp = self.LoadItemFromSessionStore('data', 'textDataEditor_' + str(self.dimensionality) + 'D')
        if temp:
            self.unboundForm.fields['textDataEditor'].initial = temp
        elif self.equation.splineFlag:
            self.unboundForm.fields['textDataEditor'].initial += self.equation.exampleData
        else:
            self.unboundForm.fields['textDataEditor'].initial += self.extraExampleDataTextForWeightedFitting + self.equation.exampleData
        
        # set any remaining form items
        temp = self.LoadItemFromSessionStore('data', 'commaConversion')
        if temp:
            self.unboundForm.fields['commaConversion'].initial = temp
        temp = self.LoadItemFromSessionStore('data', 'weightedFittingChoice')
        if temp:
            self.unboundForm.fields['weightedFittingChoice'].initial = temp
    
        # equation instance is now in hand, make items necessary for user interface
        self.dictionaryToReturn['header_text'] = 'Fitting Interface For ' + self.equation.GetDisplayName() + ' ' + str(self.dimensionality) + 'D<br>' + self.equation.GetDisplayHTML()
        self.dictionaryToReturn['title_string'] = 'ZunZunSite3 - ' + self.equation.GetDisplayName() + ' Fitting Interface'

        self.unboundForm.weightedFittingPossibleFlag = not self.spline

        temp = self.LoadItemFromSessionStore('data', 'udfEditor_' + str(self.dimensionality) + 'D')
        if temp:
            self.unboundForm.fields['udfEditor'].initial = temp

        # for the fixed and estimated coefficient templates
        if not self.equation.userSelectablePolyfunctionalFlag and not self.equation.userCustomizablePolynomialFlag and not self.equation.splineFlag and not self.equation.userDefinedFunctionFlag:
            coefficientBoundsTemplateRequirement = []
            fixedCoefficientTemplateRequirement = []
            estimatedCoefficientTemplateRequirement = []
            
            if self.equation.userSelectablePolynomialFlag:
                if str(self.dimensionality) == '2':
                    for i in range(len(zunzun.formConstants.polynomialOrder2DChoices)):
                        coefficientBoundsTemplateRequirement.append([self.equation.listOfAdditionalCoefficientDesignators[i],
                                                                          eval('self.unboundForm["upperCoefficientBound' + str(i) + '"]'),
                                                                          eval('self.unboundForm["lowerCoefficientBound' + str(i) + '"]')])
                        fixedCoefficientTemplateRequirement.append([self.equation.listOfAdditionalCoefficientDesignators[i], eval('self.unboundForm["fixedCoefficient' + str(i) + '"]')])
                        estimatedCoefficientTemplateRequirement.append([self.equation.listOfAdditionalCoefficientDesignators[i], eval('self.unboundForm["estimatedCoefficient' + str(i) + '"]')])
                else:
                    pass # not used for 3D polynomials
            else:
                coeffDesignatorList = self.equation.GetCoefficientDesignators()
                for i in range(len(coeffDesignatorList)):
                    coefficientBoundsTemplateRequirement.append([coeffDesignatorList[i],
                                                                 eval('self.unboundForm["upperCoefficientBound' + str(i) + '"]'),
                                                                 eval('self.unboundForm["lowerCoefficientBound' + str(i) + '"]')])
                    if self.equation.upperCoefficientBounds:
                        if self.equation.upperCoefficientBounds[i] != None:
                            exec('self.unboundForm.fields["upperCoefficientBound' + str(i) + '"].initial = ' + str(self.equation.upperCoefficientBounds[i]))
                    if self.equation.lowerCoefficientBounds:
                        if self.equation.lowerCoefficientBounds[i] != None:
                            exec('self.unboundForm.fields["lowerCoefficientBound' + str(i) + '"].initial = ' + str(self.equation.lowerCoefficientBounds[i]))
                    fixedCoefficientTemplateRequirement.append([coeffDesignatorList[i], eval('self.unboundForm["fixedCoefficient' + str(i) + '"]')])
                    estimatedCoefficientTemplateRequirement.append([coeffDesignatorList[i], eval('self.unboundForm["estimatedCoefficient' + str(i) + '"]')])

            self.dictionaryToReturn['coefficientBoundsTemplateRequirement'] = coefficientBoundsTemplateRequirement
            self.dictionaryToReturn['fixedCoefficientTemplateRequirement'] = fixedCoefficientTemplateRequirement
            self.dictionaryToReturn['estimatedCoefficientTemplateRequirement'] = estimatedCoefficientTemplateRequirement
            
        self.dictionaryToReturn['mainForm'] = self.unboundForm

        return self.dictionaryToReturn

    
    def SpecificEquationBoundInterfaceCode(self, request):
        pass
    
    
    def SpecificEquationUnboundInterfaceCode(self, request):
        self.dictionaryToReturn['equationHTML'] = self.equation.GetDisplayHTML()
    
        
    def CreateBoundInterfaceForm(self, request):
        
        # make a dimensionality-based bound Django form
        self.boundForm = eval('zunzun.forms.Equation_' + str(self.dimensionality) + 'D(request.POST)')
        self.boundForm.dimensionality = str(self.dimensionality)

        self.boundForm['fittingTarget'].required = True

        if self.inEquationName == 'User-Selectable Rational': # this "with offset" portion of the name is not in the URL
            if 'polyRational_OFFSET' in request.POST:
                if request.POST['polyRational_OFFSET'] == 'True':
                    self.inEquationName = self.inEquationName + " With Offset"

        self.boundForm.equation = self.GetEquationFromNameAndFamily(self.inEquationName, self.inEquationFamilyName, checkForSplinesAndUserDefinedFunctionsFlag = 1)
        if not self.boundForm.equation: # could not find a matching equation or spline
            raise Exception ('Could not find the equation ' + self.inEquationName + " in the equation family " + self.inEquationFamilyName + ".")

        self.SpecificEquationBoundInterfaceCode(request)
        
        self.equationInstance = self.boundForm.equation


    def GenerateListOfWorkItems(self):

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Fitting Data"})
        
        try:
            self.dataObject.equation.Solve()
        except:
            itemsToRender = {}
            itemsToRender['error0'] = str(sys.exc_info()[0])
            itemsToRender['error1'] = str(sys.exc_info()[1])
            open(os.path.join(settings.TEMP_FILES_DIR, self.dataObject.uniqueString + ".html"), "w").write(render_to_string('zunzun/exception_while_fitting_an_equation.html', itemsToRender))            
            self.SaveDictionaryOfItemsToSessionStore('status', {'redirectToResultsFileOrURL':os.path.join(settings.TEMP_FILES_DIR, self.dataObject.uniqueString + ".html")})


    def GetEquationFromNameAndFamily(self, inEquationName, inEquationFamilyName, checkForSplinesAndUserDefinedFunctionsFlag):
    
        equation = None
        if self.dimensionality == 2: # 2D
            submodules = inspect.getmembers(pyeq3.Models_2D)
        else:
            submodules = inspect.getmembers(pyeq3.Models_3D)

        for submodule in submodules:
            if inspect.ismodule(submodule[1]):
                if submodule[0] != inEquationFamilyName:
                    continue
                for equationClass in inspect.getmembers(submodule[1]):
                    if inspect.isclass(equationClass[1]):
                        for extendedName in pyeq3.ExtendedVersionHandlers.extendedVersionHandlerNameList:
                            try:
                                tempEquation = equationClass[1]('SSQABS', extendedName)
                                if tempEquation.GetDisplayName() == inEquationName:
                                    equation = tempEquation
                            except:
                                continue
                                                    
        # not an equation, check for splines
        if not equation and checkForSplinesAndUserDefinedFunctionsFlag:
            if inEquationFamilyName == 'Spline' and inEquationName == 'Spline':
                if self.dimensionality == 2: # 2D
                    equation = pyeq3.Models_2D.Spline.Spline()
                else: # 3D
                    equation = pyeq3.Models_3D.Spline.Spline()
            if inEquationFamilyName == 'UserDefinedFunction' and inEquationName == 'UserDefinedFunction':
                if self.dimensionality == 2: # 2D
                    equation = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction()
                else: # 3D
                    equation = pyeq3.Models_3D.UserDefinedFunction.UserDefinedFunction()
                    
        return equation
