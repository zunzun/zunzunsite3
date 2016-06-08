import os, sys
import numpy
import math, matplotlib
matplotlib.use('Agg') # must be used prior to the next two statements
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import scipy, scipy.stats
import pyeq3
from scipy.stats.distributions import t


def DetermineOnOrOffFromString(in_String):
    tempString = in_String.split('_')[-1:][0].upper() # allows any amount of prefacing text
    if tempString == 'ON':
        return True
    return False


def DetermineScientificNotationFromString(inData, in_String):
    tempString = in_String.split('_')[-1:][0].upper() # allows any amount of prefacing text
    if tempString == 'ON':
        return True
    elif tempString == 'OFF':
        return False
    else: # must be AUTO
        minVal = numpy.abs(numpy.min(inData))
        maxVal = numpy.abs(numpy.max(inData))
        deltaVal = numpy.abs(maxVal - minVal)
        
        scientificNotation = False
        if (maxVal > 100.0) or (minVal < -100.0) or (deltaVal < .05):
            scientificNotation = True
    return scientificNotation

def CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_XName, in_YName, in_UseOffsetIfNeeded, in_X_UseScientificNotationIfNeeded, in_Y_UseScientificNotationIfNeeded, in_Left, in_Bottom, in_Right, in_Top): # default to lots of room around graph

    # a litle more room between x axis and tick mark labels, so not text overlap at the bottom left corner - set this before other calls
    matplotlib.rcParams['xtick.major.pad'] = 5 + (float(in_HeightInPixels) / 100.0) # minimum + some scaled
    matplotlib.rcParams['xtick.direction'] = 'out' # tick marks outside plot area
    matplotlib.rcParams['ytick.direction'] = 'out' # tick marks outside plot area
    
    matplotlib.rcParams['contour.negative_linestyle'] = 'solid' # only affects contour plots

    fig = plt.figure(figsize=(float(in_WidthInPixels ) / 100.0, float(in_HeightInPixels ) / 100.0), dpi=100)
    fig.patch.set_visible(False)
    fig.subplotpars.update(in_Left, in_Bottom, in_Right, in_Top)
    ax = fig.add_subplot(111, frameon=True)

    # white background, almost no border space
    fig.set_facecolor('w')

    xFormatter = fig.gca().xaxis.get_major_formatter()
    xFormatter._useOffset = in_UseOffsetIfNeeded
    xFormatter.set_scientific(in_X_UseScientificNotationIfNeeded)
    fig.gca().xaxis.set_major_formatter(xFormatter)

    yFormatter = fig.gca().yaxis.get_major_formatter()
    yFormatter._useOffset = in_UseOffsetIfNeeded
    yFormatter.set_scientific(in_Y_UseScientificNotationIfNeeded)
    fig.gca().yaxis.set_major_formatter(yFormatter)

    # Scale text to imagesize.  Text sizes originally determined at image size of 500 x 400
    heightRatioForTextSize = float(in_WidthInPixels) / 500.0
    widthRatioForTextSize = float(in_HeightInPixels) / 400.0
    if heightRatioForTextSize < widthRatioForTextSize:
        widthRatioForTextSize = heightRatioForTextSize
    if heightRatioForTextSize > widthRatioForTextSize:
        heightRatioForTextSize = widthRatioForTextSize
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(xlabel_i.get_fontsize() * heightRatioForTextSize) 
    xOffsetText = fig.gca().xaxis.get_offset_text()
    xOffsetText.set_fontsize(xOffsetText.get_fontsize() * heightRatioForTextSize * 0.9) 
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(ylabel_i.get_fontsize() * widthRatioForTextSize) 
    yOffsetText = fig.gca().yaxis.get_offset_text()
    yOffsetText.set_fontsize(yOffsetText.get_fontsize() * heightRatioForTextSize * 0.9) 
    
    x_label = ax.set_xlabel(in_XName)
    y_label = ax.set_ylabel(in_YName)

    x_label.set_size(x_label.get_size() * heightRatioForTextSize)
    y_label.set_size(y_label.get_size() * widthRatioForTextSize)

    # text uses relative position
    fWIP = float(in_WidthInPixels)
    fHIP = float(in_HeightInPixels)
    textWOffset = 25.0 # pixels
    textHOffset = 35.0 # pixels
    relativeWidthPos = (fWIP + textWOffset) / fWIP # plus
    relativeHeightPos = (fHIP - textHOffset) / fHIP # minus
    
    # for smallest graphs, do not "text brand" - looks ugly
    if in_WidthInPixels > 320:
        ax.text(relativeWidthPos, relativeHeightPos, 'zunzunsite',
                fontsize= 'xx-small',
                family= 'monospace',
                horizontalalignment='center',
                verticalalignment='center',
                rotation='vertical',
                transform=ax.transAxes)
    
    plt.grid(True) # call this just before returning

    return fig, ax

