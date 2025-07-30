#!/usr/bin/python3
import numpy
from pylab import *
from matplotlib.colors import *
from fepydas.datatypes.Data import Data,Data1D,Data2D, Data3D
from fepydas.datatypes.Dataset import Spectrum,SpectrumWithIRF,SpectrumSeries, Map
from fepydas.workers.Fit import Fit

class BasePlot:
  def __init__(self, polar=False):
    self.figure = figure()
    self.bottom = self.figure.add_subplot(111, polar=polar)
  
  def legend(self):
    self.bottom.legend()

  def show(self):
    show()

  def save(self, filename):
    self.figure.savefig(filename)

  def setXAxis(self, axis: Data1D):
    self.bottom.set_xlabel("{0} ({1})".format(axis.datatype.name, axis.datatype.unit))
 
  def setXRange(self, xmin, xmax):
    self.bottom.set_xlim(xmin,xmax)
 
  def setYRange(self, ymin, ymax):
    self.bottom.set_ylim(ymin,ymax)

  def setXLog(self):
    self.bottom.set_xscale("log")

  def setYLog(self):
    self.bottom.set_yscale("log")

  def setYAxis(self, data: Data):
    self.bottom.set_ylabel("{0} ({1})".format(data.datatype.name, data.datatype.unit))

class Plot1D(BasePlot):
  def __init__(self, axis: Data1D, polar=False):
    super().__init__(polar=polar)
    if polar:
      axis.values = axis.values/360*2*numpy.pi
    self.setXAxis(axis)
  def plotLine(self, x, y, label=None, linewidth=2, color=None):
    self.bottom.plot(x, y, label=label, linewidth=linewidth, color=color)
  def plotPoints(self, x, y, xerr=None, yerr=None, label=None, color=None):
    self.bottom.errorbar(x, y, xerr=xerr, yerr=yerr, label=label, fmt="o", alpha=0.2, color=color)

class Plot1DSingleAxis(Plot1D):
  def __init__(self, axis: Data1D, polar=False):
    super().__init__(axis, polar=polar)
    self.axis = axis    
  def addLine(self, data: ndarray, label=None, linewidth=2, color=None):
    self.plotLine(self.axis.values[0:len(data)], data, label=label, linewidth=linewidth, color=color)
  def addPoints(self, data: ndarray, errors = None, label=None, color=None):
    self.plotPoints(self.axis.values, data, self.axis.errors, errors, label=label, color=color)
  def addLines(self, data, labels):
    for i in range(data.shape[0]):
      self.plotLine(self.axis.values, data[i], label=labels[i])
    
class Plot1DMultiAxis(Plot1D):
  def __init__(self, axis: Data1D, data: Data1D):
    super().__init__(axis)
    self.setYAxis(data)
  def addLine(self, axis: Data1D, data: Data1D, label=None):
    #TODO: Compare Units
    self.plotLine(axis.values, data.values, label=label)

  def addPoints(self, axis: Data1D, data: Data1D, label=None):
    #TODO: Compare Units
    self.plotPoints(axis.values, data.values, label=label)

class MultiSpectrumScatterPlot(Plot1DMultiAxis):
  def __init__(self, spectra, labels):
    super().__init__(spectra[0].axis,spectra[0].data)
    for i, spectrum in enumerate(spectra):
      self.addPoints(spectrum.axis,spectrum.data,labels[i])

class Plot1DSingleLine(Plot1DSingleAxis):
  def __init__(self, axis: Data1D, data: Data1D, label=None):
    super().__init__(axis)
    self.setYAxis(data)
    self.addLine(data.values, label=label)

class Plot1DSingleScatter(Plot1DSingleAxis):
  def __init__(self, axis: Data1D, data: Data1D):
    super().__init__(axis)
    self.setYAxis(data)
    self.addPoints(data.values, data.errors)

class Plot1DMultiLineSingleAxis(Plot1DSingleAxis):
  def __init__(self, axis: Data1D, keys: Data1D, data: Data2D, polar=False, cmap=None, norm=None):
    super().__init__(axis, polar=polar)
    self.setYAxis(data)
    for i,key in enumerate(keys.values):
      if cmap and norm:
        self.addLine(data.values[i], key, color=cmap(norm(float(key))))
      else:
        self.addLine(data.values[i], key)

class Plot1DMultiScatterSingleAxis(Plot1DSingleAxis):
  def __init__(self, axis: Data1D, keys: Data1D, data: Data2D, polar=False, cmap=None, norm=None):
    super().__init__(axis, polar=polar)
    self.setYAxis(data)
    for i,key in enumerate(keys.values):
      if cmap and norm:
        self.addPoints(data.values[i], key, color=cmap(norm(float(key))))
      else:
        self.addPoints(data.values[i], key)

