import os, sys, time, math, copy
from . import MatplotlibGraphs_2D
import numpy, scipy
import pyeq3
import uuid
import settings



class Report(object):

    def __init__(self, dataObject):
        self.dataObject = dataObject
        self.stringList = []
        self.name= ""
        self.uuid = uuid.uuid4()


    def PrepareForReportOutput(self):
        self.PrepareForCharacterizerOutput()

    def PrepareForCharacterizerOutput(self):
        pass

    def CreateReportOutput(self):
        self.CreateCharacterizerOutput()


class TextOnlyReport(Report):

    def __init__(self, dataObject):
        Report.__init__(self, dataObject)

    def AddOneStatisticToStringList(self, label, selection, prefaceList):
        if prefaceList[0] + selection in self.dataObject.statistics:
            temp1 = "%- E" % self.dataObject.statistics[prefaceList[0] + selection]
            if len(temp1) < 14:
                temp1 += " "
        else:
            temp1 = "     n/a      "
        if len(prefaceList) > 1 and prefaceList[1] + selection in self.dataObject.statistics:
            temp2 = "%- E" % self.dataObject.statistics[prefaceList[1] + selection]
            if len(temp2) < 14:
                temp2 += " "
        else:
            temp2 = "     n/a      "
        if len(prefaceList) > 2 and  prefaceList[2] + selection in self.dataObject.statistics:
            temp3 = "%- E" % self.dataObject.statistics[prefaceList[2] + selection]
            if len(temp3) < 14:
                temp3 += " "
        else:
            temp3 = "     n/a      "

        if len(prefaceList) == 1:
            self.stringList.append("  " + label + temp1)
        if len(prefaceList) == 2:
            self.stringList.append("  " + label + temp1 + "    " + temp2)
        if len(prefaceList) == 3:
            self.stringList.append("  " + label + temp1 + "    " + temp2 + "    " + temp3)

    def AddStatisticsToStringList(self, prefaceList):
        self.AddOneStatisticToStringList("Minimum:             ", "_min", prefaceList)
        self.AddOneStatisticToStringList("Maximum:             ", "_max", prefaceList)
        self.AddOneStatisticToStringList("Mean:                ", "_mean", prefaceList)
        self.AddOneStatisticToStringList("Std. Error of Mean:  ", "_sem", prefaceList)
        self.AddOneStatisticToStringList("Median:              ", "_median", prefaceList)
        self.AddOneStatisticToStringList("Variance:            ", "_var", prefaceList)
        self.AddOneStatisticToStringList("Standard Deviation:  ", "_std", prefaceList)
        self.AddOneStatisticToStringList("Skew:                ", "_skew", prefaceList)
        self.AddOneStatisticToStringList("Kurtosis:            ", "_kurtosis", prefaceList)