def YieldNewExtentsAndNumberOfMajor_X_TickMarks(fig, ax, in_WidthInPixels, in_HeightInPixels, in_OffsetUsed):
    # draw everything so items can be measured for size
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    
    # some preliminary info
    xLabelPoints = ax.set_xlabel(ax.get_xlabel()).get_window_extent().get_points() # [ [x,y], [x,y] ]
    yLabelPoints = ax.set_ylabel(ax.get_ylabel()).get_window_extent().get_points() # [ [x,y], [x,y] ], rotated 90 degrees
    xTickZeroPoints = ax.get_xticklabels()[0].get_window_extent().get_points()
    if xTickZeroPoints[0][0] < -150.0: # contour plots make this very negative, if so use next tick mark
        xTickZeroPoints = ax.get_xticklabels()[1].get_window_extent().get_points()
    maxXTickIndex = len(ax.get_xticklabels())-1 # sometimes matlab's max index tick mark has no text.  Not sure about Y ticks, check just in case
    if ax.get_xticklabels()[maxXTickIndex]._text == '':
        maxXTickIndex -= 1
    maxYTickIndex = len(ax.get_yticklabels())-1 # sometimes matlab's max index tick mark has no text.  Not sure about Y ticks, check just in case
    if ax.get_yticklabels()[maxYTickIndex]._text == '':
        maxYTickIndex -= 1
    xTickIndexPoints = ax.get_xticklabels()[maxXTickIndex].get_window_extent().get_points()
    yTickZeroPoints = ax.get_yticklabels()[0].get_window_extent().get_points()
    yTickIndexPoints = ax.get_yticklabels()[maxYTickIndex].get_window_extent().get_points()
    currentPoints = ax.bbox.get_points()
    maxLeft = currentPoints[0][0]
    maxBottom = currentPoints[0][1]
    maxRight = currentPoints[1][0]
    maxTop = currentPoints[1][1]
    
    # find the most left-ward location
    if xTickZeroPoints[0][0] < maxLeft:
        maxLeft = xTickZeroPoints[0][0]
    if yTickZeroPoints[0][0] < maxLeft:
        maxLeft = yTickZeroPoints[0][0]
    if yTickIndexPoints[0][0] < maxLeft:
        maxLeft = yTickIndexPoints[0][0]
    if xLabelPoints[0][0] < maxLeft:
        maxLeft = xLabelPoints[0][0]
    if yLabelPoints[0][0] < maxLeft: # 90 degrees
        maxLeft = yLabelPoints[0][0]

    # find the most right-ward location
    if xTickIndexPoints[1][0] > maxRight:
        maxRight = xTickIndexPoints[1][0]
    if xLabelPoints[1][0] > maxRight:
        maxRight = xLabelPoints[1][0]

    # find the most bottom-ward location
    if xTickZeroPoints[0][1] < maxBottom:
        maxBottom = xTickZeroPoints[0][1]
    if xLabelPoints[0][1] < maxBottom:
        maxBottom = xLabelPoints[0][1]
    if yLabelPoints[0][1] < maxBottom:
        maxBottom = yLabelPoints[0][1] 

    # find the most top-ward location
    if yTickIndexPoints[1][1] > maxTop:
        maxTop = yTickIndexPoints[1][1]
    if True == in_OffsetUsed: # could not find a better way to get this
        yp = ax.get_yticklabels()[0].get_window_extent().get_points() 
        maxTop += yp[1][1] - yp[0][1]

    newLeft = ax.bbox._bbox.get_points()[0][0] - (float(maxLeft) / float(in_WidthInPixels)) + 0.125
    newBottom = ax.bbox._bbox.get_points()[0][1] - (float(maxBottom) / float(in_HeightInPixels)) + 0.05
    newRight = ax.bbox._bbox.get_points()[1][0] + (1.0 - (float(maxRight) / float(in_WidthInPixels))) - 0.05
    newTop = ax.bbox._bbox.get_points()[1][1] + (1.0 - (float(maxTop) / float(in_HeightInPixels))) - 0.05

    # now redraw and check number of X tick marks
    canvas.draw()

    # Calculate major number of X tick marks based on label size
    totalWidth = 0.0
    maxWidth = 0.0
    numberOfMajor_X_TickMarks = len(ax.get_xticklabels())
    for i in range(maxXTickIndex):
        w = ax.get_xticklabels()[i].get_window_extent().get_points() # the drawn text bounding box corners as numpy array of [x,y], [x,y]
        width = w[1][0] - w[0][0]
        totalWidth += width
        if width > maxWidth:
            maxWidth = width
    if totalWidth > (0.6 * ((newRight - newLeft) * float(in_WidthInPixels))): # 0.6 for some spacing between tick labels
        numberOfMajor_X_TickMarks = int(math.floor((0.6 * ((newRight - newLeft) * float(in_WidthInPixels))) / maxWidth)) 

    if numberOfMajor_X_TickMarks < 2:
        numberOfMajor_X_TickMarks = 2

    return (newLeft, newBottom, newRight, newTop, numberOfMajor_X_TickMarks,)


