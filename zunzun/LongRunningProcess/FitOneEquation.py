



import inspect, time, math, random, multiprocessing, os, sys, copy

import numpy, scipy, scipy.stats

from . import FittingBaseClass
import zunzun.forms


sys.stdout = sys.stderr # wsgi cannot send to stdout, see http://code.google.com/p/modwsgi/wiki/DebuggingTechniques



class FitOneEquation(FittingBaseClass.FittingBaseClass):

    interfaceString = 'zunzun/equation_fit_interface.html'

    
    def SaveSpecificDataToSessionStore(self):
        self.SaveDictionaryOfItemsToSessionStore('data', {'dimensionality':self.dimensionality,
                                                          'equationName':self.inEquationName,
                                                          'equationFamilyName':self.inEquationFamilyName,
                                                          'solvedCoefficients':self.dataObject.equation.solvedCoefficients,
                                                          'fittingTarget':self.dataObject.equation.fittingTarget})


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)
        s = FittingBaseClass.FittingBaseClass.TransferFormDataToDataObject(self, request)
        self.boundForm.equation.fittingTarget = self.boundForm.cleaned_data['fittingTarget']
        return s


