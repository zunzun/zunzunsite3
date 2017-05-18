import inspect, time, math, random, multiprocessing, queue, copy, sys, os

import numpy

from . import StatusMonitoredLongRunningProcessPage
from . import ReportsAndGraphs
import zunzun.forms
import zunzun.formConstants
import multiprocessing

import pyeq3



externalDataCache = pyeq3.dataCache()


def parallelWorkFunction(inParameterList):
    global externalDataCache

    try:
        j = eval(inParameterList[0] + "." + inParameterList[1] + "('" + inParameterList[9] + "', '" + inParameterList[2] + "')")
        j.dataCache = externalDataCache
        j.polyfunctional2DFlags = inParameterList[3]
        j.polyfunctional3DFlags = inParameterList[4]
        j.xPolynomialOrder = inParameterList[5]
        j.yPolynomialOrder = inParameterList[6]
        j.rationalNumeratorFlags = inParameterList[7]
        j.rationalDenominatorFlags = inParameterList[8]

        if j.ShouldDataBeRejected(j):
            return [None, inParameterList[0], inParameterList[1], inParameterList[2]]
        
        try:
            j.Solve()
            target = j.CalculateAllDataFittingTarget(j.solvedCoefficients)
        except:
            target = 1.0E300
        
        if target > 1.0E290:
            return [None, inParameterList[0], inParameterList[1], inParameterList[2]]
        
        t0 = target # always make this first for the result list sort function to work properly
        t1 = copy.copy(j.__module__)
        t2 = copy.copy(j.__class__.__name__)
        t3 = copy.copy(j.extendedVersionHandler.__class__.__name__.split('_')[1])
        t4 = copy.copy(j.polyfunctional2DFlags)
        t5 = copy.copy(j.polyfunctional3DFlags)
        t6 = copy.copy(j.xPolynomialOrder)
        t7 = copy.copy(j.yPolynomialOrder)
        t8 = copy.copy(j.rationalNumeratorFlags)
        t9 = copy.copy(j.rationalDenominatorFlags)
        t10 = copy.copy(j.fittingTarget)
        t11 = copy.copy(j.solvedCoefficients)
        
        j = None
            
        return [t0,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11]
    except:
        print('*** parallelWorkFunction exception:', str(sys.exc_info()))
        sys.stdout.flush()
        return [None, inParameterList[0], inParameterList[1], inParameterList[2]]




