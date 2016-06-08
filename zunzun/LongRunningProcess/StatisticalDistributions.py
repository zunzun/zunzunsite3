



import inspect, time, math, random, multiprocessing, io

import numpy, scipy, scipy.stats, pyeq3

from . import StatusMonitoredLongRunningProcessPage
import zunzun.forms
from . import ReportsAndGraphs



def parallelWorkFunction(distributionName, data, sortCriteriaName):
    try:
        return pyeq3.Services.SolverService.SolverService().SolveStatisticalDistribution(distributionName, data, sortCriteriaName)
    except:
        return 0


class StatisticalDistributions(StatusMonitoredLongRunningProcessPage.StatusMonitoredLongRunningProcessPage):

    interfaceString = 'zunzun/characterize_data_or_statistical_distributions_interface.html'
    equationName = None
    statisticalDistribution = True
    webFormName = 'Statistical Distributions'
    reniceLevel = 12
    characterizerOutputTrueOrReportOutputFalse = True
    evaluateAtAPointFormNeeded = False

    
    def __init__(self):
        self.parallelWorkItemsList = []

    
    def TransferFormDataToDataObject(self, request): # return any error in a user-viewable string (self.dataObject.ErrorString)
        self.pdfTitleHTML = self.webFormName + ' ' + str(self.dimensionality) + 'D'
        self.CommonCreateAndInitializeDataObject(False)
        self.dataObject.equation = self.boundForm.equationBase
        self.dataObject.equation._name = 'undefined' # the EquationBaseClass itself has no equation name
        self.dataObject.textDataEditor = self.boundForm.cleaned_data["textDataEditor"]
        self.dataObject.statisticalDistributionsSortBy = self.boundForm.cleaned_data['statisticalDistributionsSortBy']
        return ''


    def GenerateListOfWorkItems(self):
        
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Sorting Data"})
        
        # required for special beta distribution data max/min case
        self.dataObject.IndependentDataArray[0].sort()
        
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating List Of Work Items"})
        for item in inspect.getmembers(scipy.stats): # weibull max and min are duplicates of Frechet distributions
            if isinstance(item[1], scipy.stats.rv_continuous) and item[0] not in ['kstwobign', 'ncf', 'weibull_max', 'weibull_min']:
                self.parallelWorkItemsList.append(item[0])


    def PerformWorkInParallel(self):
        countOfWorkItemsRun = 0
        totalNumberOfWorkItemsToBeRun = len(self.parallelWorkItemsList)

        begin = -self.parallelChunkSize
        end = 0
        indices = []

        chunks = totalNumberOfWorkItemsToBeRun // self.parallelChunkSize
        modulus = totalNumberOfWorkItemsToBeRun % self.parallelChunkSize

        for i in range(chunks):
            begin += self.parallelChunkSize
            end += self.parallelChunkSize
            indices.append([begin, end])

        if modulus:
            indices.append([end, end + 1 + modulus])

        # sort order here
        calculateCriteriaForUseInListSorting = 'nnlf'
        if 'AIC' == self.dataObject.statisticalDistributionsSortBy:
            calculateCriteriaForUseInListSorting = 'AIC'
        if 'AICc_BA' == self.dataObject.statisticalDistributionsSortBy:
            calculateCriteriaForUseInListSorting = 'AICc_BA'
            
        for i in indices:
            parallelChunkResultsList = []
            self.pool = multiprocessing.Pool(self.GetParallelProcessCount())
            
            for item in self.parallelWorkItemsList[i[0]:i[1]]:
                parallelChunkResultsList.append(self.pool.apply_async(parallelWorkFunction, (item, self.dataObject.IndependentDataArray[0], calculateCriteriaForUseInListSorting)))
            
            for r in parallelChunkResultsList:
                returnedValue = r.get()
                if not returnedValue:
                    continue
                countOfWorkItemsRun += 1
                self.completedWorkItemsList.append(returnedValue)
                self.WorkItems_CheckOneSecondSessionUpdates(countOfWorkItemsRun, totalNumberOfWorkItemsToBeRun)
 
            self.pool.close()
            self.pool.join()
            self.pool = None
                
        # final save is outside the 'one second updates'
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Fitted %s of %s Statistical Distributions" % (countOfWorkItemsRun, totalNumberOfWorkItemsToBeRun)})
        
        for i in self.completedWorkItemsList:
            
            distro = getattr(scipy.stats, i[1]['distributionName']) # convert distro name back into a distribution object
                
            # dig out a long name
            longName = io.StringIO(distro.__doc__).readlines()[0]
            if longName[:2] == 'A ':
                longName = longName[2:]
            if longName[:3] == 'An ':
                longName = longName[3:]
            i[1]['distributionLongName'] = longName[:longName.find(' continuous')]

            '''
            # rename for special case
            if i[1]['distributionName'] == 'beta':
                if i[1]['data_max_min_as_limits'] == True:
                    i[1]['distributionLongName'] = i[1]['distributionLongName'] + ' (using data max/min as limits and not fitted)'
                else:
                    i[1]['distributionLongName'] = i[1]['distributionLongName'] + ' (calculated limits with all data points fitted)'
            '''

            # any additional info
            try:
                n = distro.__doc__.find('Notes\n')
                e = distro.__doc__.find('Examples\n')
                
                notes =  distro.__doc__[n:e]
                notes = '\n' + notes[notes.find('-\n') + 2:].replace('::', ':').strip()  
                
                i[1]['additionalInfo'] = io.StringIO(notes).readlines()
            except:
                i[1]['additionalInfo'] = ['No additional information available.']
            
            if distro.name == 'loggamma' and not distro.shapes:
                distro.shapes = 'c'
            if distro.shapes:
                parameterNames = distro.shapes.split(',') + ['location', 'scale']
            else:
                parameterNames = ['location', 'scale']
            i[1]['parameterNames'] = parameterNames
                
        self.completedWorkItemsList.sort()
        

    def WorkItems_CheckOneSecondSessionUpdates(self, countOfWorkItemsRun, totalNumberOfWorkItemsToBeRun):
        if self.oneSecondTimes != int(time.time()):
            self.CheckIfStillUsed()
            processcountString = '<br><br>Currently using 1 process (the server is busy)'
            if len(multiprocessing.active_children()) > 1:
                processcountString = '<br><br>Currently using ' + str(len(multiprocessing.active_children())) + ' parallel processes'
            self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Fitted %s of %s Statistical Distributions%s" % (countOfWorkItemsRun, totalNumberOfWorkItemsToBeRun, processcountString)})
            self.oneSecondTimes = int(time.time())
            

    def SpecificCodeForGeneratingListOfOutputReports(self):
        self.functionString = 'PrepareForCharacterizerOutput'
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating Report Objects"})
        self.dataObject.fittedStatisticalDistributionsList = self.completedWorkItemsList
        self.ReportsAndGraphsCategoryDict = ReportsAndGraphs.StatisticalDistributionReportsDict(self.dataObject)
