



import inspect, time, math, random, multiprocessing, os, sys, copy

import numpy, scipy, scipy.stats

from . import FittingBaseClass
import zunzun.forms
import zunzun.formConstants


sys.stdout = sys.stderr # wsgi cannot send to stdout, see http://code.google.com/p/modwsgi/wiki/DebuggingTechniques



class FitUserSelectablePolynomial(FittingBaseClass.FittingBaseClass):

    interfaceString = 'zunzun/equation_fit_interface.html'

    
    def SaveSpecificDataToSessionStore(self):
        self.SaveDictionaryOfItemsToSessionStore('data', {'dimensionality':self.dimensionality,
                                                          'equationName':self.inEquationName,
                                                          'equationFamilyName':self.inEquationFamilyName,
                                                          'solvedCoefficients':self.dataObject.equation.solvedCoefficients,
                                                          'fittingTarget':self.dataObject.equation.fittingTarget,
                                                          'xPolynomialOrder':self.dataObject.equation.xPolynomialOrder,
                                                          'yPolynomialOrder':self.dataObject.equation.yPolynomialOrder})


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)        
        s = FittingBaseClass.FittingBaseClass.TransferFormDataToDataObject(self, request)
        self.boundForm.equation.fittingTarget = self.boundForm.cleaned_data['fittingTarget']
        return s

        
    def SpecificEquationBoundInterfaceCode(self, request):
        if self.dimensionality == 2:
            self.boundForm['polynomialOrderX2D'].required = True # force form field validation
            if 'polynomialOrderX2D' in request.POST:
                self.boundForm.equation.xPolynomialOrder = int(request.POST['polynomialOrderX2D'])
                if self.boundForm.equation.xPolynomialOrder < 0:
                    self.boundForm.equation.xPolynomialOrder = 0
                if self.boundForm.equation.xPolynomialOrder > (len(zunzun.formConstants.polynomialOrder2DChoices) - 1):
                    self.boundForm.equation.xPolynomialOrder = len(zunzun.formConstants.polynomialOrder2DChoices) - 1
        else: # 3D
            self.boundForm['polynomialOrderX3D'].required = True # force form field validation
            self.boundForm['polynomialOrderY3D'].required = True # force form field validation
            if 'polynomialOrderX3D' in request.POST:
                self.boundForm.equation.xPolynomialOrder = int(request.POST['polynomialOrderX3D'])
                if self.boundForm.equation.xPolynomialOrder < 0:
                    self.boundForm.equation.xPolynomialOrder = 0
                if self.boundForm.equation.xPolynomialOrder > (len(zunzun.formConstants.polynomialOrder3DChoices) - 1):
                    self.boundForm.equation.xPolynomialOrder = len(fzunzun.ormConstants.polynomialOrder3DChoices) - 1
            if 'polynomialOrderY3D' in request.POST:
                self.boundForm.equation.yPolynomialOrder = int(request.POST['polynomialOrderY3D'])
                if self.boundForm.equation.yPolynomialOrder < 0:
                    self.boundForm.equation.yPolynomialOrder = 0
                if self.boundForm.equation.yPolynomialOrder > (len(zunzun.formConstants.polynomialOrder3DChoices) - 1):
                    self.boundForm.equation.yPolynomialOrder = len(zunzun.formConstants.polynomialOrder3DChoices) - 1


    def SpecificEquationUnboundInterfaceCode(self, request):
        if self.rank:
            self.equation.xPolynomialOrder = self.functionFinderResultsList[self.rank-1][6]
            if self.dimensionality == 2:
                self.unboundForm.fields['polynomialOrderX2D'].initial = str(self.equation.xPolynomialOrder)
            else:
                self.equation.yPolynomialOrder = self.functionFinderResultsList[self.rank-1][7]
                self.unboundForm.fields['polynomialOrderX3D'].initial = str(self.equation.xPolynomialOrder)
                self.unboundForm.fields['polynomialOrderY3D'].initial = str(self.equation.yPolynomialOrder)
        FittingBaseClass.FittingBaseClass.SpecificEquationUnboundInterfaceCode(self, request)
