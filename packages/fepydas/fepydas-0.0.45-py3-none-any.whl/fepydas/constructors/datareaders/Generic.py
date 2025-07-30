#!/usr/bin/python3
import numpy
import pickle
from fepydas.datatypes.Data import Data1D,Data2D,DataType
import fepydas.datatypes as datatypes
from fepydas.datatypes.Dataset import SpectraWithCommonIRF,Spectrum,SpectrumWithIRF,SpectrumSeries,PLE
from fepydas.constructors.datareaders.Proprietary import BeckerHicklHistogram, PicoHarpHistogram, TimeHarpHistogram


def GenericXY(x,xname,xunit,y,yname,yunit):
  return Spectrum(Data1D(x,DataType(xname,xunit)),Data1D(x,DataType(xname,xunit)))


def GenericXMultiY(x,xname,xunit,y,yname,yunit,keys,keyname,keyunit):
  return SpectrumSeries(Data1D(x,DataType(xname,xunit)),Data1D(keys,DataType(keyname,keyunit)),Data2D(y,DataType(yname,yunit)))


def ASCII(filename, delimiter="\t",missing_values='', skip_header=0):
  data = numpy.genfromtxt(filename,delimiter=delimiter,missing_values=missing_values,skip_header=skip_header,encoding="Latin-1")
  print("ASCII File {0}. Shape:{1}".format(filename,data.shape))
  return data

def ASCII_SpectrumRowSeries(filename, xType:DataType, keyType:DataType, valueType:DataType):
  data = ASCII(filename)
  xAxis = Data1D(data[0,:],xType)
  keyAxis = Data1D(numpy.arange(len(data[:,0])-1),keyType)
  vals = Data2D(data[1:,:],valueType)
  return SpectrumSeries(xAxis,keyAxis,vals)

def ASCII_Histogram(filename,resolution):
  data = ASCII(filename,delimiter=" ",skip_header=10)
  xAxis = Data1D(numpy.arange(len(data))*resolution,datatypes.TIME_ns)
  yAxis = Data1D(data,datatypes.COUNTS)
  return Spectrum(xAxis,yAxis)

def Binary(filename):
    return pickle.load(open(filename,"rb"))

def HistogramReader(filename):
    print("Reading {0}".format(filename))
    filetype = filename[-3:]
    if filetype=="phu":
       time, data = PicoHarpHistogram(filename)
    elif filetype=="thi":
       time, data = TimeHarpHistogram(filename)
    elif filetype=="sdt":
       time, data = BeckerHicklHistogram(filename)
    else:
       print("Unsupported Histogram Type: .{0}".format(filetype))
    axis = Data1D(time,datatypes.TIME_ns)
    data = Data1D(data,datatypes.COUNTS)
    return axis, data

def Histogram(filename):
    axis, data = HistogramReader(filename)
    return Spectrum(axis,data)    

def HistogramWithIRF(filename,filenameIRF):
    histoTime, histoData = HistogramReader(filename)
    IRFTime, IRFData = HistogramReader(filenameIRF)
    if numpy.sum(histoTime.values-IRFTime.values)>0:
        print("Warning, IRF and Decay Histogram Time Axes not compatible!!")
    return SpectrumWithIRF(histoTime, histoData, IRFData)

def HistogramsWithCommonIRF(filenames, filenameIRF):
    IRFTime, IRFData = HistogramReader(filenameIRF)
    data = numpy.ndarray(shape=(len(filenames),len(IRFTime.values)))
    for i, n in enumerate(filenames):
      histoTime, histoData = HistogramReader(n)
      if numpy.sum(histoTime.values-IRFTime.values)>0:
        print("Warning, IRF and Decay Histogram Time Axes not compatible for {0}!!".format(n))
      data[i,:] = histoData.values
      filenames[i] = filenames[i].split("/")[-1]
    CombinedData = Data2D(data,IRFData.datatype)
    return SpectraWithCommonIRF(IRFTime, CombinedData, IRFData, Data1D(filenames,DataType("Filename","")))
