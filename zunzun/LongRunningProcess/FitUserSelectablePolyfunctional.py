



import inspect, time, math, random, multiprocessing, os, sys, copy

import numpy, scipy, scipy.stats

from . import FittingBaseClass
import zunzun.forms
import zunzun.formConstants
import pyeq3

sys.stdout = sys.stderr # wsgi cannot send to stdout, see http://code.google.com/p/modwsgi/wiki/DebuggingTechniques



class FitUserSelectablePolyfunctional(FittingBaseClass.FittingBaseClass):

    interfaceString = 'zunzun/equation_fit_interface.html'
    X2DList = pyeq3.PolyFunctions.GenerateListForPolyfunctionals_2D()
    X3DList = pyeq3.PolyFunctions.GenerateListForPolyfunctionals_3D_X()
    Y3DList = pyeq3.PolyFunctions.GenerateListForPolyfunctionals_3D_Y()        

    
    def SaveSpecificDataToSessionStore(self):
        self.SaveDictionaryOfItemsToSessionStore('data', {'dimensionality':self.dimensionality,
                                                          'equationName':self.inEquationName,
                                                          'equationFamilyName':self.inEquationFamilyName,
                                                          'solvedCoefficients':self.dataObject.equation.solvedCoefficients,
                                                          'fittingTarget':self.dataObject.equation.fittingTarget,
                                                          'polyfunctional2DFlags':self.dataObject.equation.polyfunctional2DFlags,
                                                          'polyfunctional3DFlags':self.dataObject.equation.polyfunctional3DFlags})


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)        
        s = FittingBaseClass.FittingBaseClass.TransferFormDataToDataObject(self, request)
        self.boundForm.equation.fittingTarget = self.boundForm.cleaned_data['fittingTarget']
        return s

        
    def SpecificEquationBoundInterfaceCode(self, request):
        self.boundForm.equation.polyfunctional2DFlags = []
        self.boundForm.equation.polyfunctional3DFlags = []
        
        if self.dimensionality == 2:
            for i in range(len(self.X2DList)):
                self.boundForm['polyFunctional_X' + str(i)].required = True # force form field validation
                if request.POST['polyFunctional_X' + str(i)] == 'True':
                    self.boundForm.equation.polyfunctional2DFlags.append(i)
        else: # 3D
            for i in range(len(self.X3DList)):
                for j in range(len(self.Y3DList)):
                    self.boundForm['polyFunctional_X' + str(i) + 'Y' + str(j)].required = True # force form field validation
                    if request.POST['polyFunctional_X' + str(i) + 'Y' + str(j)] == 'True':
                        self.boundForm.equation.polyfunctional3DFlags.append([i, j])


    def SpecificEquationUnboundInterfaceCode(self, request):
                
        if self.rank:
            self.equation.polyfunctional2DFlags = self.functionFinderResultsList[self.rank-1][4]
            self.equation.polyfunctional3DFlags = self.functionFinderResultsList[self.rank-1][5]
            if self.dimensionality == 2:
                Polyfun2DColorList = []
                for i in range(len(self.X2DList)):
                    if i in self.functionFinderResultsList[self.rank-1][4]:
                        Polyfun2DColorList.append(('rgb(255,255,255)', i, self.X2DList[i].HTML))
                    else:
                        Polyfun2DColorList.append(('rgb(211,211,211)', i, self.X2DList[i].HTML))
                self.dictionaryToReturn['Polyfun2DColorList'] = Polyfun2DColorList
            else: # 3D
                Polyfun3DColorList = []
                for i in range(len(self.X3DList)):
                    for j in range(len(self.Y3DList)):
                        if [i,j] in self.functionFinderResultsList[self.rank-1][5]:
                            if i == 0 and j == 0:
                                Polyfun3DColorList.append(('rgb(255,255,255)', i, j, 'Offset', ''))
                            elif i > 0 and j == 0:
                                Polyfun3DColorList.append(('rgb(255,255,255)', i, j, self.X3DList[i].HTML, ''))
                            elif i == 0 and j > 0:
                                Polyfun3DColorList.append(('rgb(255,255,255)', i, j, '', self.Y3DList[j].HTML))
                            else:
                                Polyfun3DColorList.append(('rgb(255,255,255)', i, j, self.X3DList[i].HTML, self.Y3DList[j].HTML))
                        else:
                            if i == 0 and j == 0:
                                Polyfun3DColorList.append(('rgb(211,211,211)', i, j, 'Offset', ''))
                            elif i > 0 and j == 0:
                                Polyfun3DColorList.append(('rgb(211,211,211)', i, j, self.X3DList[i].HTML, ''))
                            elif i == 0 and j > 0:
                                Polyfun3DColorList.append(('rgb(211,211,211)', i, j, '', self.Y3DList[j].HTML))
                            else:
                                Polyfun3DColorList.append(('rgb(211,211,211)', i, j, self.X3DList[i].HTML, self.Y3DList[j].HTML))
                    self.dictionaryToReturn['Polyfun3DColorList'] = Polyfun3DColorList
        else:
            if self.dimensionality == 2:
                Polyfun2DColorList = []
                for i in range(len(self.X2DList)):
                    Polyfun2DColorList.append(('rgb(211,211,211)', i, self.X2DList[i].HTML))
                self.dictionaryToReturn['Polyfun2DColorList'] = Polyfun2DColorList
            else: # 3D
                Polyfun3DColorList = []
                for i in range(len(self.X3DList)):
                    for j in range(len(self.Y3DList)):
                        if i == 0 and j == 0:
                            Polyfun3DColorList.append(('rgb(211,211,211)', i, j, 'Offset', ''))
                        elif i > 0 and j == 0:
                            Polyfun3DColorList.append(('rgb(211,211,211)', i, j, self.X3DList[i].HTML, ''))
                        elif i == 0 and j > 0:
                            Polyfun3DColorList.append(('rgb(211,211,211)', i, j, '', self.Y3DList[j].HTML))
                        else:
                            Polyfun3DColorList.append(('rgb(211,211,211)', i, j, self.X3DList[i].HTML, self.Y3DList[j].HTML))
                self.dictionaryToReturn['Polyfun3DColorList'] = Polyfun3DColorList
        FittingBaseClass.FittingBaseClass.SpecificEquationUnboundInterfaceCode(self, request)
