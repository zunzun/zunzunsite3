



import sys
import django.forms
import django.utils.encoding
from . import myWidgets
import pyeq3
from . import formConstants
import unicodedata


class EvaluateAtAPointForm_2D(django.forms.Form) :
    x = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'15', 'onKeyPress':'return submitenter(this,event)'}), required=True)



class EvaluateAtAPointForm_3D(EvaluateAtAPointForm_2D) :
    y = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'15', 'onKeyPress':'return submitenter(this,event)'}), required=True)



class FeedbackForm(django.forms.Form):
    feedbackText = django.forms.CharField(widget=django.forms.widgets.Textarea(attrs={'cols':'70', 'rows':'9', 'WRAP':'OFF'}) )
    emailAddress = django.forms.CharField(max_length=75, required=False)

    
    def clean_feedbackText(self):
        data = self.cleaned_data['feedbackText']

        # check for 'no data', i.e., just pressing the button to see what happens
        if len(data) < 3:
            raise django.forms.ValidationError('The entry %s is too short to be considered valid feedback.' % data)

        # check for link spammers
        if data.lower().count('{vo{vo,') > 0:
            raise django.forms.ValidationError('Found the string "{vo{vo, " at least once, this is almost always from link spammer bots - ignoring.')

        if data.lower().count('</a>, [url=') > 0:
            raise django.forms.ValidationError('Found the string "</a>, [url=" at least once, this is almost always from link spammer bots - ignoring.')

        if data.lower().count('a href=') > 0:
            raise django.forms.ValidationError('Found the string "a href=" at least once, this is almost always from link spammer bots - ignoring.')


        return data



