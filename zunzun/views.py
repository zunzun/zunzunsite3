from django.shortcuts import render
from django.shortcuts import render_to_response
import django.http # to raise 404's
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import Context, Template, loader
from django.views.decorators.cache import cache_control
from django.contrib.sessions.backends.db import SessionStore
from django.db import close_old_connections
from django.core.mail import EmailMessage

import settings
import django.http

import os, sys, time, urllib.request, urllib.parse, urllib.error, signal, copy, pickle
from . import forms, formConstants
import numpy, multiprocessing

import zunzun
import pyeq3
from . import LongRunningProcess

sys.stdout = sys.stderr # wsgi cannot send to stdout, see http://code.google.com/p/modwsgi/wiki/DebuggingTechniques


@cache_control(no_cache=True)
def EvaluateAtAPointView(request):
    import os, sys, time
    
    if CommonToAllViews(request): # any referrer blocks or web request checks processed here
        raise django.http.Http404
        
    # only allow POST for this view
    if request.method != 'POST':
        return HttpResponse('I am not able to process your request.')

    # used to read data from session
    if 'session_key_data' not in list(request.session.keys()):
        return HttpResponse('I was unable to read required session data, my apologies. Are session cookies turned off in your browser?')
    
    LRP = LongRunningProcess.FittingBaseClass.FittingBaseClass()
    LRP.session_key_data = request.session['session_key_data']
    
    # instantiate an equation object using session equation family and name
    LRP.dimensionality = LRP.LoadItemFromSessionStore('data', 'dimensionality')
    inEquationName = LRP.LoadItemFromSessionStore('data', 'equationName')
    inEquationFamilyName = LRP.LoadItemFromSessionStore('data', 'equationFamilyName')
    equation = LRP.GetEquationFromNameAndFamily(inEquationName, inEquationFamilyName, checkForSplinesAndUserDefinedFunctionsFlag = 1)
    if not equation: # could not find a matching equation
        return HttpResponse('Could not find the equation "' + str(inEquationName) + '" in the equation family "' + str(inEquationFamilyName) + '".')
    
    # read equation-specific information from session data and assign to equation object
    if equation.splineFlag:
        equation.scipySpline = LRP.LoadItemFromSessionStore('data', 'scipySpline')
    elif equation.userDefinedFunctionFlag:
        equation.userDefinedFunctionText = LRP.LoadItemFromSessionStore('data', 'udfEditor_' + str(equation.GetDimensionality()) + 'D')
        equation.ParseAndCompileUserFunctionString(equation.userDefinedFunctionText)        
    elif equation.userSelectablePolynomialFlag:
        equation.xPolynomialOrder = LRP.LoadItemFromSessionStore('data', 'xPolynomialOrder')
        equation.yPolynomialOrder = LRP.LoadItemFromSessionStore('data', 'yPolynomialOrder')
    elif equation.userSelectableRationalFlag:
        equation.rationalNumeratorFlags = LRP.LoadItemFromSessionStore('data', 'rationalNumeratorFlags')
        equation.rationalDenominatorFlags = LRP.LoadItemFromSessionStore('data', 'rationalDenominatorFlags')
    elif equation.userSelectablePolyfunctionalFlag:
        equation.polyfunctional2DFlags = LRP.LoadItemFromSessionStore('data', 'polyfunctional2DFlags')
        equation.polyfunctional3DFlags = LRP.LoadItemFromSessionStore('data', 'polyfunctional3DFlags')
    elif equation.userCustomizablePolynomialFlag:
        equation.polynomial2DFlags = LRP.LoadItemFromSessionStore('data', 'polynomial2DFlags')
    else:
        equation.fittingTarget = LRP.LoadItemFromSessionStore('data', 'fittingTarget')

    equation.solvedCoefficients = LRP.LoadItemFromSessionStore('data', 'solvedCoefficients')
    
    # make bound Django form and call form.is_valid()
    try:
        evaluationForm = eval('forms.EvaluateAtAPointForm_' + str(LRP.dimensionality) + 'D(request.POST)')
    except:
        time.sleep(1.0)
        evaluationForm = eval('forms.EvaluateAtAPointForm_' + str(LRP.dimensionality) + 'D(request.POST)')
        
    if not evaluationForm.is_valid():
        return HttpResponse('Invalid data submitted, please try again.')

    # load data to be evaluated from the cleaned form data
    if LRP.dimensionality == 2:
        equation.dataCache.allDataCacheDictionary['IndependentData'] = numpy.array([[evaluationForm.cleaned_data['x']], [1.0]])
    else:
        equation.dataCache.allDataCacheDictionary['IndependentData'] = numpy.array([[evaluationForm.cleaned_data['x']], [evaluationForm.cleaned_data['y']]])
    equation.dataCache.FindOrCreateAllDataCache(equation)

    # evaluate data, checking bounds of result
    try:
        pointValue = equation.CalculateModelPredictions(equation.solvedCoefficients, equation.dataCache.allDataCacheDictionary)
        try:
            pointValue = pointValue[0] # spline evaluation was returning scalar and not array
        except:
            pass
        if pointValue < 1.0E300 and pointValue > -1.0E300:
            pointValueAsString = 'evaluates to <b>' + str(pointValue) + '</b>'
        else:
            pointValueAsString = 'Evaluation was outside numeric bounds of +/- 1.0E300, please check the data.'
    except:
        exceptionString = str(sys.exc_info()[0]) + '  ' + str(sys.exc_info()[1]) + '\n'
        exceptionString += inEquationFamilyName + '\n'
        exceptionString += inEquationName + '\n'
        exceptionString += str(equation.solvedCoefficients) + '\n'
        exceptionString += str(equation.dataCache.allDataCacheDictionary['IndependentData'])
        pointValueAsString = 'Exception in evaluation, please check the data. Exception text: ' + exceptionString
        EmailMessage('Site exception in evaluation at a point', exceptionString, to = [settings.EXCEPTION_EMAIL_ADDRESS]).send()
    return HttpResponse(pointValueAsString)