def HistogramPlot_NoDataObject(in_DataToPlot, in_FileNameAndPath, in_DataName, in_FillColor, in_WidthInPixels, in_HeightInPixels, in_UseOffsetIfNeeded, in_UseScientificNotationIfNeeded, inPNGOnlyFlag, in_pdfFlag, in_distro, in_params):

    # decode ends of strings ('XYZ_ON', 'XYZ_OFF', 'XYZ_AUTO', etc.) to boolean values
    scientificNotation = DetermineScientificNotationFromString(in_DataToPlot, in_UseScientificNotationIfNeeded)
    useOffsetIfNeeded = DetermineOnOrOffFromString(in_UseOffsetIfNeeded)

    numberOfBins = len(in_DataToPlot) // 2
    if numberOfBins > 25:
        numberOfBins = 25
    if numberOfBins < 5:
        numberOfBins = 5

    # first with 0, 0, 1, 1
    title = 'Frequency'
    if in_pdfFlag:
        title = 'Normalized Frequency'
        
    fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataName, title, useOffsetIfNeeded, scientificNotation, False, 0.0, 0.0, 1.0, 1.0)
    
    # histogram of data
    n, bins, patches = ax.hist(in_DataToPlot, numberOfBins, facecolor=in_FillColor)
    
    # some axis space at the top of the graph
    ylim = ax.get_ylim()
    if ylim[1] == max(n):
        ax.set_ylim(0.0, ylim[1] + 1)

    newLeft, newBottom, newRight, newTop, numberOfMajor_X_TickMarks = YieldNewExtentsAndNumberOfMajor_X_TickMarks(fig, ax, in_WidthInPixels, in_HeightInPixels, False)

    # now with scaled
    title = 'Frequency'
    if in_pdfFlag:
        title = 'Normalized Frequency'
 
    fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataName, title, useOffsetIfNeeded, scientificNotation, False, newLeft, newBottom, newRight, newTop)
    
    # histogram of data
    normalized = False
    if in_pdfFlag:
        normalized = True
    n, bins, patches = ax.hist(in_DataToPlot, numberOfBins, facecolor=in_FillColor, normed=normalized)

    # if statistical distribution plot, show pdf
    if in_pdfFlag:
        xmin, xmax = ax.get_xlim()
        if ax.xaxis.get_majorticklocs()[0] < xmin:
            xmin = ax.xaxis.get_majorticklocs()[0]
        if ax.xaxis.get_majorticklocs()[len(ax.xaxis.get_majorticklocs()) - 1] > xmax:
            xmax = ax.xaxis.get_majorticklocs()[len(ax.xaxis.get_majorticklocs()) - 1]
        xmin = xmin + ((xmax - xmin) / 1000.0) # do not use new bounds, be ju-u-u-ust inside
        xmax = xmax - ((xmax - xmin) / 1000.0) # do not use new bounds, be ju-u-u-ust inside
        lin = numpy.linspace(xmin, xmax, 300)
        parms = in_params[:-2]
        pdf = in_distro.pdf(lin, *parms, loc = in_params[-2], scale = in_params[-1])
        ax.plot(lin, pdf)
    
    # some axis space at the top of the graph
    ylim = ax.get_ylim()
    if ylim[1] == max(n):
        ax.set_ylim(0.0, ylim[1] + 1)

    if  len(ax.get_xticklabels()) > numberOfMajor_X_TickMarks:
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(numberOfMajor_X_TickMarks))

    fig.savefig(in_FileNameAndPath[:-3] + 'png', format = 'png')
    if not inPNGOnlyFlag:
        fig.savefig(in_FileNameAndPath[:-3] + 'svg', format = 'svg')
        plt.close()


