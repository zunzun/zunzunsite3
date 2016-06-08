import inspect, time, math, random, multiprocessing

import numpy, scipy, scipy.stats

from django.template.loader import render_to_string

from . import FittingBaseClass
import zunzun.forms



class FitSpline(FittingBaseClass.FittingBaseClass):

    interfaceString = 'zunzun/equation_fit_interface.html'
    spline = True

    
    def SaveSpecificDataToSessionStore(self):
        self.SaveDictionaryOfItemsToSessionStore('data', {'dimensionality':self.dimensionality,
                                                          'equationName':self.inEquationName,
                                                          'equationFamilyName':self.inEquationFamilyName,
                                                          'scipySpline':self.dataObject.equation.scipySpline,
                                                          'solvedCoefficients':self.dataObject.equation.solvedCoefficients})


    def SpecificEquationBoundInterfaceCode(self, request):
        self.boundForm['fittingTarget'].required = False # not used in splines
        self.boundForm['splineSmoothness'].required = True # force form field validation
        self.boundForm['splineOrderX'].required = True # force form field validation
        if self.dimensionality == 3:
            self.boundForm['splineOrderY'].required = True # force form field validation
        
        
    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)
        s = FittingBaseClass.FittingBaseClass.TransferFormDataToDataObject(self, request)

        self.boundForm.equation.smoothingFactor = self.boundForm.cleaned_data['splineSmoothness']
        self.boundForm.equation.xOrder = int(self.boundForm.cleaned_data['splineOrderX'])
        if self.dimensionality == 3:
            self.boundForm.equation.yOrder = int(self.boundForm.cleaned_data['splineOrderY'])
        return s