# enter in Text Reports at bottom
class CodeReportCPP(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag:
            self.name= ""
            return
        self.name = "Source Code in C++"
        self.uniqueAnchorName = 'CppSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeCPP(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportFORTRAN90(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag or self.dataObject.equation.splineFlag:
            self.name= ""
            return
        self.name = "Source Code in Fortran90"
        self.uniqueAnchorName = 'Fortran90SourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeFORTRAN90(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportJAVA(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag:
            self.name= ""
            return
        self.name = "Source Code in Java"
        self.uniqueAnchorName = 'JavaSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeJAVA(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportJAVASCRIPT(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag:
            self.name= ""
            return
        self.name = "Source Code in JavaScript"
        self.uniqueAnchorName = 'JavaScriptSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeJAVASCRIPT(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportJULIA(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag or self.dataObject.equation.splineFlag:
            self.name= ""
            return
        self.name = "Source Code in Julia"
        self.uniqueAnchorName = 'JuliaSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeJULIA(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportPYTHON(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag:
            self.name= ""
            return
        self.name = "Source Code in Python"
        self.uniqueAnchorName = 'PythonSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodePYTHON(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportCSHARP(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag or self.dataObject.equation.splineFlag:
            self.name= ""
            return
        self.name = "Source Code in C#"
        self.uniqueAnchorName = 'CSSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeCSHARP(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportSCILAB(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag or self.dataObject.equation.splineFlag:
            self.name= ""
            return
        self.name = "Source Code in SCILAB"
        self.uniqueAnchorName = 'SCILABSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeSCILAB(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportMATLAB(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag or self.dataObject.equation.splineFlag:
            self.name= ""
            return
        self.name = "Source Code in MATLAB"
        self.uniqueAnchorName = 'MATLABSourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeMATLAB(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class CodeReportVBA(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.userDefinedFunctionFlag or self.dataObject.equation.splineFlag:
            self.name= ""
            return
        self.name = "Source Code in VBA"
        self.uniqueAnchorName = 'VBASourceCode'
        
    def CreateReportOutput(self):
        code = pyeq3.outputSourceCodeService().GetOutputSourceCodeVBA(self.dataObject.equation)
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            code = code.replace("Fitting target value =", "Fitting target value (weighted) = ")
        self.stringList.append('<textarea rows="24" cols="85" wrap="OFF">' +  code + '</textarea>')



# enter in Text Reports at bottom
class UserDefinedFunctionText(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if not self.dataObject.equation.userDefinedFunctionFlag:
            self.name= ""
            return
        self.name = "User Defined Function Text"
        self.uniqueAnchorName = "UserDefinedFunctionText"
        
    def CreateReportOutput(self):
        self.stringList.append(self.dataObject.equation.userDefinedFunctionText + '\n')



# enter in Text Reports at bottom
class CoefficientListing(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.splineFlag:
            self.name = "Coefficients And Knot Points"
        else:
            self.name = "Coefficients"
        self.uniqueAnchorName = "Coefficients"

        
    def CreateReportOutput(self):
        self.stringList.append(self.dataObject.equation.GetDisplayHTML() + '\n')
        
        if self.dataObject.equation.splineFlag:
            if self.dataObject.dimensionality == 2:
                coeffs = self.dataObject.equation.scipySpline._eval_args[1]
                xKnots = self.dataObject.equation.scipySpline._eval_args[0]
            else:
                coeffs = self.dataObject.equation.scipySpline.get_coeffs()
                xKnots = self.dataObject.equation.scipySpline.get_knots()[0]
                yKnots = self.dataObject.equation.scipySpline.get_knots()[1]
        else:
            coeffs = self.dataObject.equation.solvedCoefficients
            fittingTargetText = "Fitting target of lowest " + self.dataObject.equation.fittingTargetDictionary[self.dataObject.equation.fittingTarget]
            if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
                fittingTargetText += " (weighted)"
            self.stringList.append(fittingTargetText + " = %.16E" % (self.dataObject.equation.CalculateAllDataFittingTarget(self.dataObject.equation.solvedCoefficients)) + '\n')
            
        
        for i in range(len(coeffs)):
            if self.dataObject.equation.splineFlag:
                designator = 'coeff ' + str(i)
            else:
                designator = self.dataObject.equation.GetCoefficientDesignators()[i]
            if coeffs[i] < 0.0:
                self.stringList.append("%s = %-.16E" % (designator, coeffs[i]))
            else: # need a hard space if there is no negative sign
                self.stringList.append("%s =  %-.16E" % (designator, coeffs[i]))

        if self.dataObject.equation.splineFlag:
            self.stringList.append("<br>")
            if self.dataObject.dimensionality == 2:
                for i in range(len(xKnots)):
                    designator = 'knot point ' + str(i)
                    if xKnots[i] < 0.0:
                        self.stringList.append("%s = %-.16E" % (designator, xKnots[i]))
                    else: # need a hard space if there is no negative sign
                        self.stringList.append("%s =  %-.16E" % (designator, xKnots[i]))
            else:
                for i in range(len(xKnots)):
                    designator = 'X knot point ' + str(i)
                    if xKnots[i] < 0.0:
                        self.stringList.append("%s = %-.16E" % (designator, xKnots[i]))
                    else: # need a hard space if there is no negative sign
                        self.stringList.append("%s =  %-.16E" % (designator, xKnots[i]))
                        
                self.stringList.append("<br>")

                for i in range(len(yKnots)):
                    designator = 'Y knot point ' + str(i)
                    if yKnots[i] < 0.0:
                        self.stringList.append("%s = %-.16E" % (designator, yKnots[i]))
                    else: # need a hard space if there is no negative sign
                        self.stringList.append("%s =  %-.16E" % (designator, yKnots[i]))



# enter in Text Reports at bottom
class CoefficientAndFitStatistics(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.equation.splineFlag:
            self.name = "Fit Statistics"
        else:
            self.name = "Coefficient and Fit Statistics"
        self.uniqueAnchorName = 'CoeffAndFitStats'
        
    def CreateReportOutput(self):
        self.stringList.append('</pre>')
        
        self.stringList.append('Most statstics from scipy.odr.odrpack and http://www.scipy.org/Cookbook/OLS<br>')
        self.stringList.append('LL, AIC and BIC from http://stackoverflow.com/questions/7458391/python-multiple-linear-regression-using-ols-code-with-specific-data<br>')

        weightedString = ''
        if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
            weightedString = '_weighted'
            self.stringList.append('<br><b>Note:</b> These statistics use the weights supplied during the fit<br>')

        self.stringList.append('<br>')
        self.stringList.append('If you entered coefficient bounds. Parameter statistics may<br>')
        self.stringList.append('not be valid for parameter values at or near the bounds.<br>')
        self.stringList.append('<br>')

        self.stringList.append('<table style="font-family: monospace"><tr><td align="left"><br>')

        self.stringList.append('Degrees of freedom (error): ' + str(eval('self.dataObject.equation.df_e' + weightedString)) + '<br>')
        self.stringList.append('Degrees of freedom (regression): ' + str(eval('self.dataObject.equation.df_r' + weightedString)) + '<br>')
            
        if eval('self.dataObject.equation.sumOfSquaredErrors' + weightedString) == None:
            self.stringList.append('Chi-squared: n/a' + '<br>')
        else:
            self.stringList.append('Chi-squared: ' + str(eval('self.dataObject.equation.sumOfSquaredErrors' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.r2' + weightedString) == None:
            self.stringList.append('R-squared: n/a' + '<br>')
        else:
            self.stringList.append('R-squared: ' + str(eval('self.dataObject.equation.r2' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.r2adj' + weightedString) == None:
            self.stringList.append('R-squared adjusted: n/a' + '<br>')
        else:
            self.stringList.append('R-squared adjusted: ' + str(eval('self.dataObject.equation.r2adj' + weightedString)) + '<br>')

        if eval('self.dataObject. equation.Fstat' + weightedString) == None:
            self.stringList.append('Model F-statistic: n/a' + '<br>')
        else:
            self.stringList.append('Model F-statistic: ' + str(eval('self.dataObject.equation.Fstat' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.Fpv' + weightedString) == None:
            self.stringList.append('Model F-statistic p-value: n/a' + '<br>')
        else:
            self.stringList.append('Model F-statistic p-value: ' + str(eval('self.dataObject.equation.Fpv' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.ll' + weightedString) == None:
            self.stringList.append('Model log-likelihood: n/a' + '<br>')
        else:
            self.stringList.append('Model log-likelihood: ' + str(eval('self.dataObject.equation.ll' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.aic' + weightedString) == None:
            self.stringList.append('AIC: n/a' + '<br>')
        else:
            self.stringList.append('AIC: ' + str(eval('self.dataObject.equation.aic' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.bic' + weightedString)== None:
            self.stringList.append('BIC: n/a' + '<br>')
        else:
            self.stringList.append('BIC: ' + str(eval('self.dataObject.equation.bic' + weightedString)) + '<br>')

        if eval('self.dataObject.equation.rmse' + weightedString) == None:
            self.stringList.append('Root Mean Squared Error (RMSE): n/a' + '<br>')
        else:
            self.stringList.append('Root Mean Squared Error (RMSE): ' + str(eval('self.dataObject.equation.rmse' + weightedString)) + '<br>')

        self.stringList.append('\n' + '<br>')
        
        if self.dataObject.equation.splineFlag:
            self.stringList.append('</td></tr></table>\n')
            self.stringList.append('<pre>')
            return
            
        for i in range(len(self.dataObject.equation.solvedCoefficients)):
            if str(eval('self.dataObject.equation.tstat_beta' + weightedString)) == 'None':
                tstat = 'n/a'
            else:
                tstat = '%-.5E' %  (eval('self.dataObject.equation.tstat_beta' + weightedString)[i])

            if str(eval('self.dataObject.equation.pstat_beta' + weightedString)) == 'None':
                pstat = 'n/a'
            else:
                pstat = '%-.5E' %  (eval('self.dataObject.equation.pstat_beta' + weightedString)[i])

            self.stringList.append("%s = %-.16E" % (self.dataObject.equation.GetCoefficientDesignators()[i], self.dataObject.equation.solvedCoefficients[i]) + '<br>')
            try:
                self.stringList.append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; std err: %-.5E" % (eval('self.dataObject.equation.sd_beta' + weightedString)[i]) + '<br>')
            except:
                self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; std err: n/a<br>')
            self.stringList.append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; t-stat: " + tstat + '<br>')
            self.stringList.append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; p-stat: " + pstat + '<br>')
            self.stringList.append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 95% confidence intervals:" + ' [%-.5E, %-.5E]' % (eval('self.dataObject.equation.ci' + weightedString)[i][0], eval('self.dataObject.equation.ci' + weightedString)[i][1]) + '<br>')

        self.stringList.append('\n' + '<br>')
        self.stringList.append("Coefficient Covariance Matrix" + '<br>')
        for i in eval('self.dataObject.equation.cov_beta' + weightedString):
            self.stringList.append(str(i) + '<br>')
        self.stringList.append('</td></tr></table>\n')
        self.stringList.append('<pre>')



# enter in Text Reports at bottom
class ErrorListing(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        self.name = "Error Listing"
        self.uniqueAnchorName = "ErrorListing"
        
    def CreateReportOutput(self):
        datalen = len(self.dataObject.equation.dataCache.allDataCacheDictionary['DependentData'])

        # determine number of digits of precision for display
        dopIndep1 = 10
        dopIndep2 = 10
        dopDep = 10
        
        breakLoop = False
        for i in reversed(list(range(dopIndep1))):
            if breakLoop == True:
                break
            for j in range(datalen): # number of data points
                datapoint = self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][0][j]
                if float(('% .' + str(i+1) + 'E') % (datapoint)) != float(('% .' + str(i) + 'E') % (datapoint)):
                    dopIndep1 = i+1
                    breakLoop = True
                    break
        
        breakLoop = False
        for i in reversed(list(range(dopDep))):
            if breakLoop == True:
                break
            for j in range(datalen): # number of data points
                datapoint = self.dataObject.equation.dataCache.allDataCacheDictionary['DependentData'][j]
                if float(('% .' + str(i+1) + 'E') % (datapoint)) != float(('% .' + str(i) + 'E') % (datapoint)):
                    dopDep = i+1
                    breakLoop = True
                    break
                    
        if self.dataObject.dimensionality == 3:
            breakLoop = False
            for i in reversed(list(range(dopIndep2))):
                if breakLoop == True:
                    break
                for j in range(datalen): # number of data points
                    datapoint = self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][1][j]
                    if float(('% .' + str(i+1) + 'E') % (datapoint)) != float(('% .' + str(i) + 'E') % (datapoint)):
                        dopIndep2 = i+1
                        breakLoop = True
                        break
        
        # now create report
        self.stringList.append("<table>")

        if self.dataObject.dimensionality == 2:
            self.stringList.append("<tr><td align=center> Independent Data </td><td align=center> Dependent Data </td><td align=center> Predicted </td><td align=center> Abs Error </td><td align=center> Rel Error </td></tr>")
            if str(self.dataObject.equation.modelRelativeError) == 'None':
                for i in range(datalen): # number of data points
                    tempString = "<tr><td align=center> % ." + str(dopIndep1) + "E </td><td align=center> % ." + str(dopDep) + "E </td><td align=center> % .10E </td><td align=center> % .6E </td><td align=center> n/a </td></tr>"
                    self.stringList.append(tempString % (self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][0][i], self.dataObject.equation.dataCache.allDataCacheDictionary['DependentData'][i], self.dataObject.equation.modelPredictions[i], self.dataObject.equation.modelAbsoluteError[i]))
            else:
                for i in range(datalen): # number of data points
                    tempString = "<tr><td align=center> % ." + str(dopIndep1) + "E </td><td align=center> % ." + str(dopDep) + "E </td><td align=center> % .10E </td><td align=center> % .6E </td><td align=center> % .6E </td></tr>"
                    self.stringList.append(tempString % (self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][0][i], self.dataObject.equation.dataCache.allDataCacheDictionary['DependentData'][i], self.dataObject.equation.modelPredictions[i], self.dataObject.equation.modelAbsoluteError[i], self.dataObject.equation.modelRelativeError[i]))
        else:
            self.stringList.append("<tr><td align=center> Indep. Data 1 </td><td align=center> Indep. Data 2 </td><td align=center> Dependent Data </td><td align=center> Predicted </td><td align=center> Abs Error </td><td align=center> Rel Error <td></tr>")
            if str(self.dataObject.equation.modelRelativeError) == 'None':
                for i in range(datalen): # number of data points
                    tempString = "<tr><td align=center> % ." + str(dopIndep1) + "E </td><td align=center> % ." + str(dopIndep2) + "E </td><td align=center> % ." + str(dopDep) + "E </td><td align=center> % .10E </td><td align=center> % .6E </td><td align=center> n/a </td></tr>"
                    self.stringList.append(tempString % (self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][0][i], self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][1][i], self.dataObject.equation.dataCache.allDataCacheDictionary['DependentData'][i], self.dataObject.equation.modelPredictions[i], self.dataObject.equation.modelAbsoluteError[i]))
            else:
                for i in range(datalen): # number of data points
                    tempString = "<tr><td align=center> % ." + str(dopIndep1) + "E </td><td align=center> % ." + str(dopIndep2) + "E </td><td align=center> % ." + str(dopDep) + "E </td><td align=center> % .10E </td><td align=center> % .6E </td><td align=center> % .6E </td></tr>"
                    self.stringList.append(tempString % (self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][0][i], self.dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'][1][i], self.dataObject.equation.dataCache.allDataCacheDictionary['DependentData'][i], self.dataObject.equation.modelPredictions[i], self.dataObject.equation.modelAbsoluteError[i], self.dataObject.equation.modelRelativeError[i]))

        self.stringList.append("</table>")



# enter in Text Reports at bottom
class StatisticsListing(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        self.name = "Error Statistics"
        self.uniqueAnchorName = 'ErrorStatistics'

    def CreateReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 0:
            self.stringList.append("                      Absolute Error     Relative Error\n")
            self.AddStatisticsToStringList(["abs_err", "rel_err"])
        else:
            self.stringList.append("NOTE: Relative error statistics cannot be compiled, as at least one of")
            self.stringList.append("the dependent variable data points contains a value of exactly zero.\n")
            self.stringList.append("                   Absolute Error\n")
            self.AddStatisticsToStringList(["abs_err"])



# enter in Text Reports at bottom
class CharacterizerStatisticsListing(TextOnlyReport):

    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)

    def PrepareForCharacterizerOutput(self):
        self.name = "Data Statistics"
        self.uniqueAnchorName = "DataStatistics"

    def CreateCharacterizerOutput(self):
        if self.dataObject.dimensionality == 1:
            self.stringList.append("                             X\n")
            self.AddStatisticsToStringList(["1"])

        if self.dataObject.dimensionality == 2:
            self.stringList.append("                             X                Y\n")
            self.AddStatisticsToStringList(["1", "2"])

        if self.dataObject.dimensionality == 3:
            self.stringList.append("                             X                 Y               Z\n")
            self.AddStatisticsToStringList(["1", "2", "3"])



# enter in Text Reports at bottom
class StatisticalDistributions(TextOnlyReport):
    def __init__(self, dataObject):
        TextOnlyReport.__init__(self, dataObject)


    def PrepareForCharacterizerOutput(self):

        self.numberOfFittedDistributions = len(self.dataObject.fittedStatisticalDistributionsList)
        if self.numberOfFittedDistributions == 0:
            return

        self.name = self.dataObject.IndependentDataName1 + " Top " + str(self.numberOfFittedDistributions) + " Statistical Distributions"
        self.uniqueAnchorName = "XStatDist"


    def CreateCharacterizerOutput(self):
        self.stringList.append('</pre><table style="font-family: monospace"><tr><td align="left">')
        
        # these are also in the graph reports
        rank = 1
        for i in self.dataObject.fittedStatisticalDistributionsList:
            self.stringList.append("<b>Rank " + str(rank) + ": " + i[1]['distributionLongName'] + ' distribution</b><BR>')
            rank += 1
            self.stringList.append('http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.' + i[1]['distributionName'] + '.html<br>')
            
            self.stringList.append('<br>')
            
            self.stringList.append("Fit Statistics for " + str(len(self.dataObject.IndependentDataArray[0])) + " data points:<br>")
            self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "Negative Two Log Likelihood = %-.16E<br>" % (2.0 * i[1]['nnlf']))
            if numpy.isfinite(i[1]['AIC']):
                self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AIC = %-.16E<br>" % (i[1]['AIC']))
            else:
                self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AIC = N/A<br>")
            if numpy.isfinite(i[1]['AICc_BA']):
                self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AICc (Burnham and Anderson) = %-.16E<br>" % (i[1]['AICc_BA']))
            else:
                self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AICc (Burnham and Anderson) = N/A<br>")
            
            self.stringList.append('<br><br>')
            
            self.stringList.append('Parameters:<BR>')
            for parmIndex in range(len(i[1]['parameterNames'])):
                self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + i[1]['parameterNames'][parmIndex] + ' = %-.16E' % (i[1]['fittedParameters'][parmIndex]) + "<BR>")
                
            self.stringList.append('<br>')

            self.stringList.append('Additional Information:')
            for infoString in i[1]['additionalInfo']:
                self.stringList.append(infoString.replace(' ', '&nbsp;') + '<BR>')

            self.stringList.append('<BR><BR><BR>')
        self.stringList.append('</td></tr></table><pre>')



class GraphReport(Report):

    def __init__(self, dataObject):
        Report.__init__(self, dataObject)
        self.DataGraph = 0
        self.HistogramFlag = 0
        self.StatisticsGraph = 1
        self.RequiresRelativeError = 0
        self.animationFlag = 0
        self.animationFrameSeparation = 2 # angular distance between animation frames
        self.rank = '' # function finders use rank to distinguish different graph reports
        
        
    def GetRankString(self):
        if self.rank:
            return "_" + str(self.rank)
        return ''


    
# enter in Graph Reports at bottom
class AbsoluteErrorHistogram(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.HistogramFlag = 1

    def PrepareForReportOutput(self):
        self.name = "Histogram of Absolute Error"
        self.uniqueAnchorName = "AbsErrHist"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateReportOutput(self):        
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject, self.physicalFileLocation, "Absolute Error", self.dataObject.equation.modelAbsoluteError)



# enter in Graph Reports at bottom
class RelativeErrorHistogram(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1
        self.HistogramFlag = 1

    def PrepareForReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            self.name= ""
            return
        self.name = "Histogram of Relative Error"
        self.uniqueAnchorName = "RelErrHist"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateReportOutput(self):
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject, self.physicalFileLocation, "Relative Error", self.dataObject.equation.modelRelativeError)



# enter in Graph Reports at bottom
class PercentErrorHistogram(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1
        self.HistogramFlag = 1

    def PrepareForReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            self.name = "" # used as a 'do not create' flag
            return
        self.name = "Histogram of Percent Error"
        self.uniqueAnchorName = "PerErrHist"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateReportOutput(self):
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject, self.physicalFileLocation, "Percent Error", self.dataObject.equation.modelPercentError)



# enter in Graph Reports at bottom
class Data1Histogram(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.HistogramFlag = 1

    def PrepareForCharacterizerOutput(self):
        self.name = "Histogram of " + self.dataObject.IndependentDataName1
        self.uniqueAnchorName = "XDataHist"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject, self.physicalFileLocation, self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0])



# enter in Graph Reports at bottom
class Data2Histogram(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.HistogramFlag = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = "Histogram of " + self.dataObject.IndependentDataName2
        self.uniqueAnchorName = "YDataHist"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject, self.physicalFileLocation, self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1])



# enter in Graph Reports at bottom
class DependentDataHistogram(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.HistogramFlag = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality == 1:
            return
        if self.dataObject.dimensionality == 2:
            self.uniqueAnchorName = "YDataHist"
        else:
            self.uniqueAnchorName = "ZDataHist"
        self.name = "Histogram of " + self.dataObject.DependentDataName
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject, self.physicalFileLocation, self.dataObject.DependentDataName, self.dataObject.DependentDataArray)



# enter in Graph Reports at bottom
class AbsoluteErrorVsDependentData_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        self.name = "Absolute Error vs. " + self.dataObject.DependentDataName
        self.uniqueAnchorName = "AbsErrVsDepData"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinXAxis = self.dataObject.LogLinY
        else:
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinXAxis = self.dataObject.LogLinZ
            
    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray,  self.ScientificNotationXAxis,
                                      "Absolute Error",  self.dataObject.equation.modelAbsoluteError,  "AUTO",
                                      0, "", "",
                                      'LIN', self.LogLinXAxis)



# enter in Graph Reports at bottom
class AbsoluteErrorVsIndependentData1_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        self.name = "Absolute Error vs. " + self.dataObject.IndependentDataName1
        self.uniqueAnchorName = "AbsErrVsIndepData1"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      "Absolute Error", self.dataObject.equation.modelAbsoluteError, "AUTO",
                                      0, "", "",
                                      'LIN', self.dataObject.LogLinX)



# enter in Graph Reports at bottom
class AbsoluteErrorVsIndependentData2_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)

    def PrepareForReportOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        self.name = "Absolute Error vs. " + self.dataObject.IndependentDataName2
        self.uniqueAnchorName = "AbsErrVsIndepData2"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      "Absolute Error", self.dataObject.equation.modelAbsoluteError, "AUTO",
                                      0, "", "",
                                      'LIN', self.dataObject.LogLinY)



# enter in Graph Reports at bottom
class RelativeErrorVsDependentData_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            return
        self.name = "Relative Error vs. " + self.dataObject.DependentDataName
        self.uniqueAnchorName = "RelErrVsDepData"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinXAxis = self.dataObject.LogLinY
        else:
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinXAxis = self.dataObject.LogLinZ

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray, self.ScientificNotationXAxis,
                                      "Relative Error", self.dataObject.equation.modelRelativeError, "AUTO",
                                      0, "", "",
                                      'LIN', self.LogLinXAxis)



# enter in Graph Reports at bottom
class PercentErrorVsDependentData_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            return
        self.name = "Percent Error vs. " + self.dataObject.DependentDataName
        self.uniqueAnchorName = "PerErrVsDepData"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinXAxis = self.dataObject.LogLinY
        else:
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinXAxis = self.dataObject.LogLinZ

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray, self.ScientificNotationXAxis,
                                      "Percent Error", self.dataObject.equation.modelPercentError, "AUTO",
                                      0, "", "",
                                      'LIN', self.LogLinXAxis)



# enter in Graph Reports at bottom
class RelativeErrorVsIndependentData1_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            return
        self.name = "Relative Error vs. " + self.dataObject.IndependentDataName1
        self.uniqueAnchorName = "RelErrVsIndepData1"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      "Relative Error", self.dataObject.equation.modelRelativeError, "AUTO",
                                      0, "", "",
                                      'LIN', self.dataObject.LogLinX)



# enter in Graph Reports at bottom
class PercentErrorVsIndependentData1_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForReportOutput(self):
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            return
        self.name = "Percent Error vs. " + self.dataObject.IndependentDataName1
        self.uniqueAnchorName = "PerErrVsIndepData1"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      "Percent Error", self.dataObject.equation.modelPercentError, "AUTO",
                                      0, "", "",
                                      'LIN', self.dataObject.LogLinX)



# enter in Graph Reports at bottom
class RelativeErrorVsIndependentData2_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForReportOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            return
        self.name = "Relative Error vs. " + self.dataObject.IndependentDataName2
        self.uniqueAnchorName = "RelErrVsIndepData2"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      "Relative Error", self.dataObject.equation.modelRelativeError, "AUTO",
                                      0, "", "",
                                      'LIN', self.dataObject.LogLinY)



# enter in Graph Reports at bottom
class PercentErrorVsIndependentData2_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForReportOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            return
        self.name = "Percent Error vs. " + self.dataObject.IndependentDataName2
        self.uniqueAnchorName = "PerErrVsIndepData2"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      "Percent Error", self.dataObject.equation.modelPercentError, "AUTO",
                                      0, "", "",
                                      'LIN', self.dataObject.LogLinY)



# enter in Graph Reports at bottom
class DependentDataVsIndependentData1_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality == 1:
            return
        self.name = self.dataObject.DependentDataName + " vs. " + self.dataObject.IndependentDataName1
        self.uniqueAnchorName = "DepDataVsIndepData1"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.YorZ = 'Y'
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinYAxis = self.dataObject.LogLinY
        else:
            self.YorZ = 'Z'
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinYAxis = self.dataObject.LogLinZ

    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray, self.ScientificNotationXAxis,
                                      1, 'X', self.YorZ,
                                      self.LogLinYAxis, self.dataObject.LogLinX)


# enter in Graph Reports at bottom
class DependentDataVsIndependentData1_ModelPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForReportOutput(self):
        
        self.name = self.dataObject.DependentDataName + " vs. " + self.dataObject.IndependentDataName1
        if self.dataObject.dimensionality == 2:
            self.name += ' with model'
        else:
            self.name = ''
        self.uniqueAnchorName = "DepDataVsIndepData1_modelplot"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.YorZ = 'Y'
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinYAxis = self.dataObject.LogLinY
        else:
            self.YorZ = 'Z'
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinYAxis = self.dataObject.LogLinZ

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ModelAndScatterPlot(self.dataObject, self.physicalFileLocation,
                                          self.dataObject.IndependentDataName1,
                                          self.dataObject.DependentDataName,
                                          0,
                                          self.LogLinYAxis, self.dataObject.LogLinX,
                                          False)


# enter in Graph Reports at bottom
class DependentDataVsIndependentData1_ConfidenceIntervals(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForReportOutput(self):
        self.name = self.dataObject.DependentDataName + " vs. " + self.dataObject.IndependentDataName1
        if self.dataObject.dimensionality == 2:
            if len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']):
                self.name += ' with 95% confidence intervals (weighted)'
            else:
                self.name += ' with 95% confidence intervals'
        else:
            self.name = ''
        self.uniqueAnchorName = "DepDataVsIndepData1_ci"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.YorZ = 'Y'
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinYAxis = self.dataObject.LogLinY
        else:
            self.YorZ = 'Z'
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinYAxis = self.dataObject.LogLinZ

    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ModelAndScatterPlot(self.dataObject, self.physicalFileLocation,
                                          self.dataObject.IndependentDataName1,
                                          self.dataObject.DependentDataName,
                                          0,
                                          self.LogLinYAxis, self.dataObject.LogLinX,
                                          True)


# enter in Graph Reports at bottom
class DependentDataVsIndependentData2_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = self.dataObject.DependentDataName + " vs. " + self.dataObject.IndependentDataName2
        self.uniqueAnchorName = "DepDataVsIndepData2"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray, self.dataObject.ScientificNotationZ,
                                      1, "Y", "Z",
                                      self.dataObject.LogLinZ, self.dataObject.LogLinY)


# enter in Graph Reports at bottom
class IndependentData1VsDependentData_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality == 1:
            return
        self.name = self.dataObject.IndependentDataName1 + " vs. " + self.dataObject.DependentDataName
        self.uniqueAnchorName = "IndepData1VsDepData"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        if self.dataObject.dimensionality == 2:
            self.YorZ = "Y"
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationY
            self.LogLinXAxis = self.dataObject.LogLinY
        else:
            self.YorZ = "Z"
            self.ScientificNotationXAxis = self.dataObject.ScientificNotationZ
            self.LogLinXAxis = self.dataObject.LogLinZ

    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray, self.ScientificNotationXAxis,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      1, self.YorZ, "X",
                                      self.dataObject.LogLinX, self.LogLinXAxis)


# enter in Graph Reports at bottom
class IndependentData1VsIndependentData2_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = self.dataObject.IndependentDataName1 + " vs. "  + self.dataObject.IndependentDataName2
        self.uniqueAnchorName = "IndepData1VsIndepData2"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      1, "Y", "X",
                                      self.dataObject.LogLinX, self.dataObject.LogLinY)


# enter in Graph Reports at bottom
class IndependentData2VsDependentData_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = self.dataObject.IndependentDataName2 + " vs. "  + self.dataObject.DependentDataName
        self.uniqueAnchorName = "IndepData2VsDepData"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.DependentDataName, self.dataObject.DependentDataArray, self.dataObject.ScientificNotationZ,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      1, "Z", "Y",
                                      self.dataObject.LogLinY, self.dataObject.LogLinZ)


