import sys, os, time, multiprocessing, io, string, pickle
from bs4 import BeautifulSoup # don't need everything, it has several components

import settings
import django.http # to raise 404's
import django.utils.encoding
from django.db import close_old_connections
from django.contrib.sessions.backends.db import SessionStore
from django.template.loader import render_to_string

import reportlab
import reportlab.platypus
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import reportlab.lib.pagesizes

from . import DataObject
from . import ClassForAttachingProperties
from . import ReportsAndGraphs

import zunzun.forms
from . import DefaultData

import pyeq3



def ParallelWorker_CreateReportOutput(inReportObject):
    try:
        if inReportObject.dataObject.equation.GetDisplayName() == 'User Defined Function': # User Defined Function will not pickle, see http://support.picloud.com/entries/122330-an-error-i-don-t-understand
            inReportObject.dataObject.equation.userDefinedFunctionText = inReportObject.dataObject.userDefinedFunctionText
            inReportObject.dataObject.equation.ParseAndCompileUserFunctionString(inReportObject.dataObject.equation.userDefinedFunctionText)

        inReportObject.CreateReportOutput()

        return [inReportObject.name, inReportObject.stringList, ''] # name for lookup, stringList for data, empty string for no exception
    except:
        return [inReportObject.name, 0, str(sys.exc_info()[0]) + str(sys.exc_info()[1])]



def ParallelWorker_CreateCharacterizerOutput(inReportObject):
    try:
        inReportObject.CreateCharacterizerOutput()
        return [inReportObject.name, inReportObject.stringList, ''] # name for lookup, stringList for data
    except:
        return [inReportObject.name, 0, str(sys.exc_info()[0]) + str(sys.exc_info()[1])]


# from http://code.activestate.com/recipes/576832-improved-reportlab-recipe-for-page-x-of-y/
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        self.drawRightString(200*mm, 20*mm, "Page %d of %d" % (self._pageNumber, page_count))
        self.drawCentredString(25*mm, 20*mm, 'https://github.com/zunzun/zunzunsite3')