def ScatterPlotWithOptionalModel_NoDataObject(in_DataToPlot, in_FileNameAndPath, in_DataNameX, in_DataNameY, in_WidthInPixels, in_HeightInPixels,
                    in_Equation, in_UseOffsetIfNeeded, in_ReverseXY, in_X_UseScientificNotationIfNeeded, in_Y_UseScientificNotationIfNeeded, in_GraphBounds,
                    in_LogY, in_LogX, inPNGOnlyFlag, inConfidenceIntervalsFlag):

    # decode ends of strings ('XYZ_ON', 'XYZ_OFF', 'XYZ_AUTO', etc.) to boolean values
    scientificNotationX = DetermineScientificNotationFromString(in_DataToPlot[0], in_X_UseScientificNotationIfNeeded)
    scientificNotationY = DetermineScientificNotationFromString(in_DataToPlot[1], in_Y_UseScientificNotationIfNeeded)
    useOffsetIfNeeded = DetermineOnOrOffFromString(in_UseOffsetIfNeeded)
    reverseXY = DetermineOnOrOffFromString(in_ReverseXY)

    if in_Equation: # make model data for plotting, clipping at boundaries
        lowerXbound = in_GraphBounds[0]
        upperXbound = in_GraphBounds[1]

        if in_Equation.independentData1CannotContainNegativeFlag and lowerXbound < 0.0:
            lowerXbound = 0.0
        if in_Equation.independentData1CannotContainZeroFlag and lowerXbound == 0.0:
            lowerXbound = 1.0E-300
        if in_Equation.independentData1CannotContainPositiveFlag and upperXbound > 0.0:
            upperXbound = 0.0
        if in_Equation.independentData1CannotContainZeroFlag and upperXbound == 0.0:
            upperXbound = 1.0E-300

        xRange = numpy.arange(lowerXbound, upperXbound, (upperXbound - lowerXbound) / (20.0 * float(in_WidthInPixels + in_HeightInPixels))) # make this 'reverse-xy-independent'
        tempDataCache = in_Equation.dataCache
        
        in_Equation.dataCache = pyeq3.dataCache()
        in_Equation.dataCache.allDataCacheDictionary['IndependentData'] = numpy.array([xRange, xRange])
        in_Equation.dataCache.FindOrCreateAllDataCache(in_Equation)
        yRange = in_Equation.CalculateModelPredictions(in_Equation.solvedCoefficients, in_Equation.dataCache.allDataCacheDictionary)
        
        in_Equation.dataCache = tempDataCache

    if reverseXY:
        fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataNameX, in_DataNameY, useOffsetIfNeeded, scientificNotationY, scientificNotationX, 0.0, 0.0, 1.0, 1.0)
        ax.plot(numpy.array([in_GraphBounds[2], in_GraphBounds[3]]), numpy.array([in_GraphBounds[0], in_GraphBounds[1]])) # first ax.plot() is only with extents
        newLeft, newBottom, newRight, newTop, numberOfMajor_X_TickMarks = YieldNewExtentsAndNumberOfMajor_X_TickMarks(fig, ax, in_WidthInPixels, in_HeightInPixels, scientificNotationY or useOffsetIfNeeded)
        fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataNameX, in_DataNameY, useOffsetIfNeeded, scientificNotationY, scientificNotationX, newLeft, newBottom, newRight, newTop)
        
        if in_LogY == 'LOG' and in_LogX == 'LOG':
            loglinplot = ax.loglog
        elif in_LogY == 'LIN' and in_LogX == 'LOG':
            loglinplot = ax.semilogx
        elif in_LogY == 'LOG' and in_LogX == 'LIN':
            loglinplot = ax.semilogy
        else:
            loglinplot = ax.plot
        
        if  len(ax.get_xticklabels()) > numberOfMajor_X_TickMarks:
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(numberOfMajor_X_TickMarks))
            
        loglinplot(numpy.array([in_GraphBounds[2], in_GraphBounds[3]]), numpy.array([in_GraphBounds[0], in_GraphBounds[1]]), visible=False)
        loglinplot(in_DataToPlot[1], in_DataToPlot[0], 'o', markersize=3)

        if (min(in_DataToPlot[0]) < in_GraphBounds[0]) or (max(in_DataToPlot[0]) > in_GraphBounds[1]):
            matplotlib.pyplot.ylim(in_GraphBounds[0], in_GraphBounds[1])
        if (min(in_DataToPlot[1]) < in_GraphBounds[2]) or (max(in_DataToPlot[1]) > in_GraphBounds[3]):
            matplotlib.pyplot.xlim(in_GraphBounds[2], in_GraphBounds[3])
        
    else:
        fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataNameX, in_DataNameY, useOffsetIfNeeded, scientificNotationX, scientificNotationY, 0.0, 0.0, 1.0, 1.0)
        ax.plot(numpy.array([in_GraphBounds[0], in_GraphBounds[1]]), numpy.array([in_GraphBounds[2], in_GraphBounds[3]])) # first ax.plot() is only with extents
        newLeft, newBottom, newRight, newTop, numberOfMajor_X_TickMarks = YieldNewExtentsAndNumberOfMajor_X_TickMarks(fig, ax, in_WidthInPixels, in_HeightInPixels, scientificNotationY or useOffsetIfNeeded)
        fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataNameX, in_DataNameY, useOffsetIfNeeded, scientificNotationX, scientificNotationY, newLeft, newBottom, newRight, newTop)
        
        if in_LogY == 'LOG' and in_LogX == 'LOG':
            loglinplot = ax.loglog
        elif in_LogY == 'LIN' and in_LogX == 'LOG':
            loglinplot = ax.semilogx
        elif in_LogY == 'LOG' and in_LogX == 'LIN':
            loglinplot = ax.semilogy
        else:
            loglinplot = ax.plot
        
        if  len(ax.get_xticklabels()) > numberOfMajor_X_TickMarks:
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(numberOfMajor_X_TickMarks))
            
        loglinplot(numpy.array([in_GraphBounds[0], in_GraphBounds[1]]), numpy.array([in_GraphBounds[2], in_GraphBounds[3]]), visible=False)
        loglinplot(in_DataToPlot[0], in_DataToPlot[1], 'o', markersize=3)
                            
        if (min(in_DataToPlot[0]) <= in_GraphBounds[0]) or (max(in_DataToPlot[0]) >= in_GraphBounds[1]):
            matplotlib.pyplot.xlim(in_GraphBounds[0], in_GraphBounds[1])
        if (min(in_DataToPlot[1]) <= in_GraphBounds[2]) or (max(in_DataToPlot[1]) >= in_GraphBounds[3]):
            matplotlib.pyplot.ylim(in_GraphBounds[2], in_GraphBounds[3])

        if in_Equation:
            booleanMask = yRange > matplotlib.pyplot.ylim()[0]
            booleanMask &= (yRange < matplotlib.pyplot.ylim()[1])
            booleanMask &= (xRange > matplotlib.pyplot.xlim()[0])
            booleanMask &= (xRange < matplotlib.pyplot.xlim()[1])
            loglinplot(xRange[booleanMask], yRange[booleanMask], 'k') # model on top of data points

            if inConfidenceIntervalsFlag:
                # now calculate confidence intervals for new test x-series
                # http://support.sas.com/documentation/cdl/en/statug/63347/HTML/default/viewer.htm#statug_nlin_sect026.htm
                # http://www.staff.ncl.ac.uk/tom.holderness/software/pythonlinearfit
                mean_x = numpy.mean(in_DataToPlot[0])			# mean of x
                n = in_Equation.nobs		    # number of samples in origional fit
                
                if len(in_Equation.dataCache.allDataCacheDictionary['Weights']):
                    t_value = scipy.stats.t.ppf(0.975, in_Equation.df_e_weighted) # (1.0 - (a/2)) is used for two-sided t-test critical value, here a = 0.05
                                        
                    confs = t_value * numpy.sqrt((in_Equation.sumOfSquaredErrors_weighted/in_Equation.df_e_weighted)*(1.0/n + (numpy.power((xRange-mean_x),2)/
                                            ((numpy.sum(numpy.power(in_DataToPlot[0],2)))-n*(numpy.power(mean_x,2))))))
                else:
                    t_value = scipy.stats.t.ppf(0.975, in_Equation.df_e) # (1.0 - (a/2)) is used for two-sided t-test critical value, here a = 0.05
                                        
                    confs = t_value * numpy.sqrt((in_Equation.sumOfSquaredErrors/in_Equation.df_e)*(1.0/n + (numpy.power((xRange-mean_x),2)/
                                            ((numpy.sum(numpy.power(in_DataToPlot[0],2)))-n*(numpy.power(mean_x,2))))))

                # get lower and upper confidence limits based on predicted y and confidence intervals
                upper = yRange + abs(confs)
                lower = yRange - abs(confs)
                
                booleanMask &= (numpy.array(yRange) < 1.0E290)
                booleanMask &= (upper < 1.0E290)
                booleanMask &= (lower < 1.0E290)
                
                # color scheme improves visibility on black background lines or points
                loglinplot(xRange[booleanMask], lower[booleanMask], linestyle='solid', color='white')
                loglinplot(xRange[booleanMask], upper[booleanMask], linestyle='solid', color='white')
                loglinplot(xRange[booleanMask], lower[booleanMask], linestyle='dashed', color='blue')
                loglinplot(xRange[booleanMask], upper[booleanMask], linestyle='dashed', color='blue')

    fig.savefig(in_FileNameAndPath[:-3] + 'png', format = 'png')
    if not inPNGOnlyFlag:
        fig.savefig(in_FileNameAndPath[:-3] + 'svg', format = 'svg')
    plt.close()    