class UsesDataForm_BaseClass(django.forms.Form) :
    weightedFittingChoice = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.weightedFittingChoices, initial='OFF', required=False)
    udfEditor = django.forms.CharField( widget=django.forms.widgets.Textarea(attrs={'cols':'60', 'rows':'14'}), required=False)
    textDataEditor = django.forms.CharField( widget=django.forms.widgets.Textarea(attrs={'cols':'55', 'rows':'15'}), initial=formConstants.initialDataEntryText )
    commaConversion = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.commaConversionChoices, initial='S' )
    for i in range(25):
        exec('upperCoefficientBound' + str(i) + " = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)")
        exec('lowerCoefficientBound' + str(i) + " = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)")
        exec('fixedCoefficient' + str(i) + " = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)")
        exec('estimatedCoefficient' + str(i) + " = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)")


    def LoadAndVerifyCoefficientBounds(self):
        upperCoefficientBoundsList = []
        for i in range(25):
            fieldName = 'upperCoefficientBound' + str(i)
            if fieldName in list(self.cleaned_data.keys()):
                try:
                    if None == self.cleaned_data[fieldName]:
                        upperCoefficientBoundsList.append(None)
                    else:
                        bound = float(self.cleaned_data[fieldName])
                        upperCoefficientBoundsList.append(bound)
                except:
                    raise django.forms.ValidationError('One of the upper coefficient bounds you entered was "' + str(self.cleaned_data[fieldName]) + '", and this could not be converted to a number.')
            else:
                upperCoefficientBoundsList.append(None)

        # if no user-supplied upper coefficient bounds were found, default to an empty list
        upperCoefficientBoundsCount = 0
        for i in upperCoefficientBoundsList:
            if i is not None:
                upperCoefficientBoundsCount += 1
        if 0 == upperCoefficientBoundsCount:
            upperCoefficientBoundsList = []

        ############################################

        lowerCoefficientBoundsList = []
        for i in range(25):
            fieldName = 'lowerCoefficientBound' + str(i)
            if fieldName in list(self.cleaned_data.keys()):
                try:
                    if None == self.cleaned_data[fieldName]:
                        lowerCoefficientBoundsList.append(None)
                    else:
                        bound = float(self.cleaned_data[fieldName])
                        lowerCoefficientBoundsList.append(bound)
                except:
                    raise django.forms.ValidationError('One of the lower coefficient bounds you entered was "' + str(self.cleaned_data[fieldName]) + '", and this could not be converted to a number.')
            else:
                lowerCoefficientBoundsList.append(None)
    
        # if no user-supplied lower coefficient bounds were found, default to an empty list
        lowerCoefficientBoundsCount = 0
        for i in lowerCoefficientBoundsList:
            if i is not None:
                lowerCoefficientBoundsCount += 1
        if 0 == lowerCoefficientBoundsCount:
            lowerCoefficientBoundsList = []
            
        ############################################
        
        if (upperCoefficientBoundsList != []) and (lowerCoefficientBoundsList != []):
            for i in range(25):
                if (upperCoefficientBoundsList[i] != None) and (lowerCoefficientBoundsList[i] != None):
                    if upperCoefficientBoundsList[i] <= lowerCoefficientBoundsList[i]:
                        exceptionString  = 'One of the upper coefficient bounds you entered was "'
                        exceptionString += str(upperCoefficientBoundsList[i])
                        exceptionString += ', and this was less than or equal to the associated lower bound of '
                        exceptionString += str(lowerCoefficientBoundsList[i]) + '.'
                        raise django.forms.ValidationError(exceptionString)

        ############################################

        self.cleaned_data['upperCoefficientBoundsList'] = upperCoefficientBoundsList
        self.cleaned_data['lowerCoefficientBoundsList'] = lowerCoefficientBoundsList


    def LoadAndVerifyFixedCoefficients(self):
        fixedCoefficientList = []
        for i in range(25):
            fieldName = 'fixedCoefficient' + str(i)
            if fieldName in list(self.cleaned_data.keys()):
                try:
                    if None == self.cleaned_data[fieldName]:
                        fixedCoefficientList.append(None)
                    else:
                        fixedCoefficient = float(self.cleaned_data[fieldName])
                        fixedCoefficientList.append(fixedCoefficient)
                except:
                    raise django.forms.ValidationError('One of the fixed coefficient values you entered was "' + str(self.cleaned_data[fieldName]) + '", and this could not be converted to a number.')
            else:
                fixedCoefficientList.append(None)

        # if no user-supplied fixed coefficients were found, default to an empty list
        fixedCoefficientCount = 0
        for i in fixedCoefficientList:
            if i is not None:
                fixedCoefficientCount += 1
        if 0 == fixedCoefficientCount:
            fixedCoefficientList = []
            
        self.cleaned_data['fixedCoefficientList'] = fixedCoefficientList


    def LoadAndVerifyEstimatedCoefficients(self):
        estimatedCoefficientList = []
        for i in range(25):
            fieldName = 'estimatedCoefficient' + str(i)
            if fieldName in list(self.cleaned_data.keys()):
                try:
                    if None == self.cleaned_data[fieldName]:
                        estimatedCoefficientList.append(None)
                    else:
                        estimatedCoefficient = float(self.cleaned_data[fieldName])
                        estimatedCoefficientList.append(estimatedCoefficient)
                except:
                    raise django.forms.ValidationError('One of the estimated coefficient values you entered was "' + str(self.cleaned_data[fieldName]) + '", and this could not be converted to a number.')
            else:
                estimatedCoefficientList.append(None)

        # if no user-supplied estimated coefficients were found, default to an empty list
        estimatedCoefficientCount = 0
        for i in estimatedCoefficientList:
            if i is not None:
                estimatedCoefficientCount += 1
        if 0 == estimatedCoefficientCount:
            estimatedCoefficientList = []
            
        self.cleaned_data['estimatedCoefficientList'] = estimatedCoefficientList


    def LoadAndVerifyTextData(self):
        
        if "textDataEditor" not in list(self.cleaned_data.keys()):
            raise django.forms.ValidationError('Could not find any text data.  Please enter text data and try again.')

        temp = self.cleaned_data["textDataEditor"]
        temp = str(temp)
        if len(temp) < 2: # no text data at all
            raise django.forms.ValidationError('Could not find sufficient text data.  Please check the text data and try again.')
        
        # form spammers usually leave out non-text-entry fields.
        if 'commaConversion' not in list(self.cleaned_data.keys()):
            raise django.forms.ValidationError('Missing form data, no comma conversion specified.')

        # comma conversions
        if self.cleaned_data["commaConversion"] == "D": # decimal separator
            temp = temp.replace(",",".")
        elif self.cleaned_data["commaConversion"] == "I": # as if they don't exist
            temp = temp.replace(",","")
        else:
            temp = temp.replace(","," ") # default to the original default conversion

        # replace these characters with spaces for use by float()
        temp = temp.replace("$"," ")
        temp = temp.replace("%"," ")
        temp = temp.replace("("," ")
        temp = temp.replace(")"," ")
        temp = temp.replace("{"," ")
        temp = temp.replace("}"," ")


        #TODO - are these still necessary?
        # replace \r\n with \n
        temp = temp.replace('\r\n','\n')
        # replace remaining \r with \n
        temp = temp.replace('\r','\n')


        # replace HTML spaces and tabs with spaces
        temp = temp.replace("&nbsp;"," ")
        temp = temp.replace("&#9;"," ")
        temp = temp.replace("&#09;"," ")
        temp = temp.replace("&#32;"," ")

        self.equationBase = pyeq3.IModel.IModel()
        self.equationBase._dimensionality = int(self.dimensionality)
        
        useWeightedFittingFlag = False # default is no weighted fitting
        if "weightedFittingChoice" in list(self.cleaned_data.keys()):
            if self.cleaned_data["weightedFittingChoice"] == "ON":
                useWeightedFittingFlag = True

        temp = temp.replace('\\r\\n', '\n') # for the pyeq3 readlines() in dataConvertorService()
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(temp, self.equationBase, useWeightedFittingFlag)
        
        self.cleaned_data['IndependentData'] = self.equationBase.dataCache.allDataCacheDictionary['IndependentData'] 
        if self.dimensionality != '1':
            self.cleaned_data['DependentData'] = self.equationBase.dataCache.allDataCacheDictionary['DependentData'] 

        # Data errors go here
        dataLength = len(self.equationBase.dataCache.allDataCacheDictionary['IndependentData'] [0])
        if dataLength == 0:
            raise django.forms.ValidationError("No data points found in your text - is weighting on?")
        if dataLength > 10100:
            raise django.forms.ValidationError("Your data has " + str(dataLength) + " data points, the site is currently limited to 10,000.")


    def LoadandVerifyGraphScales(self):        
        graphScaleX = float(self.cleaned_data['graphScaleRadioButtonX'])
        minManualScaleX = 0.0
        maxManualScaleX = 0.0
        if graphScaleX > 98.0: # manual entry chosen
            try:
                minManualScaleX = float(self.cleaned_data['graphScaleManuallyEnteredMinX'])
            except:
                raise django.forms.ValidationError('Manual X scaling was chosen, but the minimum X value that was entered could not be converted to a number.')
            try:
                maxManualScaleX = float(self.cleaned_data['graphScaleManuallyEnteredMaxX'])
            except:
                raise django.forms.ValidationError('Manual X scaling was chosen, but the maximum X value that was entered could not be converted to a number.')
            if minManualScaleX == maxManualScaleX:
                raise django.forms.ValidationError('Manual X scaling was chosen, but the minimum and maximum values entered are identical.')
            if minManualScaleX > maxManualScaleX:
                raise django.forms.ValidationError('Manual X scaling was chosen, but the minimum X scale was greater than the maximum X scale.')
        self.cleaned_data['graphScaleX'] = graphScaleX
        self.cleaned_data['minManualScaleX'] = minManualScaleX
        self.cleaned_data['maxManualScaleX'] = maxManualScaleX
            
        if int(self.dimensionality) > 1:
            graphScaleY = float(self.cleaned_data['graphScaleRadioButtonY'])
            minManualScaleY = 0.0
            maxManualScaleY = 0.0
            if graphScaleY > 98.0: # manual entry chosen
                try:
                    minManualScaleY = float(self.cleaned_data['graphScaleManuallyEnteredMinY'])
                except:
                    raise django.forms.ValidationError('Manual Y scaling was chosen, but the minimum Y value that was entered could not be converted to a number.')
                try:
                    maxManualScaleY = float(self.cleaned_data['graphScaleManuallyEnteredMaxY'])
                except:
                    raise django.forms.ValidationError('Manual Y scaling was chosen, but the maximum Y value that was entered could not be converted to a number.')
                if minManualScaleY == maxManualScaleY:
                    raise django.forms.ValidationError('Manual Y scaling was chosen, but the minimum and maximum values entered are identical.')
                if minManualScaleY > maxManualScaleY:
                    raise django.forms.ValidationError('Manual Y scaling was chosen, but the minimum Y scale was greater than the maximum Y scale.')
            self.cleaned_data['graphScaleY'] = graphScaleY
            self.cleaned_data['minManualScaleY'] = minManualScaleY
            self.cleaned_data['maxManualScaleY'] = maxManualScaleY
                
        if int(self.dimensionality) > 2:
            graphScaleZ = float(self.cleaned_data['graphScaleRadioButtonZ'])
            minManualScaleZ = 0.0
            maxManualScaleZ = 0.0
            if graphScaleZ > 98.0: # manual entry chosen
                try:
                    minManualScaleZ = float(self.cleaned_data['graphScaleManuallyEnteredMinZ'])
                except:
                    raise django.forms.ValidationError('Manual Z scaling was chosen, but the minimum Z value that was entered could not be converted to a number.')
                try:
                    maxManualScaleZ = float(self.cleaned_data['graphScaleManuallyEnteredMaxZ'])
                except:
                    raise django.forms.ValidationError('Manual Z scaling was chosen, but the maximum Z value that was entered could not be converted to a number.')
                if minManualScaleZ == maxManualScaleZ:
                    raise django.forms.ValidationError('Manual Z scaling was chosen, but the minimum and maximum values entered are identical.')
                if minManualScaleZ > maxManualScaleZ:
                    raise django.forms.ValidationError('Manual Z scaling was chosen, but the minimum Z scale was greater than the maximum Z scale.')
            self.cleaned_data['graphScaleZ'] = graphScaleZ
            self.cleaned_data['minManualScaleZ'] = minManualScaleZ
            self.cleaned_data['maxManualScaleZ'] = maxManualScaleZ


    def clean(self):
        self.LoadAndVerifyTextData()
        self.LoadandVerifyGraphScales()
        self.LoadAndVerifyEstimatedCoefficients()
        self.LoadAndVerifyFixedCoefficients()
        self.LoadAndVerifyCoefficientBounds()
        return self.cleaned_data