# enter in Graph Reports at bottom
class IndependentData2VsIndependentData1_ScatterPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = self.dataObject.IndependentDataName2 + " vs. "  + self.dataObject.IndependentDataName1
        self.uniqueAnchorName = "IndepData2VsIndepData1"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"

    def CreateCharacterizerOutput(self):
        MatplotlibGraphs_2D.ScatterPlot(self.dataObject, self.physicalFileLocation,
                                      self.dataObject.IndependentDataName1, self.dataObject.IndependentDataArray[0], self.dataObject.ScientificNotationX,
                                      self.dataObject.IndependentDataName2, self.dataObject.IndependentDataArray[1], self.dataObject.ScientificNotationY,
                                      1, "X", "Y",
                                      self.dataObject.LogLinY, self.dataObject.LogLinX)


# enter in Graph Reports at bottom
class AbsErrScatterPlot3D(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)


    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = "Absolute Error Scatter Plot"
        self.uniqueAnchorName = "AbsErrScatterPlot3D"
        self.dataObject.ScientificNotationZ = 'AUTO'
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        dataObject = copy.copy(self.dataObject)
        dataObject.DependentDataName = "Absolute Error"
        dataObject.DependentDataArray = self.dataObject.equation.modelAbsoluteError
        dataObject.CalculateDataStatistics()
        self.Extrapolation_z = 0.05
        dataObject.CalculateGraphBoundaries()
        from . import MatplotlibGraphs_3D
        MatplotlibGraphs_3D.ScatterPlot3D(dataObject, self.physicalFileLocation)