def ContourPlot_NoDataObject(X, Y, Z, in_DataToPlot, in_FileNameAndPath, in_DataNameX, in_DataNameY, in_WidthInPixels, in_HeightInPixels,
                    in_UseOffsetIfNeeded, in_X_UseScientificNotationIfNeeded, in_Y_UseScientificNotationIfNeeded, inPNGOnlyFlag, in_Rectangle=None):

    # decode ends of strings ('XYZ_ON', 'XYZ_OFF', 'XYZ_AUTO', etc.) to boolean values
    scientificNotationX = DetermineScientificNotationFromString(in_DataToPlot[0], in_X_UseScientificNotationIfNeeded)
    scientificNotationY = DetermineScientificNotationFromString(in_DataToPlot[1], in_Y_UseScientificNotationIfNeeded)
    useOffsetIfNeeded = DetermineOnOrOffFromString(in_UseOffsetIfNeeded)

    fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataNameX, in_DataNameY, useOffsetIfNeeded, scientificNotationY, scientificNotationX, 0.0, 0.0, 1.0, 1.0)

    CS = plt.contour(X, Y, Z, 1, colors='k')
    
    newLeft, newBottom, newRight, newTop, numberOfMajor_X_TickMarks = YieldNewExtentsAndNumberOfMajor_X_TickMarks(fig, ax, in_WidthInPixels, in_HeightInPixels, scientificNotationY or useOffsetIfNeeded)
    fig, ax = CommonPlottingCode(in_WidthInPixels, in_HeightInPixels, in_DataNameX, in_DataNameY, useOffsetIfNeeded, scientificNotationY, scientificNotationX, newLeft, newBottom, newRight, newTop)

    if in_Rectangle:
        ax.add_patch(in_Rectangle)

    ax.plot(in_DataToPlot[0], in_DataToPlot[1], 'o', color='0.8', markersize=3) # now that autoscaling is done, use all data for scatterplot - draw these first so contour lines overlay.  Color=number is grayscale

    numberOfContourLines = int(math.ceil(math.sqrt(in_WidthInPixels + in_HeightInPixels) / 3.0))
    CS = plt.contour(X, Y, Z, numberOfContourLines, colors='k')
    plt.clabel(CS, fontsize=8, inline=1, fmt='%1.3g') # minimum legible font size
                
    fig.savefig(in_FileNameAndPath[:-3] + 'png', format = 'png')
    if not inPNGOnlyFlag:
        fig.savefig(in_FileNameAndPath[:-3] + 'svg', format = 'svg')
    plt.close()    


