import numpy
import os
from fepydas.datatypes.Dataset import Spectrum, PLE, SpectrumSeries, SparseSpectrumMap
from fepydas.constructors.datareaders.Generic import ASCII
from fepydas.datatypes.Data import Data1D, Data2D, Data3D, DataType
import fepydas.datatypes as datatypes

def Automatic(filename):
  file = open(filename, encoding="Latin-1")
  done = False
  headers = {}
  while not done:
    line = file.readline().strip().split(" = ")
    #print(line)
    if line[0]=="HEADER":
      done = True
    else:
      headers[line[0]] = line[1:]
  #Header Done
  if headers["Measurement Type"][0] == "Mapscan Cube":
    #For Mapscans, the Header is followed by a section showing the mapping using X and O.
    map_x = int(headers["Map Dimension X"][0])
    map_y = int(headers["Map Dimension Y"][0])
    map_x0 = float(headers["Map Edge Position X (µm)"][0])
    map_y0 = float(headers["Map Edge Position Y (µm)"][0])
    map_pitch = float(headers["Map Pitch (µm)"][0])
    file.readline() #---
    mapping = numpy.ndarray(shape=(map_x,map_y,2), dtype=numpy.float64)
    bool_mask = numpy.ndarray(shape=(map_x,map_y), dtype=bool)
    mask = numpy.ndarray(shape=(map_x,map_y), dtype=numpy.float64)
    num = 0
    for i in range(map_y):
      line = file.readline()
      for j in range(map_x):
        mapping[j,map_y-1-i]=[map_x0+j*map_pitch, map_y0+(map_y-1-i)*map_pitch]
        if (line[j]=="X"):
          bool_mask[j,map_y-1-i] = True
          num+=1
        else:
          bool_mask[j,map_y-1-i] = False
    file.readline() #---
    
    names = file.readline().strip().split("\t")
    units = file.readline().strip().split("\t")
    
    endOfAxis = False
    axisData = []
    while not endOfAxis:
      value = file.readline().strip()
      if value == "---":
        break
      axisData.append(float(value.split("\t")[0]))
    axis = Data1D(numpy.array(axisData),DataType(names[0],units[0]))

    raw = numpy.fromfile(file, dtype = numpy.dtype(">u8"))[1:] #64bit uint big-endian
    actual_num = int(numpy.floor(len(raw)/len(axis.values)))
    data = numpy.ndarray(shape=(actual_num, len(axis.values)))
    #It seems that this array is transposed?
    data = raw.reshape((len(axis.values), actual_num)).T
    n = 0
    for i in range(map_x):
      for j in range(map_y):
        if bool_mask[i,j]:
          if n < actual_num: #Ignore missing pixels
            mask[i,j] = n
          else:
            mask[i,j] = numpy.nan
          n+=1
        else:
          mask[i,j] = numpy.nan
    sparsemap = SparseSpectrumMap(axis, Data2D(data.astype(numpy.float64), datatypes.COUNTS), Data3D(mapping, datatypes.POS_um), Data2D(mask, datatypes.NUMBER), None, headers)
    if int(headers["Dark Frames"][0])>0:
      #Has been corrected and is offset by 1000
      if "Dark Offset" in headers.keys():
        sparsemap.data.values -= int(headers["Dark Offset"][0])
      else:
        sparsemap.data.values -= 1000
    return sparsemap
  else:
    names = file.readline().strip().split("\t")
    units = file.readline().strip().split("\t")
    length = len(headers)+3
    file.close()
    data = ASCII(filename, skip_header=length).T
    if (data[0,0] == numpy.inf or data[0,0] == -numpy.inf):
      axis = Data1D(data[1,:],DataType(names[1],units[1]))
    else:
      axis = Data1D(data[0,:],DataType(names[0],units[0]))
    if headers["Measurement Type"][0] == "Series":
      #2D
      values = Data2D(data[2:,:],datatypes.COUNTS)
      if int(headers["Dark Frames"][0])>0:
        #Has been corrected and is offset by 1000
        if "Dark Offset" in headers.keys():
          values.values -= int(headers["Dark Offset"][0])
        else:
          values.values-=1000
      if headers["Measurement Type"][1] == "PLE Xe Arc Lamp":
        dtype = DataType("Excitation Wavelength","nm")
      else:
        if len(units)>2:
          dtype = DataType(headers["Measurement Type"][1],units[2])
        else:
          dtype = DataType(headers["Measurement Type"][1],"a.u.")
      keys = Data1D(numpy.array(names[2:2+values.values.shape[0]]).astype(numpy.float64),dtype)
      if int(headers["Dark Frames"][0])>0 and int(headers["Dark Offset"][0]) == 0:
        #This is a Time Series of Dark Spectra, the last Dark Spectrum is the AVG used for correct
        keyvals = numpy.arange(1,int(headers["Dark Frames"][0])+2)
        keys.values = keyvals.astype(str)
        keys.values[-1] = "Average"
      if headers["Measurement Type"][1] == "PLE Xe Arc Lamp":
        return PLE(axis,keys,values,None,None,headers)
      else:
        if "Power Track" in headers.keys() and (headers["Power Track"][0] == "Record" or headers["Power Track"][0] == "Correct"):
          powers = Data1D(numpy.array(units[2+values.values.shape[0]:2+2*values.values.shape[0]]).astype(numpy.float64),DataType("Power","mW"))
        else:
          powers = None
        return SpectrumSeries(axis,keys,values,headers,powers)
    elif headers["Measurement Type"][0] == "PLE Response":
      values = Data1D(data[1,:],DataType(names[1],units[1]))
      return Spectrum(axis, values, headers)
    elif headers["Measurement Type"][0] == "Histogram":
      values = Data1D(data[1,:],datatypes.COUNTS)
      return Spectrum(axis,values, headers)
    else:
      #1D
      values = Data1D(data[2,:],datatypes.COUNTS)
      return Spectrum(axis, values, headers)
