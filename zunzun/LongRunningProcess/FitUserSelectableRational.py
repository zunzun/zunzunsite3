



import inspect, time, math, random, multiprocessing, os, sys, copy

import numpy, scipy, scipy.stats

from . import FittingBaseClass
import zunzun.forms
import zunzun.formConstants
import pyeq3


sys.stdout = sys.stderr # wsgi cannot send to stdout, see http://code.google.com/p/modwsgi/wiki/DebuggingTechniques



class FitUserSelectableRational(FittingBaseClass.FittingBaseClass):

    interfaceString = 'zunzun/equation_fit_interface.html'
    reniceLevel = 13
    X2DList = pyeq3.PolyFunctions.GenerateListForRationals_2D()

    
    def SaveSpecificDataToSessionStore(self):
        self.SaveDictionaryOfItemsToSessionStore('data', {'dimensionality':self.dimensionality,
                                                          'equationName':self.inEquationName,
                                                          'equationFamilyName':self.inEquationFamilyName,
                                                          'solvedCoefficients':self.dataObject.equation.solvedCoefficients,
                                                          'fittingTarget':self.dataObject.equation.fittingTarget,
                                                          'rationalNumeratorFlags':self.dataObject.equation.rationalNumeratorFlags,
                                                          'rationalDenominatorFlags':self.dataObject.equation.rationalDenominatorFlags})


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)        
        s = FittingBaseClass.FittingBaseClass.TransferFormDataToDataObject(self, request)
        self.boundForm.equation.fittingTarget = self.boundForm.cleaned_data['fittingTarget']
        return s

        
    def SpecificEquationBoundInterfaceCode(self, request):
        if self.dimensionality == 2:
            for i in range(len(self.X2DList)):
                self.boundForm['polyRational_X_N' + str(i)].required = True # force form field validation
                self.boundForm['polyRational_X_D' + str(i)].required = True # force form field validation
                
            self.boundForm['polyRational_OFFSET'].required = True # force form field validation
            self.boundForm.equation.rationalNumeratorFlags = []
            self.boundForm.equation.rationalDenominatorFlags = []
            for i in range(len(self.X2DList)):
                if request.POST['polyRational_X_N' + str(i)] == 'True':
                    self.boundForm.equation.rationalNumeratorFlags.append(i)
                if request.POST['polyRational_X_D' + str(i)] == 'True':
                    self.boundForm.equation.rationalDenominatorFlags.append(i)


    def SpecificEquationUnboundInterfaceCode(self, request):
        if self.rank: # coming from a Function Finder
            self.equation.solvedCoefficients = self.functionFinderResultsList[self.rank-1][11]
            self.equation.rationalNumeratorFlags = self.functionFinderResultsList[self.rank-1][8]
            self.equation.rationalDenominatorFlags = self.functionFinderResultsList[self.rank-1][9]
            Polyrat2DNumeratorColorList = [] # Numerator
            for i in range(len(self.X2DList)):
                if i in self.functionFinderResultsList[self.rank-1][8]:
                    Polyrat2DNumeratorColorList.append(('rgb(255,255,255)', i, self.X2DList[i].HTML))
                else:
                    Polyrat2DNumeratorColorList.append(('rgb(211,211,211)', i, self.X2DList[i].HTML))
            self.dictionaryToReturn['Polyrat2DNumeratorColorList'] = Polyrat2DNumeratorColorList
            Polyrat2DDenominatorColorList = [] # Denominator
            for i in range(len(self.X2DList)):
                if i in self.functionFinderResultsList[self.rank-1][9]:
                    Polyrat2DDenominatorColorList.append(('rgb(255,255,255)', i, self.X2DList[i].HTML))
                else:
                    Polyrat2DDenominatorColorList.append(('rgb(211,211,211)', i, self.X2DList[i].HTML))
            self.dictionaryToReturn['Polyrat2DDenominatorColorList'] = Polyrat2DDenominatorColorList
            if len(self.equation.solvedCoefficients) == len(self.equation.rationalNumeratorFlags) + len(self.equation.rationalDenominatorFlags):
                self.dictionaryToReturn['colorOffset'] = 'rgb(211,211,211)' # Offset Term NOT used
            else:
                self.dictionaryToReturn['colorOffset'] = 'rgb(255,255,255)' # Offset Term used
        else: # NOT coming from a function finder
            Polyrat2DNumeratorColorList = [] # Numerator
            for i in range(len(self.X2DList)):
                Polyrat2DNumeratorColorList.append(('rgb(211,211,211)', i, self.X2DList[i].HTML))
            self.dictionaryToReturn['Polyrat2DNumeratorColorList'] = Polyrat2DNumeratorColorList
            Polyrat2DDenominatorColorList = [] # Denominator
            for i in range(len(self.X2DList)):
                Polyrat2DDenominatorColorList.append(('rgb(211,211,211)', i, self.X2DList[i].HTML))
            self.dictionaryToReturn['Polyrat2DDenominatorColorList'] = Polyrat2DDenominatorColorList
            self.dictionaryToReturn['colorOffset'] = 'rgb(211,211,211)' # Offset Term
        FittingBaseClass.FittingBaseClass.SpecificEquationUnboundInterfaceCode(self, request)