class CharacterizeDataForm_BaseClass (UsesDataForm_BaseClass) :

    graphSize = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.graphSizeOptions, initial='800x600' )
    statisticalDistributionsSortBy = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.statisticalDistributionsSortByChoices, initial='AIC', required=False)



class CharacterizeDataForm_1D (CharacterizeDataForm_BaseClass) :
    scientificNotationX = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.scientificNotationChoices, initial='AUTO')
    logLinX = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.logLinChoices, initial='LIN')
    dataNameX = django.forms.CharField(max_length=40, initial='X data')
    graphScaleRadioButtonX = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.graphScaleChoices, initial='0.050' )
    graphScaleManuallyEnteredMaxX = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)
    graphScaleManuallyEnteredMinX = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)

    def clean_dataNameX(self):
        return self.cleaned_data['dataNameX']



class CharacterizeDataForm_2D (CharacterizeDataForm_1D) :
    scientificNotationY = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.scientificNotationChoices, initial='AUTO' )
    logLinY = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.logLinChoices, initial='LIN')
    dataNameY = django.forms.CharField(max_length=40, initial='Y data')
    graphScaleRadioButtonY = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.graphScaleChoices, initial='0.050' )
    graphScaleManuallyEnteredMaxY = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)
    graphScaleManuallyEnteredMinY = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)

    def clean_dataNameY(self):
        return self.cleaned_data['dataNameY']


        