# enter in Graph Reports at bottom
class RelErrScatterPlot3D(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1


    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            self.name= ""
            return
        self.name = "Relative Error Scatter Plot"
        self.uniqueAnchorName = "RelErrScatterPlot3D"
        self.dataObject.ScientificNotationZ = 'AUTO'
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        dataObject = copy.copy(self.dataObject)
        dataObject.DependentDataName = "Relative Error"
        dataObject.DependentDataArray = self.dataObject.equation.modelRelativeError
        dataObject.CalculateDataStatistics()
        self.Extrapolation_z = 0.05
        dataObject.CalculateGraphBoundaries()
        from . import MatplotlibGraphs_3D
        MatplotlibGraphs_3D.ScatterPlot3D(dataObject, self.physicalFileLocation)


# enter in Graph Reports at bottom
class PerErrScatterPlot3D(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.RequiresRelativeError = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        if self.dataObject.equation.dataCache.DependentDataContainsZeroFlag == 1:
            self.name= ""
            return
        self.name = "Percent Error Scatter Plot"
        self.uniqueAnchorName = "PerErrScatterPlot3D"
        self.dataObject.ScientificNotationZ = 'AUTO'
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        dataObject = copy.copy(self.dataObject)
        dataObject.DependentDataName = "Percent Error"
        dataObject.DependentDataArray = self.dataObject.equation.modelPercentError
        dataObject.CalculateDataStatistics()
        self.Extrapolation_z = 0.05
        dataObject.CalculateGraphBoundaries()
        from . import MatplotlibGraphs_3D
        MatplotlibGraphs_3D.ScatterPlot3D(dataObject, self.physicalFileLocation)


# enter in Graph Reports at bottom
class ScatterPlot3D(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.DataGraph = 1

    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality != 3:
            return
        self.name = "Scatter Plot"
        self.uniqueAnchorName = "ScatterPlot3D"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateCharacterizerOutput(self):
        from . import MatplotlibGraphs_3D
        MatplotlibGraphs_3D.ScatterPlot3D(self.dataObject, self.physicalFileLocation)



# enter in Graph Reports at bottom
class SurfacePlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0

    def PrepareForReportOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        self.name = "Surface Plot"
        self.uniqueAnchorName = "SurfacePlot"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateReportOutput(self):
        from . import MatplotlibGraphs_3D
        MatplotlibGraphs_3D.SurfacePlot(self.dataObject, self.physicalFileLocation)



# enter in Graph Reports at bottom
class ContourPlot(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0

    def PrepareForReportOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        self.name = "Contour Plot"
        self.uniqueAnchorName = "ContourPlot"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        
    def CreateReportOutput(self):
        MatplotlibGraphs_2D.ContourPlot(self.dataObject, self.physicalFileLocation)


# enter in Graph Reports at bottom
class StatisticalDistributionHistogram(GraphReport):

    def __init__(self, dataObject, distributionIndex):
        GraphReport.__init__(self, dataObject)
        self.HistogramFlag = 1
        self.distributionIndex = distributionIndex


    def PrepareForCharacterizerOutput(self):
        self.name= ""

        self.numberOfFittedDistributions = len(self.dataObject.fittedStatisticalDistributionsList)
        if self.numberOfFittedDistributions <= self.distributionIndex:
            return

        i = self.dataObject.fittedStatisticalDistributionsList[self.distributionIndex]

        # these are also in the text reports
        self.stringList.append('</pre><table style="font-family: monospace"><tr><td align="left">')
        self.stringList.append(i[1]['distributionLongName'] + ' distribution<BR>')
        self.stringList.append('http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.' + i[1]['distributionName'] + '.html<BR>')

        self.stringList.append('<br>')

        self.stringList.append("Fit Statistics for " + str(len(self.dataObject.IndependentDataArray[0])) + " data points:<br>")
        self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "Negative Two Log Likelihood = %-.16E<br>" % (2.0 * i[1]['nnlf']))
        if numpy.isfinite(i[1]['AIC']):
            self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AIC = %-.16E<br>" % (i[1]['AIC']))
        else:
            self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AIC = N/A<br>")
        if numpy.isfinite(i[1]['AICc_BA']):
            self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AICc (Burnham and Anderson) = %-.16E<br>" % (i[1]['AICc_BA']))
        else:
            self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + "AICc (Burnham and Anderson) = N/A<br>")
        
        self.stringList.append('<br><br>')
        
        self.stringList.append('Parameters:<BR>')
        for parmIndex in range(len(i[1]['parameterNames'])):
            self.stringList.append('&nbsp;&nbsp;&nbsp;&nbsp;' + i[1]['parameterNames'][parmIndex] + ' = %-.16E' % (i[1]['fittedParameters'][parmIndex]) + "<BR>")
            
        self.stringList.append('<br>')

        self.stringList.append('Additional Information:')
        for infoString in i[1]['additionalInfo']:
            self.stringList.append(infoString.replace(' ', '&nbsp;') + '<BR>')
            
        self.stringList.append('</td></tr></table><pre>')

        self.name = self.dataObject.IndependentDataName1 + " Rank " + str(self.distributionIndex + 1) + ": " + i[1]['distributionLongName']
        self.uniqueAnchorName = "XStatDistHist_" + str(self.distributionIndex)

        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".png"
 
        
    def CreateCharacterizerOutput(self):
        self.dataObject.distributionIndex = self.distributionIndex
        
        distro = self.dataObject.fittedStatisticalDistributionsList[self.distributionIndex][1]
        
        MatplotlibGraphs_2D.HistogramPlot(self.dataObject,
                                       self.physicalFileLocation,
                                       self.dataObject.IndependentDataName1 + ": " + distro['distributionLongName'] + " distribution",
                                       self.dataObject.IndependentDataArray[0],
                                       1)



# enter in Graph Reports at bottom
class ScatterAnimation(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.animationFlag = 1
        self.DataGraph = 1
        
        # used in creating individual animation frames on clusters
        self.functionString = 'MatplotlibGraphs_3D.ScatterPlot3D'


    def PrepareForCharacterizerOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        if self.dataObject.animationHeight == 0:
            return
        
        self.name = "GIF Scatter Animation"
        self.uniqueAnchorName = "ScatterAnimation"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + ".gif"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + ".gif"
            

    def CreateCharacterizerOutput(self):
        from . import MatplotlibGraphs_3D
        
        dataObject = copy.copy(self.dataObject)
        dataObject.graphHeight = self.dataObject.animationHeight
        dataObject.graphWidth = self.dataObject.animationWidth
        dataObject.CalculateGraphBoundaries()
        
        try:
            [fig, ax, plt] = eval(self.functionString + '(dataObject, None)')

            for i in range(0,360, self.animationFrameSeparation): 
                padstr = ''
                if i < 100:
                    padstr = '0'
                if i  < 10:
                    padstr = '00'

                ax.view_init(elev=dataObject.altimuth3D, azim=i)
                frameName = self.physicalFileLocation[:-4] + '__' + padstr + str(i) + ".png"
                fig.savefig(frameName, format = 'png')
                
                # convert PNG file to GIF for gifsicle
                p = os.popen('mogrify -format gif ' + frameName)
                p.close()
                
            plt.close('all')
            p = os.popen('gifsicle --colors 256 --loopcount  ' + self.physicalFileLocation[:-4] + '__*gif > ' + self.physicalFileLocation)
            p.close()
            p = os.popen('rm ' + self.physicalFileLocation[:-4] + '__*')
            p.close()
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])



# enter in Graph Reports at bottom
class SurfaceAnimation(GraphReport):

    def __init__(self, dataObject):
        GraphReport.__init__(self, dataObject)
        self.StatisticsGraph = 0
        self.animationFlag = 1
        
        # used in creating individual animation frames on clusters
        self.functionString = 'MatplotlibGraphs_3D.SurfacePlot'


    def PrepareForReportOutput(self):
        if self.dataObject.dimensionality == 2:
            return
        if self.dataObject.animationHeight == 0:
            return
        
        self.name = "GIF Surface Animation"
        self.uniqueAnchorName = "SurfaceAnimation"
        self.physicalFileLocation = "%s/%s%s" % (settings.TEMP_FILES_DIR, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".gif"
        self.websiteFileLocation = "%s%s%s" % (settings.STATIC_URL, self.uniqueAnchorName, self.dataObject.uniqueString) + self.GetRankString() + ".gif"


    def CreateReportOutput(self):
        try:
            from . import MatplotlibGraphs_3D
            
            dataObject = copy.copy(self.dataObject)
            dataObject.graphHeight = dataObject.animationHeight
            dataObject.graphWidth = dataObject.animationWidth
            dataObject.CalculateGraphBoundaries()

            [fig, ax, plt] = eval(self.functionString + '(dataObject, None)')


            for i in range(0,360,self.animationFrameSeparation): 
                padstr = ''
                if i < 100:
                    padstr = '0'
                if i  < 10:
                    padstr = '00'

                ax.view_init(elev=dataObject.altimuth3D, azim=i)
                frameName = self.physicalFileLocation[:-4] + '__' + padstr + str(i) + ".png"
                fig.savefig(frameName, format = 'png')
                
                # convert PNG file to GIF for gifsicle
                p = os.popen('mogrify -format gif ' + frameName)
                p.close()
                
            plt.close('all')
            p = os.popen('gifsicle --colors 256 --loopcount  ' + self.physicalFileLocation[:-4] + '__*gif > ' + self.physicalFileLocation)
            p.close()
            p = os.popen('rm ' + self.physicalFileLocation[:-4] + '__*')
            p.close()
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])