def ConvertSecondsToHMS(seconds):
    hours = int(seconds / 3600.0)
    seconds -= 3600*hours
    minutes = int(seconds / 60.0)
    seconds -= int(60*minutes)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


@cache_control(no_cache=True)
def StatusView(request):
    import os, sys, time

    try:
        session_status = SessionStore(request.session['session_key_status'])
    except:
        return HttpResponse("I could not read your session data, please try again.")

    # this is done so that the "back" button does not return users to a status page when viewing FF results
    if 'redirectToResultsFileOrURL' in session_status:
        if pickle.loads(session_status['redirectToResultsFileOrURL']) != '':
            # read and reset
            redirect = pickle.loads(session_status['redirectToResultsFileOrURL'])
            session_status['redirectToResultsFileOrURL'] = pickle.dumps('')
            try: # database can lock, sleep and retry
                session_status.save()
            except:
                time.sleep(0.5)
                session_status.save()
    
            # is this a file or a URL
            if redirect.startswith(settings.TEMP_FILES_DIR):
                s = open(redirect, 'r').read()
                return HttpResponse(s)
            else: # URL
                return HttpResponseRedirect(redirect)

    session_status['time_of_last_status_check'] = pickle.dumps(time.time())
    try: # database can lock, sleep and retry
        session_status.save()
    except:
        time.sleep(0.5)
        session_status.save()
    
    try:
        currentStatus = pickle.loads(session_status['currentStatus'])
        startTime = pickle.loads(session_status['start_time'])
        timeStamp = pickle.loads(session_status['timestamp'])
    except:
        return HttpResponse("I could not read your session data, my apologies. This is usually caused by a stale browser cookie. Please delete the zunzunsite3 browser cookie and try again.")
    
    # reload every three seconds
    s = '''<html><head><meta HTTP-EQUIV=REFRESH CONTENT="3; URL='/StatusAndResults/'">
    <link rel="icon" href="/temp/static_images/favicon.ico" type="image/x-icon">
    <link rel="shortcut icon" href="/temp/static_images/favicon.ico" type="image/x-icon">
    </head><body>'''
    s += currentStatus
    s += '<br><br><br><br>'
    s += '<pre>'
    s += 'Elapsed time: ' + ConvertSecondsToHMS(time.time() - startTime) + ' (hh:mm:ss)'
    s += '\n'
    s += '\n'
    s += 'Current time on server: ' + time.asctime(time.localtime(time.time()))[:-5]
    s += '\n'
    s += 'Time of last update   : ' + time.asctime(time.localtime(timeStamp))[:-5]
    
    loadavg = os.getloadavg()
    s += '\n\n'
    s += 'Server load average for the past 1 minute:   ' + str(loadavg[0]) + '\n'
    s += 'Server load average for the past 5 minutes:  ' + str(loadavg[1]) + '\n'
    s += 'Server load average for the past 15 minutes: ' + str(loadavg[2]) + '\n\n'
    
    s += '</pre>'
    coreCount = str(multiprocessing.cpu_count())
    s += '''
<BR><BR>
<TABLE>
<TR><TD align=left>
Load < %s means the server cores are running with a light load.
</TD></TR>
<TR><TD align=left>
Load = %s means the server cores each average 100%% CPU with a single user.
</TD></TR>
<TR><TD align=left>
Load > %s means the server cores each average 100%% CPU with multiple users.
</TD></TR>
</TABLE>
''' % (coreCount, coreCount, coreCount)
    s += '</body></html>'
    
    return HttpResponse(s)


