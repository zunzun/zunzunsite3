import os, sys

import numpy
import pyeq3

import matplotlib
matplotlib.use('Agg') # immediately following the "import matplotlib" statement, web only

from mpl_toolkits.mplot3d import Axes3D # 3D apecific
from matplotlib import cm # to colormap from blue to red
import matplotlib.pyplot as plt


def SurfacePlot(dataObject, inFileName):
    # raw data for scatterplot
    x_data = dataObject.IndependentDataArray[0]
    y_data = dataObject.IndependentDataArray[1]
    z_data = dataObject.DependentDataArray

    # create X, Y, Z mesh grid for surface plot
    xModel = numpy.linspace(min(x_data), max(x_data), 20)
    yModel = numpy.linspace(min(y_data), max(y_data), 20)
    X, Y = numpy.meshgrid(xModel, yModel)
    
    tempcache = dataObject.equation.dataCache # temporarily store cache
    dataObject.equation.dataCache = pyeq3.dataCache()
    dataObject.equation.dataCache.allDataCacheDictionary['IndependentData'] = numpy.array([X, Y])
    dataObject.equation.dataCache.FindOrCreateAllDataCache(dataObject.equation)
    Z = dataObject.equation.CalculateModelPredictions(dataObject.equation.solvedCoefficients, dataObject.equation.dataCache.allDataCacheDictionary)
    dataObject.equation.dataCache = tempcache # restore cache

    # matplotlib specific code for the plots
    fig = plt.figure(figsize=(float(dataObject.graphWidth) / 100.0, float(dataObject.graphHeight) / 100.0), dpi=100)
    fig.patch.set_visible(True)
    ax = fig.gca(projection='3d')

    ax.view_init(elev=dataObject.altimuth3D, azim=dataObject.azimuth3D)    
    
    # create a surface plot using the X, Y, Z mesh data created above
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=1, antialiased=True)

    # create a scatter plot of the raw data
    if dataObject.dataPointSize3D == 0.0: # auto
        ax.scatter(x_data, y_data, z_data)
    else:
        ax.scatter(x_data, y_data, z_data, s=dataObject.dataPointSize3D)

    ax.set_title("Surface Plot") # add a title for surface plot
    ax.set_xlabel(dataObject.IndependentDataName1) # X axis data label
    ax.set_ylabel(dataObject.IndependentDataName2) # Y axis data label
    ax.set_zlabel(dataObject.DependentDataName) # Z axis data label

    if not inFileName:
        return [fig, ax, plt] # for use in creating animations
    else:
        fig.savefig(inFileName[:-3] + 'png', format = 'png')
        if not dataObject.pngOnlyFlag: # function finder results are png-only
            fig.savefig(inFileName[:-3] + 'svg', format = 'svg', )
        plt.close('all')


def ScatterPlot3D(dataObject, inFileName):
    fig = plt.figure(figsize=(float(dataObject.graphWidth) / 100.0, float(dataObject.graphHeight) / 100.0), dpi=100)
    fig.patch.set_visible(True)
    ax = fig.gca(projection='3d')
    
    ax.view_init(elev=dataObject.altimuth3D, azim=dataObject.azimuth3D)    

    x_data = dataObject.IndependentDataArray[0]
    y_data = dataObject.IndependentDataArray[1]
    z_data = dataObject.DependentDataArray
    
    if dataObject.dataPointSize3D == 0.0: # auto
        ax.scatter(x_data, y_data, z_data)
    else:
        ax.scatter(x_data, y_data, z_data, s=dataObject.dataPointSize3D)

    ax.set_title('Scatter Plot') # add a title for surface plot
    ax.set_xlabel(dataObject.IndependentDataName1) # X axis data label
    ax.set_ylabel(dataObject.IndependentDataName2) # Y axis data label
    ax.set_zlabel(dataObject.DependentDataName) # Z axis data label

    if not inFileName:
        return [fig, ax, plt] # for use in creating animations
    else:
        fig.savefig(inFileName[:-3] + 'png', format = 'png')
        fig.savefig(inFileName[:-3] + 'svg', format = 'svg')
        plt.close('all')