def ContourPlot(in_DataObject, in_FileNameAndPath):
    gridResolution = (in_DataObject.graphWidth + in_DataObject.graphHeight) / 20

    gxmin = in_DataObject.gxmin
    gxmax = in_DataObject.gxmax
    gymin = in_DataObject.gymin
    gymax = in_DataObject.gymax


    if in_DataObject.equation.independentData1CannotContainNegativeFlag and gxmin < 0.0:
        gxmin = 0.0
    if in_DataObject.equation.independentData1CannotContainZeroFlag and gxmin == 0.0:
        gxmin = 1.0E-300
    if in_DataObject.equation.independentData1CannotContainPositiveFlag and gxmax > 0.0:
        gxmax = 0.0
    if in_DataObject.equation.independentData1CannotContainZeroFlag and gxmax == 0.0:
        gxmax = 1.0E-300

        if in_DataObject.equation.independentData2CannotContainNegativeFlag and gymin < 0.0:
            gymin = 0.0
        if in_DataObject.equation.independentData2CannotContainZeroFlag and gymin == 0.0:
            gymin = 1.0E-300
        if in_DataObject.equation.independentData2CannotContainPositiveFlag and gymax > 0.0:
            gymax = 0.0
        if in_DataObject.equation.independentData2CannotContainZeroFlag and gymax == 0.0:
            gymax = 1.0E-300

    deltax = (gxmax - gxmin) / float(gridResolution)
    deltay = (gymax - gymin) / float(gridResolution)
    xRange = numpy.arange(gxmin, gxmax + deltax, deltax)
    yRange = numpy.arange(gymin, gymax + deltay/2.0, deltay)

    minZ = min(in_DataObject.DependentDataArray)
    maxZ = max(in_DataObject.DependentDataArray)

    X, Y = numpy.meshgrid(xRange, yRange)
    
    boundingRectangle = matplotlib.patches.Rectangle([gxmin, gymin], gxmax - gxmin, gymax - gymin, facecolor=(0.975, 0.975, 0.975), edgecolor=(0.9, 0.9, 0.9))
    

    Z = []
    tempDataCache = in_DataObject.equation.dataCache
    for i in range(len(X)):
        in_DataObject.equation.dataCache = pyeq3.dataCache()
        in_DataObject.equation.dataCache.allDataCacheDictionary['IndependentData'] = numpy.array([X[i], Y[i]])
        in_DataObject.equation.dataCache.FindOrCreateAllDataCache(in_DataObject.equation)
        Z.append(in_DataObject.equation.CalculateModelPredictions(in_DataObject.equation.solvedCoefficients, in_DataObject.equation.dataCache.allDataCacheDictionary))        
    in_DataObject.equation.dataCache = tempDataCache
        
    Z = numpy.array(Z)
    Z = numpy.clip(Z, minZ, maxZ)
    tempData = [in_DataObject.IndependentDataArray[0], in_DataObject.IndependentDataArray[1], in_DataObject.DependentDataArray]
    
    ContourPlot_NoDataObject(X, Y, Z, tempData, in_FileNameAndPath, in_DataObject.IndependentDataName1, in_DataObject.IndependentDataName2,
                                                in_DataObject.graphWidth, in_DataObject.graphHeight, 'UseOffset_ON', 'ScientificNotation_X_AUTO', 'ScientificNotation_Y_AUTO', in_DataObject.pngOnlyFlag, boundingRectangle)
    plt.close()