class CharacterizeDataForm_3D (CharacterizeDataForm_2D) :
    dataPointSize3D = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.dataPointSize3D_Choices, initial='0.0' , required=False)
    scientificNotationZ = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.scientificNotationChoices, initial='AUTO' )
    logLinZ = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.logLinChoices, initial='LIN')
    dataNameZ = django.forms.CharField(max_length=40, initial='Z data')
    graphScaleRadioButtonZ = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.graphScaleChoices, initial='0.050' )
    graphScaleManuallyEnteredMaxZ = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)
    graphScaleManuallyEnteredMinZ = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'10'}), required=False)
    rotationAnglesAzimuth = django.forms.ChoiceField( choices=formConstants.azimuthChoices, initial='165' )
    rotationAnglesAltimuth = django.forms.ChoiceField( choices=formConstants.altimuthChoices, initial='20' )
    animationSize = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.animationSizeOptions, initial='0x0')

    def clean_dataNameZ(self):
        return self.cleaned_data['dataNameZ']
    
    def clean_dataPointSize3D(self):
        try:
            pointSize =  float(self.cleaned_data['dataPointSize3D'])
        except:
            pointSize = 0.0
            
        return pointSize
    


class FunctionFinder (UsesDataForm_BaseClass) :
    fittingTarget = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.fittingTargetChoices, initial='SSQABS' )
    extendedEquationTypes = django.forms.MultipleChoiceField( widget=myWidgets.BR_CheckboxSelectMultiple_Widget(), choices=formConstants.extendedEquationTypeChoices, initial=['STANDARD'])
    dataNameX = django.forms.CharField(max_length=40, initial='X data')
    dataNameY = django.forms.CharField(max_length=40, initial='Y data')


    def clean(self): # override, no graph scales in form for function finders
        self.LoadAndVerifyTextData()
        if self.equationBase.dataCache.DependentDataContainsZeroFlag != 0 and self.cleaned_data['fittingTarget'][-3:] == "REL":
            raise django.forms.ValidationError('Your data contains at least one dependent data value of exactly 0.0, a relative fit cannot be performed as divide-by-zero errors would occurr.')
        return self.cleaned_data



