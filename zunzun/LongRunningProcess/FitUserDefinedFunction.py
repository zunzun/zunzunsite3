import inspect, time, math, random, multiprocessing, os, sys, copy

import numpy, scipy, scipy.stats

import settings
from django.template.loader import render_to_string

from . import FittingBaseClass
from . import ReportsAndGraphs

import zunzun.forms
import pyeq3



sys.stdout = sys.stderr # wsgi cannot send to stdout, see http://code.google.com/p/modwsgi/wiki/DebuggingTechniques



class FitUserDefinedFunction(FittingBaseClass.FittingBaseClass):

    interfaceString = 'zunzun/equation_fit_interface.html'
    userDefinedFunction = True
    reniceLevel = 15

    
    def SaveSpecificDataToSessionStore(self):
        self.SaveDictionaryOfItemsToSessionStore('data', {'dimensionality':self.dimensionality,
                                                          'equationName':self.inEquationName,
                                                          'equationFamilyName':self.inEquationFamilyName,
                                                          'solvedCoefficients':self.dataObject.equation.solvedCoefficients,
                                                          'udfEditor_' + str(self.dimensionality) + 'D':self.dataObject.equation.userDefinedFunctionText})


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)
        s = FittingBaseClass.FittingBaseClass.TransferFormDataToDataObject(self, request)
        self.boundForm.equation.fittingTarget = self.boundForm.cleaned_data['fittingTarget']
        return s


    def SpecificEquationUnboundInterfaceCode(self, request):
        self.unboundForm.fields['udfEditor'].initial = eval('zunzun.formConstants.initialUserDefinedFunctionText' + str(self.dimensionality) + 'D')
        if self.dimensionality == 2:
            self.dictionaryToReturn['udfFunctionsDict'] = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction.functionDictionary
        else:
            self.dictionaryToReturn['udfFunctionsDict'] = pyeq3.Models_3D.UserDefinedFunction.UserDefinedFunction.functionDictionary


    def SpecificEquationBoundInterfaceCode(self, request):
        self.boundForm.equation.userDefinedFunctionText = request.POST['udfEditor']
        self.boundForm.equation.ParseAndCompileUserFunctionString(self.boundForm.equation.userDefinedFunctionText)

        
    def SpecificCodeForGeneratingListOfOutputReports(self):
        self.functionString = 'PrepareForReportOutput'
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Calculating Error Statistics"})
        try:
            self.dataObject.CalculateErrorStatistics()
        except:
            itemsToRender = {}
            itemsToRender['error0'] = str(sys.exc_info()[0])
            itemsToRender['error1'] = str(sys.exc_info()[1])
            itemsToRender['extraText'] = 'Please check the text of your User Defined Function.'
            f = open(os.path.join(settings.TEMP_FILES_DIR, self.dataObject.uniqueString + ".html"), "w")
            f.write(render_to_string('zunzun/exception_while_fitting_an_equation.html', itemsToRender))
            self.SaveDictionaryOfItemsToSessionStore('status', {'redirectToResultsFileOrURL':os.path.join(settings.TEMP_FILES_DIR, self.dataObject.uniqueString + ".html")})
            import time
            time.sleep(1.0)
            if self.pool:
                self.pool.close()
                self.pool.join()
                self.pool = None
            os._exit(0)

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Calculating Parameter Statistics"})
        self.dataObject.equation.CalculateCoefficientAndFitStatistics()

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating Report Objects"})
        self.ReportsAndGraphsCategoryDict = ReportsAndGraphs.FittingReportsDict(self.dataObject)