def StatisticalDistributionReportsDict(dataObject):
    return {"Text Reports" : [CharacterizerStatisticsListing(dataObject),
                              StatisticalDistributions(dataObject)],
            "Graph Reports" : [Data1Histogram(dataObject),
                               StatisticalDistributionHistogram(dataObject,  0),
                               StatisticalDistributionHistogram(dataObject,  1),
                               StatisticalDistributionHistogram(dataObject,  2),
                               StatisticalDistributionHistogram(dataObject,  3),
                               StatisticalDistributionHistogram(dataObject,  4),
                               StatisticalDistributionHistogram(dataObject,  5),
                               StatisticalDistributionHistogram(dataObject,  6),
                               StatisticalDistributionHistogram(dataObject,  7),
                               StatisticalDistributionHistogram(dataObject,  8),
                               StatisticalDistributionHistogram(dataObject,  9),
                               StatisticalDistributionHistogram(dataObject, 10),
                               StatisticalDistributionHistogram(dataObject, 11),
                               StatisticalDistributionHistogram(dataObject, 12),
                               StatisticalDistributionHistogram(dataObject, 13),
                               StatisticalDistributionHistogram(dataObject, 14),
                               StatisticalDistributionHistogram(dataObject, 15),
                               StatisticalDistributionHistogram(dataObject, 16),
                               StatisticalDistributionHistogram(dataObject, 17),
                               StatisticalDistributionHistogram(dataObject, 18),
                               StatisticalDistributionHistogram(dataObject, 19),
                               StatisticalDistributionHistogram(dataObject, 20),
                               StatisticalDistributionHistogram(dataObject, 21),
                               StatisticalDistributionHistogram(dataObject, 22),
                               StatisticalDistributionHistogram(dataObject, 23),
                               StatisticalDistributionHistogram(dataObject, 24),
                               StatisticalDistributionHistogram(dataObject, 25),
                               StatisticalDistributionHistogram(dataObject, 26),
                               StatisticalDistributionHistogram(dataObject, 27),
                               StatisticalDistributionHistogram(dataObject, 28),
                               StatisticalDistributionHistogram(dataObject, 29),
                               StatisticalDistributionHistogram(dataObject, 30),
                               StatisticalDistributionHistogram(dataObject, 31),
                               StatisticalDistributionHistogram(dataObject, 32),
                               StatisticalDistributionHistogram(dataObject, 33),
                               StatisticalDistributionHistogram(dataObject, 34),
                               StatisticalDistributionHistogram(dataObject, 35),
                               StatisticalDistributionHistogram(dataObject, 36),
                               StatisticalDistributionHistogram(dataObject, 37),
                               StatisticalDistributionHistogram(dataObject, 38),
                               StatisticalDistributionHistogram(dataObject, 39),
                               StatisticalDistributionHistogram(dataObject, 40),
                               StatisticalDistributionHistogram(dataObject, 41),
                               StatisticalDistributionHistogram(dataObject, 42),
                               StatisticalDistributionHistogram(dataObject, 43),
                               StatisticalDistributionHistogram(dataObject, 44),
                               StatisticalDistributionHistogram(dataObject, 45),
                               StatisticalDistributionHistogram(dataObject, 46),
                               StatisticalDistributionHistogram(dataObject, 47),
                               StatisticalDistributionHistogram(dataObject, 48),
                               StatisticalDistributionHistogram(dataObject, 49),
                               StatisticalDistributionHistogram(dataObject, 50),
                               StatisticalDistributionHistogram(dataObject, 51),
                               StatisticalDistributionHistogram(dataObject, 52),
                               StatisticalDistributionHistogram(dataObject, 53),
                               StatisticalDistributionHistogram(dataObject, 54),
                               StatisticalDistributionHistogram(dataObject, 55),
                               StatisticalDistributionHistogram(dataObject, 56),
                               StatisticalDistributionHistogram(dataObject, 57),
                               StatisticalDistributionHistogram(dataObject, 58),
                               StatisticalDistributionHistogram(dataObject, 59),
                               StatisticalDistributionHistogram(dataObject, 60),
                               StatisticalDistributionHistogram(dataObject, 61),
                               StatisticalDistributionHistogram(dataObject, 62),
                               StatisticalDistributionHistogram(dataObject, 63),
                               StatisticalDistributionHistogram(dataObject, 64),
                               StatisticalDistributionHistogram(dataObject, 65),
                               StatisticalDistributionHistogram(dataObject, 66),
                               StatisticalDistributionHistogram(dataObject, 67),
                               StatisticalDistributionHistogram(dataObject, 68),
                               StatisticalDistributionHistogram(dataObject, 69),
                               StatisticalDistributionHistogram(dataObject, 70),
                               StatisticalDistributionHistogram(dataObject, 71),
                               StatisticalDistributionHistogram(dataObject, 72),
                               StatisticalDistributionHistogram(dataObject, 73),
                               StatisticalDistributionHistogram(dataObject, 74),
                               StatisticalDistributionHistogram(dataObject, 75),
                               StatisticalDistributionHistogram(dataObject, 76),
                               StatisticalDistributionHistogram(dataObject, 77),
                               StatisticalDistributionHistogram(dataObject, 78),
                               StatisticalDistributionHistogram(dataObject, 79),
                               StatisticalDistributionHistogram(dataObject, 80),
                               StatisticalDistributionHistogram(dataObject, 81),
                               StatisticalDistributionHistogram(dataObject, 82),
                               StatisticalDistributionHistogram(dataObject, 83),
                               StatisticalDistributionHistogram(dataObject, 84),
                               StatisticalDistributionHistogram(dataObject, 85),
                               StatisticalDistributionHistogram(dataObject, 86),
                               StatisticalDistributionHistogram(dataObject, 87),
                               StatisticalDistributionHistogram(dataObject, 88),
                               StatisticalDistributionHistogram(dataObject, 89),
                               StatisticalDistributionHistogram(dataObject, 90),
                               StatisticalDistributionHistogram(dataObject, 91),
                               StatisticalDistributionHistogram(dataObject, 92),
                               StatisticalDistributionHistogram(dataObject, 93),
                               StatisticalDistributionHistogram(dataObject, 94),
                               StatisticalDistributionHistogram(dataObject, 95),
                               StatisticalDistributionHistogram(dataObject, 96),
                               StatisticalDistributionHistogram(dataObject, 97),
                               StatisticalDistributionHistogram(dataObject, 98),
                               StatisticalDistributionHistogram(dataObject, 99)]
            }