class FunctionFinder_2D (FunctionFinder) :
    equationFamilyInclusion = django.forms.MultipleChoiceField( widget=myWidgets.BR_CheckboxSelectMultiple_Widget(), choices=formConstants.equationCategoryNameChoices2D, initial=formConstants.equationCategoryNameChoicesDefaultValues2D )
    smoothnessControl2D = django.forms.ChoiceField( choices=formConstants.smoothnessControl2DChoices, initial='4')



class FunctionFinder_3D (FunctionFinder) :
    equationFamilyInclusion = django.forms.MultipleChoiceField( widget=myWidgets.BR_CheckboxSelectMultiple_Widget(), choices=formConstants.equationCategoryNameChoices3D, initial=formConstants.equationCategoryNameChoicesDefaultValues3D )
    smoothnessControl3D = django.forms.ChoiceField( choices=formConstants.smoothnessControl3DChoices, initial='6')
    dataNameZ = django.forms.CharField(max_length=40, initial='Z data')



class Equation_2D(CharacterizeDataForm_2D) :
    fittingTarget = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.fittingTargetChoices, initial='SSQABS', required=False)
    polynomialOrderX2D = django.forms.ChoiceField( choices=formConstants.polynomialOrder2DChoices, initial='5', required=False)
    splineOrderX = django.forms.ChoiceField( choices=formConstants.splineOrderChoices, initial='3', required=False)
    splineSmoothness = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'12'}), initial = '1.0', required=False)

    polyLength = max(len(pyeq3.PolyFunctions.GenerateListForPolyfunctionals_2D()), len(pyeq3.PolyFunctions.GenerateListForCustomPolynomials_2D()))
    for i in range(polyLength):
        exec("polyFunctional_X" + str(i) + " = django.forms.BooleanField(widget=django.forms.widgets.HiddenInput(attrs={'value':False}), required=False)")

    for i in range(len(pyeq3.PolyFunctions.GenerateListForRationals_2D())):
        exec("polyRational_X_N" + str(i) + " = django.forms.BooleanField(widget=django.forms.widgets.HiddenInput(attrs={'value':False}), required=False)")
        exec("polyRational_X_D" + str(i) + " = django.forms.BooleanField(widget=django.forms.widgets.HiddenInput(attrs={'value':False}), required=False)")

    polyRational_OFFSET  = django.forms.BooleanField(widget=django.forms.widgets.HiddenInput(attrs={'value':False}), required=False)


    def clean(self): # watch equation. and equationBase. here
        self.__class__.__bases__[0].clean(self)
        if self.equationBase.dataCache.DependentDataContainsZeroFlag  != 0 and self.cleaned_data['fittingTarget'][-3:] == "REL":
            raise django.forms.ValidationError('Your data contains at least one dependent data value of exactly 0.0, a relative fit cannot be performed as divide-by-zero errors would occurr.')
        
        if self.equation.independentData1CannotContainZeroFlag and self.equationBase.dataCache.independentData1ContainsZeroFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-zero values for the first independent variable (X).<BR>\n"
            errorString += "At least one of the values was exactly equal to zero.<BR>\n"
            errorString += "Examples that would fail would be ln(x) and 1/x, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData1CannotContainNegativeFlag and self.equationBase.dataCache.independentData1ContainsNegativeFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-negative values for the first independent variable (X).<BR>\n"
            errorString += "At least one of the values was negative.<BR>\n"
            errorString += "Examples that would fail would be ln(x) and x<sup>0.5</sup>, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData1CannotContainPositiveFlag and self.equationBase.dataCache.independentData1ContainsPositiveFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-positive values for the first independent variable (X).<BR>\n"
            errorString += "At least one of the values was positive.<BR>\n"
            errorString += "Examples that would fail would be ln(-x) and -x<sup>0.5</sup>, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData1CannotContainBothPositiveAndNegativeFlag and self.equationBase.dataCache.independentData1ContainsPositiveFlag and self.equationBase.dataCache.independentData1ContainsNegativeFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and cannot have both positive and negative values for the first independent variable (X).<BR>\n"
            errorString += "Please check the data.\n"
            raise django.forms.ValidationError(errorString)
        
        if self.equation.splineFlag:
            if '' == self.cleaned_data['splineSmoothness']:
                raise django.forms.ValidationError('Spline was chosen, but the spline smoothness control entry did not contain a number.')
                
            try:
                splineSmoothness = float(self.cleaned_data['splineSmoothness'])
            except:
                raise django.forms.ValidationError(sys.exc_info()[1]) # re-raise as validation error
            
            self.cleaned_data['splineSmoothness'] = splineSmoothness

        if not self.equation.splineFlag and not self.equation.userDefinedFunctionFlag:
            if len(self.equation.GetCoefficientDesignators()) > len(self.equationBase.dataCache.allDataCacheDictionary['IndependentData'][0]):
                raise django.forms.ValidationError("The selected model has more coefficients than data points, I cannot model the data to this equation.")

            if len(self.equation.GetCoefficientDesignators()) == 0:
                raise django.forms.ValidationError("There are no coefficients to be modeled in this equation.")

        if self.equation.splineFlag:
            if (int(self.cleaned_data['splineOrderX']) + 1) > len(self.equationBase.dataCache.allDataCacheDictionary['IndependentData'][0]):
                raise django.forms.ValidationError("The selected spline order has more coefficients than the given number of data points, I cannot model the data to this spline.")

        if self.equation.userDefinedFunctionFlag:
            self.equation.userDefinedFunctionText = self.cleaned_data["udfEditor"]
            if self.equation.userDefinedFunctionText == '':
                raise django.forms.ValidationError("You entered no text as a User Defined Function. Please enter a function.")
            try:
                self.equation.ParseAndCompileUserFunctionString(self.equation.userDefinedFunctionText)
            except:
                raise django.forms.ValidationError(sys.exc_info()[1]) # re-raise as validation error

        return self.cleaned_data


        