def HistogramPlot(in_DataObject, in_FileNameAndPath, in_DataName, in_DataToPlot, in_pdfFlag=0):
    distro = None
    params = None
    if in_pdfFlag:
        distro = getattr(scipy.stats, in_DataObject.fittedStatisticalDistributionsList[in_DataObject.distributionIndex][1]['distributionName']) # convert distro name back into a distribution object
        params = in_DataObject.fittedStatisticalDistributionsList[in_DataObject.distributionIndex][1]['fittedParameters']
        
    HistogramPlot_NoDataObject(in_DataToPlot, in_FileNameAndPath, in_DataName,
                               'lightgrey', in_DataObject.graphWidth, in_DataObject.graphHeight, 'UseOffset_ON',
                               'ScientificNotation_AUTO', in_DataObject.pngOnlyFlag, in_pdfFlag, distro, params)
    plt.close()


def ScatterPlot(in_DataObject, FileName, XAxisName, XAxisData, ScientificNotationX, YAxisName, YAxisData, ScientificNotationY, UseDataObjectGraphRangeOrCalculate, Range1, Range2, in_LogY, in_LogX):
    
    if UseDataObjectGraphRangeOrCalculate: # for data graphs scale with user-supplied values.  For error graphs calculate
        if Range1 == "X":
            gxmin = in_DataObject.gxmin
            gxmax = in_DataObject.gxmax
        if Range1 == "Y":
            gxmin = in_DataObject.gymin
            gxmax = in_DataObject.gymax
        if Range1 == "Z":
            gxmin = in_DataObject.gzmin
            gxmax = in_DataObject.gzmax
            
        if Range2 == "X":
            gymin = in_DataObject.gxmin
            gymax = in_DataObject.gxmax
        if Range2 == "Y":
            gymin = in_DataObject.gymin
            gymax = in_DataObject.gymax
        if Range2 == "Z":
            gymin = in_DataObject.gzmin
            gymax = in_DataObject.gzmax
            
    else: # use 1/20 of delta (error graphs, etc.)
        xmax = max(XAxisData)
        xmin = min(XAxisData)
        ymax = max(YAxisData)
        ymin = min(YAxisData)

        deltax = xmax - xmin
        deltay = ymax - ymin

        gxmin = xmin - (deltax/20.0)
        gxmax = xmax + (deltax/20.0)
        gymin = ymin - (deltay/20.0)
        gymax = ymax + (deltay/20.0)

    ScatterPlotWithOptionalModel_NoDataObject([XAxisData, YAxisData], FileName, XAxisName, YAxisName,
                    in_DataObject.graphWidth, in_DataObject.graphHeight, None, 'UseOffset_ON',
                    'reverseXY_OFF', 'XScientificNotation_' + ScientificNotationX, 'YScientificNotation_' + ScientificNotationY,
                    [gxmin, gxmax, gymin, gymax],
                    in_LogY, in_LogX, in_DataObject.pngOnlyFlag,
                    False)
    plt.close()

def ModelAndScatterPlot(in_DataObject, FileName, XAxisName, YAxisName, ReverseXY, in_LogY, in_LogX, inConfidenceIntervalsFlag):
    if ReverseXY:
        reverseXY_string = 'reverseXY_ON'
    else:
        
        reverseXY_string = 'reverseXY_OFF'
        
    gxmin = in_DataObject.gxmin
    gxmax = in_DataObject.gxmax
    gymin = in_DataObject.gymin
    gymax = in_DataObject.gymax

    ScatterPlotWithOptionalModel_NoDataObject([in_DataObject.IndependentDataArray[0], in_DataObject.DependentDataArray], FileName,
                    XAxisName, YAxisName, in_DataObject.graphWidth, in_DataObject.graphHeight, in_DataObject.equation, 'UseOffset_ON',
                    reverseXY_string, 'XScientificNotation_' + in_DataObject.ScientificNotationX, 'YScientificNotation_' + in_DataObject.ScientificNotationY,
                    [gxmin, gxmax, gymin, gymax],
                    in_LogY, in_LogX, in_DataObject.pngOnlyFlag,
                    inConfidenceIntervalsFlag)
    plt.close()

