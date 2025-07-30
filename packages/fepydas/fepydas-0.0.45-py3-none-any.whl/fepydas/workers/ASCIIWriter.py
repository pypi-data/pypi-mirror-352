#!/usr/bin/python3
import numpy


class BaseWriter:
  def __init__(self, filename):
    self.f = open(filename,"wb")

class MultiSpectrumWriter(BaseWriter):
  def __init__(self, filename):
    super().__init__(filename)
    self.data = []
    self.names = []
    self.units = []
    self.identifiers = []

  def addX(self, data, identifier):
    self.data.append(data.values)
    self.names.append(data.datatype.name)
    self.units.append(data.datatype.unit)
    self.identifiers.append(identifier)
    if data.errors is not None:
      self.data.append(data.errors)
      self.names.append(data.datatype.name)
      self.units.append(data.datatype.unit)
      self.identifiers.append(identifier+"_Error")

  def addY(self, data, identifier):
    if len(data.values) < len(self.data[0]):
      vals = numpy.zeros(self.data[0].shape)
      vals[0:len(data.values)] = data.values
    else:
      vals = data.values
    self.data.append(vals)   
    self.names.append(data.datatype.name)
    self.units.append(data.datatype.unit)
    self.identifiers.append(identifier)
    if data.errors is not None:
      self.data.append(data.errors)
      self.names.append(data.datatype.name)
      self.units.append(data.datatype.unit)
      self.identifiers.append(identifier+"_Error")
 
  def addMultiY(self, Ys, labels, commonlabel=""):
    for i,Y in enumerate(Ys):
      self.data.append(Y)
      self.identifiers.append("{0}".format(labels[i])+commonlabel)

  def addSpectrum(self, spectrum, identifier="Y"):
    self.addX(spectrum.axis, "X")
    self.addY(spectrum.data, identifier)

  def addSpectra(self, spectra):
    self.addX(spectra.axis, "X")
    self.addMultiY(spectra.data.values, spectra.keys.values)
  
  def addFit(self, spectrum, fit, convolve=False):
    if convolve:
      y = spectrum.evaluateConvolutionFit(fit)
    else:
      y = fit.evaluate(self.data[0])
    self.addY(y, fit.__class__.__name__)

  def addFits(self, fit):
    self.addMultiY(fit.batchEvaluate(self.data[0]), self.headers[1:], fit.__class__.__name__)

  def write(self, fmt="%4f"):
    data = numpy.array(self.data).T
    self.f.write(("\t".join(self.identifiers)+"\n").encode("utf-8"))
    self.f.write(("\t".join(self.names)+"\n").encode("utf-8"))
    self.f.write(("\t".join(self.units)+"\n").encode("utf-8"))
    numpy.savetxt(self.f, data, fmt=fmt, delimiter="\t")
    self.f.close()

class SpectrumWithFitWriter(MultiSpectrumWriter):
  def __init__(self, filename, spectrum, fit, withIRF=False):
    super().__init__(filename)
    self.addSpectrum(spectrum, identifier="Data")
    if withIRF: 
      self.addY(spectrum.IRF, identifier="IRF")
    self.addFit(spectrum, fit, withIRF)
    self.write()
   