@cache_control(no_cache=True)
def LongRunningProcessView(request, inDimensionality, inEquationFamilyName='', inEquationName=''): # from urls.py, inDimensionality can only be '1', '2' or '3'
    import os, sys, time

    if -1 != request.path.find('FitEquation__1___/') or -1 != request.path.find('Equation/'): # redundant but explicit
        if -1 != request.path.find('UserDefinedFunction'):
            LRP = LongRunningProcess.FitUserDefinedFunction.FitUserDefinedFunction()
        elif -1 != request.path.find('User-Selectable Polyfunctional'):
            LRP = LongRunningProcess.FitUserSelectablePolyfunctional.FitUserSelectablePolyfunctional()
        elif -1 != request.path.find('User-Selectable Polynomial'):
            LRP = LongRunningProcess.FitUserSelectablePolynomial.FitUserSelectablePolynomial()
        elif -1 != request.path.find('User-Customizable Polynomial'):
            LRP = LongRunningProcess.FitUserCustomizablePolynomial.FitUserCustomizablePolynomial()
        elif -1 != request.path.find('User-Selectable Rational'):
            LRP = LongRunningProcess.FitUserSelectableRational.FitUserSelectableRational()
        elif -1 != request.path.find('Spline'):
            LRP = LongRunningProcess.FitSpline.FitSpline()
        else:
            LRP = LongRunningProcess.FitOneEquation.FitOneEquation()
    elif -1 != request.path.find('CharacterizeData/'):
        LRP = LongRunningProcess.CharacterizeData.CharacterizeData()        
    elif -1 != request.path.find('StatisticalDistributions/'):
        LRP = LongRunningProcess.StatisticalDistributions.StatisticalDistributions()
    elif -1 != request.path.find('FunctionFinder__1___/'):
        LRP = LongRunningProcess.FunctionFinder.FunctionFinder()        
    elif -1 != request.path.find('FunctionFinderResults/'):
        if request.method != 'GET': # send an error message
            return HttpResponse("The function finder results view was called incorrectly.")
        if 'RANK' not in list(request.GET.keys()): # send an error message
            return HttpResponse("The function finder results view was not called correctly.")
        try:
            rank = int(request.GET['RANK'])
        except:
            return HttpResponse('Incorrect call to function finder results view.')
        if rank < 1 or rank > 10000000: # must be between 1 and 10 million
            return HttpResponse('Call to function finder results view was incorrect.')
        LRP = LongRunningProcess.FunctionFinderResults.FunctionFinderResults()
        LRP.rank = rank
        
    else:
        return HttpResponse("I could not understand the web request.")
        
    #####################################################################
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #####################################################################

    LRP.inEquationName = urllib.parse.unquote(inEquationName)
    LRP.inEquationFamilyName = urllib.parse.unquote(inEquationFamilyName)
    LRP.dimensionality = int(inDimensionality)

    if CommonToAllViews(request): # any referrer blocks or web request checks processed here
        raise django.http.Http404

    if 'session_key_status' not in list(request.session.keys()):
        s = SessionStore()
        try: # database can lock, sleep and retry
            s.save()
        except:
            time.sleep(0.5)
            s.save()
        request.session['session_key_status'] = s.session_key
    LRP.session_key_status = request.session['session_key_status']

    if 'session_key_data' not in list(request.session.keys()):
        s = SessionStore()
        try: # database can lock, sleep and retry
            s.save()
        except:
            time.sleep(0.5)
            s.save()
        request.session['session_key_data'] = s.session_key
    LRP.session_key_data = request.session['session_key_data']

    if 'session_key_functionfinder' not in list(request.session.keys()):
        s = SessionStore()
        try: # database can lock, sleep and retry
            s.save()
        except:
            time.sleep(0.5)
            s.save()
        request.session['session_key_functionfinder'] = s.session_key
    LRP.session_key_functionfinder = request.session['session_key_functionfinder']

    # if this is not a POST, send an interface if needed
    if LRP.userInterfaceRequired:
        if request.method != 'POST':
            request.session['cookie_test'] = 1
            try:
                return render(request, LRP.interfaceString, LRP.CreateUnboundInterfaceForm(request))
                #return render_to_response(LRP.interfaceString, LRP.CreateUnboundInterfaceForm(request))
            except:
                return HttpResponse(repr(sys.exc_info()[0]) + '<br>' + repr(sys.exc_info()[1]))

    if 'cookie_test' not in list(request.session.keys()):
        return HttpResponse("This web site requires a temporary session cookie.  Please enable session cookies (or reload the home page) and try again.")

    if LRP.userInterfaceRequired:
        try:
            LRP.CreateBoundInterfaceForm(request)
        except:
            return HttpResponse(str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
        if not LRP.boundForm.is_valid():
            LRP.items_to_render = {}
            LRP.items_to_render['mainForm'] = LRP.boundForm
            LRP.items_to_render['EvaluateAtAPointForm'] = LRP.evaluationForm
            return render_to_response('zunzun/invalid_form_data.html', LRP.items_to_render)


    returnString = LRP.TransferFormDataToDataObject(request)
    if returnString:
        return HttpResponse(returnString)
    

    if -1 == request.path.find('FunctionFinderResults/') and LRP.equationInstance:
        errorString = LRP.CheckDataForZeroAndPositiveAndNegative()
        if errorString:
            return render_to_response('zunzun/generic_error.html', {'error':errorString})

    LRP.SetInitialStatusDataIntoSessionVariables(request)

    try: # database can lock, sleep and retry
        request.session.save()
    except:
        time.sleep(0.5)
        request.session.save()
    close_old_connections()

    processID_1 = os.fork()
    if processID_1 == 0: # child process, kill when done
        '''
        # daemon-ization did not help mod_wsgi number of processes slowly reducing, commenting out
        # decouple from parent and double fork
        # http://code.activestate.com/recipes/66012-fork-a-daemon-process-on-unix/
        os.setsid()
        os.umask(0)
        processID_2 = os.fork()
        if processID_2 != 0:
            sys.exit(0) # kill the intermediate now-unused process
        '''
        os.nice(LRP.reniceLevel)

        try:
            LRP.PerformAllWork()
        except:
            import traceback
            print('*** Site top-level exception from LRP', str(sys.exc_info()[0]) + '  ' + str(sys.exc_info()[1]))
            sys.stdout.flush()
        
            extraInfo = '\n\nrequest.META info:\n'
            for item in request.META:
                extraInfo += str(item) + ' : ' + str(request.META[item]) + '\n'
                
            print(traceback.format_exc())
            EmailMessage('Site Top-level exception from LRP',  traceback.format_exc() + '\n\n\n' + extraInfo, to = [settings.EXCEPTION_EMAIL_ADDRESS]).send()
            LRP.SaveDictionaryOfItemsToSessionStore('status', {'currentStatus':"An unknown exception has occurred, and an email with details has been sent to the site administrator. These are sometimes caused by taking the exponent of large numbers."})
        finally:
            time.sleep(1.0)
            if LRP.pool:
                LRP.pool.close()
                LRP.pool.join()
            os._exit(0) # kill this child process
        
    # using HTTP_HOST allows dev server
    return HttpResponseRedirect('http://' + request.META['HTTP_HOST'] + '/StatusAndResults/')


@cache_control(no_cache=True)
def FeedbackView(request):
    import datetime
    import os, sys, time
    
    if CommonToAllViews(request): # any referrer blocks or web request checks processed here
        raise django.http.Http404

    if request.method == 'POST':
        try:
            form = forms.FeedbackForm(request.POST)
        except:
            time.sleep(1.0)
            form = forms.FeedbackForm(request.POST)
        if not form.is_valid(): # validators added, see form definition
            items_to_render = {}
            items_to_render['mainForm'] = form
            return render_to_response('zunzun/invalid_form_data.html', items_to_render)
        msg = 'Email from ' + form.cleaned_data['emailAddress'] + '\n\nAt ' + str(datetime.datetime.now()) + "\n\n" + form.cleaned_data['feedbackText']
        EmailMessage('ZunZunSite3 Feedback Form', msg, to = [settings.FEEDBACK_EMAIL_ADDRESS]).send()

        return render_to_response('zunzun/feedback_reply.html', {})
    else: # not a POST
        return HttpResponseRedirect('/')


@cache_control(no_cache=True)
def HomePageView(request):
    import os, sys, time

    # whenever the home page is loaded, clear expired sessions
    SessionStore().clear_expired()

    # whenever the home page is loaded, make sure there is
    # space in the temp directory for newly created files    
    totalDirSize = 0
    dirInfo = []
    for item in os.listdir(settings.TEMP_FILES_DIR):
        itempath = os.path.join(settings.TEMP_FILES_DIR, item)
        if os.path.isfile(itempath):
            fileSize = os.path.getsize(itempath)
            fileMtime = os.path.getmtime(itempath) # to sort by creation time
            dirInfo.append([fileMtime, fileSize, item])
            totalDirSize += fileSize
    
    # approximately the max temp directory number of bytes
    maxSize = settings.MAX_TEMP_DIR_SIZE_IN_MBYTES * 1000000
    tempDir = settings.TEMP_FILES_DIR

    if totalDirSize > maxSize:
        totalReduction = 0
        reductionAmount = (totalDirSize - maxSize) + (maxSize * 0.25)
        dirInfo.sort() # delete oldest files first
        for fileItem in dirInfo:
            if totalReduction < reductionAmount:
                totalReduction += fileItem[1]
                try: # prevent possible exceptions from race conditions
                    os.remove(os.path.join(tempDir, fileItem[2]))
                except:
                    pass
            else:
                break

    # now start code for view generation
    if CommonToAllViews(request): # any referrer blocks or web request checks processed here
        raise django.http.Http404
    
    request.session['cookie_test'] = 1

    items_to_render = {}
    items_to_render['dim_to_spline_list'] = [['2',  pyeq3.Models_2D.Spline.Spline()], ['3',  pyeq3.Models_3D.Spline.Spline()]]
    items_to_render['dim_to_map_list'] = [['2', GetEquationInfoDictionary(2, 'Standard')], ['3', GetEquationInfoDictionary(3, 'Standard')]]
    items_to_render['header_text'] = 'ZunZunSite3 Online Curve Fitting<br>and Surface Fitting Web Site'
    items_to_render['feedbackForm'] = forms.FeedbackForm()
    items_to_render['loadavg'] = os.getloadavg()

    return render_to_response('zunzun/home_page.html', items_to_render)


@cache_control(no_cache=True)
def AllEquationsView(request, inDimensionality, inAllOrStandardOnly): # from urls.py, inDimensionality can only be '2' or '3'
    import os, sys, time
    
    if CommonToAllViews(request): # any referrer blocks or web request checks processed here
        raise django.http.Http404

    items_to_render = {}

    if '2' == inDimensionality:
        items_to_render['sortedEquationClassPropertiesList'] = GetEquationInfoDictionary(2, inAllOrStandardOnly)
    else:
        items_to_render['sortedEquationClassPropertiesList'] = GetEquationInfoDictionary(3, inAllOrStandardOnly)
    
    if inAllOrStandardOnly == 'All':
        items_to_render['header_text'] = 'ZunZunSite3 List Of All ' + inDimensionality + 'D Equations'
    else:
        items_to_render['header_text'] = 'ZunZunSite3 List Of All Standard ' + inDimensionality + 'D Equations'
        
    items_to_render['dimensionality'] = inDimensionality
    
    return render_to_response('zunzun/list_all_equations.html', items_to_render)


def GetEquationInfoDictionary(inDimensionality, inAllOrStandardOnly):
    import inspect
    
    if inDimensionality == 2:
        submodules = inspect.getmembers(pyeq3.Models_2D)
    else:
        submodules = inspect.getmembers(pyeq3.Models_3D)
        
    submoduleNameList = []
    for submodule in submodules:
        if inspect.ismodule(submodule[1]):
            submoduleNameList.append(submodule[0])
    submoduleNameList.sort()

    if inAllOrStandardOnly == 'Standard':
        extendedNameList = ['Default', 'Offset']
    else:
        extendedNameList = pyeq3.ExtendedVersionHandlers.extendedVersionHandlerNameList

    allEquationClassPropertiesList = []

    for submoduleName in submoduleNameList:
        for submodule in submodules:
            if inspect.ismodule(submodule[1]):
                if submodule[0] != submoduleName:
                    continue
                for extendedName in extendedNameList:
                    for equationClass in inspect.getmembers(submodule[1]):
                        if inspect.isclass(equationClass[1]):
                            
                            if equationClass[1].splineFlag or equationClass[1].userDefinedFunctionFlag:
                                continue
                            
                            # special case as user can select an "offset" flag on the user interface
                            if (equationClass[0] == 'UserSelectableRational' or equationClass[0] == 'UserSelectablePolyfunctional') and extendedName != 'Default': # only need to see default versions of these
                                continue
                                                                
                            try:
                                equation = equationClass[1]('SSQABS', extendedName)
                            except:
                                continue
                            
                            extendedSuffix = equation.extendedVersionHandler.__class__.__name__.split('_')[1]
                            
                            if equation.autoGenerateOffsetForm == False and -1 != extendedSuffix.find('Offset'):
                                continue
                            if equation.autoGenerateReciprocalForm == False and  -1 != extendedSuffix.find('Reciprocal'):
                                continue
                            if equation.autoGenerateInverseForms == False and  -1 != extendedSuffix.find('Inverse'):
                                continue
                            if equation.autoGenerateGrowthAndDecayForms == False and -1 != extendedSuffix.find('Growth'):
                                continue
                            if equation.autoGenerateGrowthAndDecayForms == False and -1 != extendedSuffix.find('Decay'):
                                continue
                        
                            temp = ClassForAttachingProperties()
                            
                            temp.submoduleName = submoduleName
                            temp.extendedName = extendedName
                            temp.name = equation.GetDisplayName()
                            temp.HTML = equation.GetDisplayHTML()
                            temp.webCitationLink = equation.webReferenceURL
                            temp.url_quote_name = urllib.parse.quote(temp.name)
                            if '<BR>' in temp.HTML.upper():
                                temp.multiLineHtmlFlag = True

                            # add item to dictionary
                            allEquationClassPropertiesList.append(temp)

    allEquationClassPropertiesList.sort(key=keyFunctionToSortListOfEquationPropertyClasses)
    for index in range(1, len(allEquationClassPropertiesList)):
        if index == 1:
            allEquationClassPropertiesList[index-1].firstItemInSubmoduleFlag = True
        else:
            if allEquationClassPropertiesList[index].submoduleName != allEquationClassPropertiesList[index-1].submoduleName:
                allEquationClassPropertiesList[index-1].lastItemInSubmoduleFlag = True
                allEquationClassPropertiesList[index].firstItemInSubmoduleFlag = True
                allEquationClassPropertiesList[index-1].lastItemInExtendedNameFlag = True
                allEquationClassPropertiesList[index].firstItemInExtendedNameFlag = True
            
        if index == 1:
            allEquationClassPropertiesList[index-1].firstItemInExtendedNameFlag = True
        else:
            if allEquationClassPropertiesList[index].extendedName != allEquationClassPropertiesList[index-1].extendedName:
                allEquationClassPropertiesList[index-1].lastItemInExtendedNameFlag = True
                allEquationClassPropertiesList[index].firstItemInExtendedNameFlag = True

        allEquationClassPropertiesList[len(allEquationClassPropertiesList)-1].lastItemInSubmoduleFlag = True
        allEquationClassPropertiesList[len(allEquationClassPropertiesList)-1].lastItemInExtendedNameFlag = True
            
    return allEquationClassPropertiesList


def CommonToAllViews(request):
    if request.META['REQUEST_METHOD'] not in ['GET', 'POST']:
        raise django.http.Http404
    return False # all OK


class ClassForAttachingProperties:
    multiLineHtmlFlag = False
    moduleName = 'moduleName'
    name = 'name'
    extendedName = 'extendedName'
    HTML = 'HTML'
    webCitationLink = ''
    url_quote_name = 'url_quote_name'
    firstItemInSubmoduleFlag = False
    firstItemInExtendedNameFlag = False
    lastItemInSubmoduleFlag = False
    lastItemInExtendedNameFlag = False


def keyFunctionToSortListOfEquationPropertyClasses(item):
    # logic is to sort for display in this order:
    # 1) submodule name
    # 2) extendedModuleName - Default first, then Offset, then others
    # 3) name

    # underscores sort first
    extendedName = item.extendedName
    if extendedName == 'Default':
        extendedName = '_Default'
    if extendedName == 'Offset':
        extendedName = '_Offset'
        
    return item.submoduleName + extendedName + item.name