def serialWorker(obj, inputList, outputList):
    for i in range(len(inputList)):
        try:
            result = parallelWorkFunction(inputList[i])
            if result[0]:
                outputList.append(result)
                obj.countOfSerialWorkItemsRun += 1
            if (obj.countOfSerialWorkItemsRun % 50) == 0:
                obj.WorkItems_CheckOneSecondSessionUpdates()
        except:
            print('**** serialWorker exception:', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
            sys.stdout.flush()


def parallelWorker(inputList, outputQueue):
    for i in range(len(inputList)):
        try:
            outputQueue.put(parallelWorkFunction(inputList[i]))
        except:
            print('**** parallelWorker exception:', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
            sys.stdout.flush()



class FunctionFinder(StatusMonitoredLongRunningProcessPage.StatusMonitoredLongRunningProcessPage):

    interfaceString = 'zunzun/function_finder_interface.html'
    reniceLevel = 19


    def __init__(self):
        self.equationName = None
        self.dictionaryOf_BothGoodAndBadCacheData_Flags = {}
        self.numberOfEquationsScannedSoFar = 0
        self.fit_exception_count = 0
        self.fit_skip_count = 0
        self.linearFittingList = []
        self.parallelWorkItemsList = []
        self.parallelFittingResultsByEquationFamilyDictionary = {}
        self.functionFinderResultsList = []
        self.maxFFResultsListSize = 1000 # use ""best"" results  only for database speed and size
        self.bestFFResultTracker = 1.0E300 # to keep track of "best" results


    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)
        self.CommonCreateAndInitializeDataObject(True)
        self.dataObject.equation = self.boundForm.equationBase
        self.dataObject.textDataEditor = self.boundForm.cleaned_data["textDataEditor"]
        self.dataObject.weightedFittingChoice = self.boundForm.cleaned_data["weightedFittingChoice"]
        self.dataObject.extendedEquationTypes = self.boundForm.cleaned_data['extendedEquationTypes']
        self.dataObject.equationFamilyInclusion = self.boundForm.cleaned_data['equationFamilyInclusion']
        self.dataObject.fittingTarget = self.boundForm.cleaned_data['fittingTarget']
        self.dataObject.Max2DPolynomialOrder = len(zunzun.formConstants.polynomialOrder2DChoices) - 1
        self.dataObject.Max3DPolynomialOrder = len(zunzun.formConstants.polynomialOrder3DChoices) - 1
        self.dataObject.maxCoeffs = eval("int(self.boundForm.cleaned_data['smoothnessControl" + str(self.dataObject.dimensionality) + "D'])")
        self.dataObject.maxOrEqual = self.boundForm.cleaned_data['smoothnessExactOrMax']
        return ''


    def RenderOutputHTMLToAFileAndSetStatusRedirect(self):
        import time
        
        self.SaveDictionaryOfItemsToSessionStore('functionfinder', {'functionFinderResultsList':self.functionFinderResultsList})
        
        self.SaveDictionaryOfItemsToSessionStore('data', {'textDataEditor':self.dataObject.textDataEditor,
                                                           'weightedFittingChoice':self.dataObject.weightedFittingChoice,
                                                           'fittingTarget':self.dataObject.fittingTarget,
                                                           'DependentDataArray':self.dataObject.DependentDataArray,
                                                           'IndependentDataArray':self.dataObject.IndependentDataArray})
        
        self.SaveDictionaryOfItemsToSessionStore('status', {'redirectToResultsFileOrURL':'/FunctionFinderResults/' + str(self.dataObject.dimensionality) + '/?RANK=1&unused=' + str(time.time())})
        

    def AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond(self):
        global externalDataCache

        self.numberOfEquationsScannedSoFar += 1
        
        # fit data and only keep non-exception fits
        self.dataObject.equationdataCache = externalDataCache

        # smoothness control
        if self.dataObject.maxOrEqual == 'M': # Max
            if len(self.dataObject.equation.GetCoefficientDesignators()) > self.dataObject.maxCoeffs:
                self.fit_skip_count += 1
                return
        else: # Equal
            if len(self.dataObject.equation.GetCoefficientDesignators()) != self.dataObject.maxCoeffs:
                self.fit_skip_count += 1
                return

        # check for ncoeffs > nobs
        if len(self.dataObject.equation.GetCoefficientDesignators()) > self.dataLength:
            self.fit_skip_count += 1
            return
    
        # check for functions requiring non-zero nor non-negative data such as 1/x, etc.
        if self.dataObject.equation.ShouldDataBeRejected(self.dataObject.equation):
            self.fit_skip_count += 1
            return

        # see if the cache generation yielded any overly large numbers or exceptions
        try:
            self.dataObject.equation.dataCache.FindOrCreateAllDataCache(self.dataObject.equation)
        except:
            self.fit_skip_count += 1
            return
        for i in self.dataObject.equation.GetDataCacheFunctions():
            if (i[0] in self.dictionaryOf_BothGoodAndBadCacheData_Flags) != 1: # if not in the cached flags, add it
                if max(self.dataObject.equation.dataCache.allDataCacheDictionary[i[0]]) >= 1.0E300:
                    self.dictionaryOf_BothGoodAndBadCacheData_Flags[i[0]] = False # (bad)
                else:
                    self.dictionaryOf_BothGoodAndBadCacheData_Flags[i[0]] = True # (good)
            if self.dictionaryOf_BothGoodAndBadCacheData_Flags[i[0]] == False: # if bad
                self.fit_skip_count += 1
                return
                
        t0 = copy.copy(self.dataObject.equation.__module__)
        t1 = copy.copy(self.dataObject.equation.__class__.__name__)
        t2 = copy.copy(self.dataObject.equation.extendedVersionHandler.__class__.__name__.split('_')[1])
        t3 = copy.copy(self.dataObject.equation.polyfunctional2DFlags)
        t4 = copy.copy(self.dataObject.equation.polyfunctional3DFlags)
        t5 = copy.copy(self.dataObject.equation.xPolynomialOrder)
        t6 = copy.copy(self.dataObject.equation.yPolynomialOrder)
        t7 = copy.copy(self.dataObject.equation.rationalNumeratorFlags)
        t8 = copy.copy(self.dataObject.equation.rationalDenominatorFlags)
        t9 = copy.copy(self.dataObject.equation.fittingTarget)

        if self.dataObject.equation.CanLinearSolverBeUsedForSSQABS() and self.dataObject.equation.fittingTarget == "SSQABS":
            self.linearFittingList.append([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9])
        else:
            self.parallelWorkItemsList.append([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9])
            if t0 not in list(self.parallelFittingResultsByEquationFamilyDictionary.keys()):
                self.parallelFittingResultsByEquationFamilyDictionary[t0] = [0, 0]
            self.parallelFittingResultsByEquationFamilyDictionary[t0][0] += 1
        self.WorkItems_CheckOneSecondSessionUpdates_Scanning()


    def GenerateListOfWorkItems(self):
        global externalDataCache

        externalDataCache = self.dataObject.equation.dataCache
        
        self.dataLength = len(externalDataCache.allDataCacheDictionary['DependentData'])
        
        # loop through all equations
        if self.dataObject.dimensionality == 2:
            loopover = inspect.getmembers(pyeq3.Models_2D)
        else:
            loopover = inspect.getmembers(pyeq3.Models_3D)
        for submodule in loopover:
            if inspect.ismodule(submodule[1]):
                if submodule[0] not in self.dataObject.equationFamilyInclusion:
                    continue
                for equationClass in inspect.getmembers(submodule[1]):
                    if inspect.isclass(equationClass[1]):
                        for extendedName in pyeq3.ExtendedVersionHandlers.extendedVersionHandlerNameList:
                        
                            if 'STANDARD' not in self.dataObject.extendedEquationTypes:
                                if extendedName == '' or extendedName == 'Default' or extendedName == 'Offset':
                                    continue
                            if 'RECIPROCAL' not in self.dataObject.extendedEquationTypes:
                                if -1 != extendedName.find('Reciprocal'):
                                    continue
                            if 'INVERSE' not in self.dataObject.extendedEquationTypes:
                                if -1 != extendedName.find('Inverse'):
                                    continue
                            if 'LINEAR_GROWTH' not in self.dataObject.extendedEquationTypes:
                                if -1 != extendedName.find('LinearGrowth'):
                                    continue
                            if 'LINEAR_DECAY' not in self.dataObject.extendedEquationTypes:
                                if -1 != extendedName.find('LinearDecay'):
                                    continue
                            if 'EXPONENTIAL_GROWTH' not in self.dataObject.extendedEquationTypes:
                                if -1 != extendedName.find('ExponentialGrowth'):
                                    continue
                            if 'EXPONENTIAL_DECAY' not in self.dataObject.extendedEquationTypes:
                                if -1 != extendedName.find('ExponentialDecay'):
                                    continue

                            if (-1 != extendedName.find('Offset')) and (equationClass[1].autoGenerateOffsetForm == False):
                                continue
                            if (-1 != extendedName.find('Reciprocal')) and (equationClass[1].autoGenerateReciprocalForm == False):
                                continue
                            if (-1 != extendedName.find('Inverse')) and (equationClass[1].autoGenerateInverseForms == False):
                                continue
                            if (-1 != extendedName.find('Growth')) and (equationClass[1].autoGenerateGrowthAndDecayForms == False):
                                continue
                            if (-1 != extendedName.find('Decay')) and (equationClass[1].autoGenerateGrowthAndDecayForms == False):
                                continue
 
                            try:
                                j = equationClass[1](self.dataObject.fittingTarget, extendedName)
                            except:
                                continue
                                                        
                            self.dataObject.equation = j
                            self.dataObject.equation.FamilyName = submodule[0]
                            
                            self.dataObject.equation.dataCache = externalDataCache
                            
                            if self.dataObject.equation.userSelectablePolynomialFlag == False and self.dataObject.equation.userCustomizablePolynomialFlag == False and self.dataObject.equation.userSelectablePolyfunctionalFlag == False and self.dataObject.equation.userSelectableRationalFlag == False:
                                self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()
        
                            if self.dataObject.equation.userSelectablePolynomialFlag == True:
                                if self.dataObject.equation.GetDimensionality() == 2:
                                    for k in range(self.dataObject.Max2DPolynomialOrder+1):
                                        self.dataObject.equation.xPolynomialOrder = k
                                        self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()
                                else:
                                    for k in range(self.dataObject.Max3DPolynomialOrder+1):
                                        for l in range(self.dataObject.Max3DPolynomialOrder+1):
                                            self.dataObject.equation.xPolynomialOrder = k
                                            self.dataObject.equation.yPolynomialOrder = l
                                            self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()
        
                            # polyfunctionals are not used unless unweighted SSQ due to CPU hogging
                            if self.dataObject.equation.userSelectablePolyfunctionalFlag == True and self.dataObject.fittingTarget == "SSQABS" and len(self.dataObject.equation.dataCache.allDataCacheDictionary['Weights']) == 0:
                                functionList = []
                                if self.dataObject.equation.GetDimensionality() == 2:
                                    for i in range(len(self.dataObject.equation.polyfunctionalEquationList)):
                                        functionList.append(i)
        
                                    loopMaxCoeffs = 4
                                    for coeffNumber in range(1, loopMaxCoeffs+1):
                                        xcombolist = self.UniqueCombinations(functionList,coeffNumber)
                                        for k in xcombolist:
                                            self.dataObject.equation.__init__(self.dataObject.fittingTarget, extendedName)
                                            self.dataObject.equation.dataCache = externalDataCache
                                            self.dataObject.equation.polyfunctional2DFlags = k
                                            self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()
                                            if len(self.dataObject.equation.polyfunctional2DFlags) <= loopMaxCoeffs and 0 not in self.dataObject.equation.polyfunctional2DFlags and len(self.dataObject.equation.polyfunctional2DFlags) < self.dataObject.maxCoeffs:
                                                self.dataObject.equation.__init__(self.dataObject.fittingTarget, extendedName)
                                                self.dataObject.equation.dataCache = externalDataCache
                                                temp = copy.copy(self.dataObject.equation.polyfunctional2DFlags)
                                                temp.append(0) # offset term if one is not already used and enough coefficients
                                                self.dataObject.equation.polyfunctional2DFlags = temp
                                                self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()
        
                                else:
                                    for k in range(len(self.dataObject.equation.polyfunctionalEquationList_X)):
                                        for l in range(len(self.dataObject.equation.polyfunctionalEquationList_Y)):
                                            if [l,k] not in functionList:
                                                functionList.append([k,l])
        
                                    loopMaxCoeffs = 2
                                    xcombolist = self.UniqueCombinations(functionList, loopMaxCoeffs)
                                    for k in xcombolist:
                                        self.dataObject.equation.__init__(self.dataObject.fittingTarget, extendedName)
                                        self.dataObject.equation.dataCache = externalDataCache
                                        self.dataObject.equation.polyfunctional3DFlags = k
                                        self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()
                                        if len(self.dataObject.equation.polyfunctional3DFlags) == loopMaxCoeffs and [0, 0] not in self.dataObject.equation.polyfunctional3DFlags and len(self.dataObject.equation.polyfunctional3DFlags) < self.dataObject.maxCoeffs:
                                            self.dataObject.equation.__init__(self.dataObject.fittingTarget, extendedName)
                                            self.dataObject.equation.dataCache = externalDataCache
                                            temp = copy.copy(self.dataObject.equation.polyfunctional3DFlags)
                                            temp.append([0, 0]) # offset term if one is not already used
                                            self.dataObject.equation.polyfunctional3DFlags = temp
                                            self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()

                            # polyrationals are combinations of individual functions with some maximum number of combinations
                            if self.dataObject.equation.userSelectableRationalFlag == 1:
                                maxCoeffs = 2 # arbitrary choice of maximum number of numerator or denominator functions in a polyrational for this example
                                functionList = [] # make a list of function indices
                                for i in range(len(self.dataObject.equation.rationalEquationList)):
                                    functionList.append(i)

                                for numeratorCoeffCount in range(1, maxCoeffs+1):
                                    numeratorComboList = self.UniqueCombinations(functionList, numeratorCoeffCount)
                                    for numeratorCombo in numeratorComboList:
                                        for denominatorCoeffCount in range(1, maxCoeffs+1):
                                            denominatorComboList = self.UniqueCombinations2(functionList, denominatorCoeffCount)
                                            for denominatorCombo in denominatorComboList:
                                                self.dataObject.equation.__init__(self.dataObject.fittingTarget, extendedName)
                                                self.dataObject.equation.dataCache = externalDataCache
                                                self.dataObject.equation.rationalNumeratorFlags = numeratorCombo
                                                self.dataObject.equation.rationalDenominatorFlags = denominatorCombo
                                                self.AddEquationInfoToLinearAndParallelFittingListsAndCheckOneSecond()                                       

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Scanned %s Equations : %s OK, %s skipped, %s exceptions" % (self.numberOfEquationsScannedSoFar, len(self.linearFittingList) + len(self.parallelWorkItemsList), self.fit_skip_count, self.fit_exception_count)})


    def PerformWorkInParallel(self):
        import time

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Preparing to fit equations, one minute please..."})
        self.countOfParallelWorkItemsRun = 0
        self.countOfSerialWorkItemsRun = 0
        self.totalNumberOfParallelWorkItemsToBeRun = len(self.parallelWorkItemsList)
        self.totalNumberOfSerialWorkItemsToBeRun = len(self.linearFittingList)
        self.parallelWorkItemsList.reverse()
        
        fittingResultsQueue = multiprocessing.Queue()
        
        while len(self.parallelWorkItemsList) > 0:

            delta = self.GetParallelProcessCount() - len(multiprocessing.active_children())
            
            # increase number of parallel processes?
            granularity = 4
            equationCount = granularity
            if len(self.parallelWorkItemsList) < (granularity * multiprocessing.cpu_count() * 1.5):
                equationCount = 2
            if len(self.parallelWorkItemsList) < (granularity * multiprocessing.cpu_count() * 0.5):
                equationCount = 1
                
            if delta > 0 and len(self.parallelWorkItemsList) > 0:
                for i in range(delta):
                    taskList = []
                    while len(self.parallelWorkItemsList) > 0 and len(taskList) < equationCount:
                        taskList.append(self.parallelWorkItemsList.pop())
                    p = multiprocessing.Process(target=parallelWorker, args=(taskList, fittingResultsQueue))
                    p.start()

            self.WorkItems_CheckOneSecondSessionUpdates()
            time.sleep(1.0) # sleep for 1 second

            # transfer intermediate results to result list
            # without this processes would not start properly
            qsize = fittingResultsQueue.qsize()
            if qsize:
                for i in range(qsize):
                    resultValue = fittingResultsQueue.get()
                    if resultValue[0]:
                        if len(self.functionFinderResultsList) < self.maxFFResultsListSize:
                            self.functionFinderResultsList.append(resultValue)
                        else:
                            self.functionFinderResultsList.sort()
                            if self.functionFinderResultsList[-1][0] < self.bestFFResultTracker:
                                self.bestFFResultTracker = self.functionFinderResultsList[-1][0]
                                self.functionFinderResultsList[-1] = resultValue
                        self.countOfParallelWorkItemsRun += 1
                    else:
                        #print('*** fittingResultsQueue.get() returned', str(resultValue))
                        sys.stdout.flush()
                    self.parallelFittingResultsByEquationFamilyDictionary[resultValue[1]][1] += 1
        
        # wait for all currently active children to finish
        while multiprocessing.active_children():
            # transfer the last few result to result list
            qsize = fittingResultsQueue.qsize()
            if qsize:
                for i in range(qsize):
                    resultValue = fittingResultsQueue.get()
                    if resultValue[0]:
                        if len(self.functionFinderResultsList) < self.maxFFResultsListSize:
                            self.functionFinderResultsList.append(resultValue)
                        else:
                            self.functionFinderResultsList.sort()
                            if self.functionFinderResultsList[-1][0] < self.bestFFResultTracker:
                                self.bestFFResultTracker = self.functionFinderResultsList[-1][0]
                                self.functionFinderResultsList[-1] = resultValue
                        self.countOfParallelWorkItemsRun += 1
                    else:
                        #print('*** fittingResultsQueue.get() returned', str(resultValue))
                        sys.stdout.flush()
                    self.parallelFittingResultsByEquationFamilyDictionary[resultValue[1]][1] += 1
            self.WorkItems_CheckOneSecondSessionUpdates()
            time.sleep(1.0)

        # transfer the last few result to result list
        qsize = fittingResultsQueue.qsize()
        if qsize:
            for i in range(qsize):
                resultValue = fittingResultsQueue.get()
                if resultValue[0]:
                    if len(self.functionFinderResultsList) < self.maxFFResultsListSize:
                        self.functionFinderResultsList.append(resultValue)
                    else:
                        self.functionFinderResultsList.sort()
                        if self.functionFinderResultsList[-1][0] < self.bestFFResultTracker:
                            self.bestFFResultTracker = self.functionFinderResultsList[-1][0]
                            self.functionFinderResultsList[-1] = resultValue
                    self.countOfParallelWorkItemsRun += 1
                else:
                    #print('*** fittingResultsQueue.get() returned', str(resultValue))
                    sys.stdout.flush()
                self.parallelFittingResultsByEquationFamilyDictionary[resultValue[1]][1] += 1
        
        # linear fits are very fast - run these in the existing process which saves on interprocess communication overhead
        if self.totalNumberOfSerialWorkItemsToBeRun:
            serialWorker(self, self.linearFittingList, self.functionFinderResultsList)
            
        self.WorkItems_CheckOneSecondSessionUpdates()
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"%s Total Equations Fitted, combining lists..." % (self.countOfParallelWorkItemsRun + self.countOfSerialWorkItemsRun)})

        # transfer to result list before sorting
        for i in range(fittingResultsQueue.qsize()):
            resultValue = fittingResultsQueue.get()
            if resultValue:
                self.functionFinderResultsList.append(resultValue)

        # final status update is outside the 'one second updates'
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"%s Total Equations Fitted, sorting..." % (self.countOfParallelWorkItemsRun + self.countOfSerialWorkItemsRun)})

        self.functionFinderResultsList.sort() # uses the default sort on list element zero

        # done fitting, don't block on process ID now - see SMLRPP.CheckIfStillUsed()
        self.SaveDictionaryOfItemsToSessionStore('status', {'processID':0})


    def WorkItems_CheckOneSecondSessionUpdates(self):
        import time
        
        if self.oneSecondTimes != int(time.time()):
            self.CheckIfStillUsed()
            processcountString = '<br><br>Currently using 1 process (the server is busy)'
            if len(multiprocessing.active_children()) > 1:
                processcountString = '<br><br>Currently using ' + str(len(multiprocessing.active_children())) + ' parallel processes'
            
            familyString = ''
            sortedFamilyNameList = list(self.parallelFittingResultsByEquationFamilyDictionary.keys())
            if sortedFamilyNameList:
                familyString += '<table>'
                sortedFamilyNameList.sort()
                for familyName in sortedFamilyNameList:
                    total = self.parallelFittingResultsByEquationFamilyDictionary[familyName][0]
                    soFar = self.parallelFittingResultsByEquationFamilyDictionary[familyName][1]
                    if soFar > 0 and total != soFar: # bold the equations where fitting is underway
                        familyString += '<tr><td><b>%s</b></td><td><b>of</b></td><td><b>%s</b></td><td align="center">%s</td><td>Equations Fitted Non-Linearly</td></tr>' % (soFar, total, familyName.split('.')[-1])
                    elif total == soFar:
                        familyString += '<tr><td>%s</td><td>of</td><td>%s</td><td align="center"><b><font color="green">%s</font></b></td><td>Equations Fitted Non-Linearly</td></tr>' % (soFar, total, familyName.split('.')[-1])
                    else:
                        familyString += '<tr><td>%s</td><td>of</td><td>%s</td><td align="center">%s</td><td>Equations Fitted Non-Linearly</td></tr>' % (soFar, total, familyName.split('.')[-1])
                familyString += '</table><br>'
                if self.countOfSerialWorkItemsRun == 0:
                    self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':familyString + "<b>%s of %s</b> Equations Fitted Non-Linearly<br>%s of %s Equations Fitted Linearly" % (self.countOfParallelWorkItemsRun, self.totalNumberOfParallelWorkItemsToBeRun, self.countOfSerialWorkItemsRun, self.totalNumberOfSerialWorkItemsToBeRun) + processcountString})
                else:
                    self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':familyString + "%s of %s Equations Fitted Non-Linearly<br><b>%s of %s</b> Equations Fitted Linearly" % (self.countOfParallelWorkItemsRun, self.totalNumberOfParallelWorkItemsToBeRun, self.countOfSerialWorkItemsRun, self.totalNumberOfSerialWorkItemsToBeRun) + processcountString})
            
            self.oneSecondTimes = int(time.time())


    def WorkItems_CheckOneSecondSessionUpdates_Scanning(self):
        import time
        
        if self.oneSecondTimes != int(time.time()):
            self.CheckIfStillUsed()
            self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Scanned %s Equations : %s OK, %s skipped, %s exceptions" % (self.numberOfEquationsScannedSoFar, len(self.linearFittingList) + len(self.parallelWorkItemsList), self.fit_skip_count, self.fit_exception_count)})
            self.oneSecondTimes = int(time.time())


    def CreateUnboundInterfaceForm(self, request):
        dictionaryToReturn = {}
        dictionaryToReturn['dimensionality'] = str(self.dimensionality)
        
        dictionaryToReturn['header_text'] = 'ZunZunSite3 ' + str(self.dimensionality) + 'D Function Finder Interface'
        dictionaryToReturn['title_string'] = 'ZunZunSite3 ' + str(self.dimensionality) + 'D Function Finder Interface'

        # make a dimensionality-based unbound Django form
        if self.dimensionality == 2:
            self.unboundForm = zunzun.forms.FunctionFinder_2D()
            self.unboundForm.fields['textDataEditor'].initial += self.extraExampleDataTextForWeightedFitting + self.defaultData2D
        else:
            self.unboundForm = zunzun.forms.FunctionFinder_3D()
            self.unboundForm.fields['textDataEditor'].initial += self.extraExampleDataTextForWeightedFitting + self.defaultData3D
            
        # set the form to have either default or session text data
        temp = self.LoadItemFromSessionStore('data', 'textDataEditor_' + str(self.dimensionality) + 'D')
        if temp:
            self.unboundForm.fields['textDataEditor'].initial = temp
        temp = self.LoadItemFromSessionStore('data', 'commaConversion')
        if temp:
            self.unboundForm.fields['commaConversion'].initial = temp
        temp = self.LoadItemFromSessionStore('data', 'weightedFittingChoice')
        if temp:
            self.unboundForm.fields['weightedFittingChoice'].initial = temp
            
        self.unboundForm.weightedFittingPossibleFlag = 1
        dictionaryToReturn['mainForm'] = self.unboundForm
        
        return dictionaryToReturn


    def CreateBoundInterfaceForm(self, request):
        # make a dimensionality-based bound Django form
        self.boundForm = eval('zunzun.forms.FunctionFinder_' + str(self.dimensionality) + 'D(request.POST)')
        self.boundForm.dimensionality = str(self.dimensionality)
            

    def UniqueCombinations(self, items, n):
        if n==0:
            yield []
        else:
            for i in range(len(items)):
                for cc in self.UniqueCombinations(items[i+1:],n-1):
                    yield [items[i]]+cc


    def UniqueCombinations2(self,items2, n2):
        if n2==0:
            yield []
        else:
            for i2 in range(len(items2)):
                for cc2 in self.UniqueCombinations2(items2[i2+1:],n2-1):
                    yield [items2[i2]]+cc2


    def Combinations(self, items, n):
        if n==0:
            yield []
        else:
            for i in range(len(items)):
                for cc in self.UniqueCombinations(items[i+1:],n-1):
                    yield [items[i]]+cc


    def CreateOutputReportsInParallelUsingProcessPool(self):
        pass # function finder *results* page makes these
        
        
    def GenerateListOfOutputReports(self):
        pass # function finder *results* page makes these


    def CreateReportPDF(self):
        pass # no PDF file 