class Equation_3D (CharacterizeDataForm_3D) :
    fittingTarget = django.forms.ChoiceField( widget=django.forms.widgets.RadioSelect(renderer=myWidgets.BR_RadioFieldRenderer), choices=formConstants.fittingTargetChoices, initial='SSQABS', required=False)
    polynomialOrderX3D = django.forms.ChoiceField( choices=formConstants.polynomialOrder3DChoices, initial='3', required=False)
    polynomialOrderY3D = django.forms.ChoiceField( choices=formConstants.polynomialOrder3DChoices, initial='3', required=False)
    splineOrderX = django.forms.ChoiceField( choices=formConstants.splineOrderChoices, initial='2', required=False)
    splineOrderY = django.forms.ChoiceField( choices=formConstants.splineOrderChoices, initial='2', required=False)
    splineSmoothness = django.forms.FloatField(widget=django.forms.widgets.TextInput(attrs={'size':'12'}), initial = '1.0', required=False)

    for i in range(len(pyeq3.PolyFunctions.GenerateListForPolyfunctionals_3D_X())):
        for j in range(len(pyeq3.PolyFunctions.GenerateListForPolyfunctionals_3D_Y())):
            exec("polyFunctional_X" + str(i) + "Y" + str(j) + " = django.forms.BooleanField(widget=django.forms.widgets.HiddenInput(attrs={'value':False}), required=False)")


    def clean(self): # watch equation. and equationBase. here
        self.__class__.__bases__[0].clean(self)
        if self.equationBase.dataCache.DependentDataContainsZeroFlag != 0 and self.cleaned_data['fittingTarget'][-3:] == "REL":
            raise django.forms.ValidationError('Your data contains at least one dependent data value of exactly 0.0, a relative fit cannot be performed as divide-by-zero errors would occurr.')

        if self.equation.independentData1CannotContainZeroFlag and self.equationBase.dataCache.independentData1ContainsZeroFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-zero values for the first independent variable (X).<BR>\n"
            errorString += "At least one of the values was exactly equal to zero.<BR>\n"
            errorString += "Examples that would fail would be ln(x) and 1/x, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData2CannotContainZeroFlag and self.equationBase.dataCache.independentData2ContainsZeroFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-zero values for the second independent variable (Y).<BR>\n"
            errorString += "At least one of the values was exactly equal to zero.<BR>\n"
            errorString += "Examples that would fail would be ln(y) and 1/y, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData1CannotContainNegativeFlag and self.equationBase.dataCache.independentData1ContainsNegativeFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-negative values for the first independent variable (X).<BR>\n"
            errorString += "At least one of the values was negative.<BR>\n"
            errorString += "Examples that would fail would be ln(x) and x<sup>0.5</sup>, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData2CannotContainNegativeFlag and self.equationBase.dataCache.independentData2ContainsNegativeFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-negative values for the second independent variable (Y).<BR>\n"
            errorString += "At least one of the values was negative.<BR>\n"
            errorString += "Examples that would fail would be ln(y) and y<sup>0.5</sup>, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData1CannotContainPositiveFlag and self.equationBase.dataCache.independentData1ContainsPositiveFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-positive values for the first independent variable (X).<BR>\n"
            errorString += "At least one of the values was positive.<BR>\n"
            errorString += "Examples that would fail would be ln(-x) and -x<sup>0.5</sup>, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData2CannotContainPositiveFlag and self.equationBase.dataCache.independentData2ContainsPositiveFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and requires non-positive values for the second independent variable (Y).<BR>\n"
            errorString += "At least one of the values was positive.<BR>\n"
            errorString += "Examples that would fail would be ln(-y) and -y<sup>0.5</sup>, please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.independentData1CannotContainBothPositiveAndNegativeFlag and self.equationBase.dataCache.independentData1ContainsPositiveFlag and self.equationBase.dataCache.independentData1ContainsNegativeFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and cannot have both positive and negative values for the first independent variable (X).<BR>\n"
            errorString += "Please check the data.\n"
            raise django.forms.ValidationError(errorString)
        
        if self.equation.independentData2CannotContainBothPositiveAndNegativeFlag and self.equationBase.dataCache.independentData2ContainsPositiveFlag and self.equationBase.dataCache.independentData2ContainsNegativeFlag:
            errorString = self.equation.GetDisplayName() + " has the form<BR><BR>\n"
            errorString += self.equation.GetDisplayHTML() + "\n<BR><BR>\n"
            errorString += "and cannot have both positive and negative values for the second independent variable (Y).<BR>\n"
            errorString += "Please check the data.\n"
            raise django.forms.ValidationError(errorString)

        if self.equation.splineFlag:
            if '' == self.cleaned_data['splineSmoothness']:
                raise django.forms.ValidationError('Spline was chosen, but the spline smoothness control entry did not contain a number.')
                
            try:
                splineSmoothness = float(self.cleaned_data['splineSmoothness'])
            except:
                raise django.forms.ValidationError(sys.exc_info()[1]) # re-raise as validation error
           
            self.cleaned_data['splineSmoothness'] = splineSmoothness

        # for splines, we don't have the number of coefficients until data has been fitted
        if not self.equation.splineFlag and not self.equation.userDefinedFunctionFlag:
            if len(self.equation.GetCoefficientDesignators()) > len(self.equationBase.dataCache.allDataCacheDictionary['IndependentData'][0]):
                raise django.forms.ValidationError("The selected model has more coefficients than data points, I cannot model the data to this equation.")
            
            if len(self.equation.GetCoefficientDesignators()) == 0:
                raise django.forms.ValidationError("There are no coefficients to be modeled in this equation.")

        if self.equation.splineFlag:
            if ((int(self.cleaned_data['splineOrderX']) + 1) * (int(self.cleaned_data['splineOrderY']) + 1)) > len(self.equationBase.dataCache.allDataCacheDictionary['IndependentData'][0]):
                raise django.forms.ValidationError("The selected spline orders have more coefficients than the given number of data points, I cannot model the data to this spline.")

        if self.equation.userDefinedFunctionFlag:
            self.equation.userDefinedFunctionText = self.cleaned_data["udfEditor"]
            if self.equation.userDefinedFunctionText == '':
                raise django.forms.ValidationError("You entered no text as a User Defined Function. Please enter a function.")
            try:
                self.equation.ParseAndCompileUserFunctionString(self.equation.userDefinedFunctionText)
            except:
                raise django.forms.ValidationError(sys.exc_info()[1]) # re-raise as validation error

        return self.cleaned_data
