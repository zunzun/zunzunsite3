import string, numpy, scipy.stats

class DataObject:

    def __init__(self):
        self.dataPointSize3D = 0
        self.pngOnlyFlag = False
        
        self.IndependentDataName1 = None
        self.IndependentDataName2 = None
        self.DependentDataName = None
        
        self.IndependentDataArray = None
        self.DependentDataArray = None
        
        self.predictedList = []
        self.absoluteErrorList = []
        self.relativeErrorList = []
        self.percentErrorList = []
        self.statistics = {}
        
        self.equation = None
        self.text = None
        self.dimensionality = None

        self.xmin = None
        self.xmax = None
        self.deltax = None
        self.gxmin = None
        self.gxmax = None
        self.gdeltax = None
        self.xmin_p05 = None
        self.xmax_p05 = None
        self.deltax_p05 = None
        self.gxmin_p05 = None
        self.gxmax_p05 = None
        self.gdeltax_p05 = None

        self.ymin = None
        self.ymax = None
        self.deltay = None
        self.gymin = None
        self.gymax = None
        self.gdeltay = None
        self.ymin_p05 = None
        self.ymax_p05 = None
        self.deltay_p05 = None
        self.gymin_p05 = None
        self.gymax_p05 = None
        self.gdeltay_p05 = None

        self.zmin = None
        self.zmax = None
        self.deltaz = None
        self.gzmin = None
        self.gzmax = None
        self.gdeltaz = None
        self.zmin_p05 = None
        self.zmax_p05 = None
        self.deltaz_p05 = None
        self.gzmin_p05 = None
        self.gzmax_p05 = None
        self.gdeltaz_p05 = None
        
        self.abs_err_min_p05 = None
        self.abs_err_min_p05 = None
        self.delta_abs_err_p05 = None
        self.gabs_err_min_p05 = None
        self.gabs_err_max_p05 = None
        self.gdelta_abs_err_p05 = None

        self.rel_err_min_p05 = None
        self.rel_err_min_p05 = None
        self.delta_rel_err_p05 = None
        self.grel_err_min_p05 = None
        self.grel_err_max_p05 = None
        self.gdelta_rel_err_p05 = None
        
        self.per_err_min_p05 = None
        self.per_err_min_p05 = None
        self.delta_per_err_p05 = None
        self.gper_err_min_p05 = None
        self.gper_err_max_p05 = None
        self.gdelta_per_err_p05 = None

        self.graphWidth = None
        self.graphHeight = None
        self.animationWidth = None
        self.animationHeight = None
        self.gridResolution = None
        self.grid_dX = None
        self.grid_dY = None

        self.ScientificNotationX = "AUTO"
        self.ScientificNotationY = "AUTO"
        self.ScientificNotationZ = "AUTO"


    def CalculateStatisticsForList(self, preString, tempdata):
        # must at least have max and min
        self.statistics[preString + "_min"] = min(tempdata)
        self.statistics[preString + "_max"] = max(tempdata)

        # these we can live without
        try:
            temp = scipy.mean(tempdata)
            self.statistics[preString + "_mean"] = temp
        except:
            pass
        try:
            temp = scipy.stats.sem(tempdata)
            self.statistics[preString + "_sem"] = temp
        except:
            pass
        try:
            temp = scipy.median(tempdata)
            self.statistics[preString + "_median"] = temp
        except:
            pass
        try:
            temp = scipy.var(tempdata)
            self.statistics[preString + "_var"] = temp
        except:
            pass
        try:
            temp = scipy.std(tempdata)
            self.statistics[preString + "_std"] = temp
        except:
            pass
        try:
            temp = scipy.stats.skew(tempdata)
            self.statistics[preString + "_skew"] = temp
        except:
            pass
        try:
            temp = scipy.stats.kurtosis(tempdata)
            self.statistics[preString + "_kurtosis"] = temp
        except:
            pass


    def CalculateDataStatistics(self):
        tempdata = self.IndependentDataArray[0]
        # if max == min, add a little error
        if max(tempdata) == min(tempdata):
            if abs(tempdata[0]) < 1.0E-100:
                tempdata[0] = 1.0E-110
            else:
                tempdata[0] += tempdata[0] / 1.0E6

        self.CalculateStatisticsForList("1", tempdata)

        # do we need dim 2 stats?
        if self.dimensionality > 1:
            if self.dimensionality == 2:
                tempdata = self.DependentDataArray
            else:
                tempdata = self.IndependentDataArray[1]
            # if max == min, add a little error
            if max(tempdata) == min(tempdata):
                if abs(tempdata[0]) < 1.0E-100:
                    tempdata[0] = 1.0E-110
                else:
                    tempdata[0] += tempdata[0] / 1.0E6

            self.CalculateStatisticsForList("2", tempdata)

        # do we need dim 3 stats?
        if self.dimensionality == 3:
            tempdata = self.DependentDataArray
            # if max == min, add a little error
            if max(tempdata) == min(tempdata):
                if abs(tempdata[0]) < 1.0E-100:
                    tempdata[0] = 1.0E-110
                else:
                    tempdata[0] += tempdata[0] / 1.0E6


            self.CalculateStatisticsForList("3", tempdata)


    def CalculateErrorStatistics(self):
        
        # calculate model predictions and errors
        self.equation.CalculateModelErrors(self.equation.solvedCoefficients, self.equation.dataCache.allDataCacheDictionary)

        # absolute error statistics
        self.CalculateStatisticsForList("abs_err", self.equation.modelAbsoluteError)
        
        # relative error statistics
        if self.equation.dataCache.DependentDataContainsZeroFlag == False:
            self.CalculateStatisticsForList("rel_err", self.equation.modelRelativeError)
            self.CalculateStatisticsForList("per_err", self.equation.modelRelativeError)

        #_p05 is for error plot axes, etc.
        self.abs_err_min_p05 = self.statistics['abs_err_min']
        self.abs_err_max_p05 = self.statistics['abs_err_max']
        self.delta_abs_err_p05 = self.abs_err_max_p05 - self.abs_err_min_p05
        self.gabs_err_min_p05 = self.abs_err_min_p05 - (self.delta_abs_err_p05 * 0.05)
        self.gabs_err_max_p05 = self.abs_err_max_p05 + (self.delta_abs_err_p05 * 0.05)
        self.gdelta_abs_err_p05 = self.gabs_err_max_p05 - self.gabs_err_min_p05

        # relative error statistics
        if self.equation.dataCache.DependentDataContainsZeroFlag == 0:
            self.rel_err_min_p05 = self.statistics['rel_err_min']
            self.rel_err_max_p05 = self.statistics['rel_err_max']
            self.delta_rel_err_p05 = self.rel_err_max_p05 - self.rel_err_min_p05
            self.grel_err_min_p05 = self.rel_err_min_p05 - (self.delta_rel_err_p05 * 0.05)
            self.grel_err_max_p05 = self.rel_err_max_p05 + (self.delta_rel_err_p05 * 0.05)
            self.gdelta_rel_err_p05 = self.grel_err_max_p05 - self.grel_err_min_p05
            
            self.per_err_min_p05 = self.statistics['per_err_min']
            self.per_err_max_p05 = self.statistics['per_err_max']
            self.delta_per_err_p05 = self.per_err_max_p05 - self.per_err_min_p05
            self.gper_err_min_p05 = self.per_err_min_p05 - (self.delta_per_err_p05 * 0.05)
            self.gper_err_max_p05 = self.per_err_max_p05 + (self.delta_per_err_p05 * 0.05)
            self.gdelta_per_err_p05 = self.gper_err_max_p05 - self.gper_err_min_p05


    def CalculateGraphBoundaries(self):
        #_p05 is for error plot axes, etc.
        self.xmin_p05 = self.statistics['1_min']
        self.xmax_p05 = self.statistics['1_max']
        self.deltax_p05 = self.xmax_p05 - self.xmin_p05
        self.gxmin_p05 = self.xmin_p05 - (self.deltax_p05 * 0.05)
        self.gxmax_p05 = self.xmax_p05 + (self.deltax_p05 * 0.05)
        self.gdeltax_p05 = self.gxmax_p05 - self.gxmin_p05

        self.ymin_p05 = self.statistics['2_min']
        self.ymax_p05 = self.statistics['2_max']
        self.deltay_p05 = self.ymax_p05 - self.ymin_p05
        self.gymin_p05 = self.ymin_p05 - (self.deltay_p05 * 0.05)
        self.gymax_p05 = self.ymax_p05 + (self.deltay_p05 * 0.05)
        self.gdeltay_p05 = self.gymax_p05 - self.gymin_p05

        if self.dimensionality == 3:
            self.zmin_p05 = self.statistics['3_min']
            self.zmax_p05 = self.statistics['3_max']
            self.deltaz_p05 = self.zmax_p05 - self.zmin_p05
            self.gzmin_p05 = self.zmin_p05 - (self.deltaz_p05 * 0.05)
            self.gzmax_p05 = self.zmax_p05 + (self.deltaz_p05 * 0.05)
            self.gdeltaz_p05 = self.gzmax_p05 - self.gzmin_p05

        if self.Extrapolation_x < 98.0: # 99.0 means Manual Scaling
            self.xmin = self.statistics['1_min']
            self.xmax = self.statistics['1_max']
            self.deltax = self.xmax - self.xmin
            self.gxmin = self.xmin - (self.deltax * self.Extrapolation_x)
            self.gxmax = self.xmax + (self.deltax * self.Extrapolation_x)
            self.gdeltax = self.gxmax - self.gxmin
        else:
            self.xmin = self.Extrapolation_x_min
            self.xmax = self.Extrapolation_x_max
            self.deltax = self.xmax - self.xmin
            self.gxmin = self.xmin
            self.gxmax = self.xmax
            self.gdeltax = self.gxmax - self.gxmin

        if self.Extrapolation_y < 98.0: # 99.0 means Manual Scaling
            self.ymin = self.statistics['2_min']
            self.ymax = self.statistics['2_max']
            self.deltay = self.ymax - self.ymin
            self.gymin = self.ymin - (self.deltay * self.Extrapolation_y)
            self.gymax = self.ymax + (self.deltay * self.Extrapolation_y)
            self.gdeltay = self.gymax - self.gymin
        else:
            self.ymin = self.Extrapolation_y_min
            self.ymax = self.Extrapolation_y_max
            self.deltay = self.ymax - self.ymin
            self.gymin = self.ymin
            self.gymax = self.ymax
            self.gdeltay = self.gymax - self.gymin

        if self.dimensionality == 3:
            if self.Extrapolation_z < 98.0: # 99.0 means Manual Scaling
                self.zmin = self.statistics['3_min']
                self.zmax = self.statistics['3_max']
                self.deltaz = self.zmax - self.zmin
                self.gzmin = self.zmin - (self.deltaz * self.Extrapolation_z)
                self.gzmax = self.zmax + (self.deltaz * self.Extrapolation_z)
                self.gdeltaz = self.gzmax - self.gzmin
            else:
                self.zmin = self.Extrapolation_z_min
                self.zmax = self.Extrapolation_z_max
                self.deltaz = self.zmax - self.zmin
                self.gzmin = self.zmin
                self.gzmax = self.zmax
                self.gdeltaz = self.gzmax - self.gzmin
                
        self.gridResolution = (self.graphHeight + self.graphWidth) // 40
        self.grid_dX = self.gdeltax / float(self.gridResolution - 1)
        self.grid_dY = self.gdeltay / float(self.gridResolution - 1)


    def hex_char_to_decimal(self, character):
        """Used to turn hex input into decimal values"""
        for index in range(len(string.hexdigits)):
            if (character == string.hexdigits[index]) and (index < 16): # 0-9, a-f
                return index
            if (character == string.hexdigits[index]) and (index > 15): # A-F
                return index - 6