class SpectrumPlot(Plot1DSingleLine):
  def __init__(self, spectrum: Spectrum, label = None):
    super().__init__(spectrum.axis, spectrum.data, label=label)
  def addSpectrum(self, spectrum, label=None):
    self.addLine(spectrum.data.values, label=label)

class HistoPlot(Plot1D):
  def __init__(self, spectrum: Spectrum, label=None, n=100, bins=None):
    super().__init__(spectrum.data) #In a histogram, the data values form the axis
    if bins is not None:
      n, bins, patches = hist(spectrum.data.values.flatten(),bins=bins)
    else:
      n, bins, patches = hist(spectrum.data.values.flatten(),n)
    self.data = n

class SpectrumScatterPlot(Plot1DSingleScatter):
  def __init__(self, spectrum: Spectrum):
    super().__init__(spectrum.axis, spectrum.data)

class SpectrumScatterPlotWithFit(SpectrumScatterPlot):
  def __init__(self, spectrum: Spectrum, fit: Fit):
    super().__init__(spectrum)
    self.addLine(fit.evaluate(spectrum.axis.values))

class SpectrumWithIRFPlot(Plot1DSingleScatter):
  def __init__(self, spectrum: SpectrumWithIRF):
    super().__init__(spectrum.axis, spectrum.data)
    self.addLine(spectrum.getExtendedIRF())

class SpectrumSeriesPlot(Plot1DMultiLineSingleAxis):
  def __init__(self, spectra: SpectrumSeries, polar=False, cmap=None, norm=None):
    if (cmap and not norm) or norm=="Default":
      #The default norm is [min,max] -> [0,1]
      norm = Normalize(vmin=numpy.amin(spectra.keys.values), vmax=numpy.amax(spectra.keys.values))
    if norm and not cmap:
      #The default cmap
      cmap = LinearSegmentedColormap.from_list('my_colormap',["black","red","green","blue","white"],1000)
    super().__init__(spectra.axis, spectra.keys, spectra.data, polar=polar, cmap=cmap, norm=norm)

class SpectrumSeriesScatterPlot(Plot1DMultiScatterSingleAxis):
  def __init__(self, spectra: SpectrumSeries, polar=False, cmap=None, norm=None):
    if (cmap and not norm) or norm=="Default":
      #The default norm is [min,max] -> [0,1]
      norm = Normalize(vmin=numpy.amin(spectra.keys.values), vmax=numpy.amax(spectra.keys.values))
    if norm and not cmap:
      #The default cmap
      cmap = LinearSegmentedColormap.from_list('my_colormap',["black","red","green","blue","white"],1000)
    super().__init__(spectra.axis, spectra.keys, spectra.data, polar=polar, cmap=cmap, norm=norm)

class Plot2D(BasePlot):
  def __init__(self, axis, keys):
    super().__init__()
    self.setXAxis(axis)
    self.setYAxis(keys)

  def setZAxis(self, data: Data):
    self.colorbar.set_label("{0} ({1})".format(data.datatype.name, data.datatype.unit))
    self.colorbar.minorticks_on()

class ContourPlot(Plot2D):
  def __init__(self, spectra: SpectrumSeries, log = False):
    super().__init__(spectra.axis, spectra.keys)
    cmap = LinearSegmentedColormap.from_list('my_colormap',["black","red","green","blue","white"],1000)
    extent = [spectra.axis.values[0],spectra.axis.values[-1],spectra.keys.values[0],spectra.keys.values[-1]]
    if log:
      values = numpy.log10(spectra.data.values+0.001)
    else:
      values = spectra.data.values
    image = imshow(values,interpolation="none",cmap=cmap,origin="lower",aspect="auto",extent=extent)
    
class ContourMapPlot(Plot2D):
  def __init__(self, map: Map, log = False, colors=["black","red","orange","yellow","green","blue","white"], zRange=None):
    x, y = map.mapping.extractAxes()
    super().__init__(x, y)
    cmap = LinearSegmentedColormap.from_list('my_colormap',colors,1000)
    cmap.set_over("white")
    cmap.set_under("black")
    cmap.set_bad("violet")
    extent = [x.values[0],x.values[-1],y.values[0],y.values[-1]]
    if log:
      values = numpy.log10(map.data.values.T+0.001)
    else:
      values = map.data.values.T
    if zRange:
      zmin=zRange[0]
      zmax=zRange[1]
    else:
      zmin=None
      zmax=None
    image = imshow(values,interpolation="none",cmap=cmap,origin="lower",aspect="auto",extent=extent,vmin=zmin,vmax=zmax)
    self.colorbar = self.figure.colorbar(image, cmap=cmap)#,  ticks=range(len(colors)))
    self.setZAxis(map.data)
    