def CharacterizerReportsDict(dataObject):
    return {"Text Reports" : [CharacterizerStatisticsListing(dataObject)],
            "Graph Reports" : [Data1Histogram(dataObject),
                               Data2Histogram(dataObject),
                               DependentDataHistogram(dataObject),
                               DependentDataVsIndependentData1_ScatterPlot(dataObject),
                               DependentDataVsIndependentData2_ScatterPlot(dataObject),
                               IndependentData1VsDependentData_ScatterPlot(dataObject),
                               IndependentData1VsIndependentData2_ScatterPlot(dataObject),
                               IndependentData2VsDependentData_ScatterPlot(dataObject),
                               IndependentData2VsIndependentData1_ScatterPlot(dataObject),
                               ScatterPlot3D(dataObject),
                               ScatterAnimation(dataObject),
                               ]
            }

def FittingReportsDict(dataObject):
    return {"Text Reports" : [UserDefinedFunctionText(dataObject),
                              CoefficientListing(dataObject),
                              CoefficientAndFitStatistics(dataObject),
                              ErrorListing(dataObject),
                              StatisticsListing(dataObject),
                              CharacterizerStatisticsListing(dataObject),
                              CodeReportCPP(dataObject),
                              CodeReportFORTRAN90(dataObject),
                              CodeReportJAVA(dataObject),
                              CodeReportJULIA(dataObject),
                              CodeReportJAVASCRIPT(dataObject),
                              CodeReportPYTHON(dataObject),
                              CodeReportCSHARP(dataObject),
                              CodeReportSCILAB(dataObject),
                              CodeReportMATLAB(dataObject),
                              CodeReportVBA(dataObject)],
            "Graph Reports" : [Data1Histogram(dataObject),
                               Data2Histogram(dataObject),
                               DependentDataHistogram(dataObject),
                               AbsoluteErrorHistogram(dataObject),
                               RelativeErrorHistogram(dataObject),
                               PercentErrorHistogram(dataObject),
                               AbsoluteErrorVsIndependentData1_ScatterPlot(dataObject),
                               AbsoluteErrorVsIndependentData2_ScatterPlot(dataObject),
                               AbsoluteErrorVsDependentData_ScatterPlot(dataObject),
                               AbsErrScatterPlot3D(dataObject),
                               RelativeErrorVsIndependentData1_ScatterPlot(dataObject),
                               RelativeErrorVsIndependentData2_ScatterPlot(dataObject),
                               RelativeErrorVsDependentData_ScatterPlot(dataObject),
                               RelErrScatterPlot3D(dataObject),
                               PercentErrorVsIndependentData1_ScatterPlot(dataObject),
                               PercentErrorVsIndependentData2_ScatterPlot(dataObject),
                               PercentErrorVsDependentData_ScatterPlot(dataObject),
                               PerErrScatterPlot3D(dataObject),
                               DependentDataVsIndependentData1_ScatterPlot(dataObject),
                               DependentDataVsIndependentData2_ScatterPlot(dataObject),
                               IndependentData1VsDependentData_ScatterPlot(dataObject),
                               IndependentData1VsIndependentData2_ScatterPlot(dataObject),
                               IndependentData2VsDependentData_ScatterPlot(dataObject),
                               IndependentData2VsIndependentData1_ScatterPlot(dataObject),
                               DependentDataVsIndependentData1_ModelPlot(dataObject),
                               DependentDataVsIndependentData1_ConfidenceIntervals(dataObject),
                               ScatterPlot3D(dataObject),
                               SurfacePlot(dataObject),
                               ContourPlot(dataObject),
                               ScatterAnimation(dataObject),
                               SurfaceAnimation(dataObject),
                               ]
            }