class StatusMonitoredLongRunningProcessPage(object):

    debug = 0 # write to apache error log?

    parallelChunkSize = 16
    oneSecondTimes = 0

    inEquationName = ''
    inEquationFamilyName = ''

    session_data = None
    session_status = None
    session_functionfinder = None

    statisticalDistribution = False
    userDefinedFunction = False
    spline = False

    userInterfaceRequired = True
    reniceLevel = 10
    ppCount = 0
    completedWorkItemsList = []
    boundForm = None
    evaluationForm = None

    pool = None

    characterizerOutputTrueOrReportOutputFalse = False
    evaluateAtAPointFormNeeded = True

    equationInstance = 0

    extraExampleDataTextForWeightedFitting = '''Weighted fitting requires an additional number to
be used as a weight when fitting. The site does
not calculate any weights, which are used as:
   error = weight * (predicted - actual)
You must provide any weights you wish to use.
'''

    defaultData1D = DefaultData.defaultData1D
    defaultData2D = DefaultData.defaultData2D
    defaultData3D = DefaultData.defaultData3D


    def PerformWorkInParallel(self):
        pass


    def SaveSpecificDataToSessionStore(self):
        pass


    def GenerateListOfWorkItems(self):
        pass


    def GetParallelProcessCount(self):

        # limit based on free memory
        f = os.popen('vmstat', 'r')
        f.readline()
        f.readline()
        line = f.readline()
        f.close()
        freeRAM = line.split()[3]
        cache = line.split()[5]
        ppCount = int((float(freeRAM) + float(cache)) / 80000.0)

        if ppCount > multiprocessing.cpu_count(): # *three* extra processes
            ppCount = multiprocessing.cpu_count()
        if ppCount < 1: # need at least one process
            ppCount = 1

        # now limit based on CPU load
        f = open('/proc/loadavg', 'r')
        line = f.readline()
        f.close()
        load = float(line.split()[0])
        if load > (float(multiprocessing.cpu_count()) + 0.5) and ppCount > 3:
            ppCount = 3
        if load > (float(multiprocessing.cpu_count()) + 1.0) and ppCount > 2:
            ppCount = 2
        if load > (float(multiprocessing.cpu_count()) + 1.5) and ppCount > 1:
            ppCount = 1

        return ppCount


    def CreateReportPDF(self):

        specialExceptionFileText = 'Entered CreateReportPDF'
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Creating PDF Output File"})
        try:
            specialExceptionFileText = 'Top of function'

            scale = 72.0 / 300.0 # dpi conversion factor for PDF file images

            self.pdfFileName = self.dataObject.uniqueString + ".pdf"
            pageElements = []

            styles = reportlab.lib.styles.getSampleStyleSheet()

            styles.add(reportlab.lib.styles.ParagraphStyle(name='CenteredBodyText', parent=styles['BodyText'], alignment=reportlab.lib.enums.TA_CENTER))
            styles.add(reportlab.lib.styles.ParagraphStyle(name='SmallCode', parent=styles['Code'], fontSize=6, alignment=reportlab.lib.enums.TA_LEFT)) # 'Code' and wordwrap=CJK causes problems

            myTableStyle = [('ALIGN', (1,1), (-1,-1), 'CENTER'),
                            ('VALIGN', (1,1), (-1,-1), 'MIDDLE')]

            largeLogoImage = reportlab.platypus.Image(os.path.join(settings.TEMP_FILES_DIR, 'static_images/logo.png'), 25 * scale * 3, 25 * scale * 3)

            tableRow = [largeLogoImage,
                        'ZunZunSite3',
                        largeLogoImage]

            table = reportlab.platypus.Table([tableRow], style=myTableStyle)

            pageElements.append(table)

            pageElements.append(reportlab.platypus.XPreformatted('<br/><br/><br/><br/>', styles['CenteredBodyText']))

            if self.inEquationName:
                pageElements.append(reportlab.platypus.Paragraph(self.inEquationName, styles['CenteredBodyText']))
            pageElements.append(reportlab.platypus.XPreformatted('<br/><br/>', styles['CenteredBodyText']))

            titleXML = self.pdfTitleHTML.replace('sup>', 'super>').replace('SUP>', 'super>').replace('<br>', '<br/>').replace('<BR>', '<br/>')
            pageElements.append(reportlab.platypus.Paragraph(titleXML, styles['CenteredBodyText']))

            pageElements.append(reportlab.platypus.XPreformatted('<br/><br/>', styles['CenteredBodyText']))
            pageElements.append(reportlab.platypus.Paragraph(time.asctime(time.localtime()) + ' local server time', styles['CenteredBodyText']))

            pageElements.append(reportlab.platypus.PageBreak())

            verseInfo = self.GetVerseInfo()
            pageElements.append(reportlab.platypus.Paragraph(verseInfo[0], styles['CenteredBodyText']))
            pageElements.append(reportlab.platypus.XPreformatted('<br/><br/>', styles['CenteredBodyText']))
            pageElements.append(reportlab.platypus.Paragraph(verseInfo[1], styles['CenteredBodyText']))
            pageElements.append(reportlab.platypus.XPreformatted('<br/><br/>', styles['CenteredBodyText']))
            pageElements.append(reportlab.platypus.Paragraph('Read or search the King James Bible online at<br/>http://quod.lib.umich.edu/k/kjv/', styles['CenteredBodyText']))

            pageElements.append(reportlab.platypus.PageBreak())

            # make a page for each report output, with report name as page header
            # graphs may not exist if they raised an exception at creation time, trap and handle this condition
            for report in self.textReports:
                specialExceptionFileText = report.name
                pageElements.append(reportlab.platypus.Preformatted(report.name, styles['SmallCode']))
                pageElements.append(reportlab.platypus.XPreformatted('<br/><br/><br/>', styles['CenteredBodyText']))

                if report.stringList[0] == '</pre>': # corrects fit statistics not in PDF
                    report.stringList = report.stringList[1:]
                
                joinedString = str('\n').join(report.stringList)
                
                if -1 != report.name.find('Coefficients'):
                    joinedString = joinedString.replace('<sup>', '^')
                    joinedString = joinedString.replace('<SUP>', '^')

                soup = BeautifulSoup(joinedString, "lxml")

                notUnicodeList = []
                for i in soup.findAll(text=True):
                    notUnicodeList.append(str(i))
                replacedText = str('').join(notUnicodeList)

                replacedText = replacedText.replace('\t', '    ') # convert tabs to four spaces
                replacedText = replacedText.replace('\r\n', '\n')

                rebuiltText = ''
                for line in replacedText.split('\n'):
                    if line == '':
                        rebuiltText += '\n'
                    else:
                        if line[0] == '<':
                            splitLine = line.split('>')
                            if len(splitLine) > 1:
                                newLine = splitLine[len(splitLine)-1]
                            else:
                                newLine = ''
                        else:
                            newLine = line

                        # crude line wrapping
                        if len(newLine) > 500:
                            rebuiltText += newLine[:100] + '\n'
                            rebuiltText += newLine[100:200] + '\n'
                            rebuiltText += newLine[200:300] + '\n'
                            rebuiltText += newLine[300:400] + '\n'
                            rebuiltText += newLine[400:500] + '\n'
                            rebuiltText += newLine[500:] + '\n'
                        elif len(newLine) > 400:
                            rebuiltText += newLine[:100] + '\n'
                            rebuiltText += newLine[100:200] + '\n'
                            rebuiltText += newLine[200:300] + '\n'
                            rebuiltText += newLine[300:400] + '\n'
                            rebuiltText += newLine[400:] + '\n'
                        elif len(newLine) > 300:
                            rebuiltText += newLine[:100] + '\n'
                            rebuiltText += newLine[100:200] + '\n'
                            rebuiltText += newLine[200:300] + '\n'
                            rebuiltText += newLine[300:] + '\n'
                        elif len(newLine) > 200:
                            rebuiltText += newLine[:100] + '\n'
                            rebuiltText += newLine[100:200] + '\n'
                            rebuiltText += newLine[200:] + '\n'
                        elif len(newLine) > 100:
                            rebuiltText += newLine[:100] + '\n'
                            rebuiltText += newLine[100:] + '\n'
                        else:
                            rebuiltText += newLine + '\n'
                            
                pageElements.append(reportlab.platypus.Preformatted(rebuiltText, styles['SmallCode']))

                pageElements.append(reportlab.platypus.PageBreak())

            for report in self.graphReports:
                if report.animationFlag: # pdf files cannot contain GIF animations
                    continue
                if os.path.isfile(report.physicalFileLocation):
                    specialExceptionFileText = report.name
                    pageElements.append(reportlab.platypus.Paragraph(report.name, styles['CenteredBodyText']))
                    pageElements.append(reportlab.platypus.XPreformatted('<br/><br/>', styles['CenteredBodyText']))
                    try:
                        im = reportlab.platypus.Image(report.physicalFileLocation, self.dataObject.graphWidth * scale, self.dataObject.graphHeight * scale)
                    except:
                        time.sleep(1.0)
                        im = reportlab.platypus.Image(report.physicalFileLocation, self.dataObject.graphWidth * scale, self.dataObject.graphHeight * scale)
                    im.hAlign = 'CENTER'
                    pageElements.append(im)
                    if report.stringList != []:
                        pageElements.append(reportlab.platypus.Preformatted(report.name, styles['SmallCode']))
                        pageElements.append(reportlab.platypus.XPreformatted('<br/><br/><br/>', styles['CenteredBodyText']))
                        for line in report.stringList:
                            replacedLine = line.replace('<br>', '<br/>').replace('<BR>', '<br/>').replace('<pre>', '').replace('</pre>', '').replace('<tr>', '').replace('</tr>', '').replace('<td>', '').replace('</td>', '').replace('sup>', 'super>').replace('SUP>', 'super>').replace('\r\n', '\n').replace('\n', '<br/>').replace('&nbsp;', ' ')
                            pageElements.append(reportlab.platypus.XPreformatted(replacedLine, styles['SmallCode']))

                pageElements.append(reportlab.platypus.PageBreak())

            specialExceptionFileText = 'calling doc.build(pageElements) 0'
            try:
                doc = reportlab.platypus.SimpleDocTemplate(os.path.join(settings.TEMP_FILES_DIR, self.pdfFileName), pagesize=reportlab.lib.pagesizes.letter)
                specialExceptionFileText = 'calling doc.build(pageElements) 1'
                doc.build(pageElements, canvasmaker=NumberedCanvas)
            except:
                time.sleep(1.0)
                doc = reportlab.platypus.SimpleDocTemplate(os.path.join(settings.TEMP_FILES_DIR, self.pdfFileName), pagesize=reportlab.lib.pagesizes.letter)
                specialExceptionFileText = 'calling doc.build(pageElements) 2'
                doc.build(pageElements, canvasmaker=NumberedCanvas)
        except:
            import traceback
            print('Exception creating PDF file')
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(traceback.format_exc())
            self.pdfFileName = ''


    def BaseCreateAndInitializeDataObject(self, xName, yName, zName):
        dataObject = DataObject.DataObject()

        dataObject.ErrorString = ''
        dataObject.LogLinX = 'LIN'
        dataObject.LogLinY = 'LIN'
        dataObject.LogLinZ = 'LIN'

        settings.TEMP_FILES_DIR = settings.TEMP_FILES_DIR
        dataObject.WebsiteHTMLLocation = settings.STATIC_URL
        dataObject.WebsiteImageLocation = settings.STATIC_URL

        dataObject.dimensionality = self.dimensionality

        dataObject.IndependentDataName1 = xName
        if dataObject.dimensionality > 1:
            dataObject.IndependentDataName2 = ''
            dataObject.DependentDataName = yName
        if dataObject.dimensionality > 2:
            dataObject.IndependentDataName2 = yName
            dataObject.DependentDataName = zName

        dataObject.uniqueString = 'LRP_' + str(os.getpid()) + '_' + str(time.time()).replace('.', '_')
        dataObject.physicalStatusFileName = os.path.join(settings.TEMP_FILES_DIR, dataObject.uniqueString + '.html')
        dataObject.websiteStatusFileName = dataObject.WebsiteHTMLLocation + dataObject.uniqueString + '.html'

        return dataObject


    def CommonCreateAndInitializeDataObject(self, FF = False):

        self.dataObject = self.BaseCreateAndInitializeDataObject('', '', '')
        self.dataObject.equation = 0
        self.dataObject.fittedStatisticalDistributionsList = []
        self.dataObject.IndependentDataArray = self.boundForm.cleaned_data['IndependentData']
        if self.dataObject.dimensionality > 1:
            self.dataObject.DependentDataArray = self.boundForm.cleaned_data['DependentData']

        self.dataObject.IndependentDataName1 = self.boundForm.cleaned_data['dataNameX']
        if self.dataObject.dimensionality > 1:
            self.dataObject.IndependentDataName2 = ''
            self.dataObject.DependentDataName = self.boundForm.cleaned_data['dataNameY']
        if self.dataObject.dimensionality > 2:
            self.dataObject.IndependentDataName2 = self.boundForm.cleaned_data['dataNameY']
            self.dataObject.DependentDataName = self.boundForm.cleaned_data['dataNameZ']
            try:
                self.dataObject.dataPointSize3D = self.boundForm.cleaned_data['dataPointSize3D']
            except:
                pass

        if True == FF: # function finder, return here
            return self.dataObject

        self.dataObject.graphWidth = int(self.boundForm.cleaned_data['graphSize'].split('x')[0])
        self.dataObject.graphHeight = int(self.boundForm.cleaned_data['graphSize'].split('x')[1])
        self.dataObject.ScientificNotationX = self.boundForm.cleaned_data['scientificNotationX']
        self.dataObject.Extrapolation_x = self.boundForm.cleaned_data['graphScaleX']
        self.dataObject.Extrapolation_x_min = self.boundForm.cleaned_data['minManualScaleX']
        self.dataObject.Extrapolation_x_max = self.boundForm.cleaned_data['maxManualScaleX']
        self.dataObject.LogLinX = self.boundForm.cleaned_data['logLinX']

        if self.dataObject.dimensionality > 1:
            self.dataObject.ScientificNotationY = self.boundForm.cleaned_data['scientificNotationY']
            self.dataObject.Extrapolation_y = self.boundForm.cleaned_data['graphScaleY']
            self.dataObject.Extrapolation_y_min = self.boundForm.cleaned_data['minManualScaleY']
            self.dataObject.Extrapolation_y_max = self.boundForm.cleaned_data['maxManualScaleY']
            self.dataObject.LogLinY = self.boundForm.cleaned_data['logLinY']
        if self.dataObject.dimensionality > 2:
            self.dataObject.animationWidth = int(self.boundForm.cleaned_data['animationSize'].split('x')[0])
            self.dataObject.animationHeight = int(self.boundForm.cleaned_data['animationSize'].split('x')[1])
            self.dataObject.ScientificNotationZ = self.boundForm.cleaned_data['scientificNotationZ']
            self.dataObject.Extrapolation_z = self.boundForm.cleaned_data['graphScaleZ']
            self.dataObject.Extrapolation_z_min = self.boundForm.cleaned_data['minManualScaleZ']
            self.dataObject.Extrapolation_z_max = self.boundForm.cleaned_data['maxManualScaleZ']
            self.dataObject.LogLinZ = self.boundForm.cleaned_data['logLinZ']

        # can only take log of positive data
        if self.dataObject.LogLinX == 'LOG' and min(self.dataObject.IndependentDataArray[0]) <= 0.0:
            self.dataObject.ErrorString = 'Your X data (' + self.dataObject.IndependentDataName1 + ') contains a non-positive value and you have selected logarithmic X scaling. I cannot take the log of a non-positive number.'
        if self.dataObject.dimensionality == 2:
            if self.dataObject.LogLinY == 'LOG' and min(self.dataObject.DependentDataArray) <= 0.0:
                self.dataObject.ErrorString = 'Your Y data (' + self.dataObject.DependentDataName + ') contains a non-positive value and you have selected logarithmic Y scaling. I cannot take the log of a non-positive number.'
        if self.dataObject.dimensionality == 3:
            if self.dataObject.LogLinY == 'LOG' and min(self.dataObject.IndependentDataArray[1]) <= 0.0:
                self.dataObject.ErrorString = 'Your Y data (' + self.dataObject.IndependentDataName1 + ') contains a non-positive value and you have selected logarithmic Y scaling. I cannot take the log of a non-positive number.'
            if self.dataObject.LogLinZ == 'LOG' and min(self.dataObject.DependentDataArray) <= 0.0:
                self.dataObject.ErrorString = 'Your Z data (' + self.dataObject.DependentDataName + ') contains a non-positive value and you have selected logarithmic Z scaling. I cannot take the log of a non-positive number.'

        if self.dataObject.dimensionality == 3:            
            self.dataObject.animationWidth = int(self.boundForm.cleaned_data['animationSize'].split('x')[0])
            self.dataObject.animationHeight = int(self.boundForm.cleaned_data['animationSize'].split('x')[1])
            self.dataObject.azimuth3D = float(self.boundForm.cleaned_data['rotationAnglesAzimuth'])
            self.dataObject.altimuth3D = float(self.boundForm.cleaned_data['rotationAnglesAltimuth'])


    def SaveDictionaryOfItemsToSessionStore(self, inSessionStoreName, inDictionary):
        session = eval('self.session_' + inSessionStoreName)
        if session is None:
            session = eval('SessionStore(self.session_key_' + inSessionStoreName + ')')
        for i in list(inDictionary.keys()):
            item = inDictionary[i]
            if -1 != str(type(item)).find('byte'):
                item = django.utils.encoding.smart_bytes(item, encoding='utf-8', strings_only=True, errors='strict')
                item = str(item)
            item = pickle.dumps(item)
            
            session[i] = item

        if inSessionStoreName == 'status':
            session["timestamp"] = pickle.dumps(time.time())

        # sometimes database is momentarily locked, so retry on exception to mitigate
        try:
            session.save()
        except:
            time.sleep(0.5) # wait 1/2 second before retry
            session.save()
            
        close_old_connections()
        session = None


    def LoadItemFromSessionStore(self, inSessionStoreName, inItemName):
        session = eval('self.session_' + inSessionStoreName)
        if session is None:
            session = eval('SessionStore(self.session_key_' + inSessionStoreName + ')')
        try:
            returnItem = session[inItemName]
        except:
            returnItem = pickle.dumps(None)
        close_old_connections()
        session = None
        
        returnItem = pickle.loads(returnItem)
        return returnItem


    def PerformAllWork(self):

        self.SaveDictionaryOfItemsToSessionStore('status', {'processID':os.getpid()})

        self.GenerateListOfWorkItems()

        self.PerformWorkInParallel()

        self.GenerateListOfOutputReports()

        self.CreateOutputReportsInParallelUsingProcessPool()

        self.CreateReportPDF()

        self.RenderOutputHTMLToAFileAndSetStatusRedirect()


    def CreateOutputReportsInParallelUsingProcessPool(self):

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Running All Reports"})

        countOfReportsRun = 0
        reportsToBeRunInParallel = self.graphReports + self.textReports
        totalNumberOfReportsToBeRun = len(reportsToBeRunInParallel)

        begin = -self.parallelChunkSize
        end = 0
        indices = []

        chunks = totalNumberOfReportsToBeRun // self.parallelChunkSize
        modulus = totalNumberOfReportsToBeRun % self.parallelChunkSize

        for i in range(chunks):
            begin += self.parallelChunkSize
            end += self.parallelChunkSize
            indices.append([begin, end])

        if modulus:
            indices.append([end, end + 1 + modulus])

        for i in indices:
            parallelChunkResultsList = []

            self.pool = multiprocessing.Pool(self.GetParallelProcessCount())
            for item in reportsToBeRunInParallel[i[0]:i[1]]:
                try:
                    item.dataObject.equation.modelRelativeError
                except:
                    item.dataObject.equation.modelRelativeError = None
                if self.characterizerOutputTrueOrReportOutputFalse:
                    parallelChunkResultsList.append(self.pool.apply_async(ParallelWorker_CreateCharacterizerOutput, (item,)))
                else:
                    if item.dataObject.equation.GetDisplayName() == 'User Defined Function': # User Defined Function will not pickle, see http://support.picloud.com/entries/122330-an-error-i-don-t-understand, regenerate in the parallel pool
                        item.dataObject.userDefinedFunctionText = item.dataObject.equation.userDefinedFunctionText
                        item.dataObject.equation.userFunctionCodeObject = None
                        item.dataObject.equation.safe_dict = None
                    parallelChunkResultsList.append(self.pool.apply_async(ParallelWorker_CreateReportOutput, (item,)))

            for r in parallelChunkResultsList:
                returnedValue = r.get()
                for report in reportsToBeRunInParallel[i[0]:i[1]]:
                    if report.name == returnedValue[0]:
                        if returnedValue[2]: # exception during parallel processing
                            report.exception = True
                        report.stringList = returnedValue[1]
                countOfReportsRun += 1
                self.Reports_CheckOneSecondSessionUpdates(countOfReportsRun, totalNumberOfReportsToBeRun)

            self.pool.close()
            self.pool.join()
            self.pool = None


    def Reports_CheckOneSecondSessionUpdates(self, countOfReportsRun, totalNumberOfReportsToBeRun):
        if self.oneSecondTimes != int(time.time()):
            self.CheckIfStillUsed()
            processcountString = '<br><br>Currently using 1 process (the server is busy)'
            if len(multiprocessing.active_children()) > 1:
                processcountString = '<br><br>Currently using ' + str(len(multiprocessing.active_children())) + ' parallel processes'
            self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Created %s of %s Reports and Graphs %s" % (countOfReportsRun, totalNumberOfReportsToBeRun, processcountString)})
            self.oneSecondTimes = int(time.time())


    def CheckIfStillUsed(self):
        import time
        if self.LoadItemFromSessionStore('status', 'processID') == None:
            return

        # if a new process ID is in the session data, another process was started and this process was abandoned
        if self.LoadItemFromSessionStore('status', 'processID') != os.getpid() and self.LoadItemFromSessionStore('status', 'processID') != 0:
            print("**** SMLRPP Exiting on process ID, session_status['processID'] = ", self.LoadItemFromSessionStore('status', 'processID'), " os.getpid() = ", os.getpid())
            sys.stdout.flush()

            time.sleep(1.0)
            if self.pool:
                self.pool.close()
                self.pool.join()
                self.pool = None
            for p in multiprocessing.active_children():
                p.terminate()
            os._exit(0) # kills pool processes

        # if the status has not been checked in the past 30 seconds, this process was abandoned
        if (time.time() - self.LoadItemFromSessionStore('status', 'time_of_last_status_check')) > 300:
            print("**** SMLRPP Exiting on time of last status check")
            sys.stdout.flush()

            time.sleep(1.0)
            if self.pool:
                self.pool.close()
                self.pool.join()
                self.pool = None
            for p in multiprocessing.active_children():
                p.terminate()
            os._exit(0) # kills pool processes


    def SetInitialStatusDataIntoSessionVariables(self, request):
        self.SaveDictionaryOfItemsToSessionStore('status',
                                                 {'currentStatus':'Initializing',
                                                  'start_time':time.time(),
                                                  'time_of_last_status_check':time.time(),
                                                  'redirectToResultsFileOrURL':''})

        self.SaveDictionaryOfItemsToSessionStore('data',
                                                 {'textDataEditor_' + str(self.dimensionality) + 'D':request.POST['textDataEditor'],
                                                  'commaConversion':request.POST['commaConversion'],
                                                  'IndependentDataName1':self.dataObject.IndependentDataName1,
                                                  'IndependentDataName2':self.dataObject.IndependentDataName2,
                                                  'DependentDataName':self.dataObject.DependentDataName})


    def GetVerseInfo(self):
        reference = 'John 3:16'
        verse = 'For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.'    
        return [reference, verse]


    def SpecificCodeForGeneratingListOfOutputReports(self):

        self.functionString = 'PrepareForReportOutput'
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Calculating Error Statistics"})
        self.dataObject.CalculateErrorStatistics()

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Calculating Parameter Statistics"})
        self.dataObject.equation.CalculateCoefficientAndFitStatistics()

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating Report Objects"})
        self.ReportsAndGraphsCategoryDict = ReportsAndGraphs.FittingReportsDict(self.dataObject)


    def GenerateListOfOutputReports(self):
        self.textReports = []
        self.graphReports = []

        # calculate data statistics and graph boundaries
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Calculating Data Statistics"})
        self.dataObject.CalculateDataStatistics()

        if self.dataObject.dimensionality > 1:
            self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Calculating Graph Boundaries"})
            self.dataObject.CalculateGraphBoundaries()

        self.SpecificCodeForGeneratingListOfOutputReports()

        # generate required text reports
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating List Of Text Reports"})
        for i in self.ReportsAndGraphsCategoryDict["Text Reports"]:
            exec('i.' + self.functionString + '()')
            if i.name != '':
                self.textReports.append(i)

        # select required graph reports
        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating List Of Graphical Reports"})
        for i in self.ReportsAndGraphsCategoryDict["Graph Reports"]:
            exec('i.' + self.functionString + '()')
            if i.name != '':
                self.graphReports.append(i)


    def RenderOutputHTMLToAFileAndSetStatusRedirect(self):

        self.SaveSpecificDataToSessionStore()

        self.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"Generating Output HTML"})

        itemsToRender = {}

        import time
        itemsToRender['scripture'] = self.GetVerseInfo()

        itemsToRender['dimensionality'] = str(self.dimensionality)

        itemsToRender['header_text'] = 'ZunZunSite<br>' + self.webFormName
        itemsToRender['title_string'] = 'ZunZunSite3 ' + self.webFormName.replace('<br>', ' ')

        itemsToRender['textReports'] = self.textReports

        # get animation file sizes
        for i in self.graphReports:
            if i.animationFlag:
                try:
                    i.fileSize = os.path.getsize(i.physicalFileLocation)
                except:
                    i.fileSize = 0
        itemsToRender['graphReports'] = self.graphReports

        itemsToRender['pdfFileName'] = self.pdfFileName

        itemsToRender['statisticalDistributions'] = self.statisticalDistribution

        itemsToRender['feedbackForm'] = zunzun.forms.FeedbackForm()

        itemsToRender['equationInstance'] = self.equationInstance
        if self.evaluateAtAPointFormNeeded:
            itemsToRender['EvaluateAtAPointForm'] = eval('zunzun.forms.EvaluateAtAPointForm_' + str(self.dimensionality) + 'D()')
            itemsToRender['IndependentDataName1'] = self.dataObject.IndependentDataName1
            itemsToRender['IndependentDataName2'] = self.dataObject.IndependentDataName2
        itemsToRender['loadavg'] = os.getloadavg()
        try:
            f = open(os.path.join(settings.TEMP_FILES_DIR, self.dataObject.uniqueString + ".html"), "w")
            f.write(render_to_string('zunzun/equation_fit_or_characterizer_results.html', itemsToRender))
            f.flush()
            f.close()
        except:
            print("**** SMLRPP render", str(sys.exc_info()[0]), str(sys.exc_info()[1]))
            sys.stdout.flush()
        self.SaveDictionaryOfItemsToSessionStore('status', {'redirectToResultsFileOrURL':os.path.join(settings.TEMP_FILES_DIR, self.dataObject.uniqueString + ".html")})


    def CreateUnboundInterfaceForm(self, request): # OVERRIDDEN in fittingBaseClass
        dictionaryToReturn = {}
        dictionaryToReturn['dimensionality'] = str(self.dimensionality)

        dictionaryToReturn['header_text'] = 'ZunZunSite3 ' + str(self.dimensionality) + 'D Interface<br>' + self.webFormName
        dictionaryToReturn['title_string'] = 'ZunZunSite3 ' + str(self.dimensionality) + 'D Interface ' + self.webFormName

        # make a dimensionality-based unbound Django form
        self.unboundForm = eval('zunzun.forms.CharacterizeDataForm_' + str(self.dimensionality) + 'D()')

        # set the form to have either default or session text data
        temp = self.LoadItemFromSessionStore('data', 'textDataEditor_' + str(self.dimensionality) + 'D')
        if temp:
            self.unboundForm.fields['textDataEditor'].initial = temp
        else:
            self.unboundForm.fields['textDataEditor'].initial = zunzun.forms.formConstants.initialDataEntryText + eval('self.defaultData' + str(self.dimensionality) + 'D')
        temp = self.LoadItemFromSessionStore('data', 'commaConversion')
        if temp:
            self.unboundForm.fields['commaConversion'].initial = temp
        self.unboundForm.weightedFittingPossibleFlag = 0 # weightedFittingChoice not used in characterizers
        dictionaryToReturn['mainForm'] = self.unboundForm

        dictionaryToReturn['statisticalDistributions'] = self.statisticalDistribution

        return dictionaryToReturn


    def CreateBoundInterfaceForm(self, request): # OVERRIDDEN in fittingBaseClass
        self.boundForm = eval('zunzun.forms.CharacterizeDataForm_' + str(self.dimensionality) + 'D(request.POST)')
        self.boundForm.dimensionality = str(self.dimensionality)
        self.boundForm['statisticalDistributionsSortBy'].required = self.statisticalDistribution

