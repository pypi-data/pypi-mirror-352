#!/usr/bin/python3
from copy import deepcopy
import numpy
import pickle

from fepydas.datatypes.Data import Data, Data1D, Data2D, Data3D, Response, VacuumCorrection
from fepydas.datatypes import NUMBER
from fepydas.workers.Fit import LimitedGaussianFit, GaussianFit, CalibrationFit, Fit, LinearFit, AutomaticCalibration
from fepydas.workers.ASCIIWriter import MultiSpectrumWriter

from sklearn.decomposition import NMF, PCA, LatentDirichletAllocation
from sklearn.cluster import SpectralClustering

from scipy.interpolate import griddata

class BaseDataset:
  def saveBinary(self, filename):
    f = open(filename,"bw")
    pickle.dump(self,f)
    f.close()

class Dataset(BaseDataset):
  def __init__(self, axis: Data1D, data: Data, metadata = None):
    self.metadata = metadata
    self.axis = axis
    self.data = data

  def applyAxisTransformation(self, transformation):
    self.axis.values = transformation.apply(self.axis.values)
    print("Applied Axis Transformation")
    
  def applyVacuumCorrection(self, temperature=20, pressure=101325, humidity=0, co2=610):
    vac = VacuumCorrection(temperature, pressure, humidity, co2)
    self.axis.values = vac.apply(self.axis.values)

  def convertToEnergy(self, unit="eV"):
    self.axis.convertToEnergy(unit)
    self.data.applyJacobianTransformation(self.axis)

  def antiBloom(self, over, width=1, reverse=False):
    self.data.antiBloom(over, width=width, reverse=reverse)

  def cutAxis(self, minVal, maxVal):
    idx1, idx2 = self.axis.cutAndGetIndexRange(minVal,maxVal)
    self.data.cut(idx1,idx2)

  def cutAxisByIdx(self, minIdx, maxIdx):
    self.axis.cut(minIdx,maxIdx)
    self.data.cut(minIdx,maxIdx)

  def divideBySpectrum(self, spectrum):
    self.data.divideBy(spectrum.data.values)

class Spectrum(Dataset):
  def __init__(self, axis: Data1D, data: Data1D, metadata=None):
    super().__init__(axis,data,metadata)

  def export(self,filename):
    msw = MultiSpectrumWriter(filename)
    msw.addSpectrum(self)
    msw.write()

  def identifyPeaks(self, threshold=10, width=10):
    derivative = numpy.diff(self.data.values)
    derivative.resize(self.data.values.shape)
    nonflat = derivative != 0
    zerocrossings = numpy.diff(numpy.sign(derivative)) != 0
    zerocrossings.resize(self.data.values.shape)
    noiseLevel = self.data.values > numpy.average(self.data.values)*threshold
    peaks = zerocrossings * noiseLevel * nonflat
    print("{0} peaks detected".format(numpy.sum(peaks)))
    indeces = numpy.where(peaks)[0]
    idxRanges = []
    for i, idx in enumerate(indeces):
      if idx+width>len(self.axis.values) or idx-width<0:
        continue
      idxRanges.append([idx-width, idx+width])
    return idxRanges
    
  def normalize(self):
    self.data.normalize()

  def toPlot(self):
    from fepydas.constructors.Plots import SpectrumPlot
    return SpectrumPlot(self)

  def toScatterPlot(self):
    from fepydas.constructors.Plots import SpectrumScatterPlot
    return SpectrumScatterPlot(self)

class SpectrumSeries(Dataset):
  def __init__(self, axis:Data1D, keys:Data1D, data:Data2D, metadata=None, power=None):
    super().__init__(axis,data,metadata)
    self.keys = keys
    self.power = power
  
  def average(self, despike_method=None, despike_cutoff=1):
    return Spectrum(self.axis, self.data.average(despike_method,despike_cutoff))

  def collapse(self, filter=None):
    return Spectrum(self.axis, self.data.collapse(filter))

  def collapseDominatingCluster(self, maxClusters = None):
    averages, cluster, resp = self.performGMM(maxClusters=maxClusters)
    dominatingCluster = numpy.bincount(cluster).argmax()
    keep = numpy.where(cluster==dominatingCluster)
    return self.collapse(filter=keep)

  def cutKeys(self, min, max):
    keys = numpy.where((self.keys.values>=min) & (self.keys.values<=max))[0]
    self.keys.values = self.keys.values[keys]
    self.data.values = self.data.values[keys,:]
    
  def interpSpikes(self, despike_method=None, despike_cutoff=1, interp_method=None):
    self.data.interpSpikes(despike_method, despike_cutoff, interp_method)
                       
  def export(self, filename):
    writer = MultiSpectrumWriter(filename)
    writer.addSpectra(self)
    writer.write()

  def filterByIntegral(self, threshold=0.5):
    integrals = self.data.integrate()
    max = numpy.amax(integrals.values)
    filter = numpy.where(integrals.values/max > threshold)[0]
    self.data.values = self.data.values[filter,:]
    self.keys.values = self.keys.values[filter]
    
  def findDominatingComponents(self, n = 1, algo="NMF"):
    if algo=="NMF":
      decomp = NMF(n_components = n)
    elif algo=="PCA":
      decomp = PCA(n_components = n)
    elif algo=="LDA":
      decomp = LatentDirichletAllocation(n_components = n)
    return self.fitDominatingComponents(decomp)
    
  def fit(self, fitter:Fit):
    fitter.batchFit(self.axis.values, self.data.values)
    
  def fitDominatingComponents(self, decomp):
    decomp.fit(self.data.values)
    return decomp

  def getDataValues(self):
    return self.data.values
  
  def fitMixture(self, n=2, nmf=None):
    data = self.getDataValues()
    

    if nmf is not None:
      #pcaWorker = NMF()
      #pcaWorker.fit(data)
      #np = numpy.where(pcaWorker.explained_variance_ratio_ > pca)[0][-1]
      data = NMF(n_components = nmf).fit_transform(data)
      #print("PCA reduced complexity to {0} components".format(len(pcaWorker.explained_variance_ratio_)))

    aff = numpy.zeros(shape=(data.shape[0],data.shape[0]))
    for i in range(data.shape[0]):
      for j in range(data.shape[0]):
        aff[i,j] = numpy.dot(data[i,:],data[j,:])

    gmm = SpectralClustering(affinity="precomputed", n_jobs=-1, eigen_solver="amg", n_clusters=n)
    gmm.fit(aff)

    return gmm

  def getDominatingComponent(self, algo="PCA"):
    decomp = self.findDominatingComponents(n=1, algo=algo)
    return Spectrum(self.axis, Data1D(decomp.components_[0], self.data.datatype))

  def getDominatingComponents(self, algo="PCA", n=2):
    decomp = self.findDominatingComponents(n=n, algo=algo)
    return decomp, SpectrumSeries(self.axis, Data1D(range(n), NUMBER), Data2D(decomp.components_, self.data.datatype))

  def getProjection(self, decomp):
    return SpectrumSeries(self.keys, Data1D(range(len(decomp.components_)), NUMBER), Data2D(decomp.transform(self.data.values).T, self.data.datatype))

  def removeComponents(self, decomp):
    self.data.values -= decomp.transform(self.data.values) @ decomp.components_
  
  def removeDominatingComponents(self, n=1, algo="NMF"):
    decomp = self.findDominatingComponents(n=n, algo=algo)
    self.removeComponents(decomp)
    return decomp

  def highDynamicRange(self, max=0.99, zmin=None):
    if self.data.values.shape[0] == 1:
      #nothing to do here
      return Spectrum(deepcopy(self.axis), Data1D(self.data.values.flatten(), self.data.datatype))
    #calculate weights
    zmax = (numpy.amax(self.data.values)*max) 
    if zmin is None:
      zmin = (numpy.amin(self.data.values))
    zfloor = numpy.full_like(self.data.values, zmin)
    zceil = numpy.full_like(self.data.values, zmax)
    zcenter, zrange = (zmax+zmin)/2, (zmax-zmin)/2
    weights =(zrange - numpy.abs((numpy.maximum(numpy.minimum(self.data.values,zceil),zfloor) - zcenter))) #Low weight for low (under-exposed) or high (over-exposed) values, high weight for medium values

    #calculate mappings
    num = len(self.keys.values)
    crossweights = numpy.zeros((num,num,len(self.data.values[0,:])))
    for i in range(num):
      for j in range(num):
        crossweights[i,j,:] = numpy.multiply(weights[i,:],weights[j,:])
    integratedCWs = numpy.sum(crossweights, axis=2)
    idxs = numpy.flip(numpy.argsort(numpy.sum(integratedCWs, axis=1)))
  
    
    def linearProjection(dataIn, dataRef, crossweights):
      return dataIn*numpy.average(dataRef/dataIn, weights=crossweights)

    mapped = numpy.zeros((num))
    mapped[idxs[0]] = 1

    for i in range(len(idxs)-1):
      idx = idxs[i+1]
      usableCWs = numpy.multiply(integratedCWs[idx,:],mapped)
      best = numpy.argsort(usableCWs)[-1]
      self.data.values[idx,:] = linearProjection(self.data.values[idx,:],self.data.values[best,:], crossweights[idx,best,:])
      print("mapped",idx,"to",best)
      mapped[idx]=1

    return Spectrum(deepcopy(self.axis), Data1D(numpy.average(self.data.values, axis=0, weights=weights),self.data.datatype))

  def integrate(self):
    return Spectrum(self.keys, self.data.integrate())

  def interpolate(self, newKeys):
    oldPoints = numpy.ndarray(shape=(len(self.keys.values)*len(self.axis.values),2))
    values =numpy.ndarray(shape=(len(self.keys.values)*len(self.axis.values)))
    newPoints = numpy.ndarray(shape=(len(newKeys)*len(self.axis.values),2))

    n=0
    for it,t in enumerate(self.keys.values):
      for ix,x in enumerate(self.axis.values):
        oldPoints[n,:]=[t,x]
        values[n] = self.data.values[it,ix]
        n+=1
    n=0
    for it,t in enumerate(newKeys):
      for ix,x in enumerate(self.axis.values):
        newPoints[n,:]=[t,x]
        n+=1
    self.data.values = griddata(oldPoints, values, newPoints, method="cubic").reshape(len(newKeys),len(self.axis.values))
    self.keys.values = newKeys

  def maximum(self):
    return Spectrum(self.keys, Data1D(self.axis.values[numpy.argmax(self.data.values,axis=1)],self.axis.datatype))

  
  def normalize(self, individual=False):
    if individual:
      self.data.normalizeIndividual()
    else:
      self.data.normalize()

  def subtractBaseline(self):
    #Invoke only if no dark spectrum available!
    baseline = numpy.min(self.data.values)-1
    self.data.values-=(baseline)
    print("Baseline removed: {0}".format(baseline))

  def toPlot(self, polar=False, cmap=None, norm=None):
    from fepydas.constructors.Plots import SpectrumSeriesPlot
    return SpectrumSeriesPlot(self, polar=polar, cmap=cmap, norm=norm)

class BinnedSpectrumSeries(SpectrumSeries):
  def __init__(self, spectrumSeries, binner, num_bins):
    keys = binner.createBins(spectrumSeries.keys, num_bins)
    data, self.histogram = binner.binData(spectrumSeries.data)
    super().__init__(deepcopy(spectrumSeries.axis),keys,data)

class JoinSpectrumSeries(SpectrumSeries):
  def __init__(self, spectra, interpol=False, names=None):
    if len(spectra)==1:
      if names: keys = [names[0]]
      else: keys = [0]
      data = numpy.ndarray(shape=(1, len(spectra[0].data.values)),dtype=spectra[0].data.values.dtype)
      data[0,:] = spectra[0].data.values
      super().__init__(spectra[0].axis, Data1D(keys,None), Data2D(data,spectra[0].data.datatype))
      return
    if names:
      keys = Data1D(names, NUMBER)
    else:
      keys = Data1D(range(len(spectra)),NUMBER)
    if interpol:
      valmin, mins, maxs, res = [], [],[],[]
      for i in range(len(spectra)):
        mins.append(numpy.amin(spectra[i].axis.values))
        maxs.append(numpy.amax(spectra[i].axis.values))
        res.append(numpy.average(numpy.diff(spectra[i].axis.values)))
        if res[i] < 0: #axis must be ascending
          spectra[i].axis.values = numpy.flip(spectra[i].axis.values)
          spectra[i].data.values = numpy.flip(spectra[i].data.values)
        valmin.append(numpy.amin(spectra[i].data.values))
      resolution = numpy.abs(numpy.average(res))
      min, max = numpy.amin(mins), numpy.amax(maxs)
      valmin = numpy.amin(valmin)
      #Interpolation, set non-overlapping regions to minimum so weight will be 0
      newAxis = Data1D(numpy.linspace(min, max, int((max-min)/resolution)), spectra[0].axis.datatype)
      data = Data2D(numpy.zeros((len(spectra),len(newAxis.values))), spectra[0].data.datatype)
      for i in range(len(spectra)):
        data.values[i,:] = numpy.interp(newAxis.values, spectra[i].axis.values, spectra[i].data.values, left=valmin, right=valmin) - valmin +0.001
      super().__init__(newAxis,keys,data)
    else:
      data = Data2D(numpy.zeros((len(spectra),len(spectra[0].data.values))), spectra[0].data.datatype)
      for i in range(len(spectra)):
        data.values[i,:] = spectra[i].data.values
      #TODO check AXIS consistency
      super().__init__(spectra[0].axis,keys,data)
    #TODO default create keys in SS init

class MergeSpectraSeries(SpectrumSeries):
  def __init__(self,spectraSeries):
    first = True
    for spectrumSeries in spectraSeries:
      if first:
        super().__init__(deepcopy(spectrumSeries.axis),deepcopy(spectrumSeries.keys),deepcopy(spectrumSeries.data))
        first = False
      else:
        self.axis.append(spectrumSeries.axis.values)
        self.data.append(spectrumSeries.data.values)
        self.keys.append(spectrumSeries.keys.values)


class Map(BaseDataset):
  def __init__(self, mapping:Data3D, data:Data2D):
    self.mapping = mapping
    self.data = data

  def export(self, filename):
    writer = MultiSpectrumWriter(filename)
    x,y = self.mapping.extractAxes()
    writer.addX(x,"")
    for i in range(len(y.values)):
      writer.addY(self.data.getCrosssectionAt(i),"{0}".format(y.values[i]))
    writer.write()

  def insertFlatData(self, data):
    x, y = self.data.values.shape
    print(x,y,data.shape)
    self.data.values = data.reshape(x,y)
    
  def toPlot(self, log=False, zRange=None):
    from fepydas.constructors.Plots import ContourMapPlot
    return ContourMapPlot(self, log=log, zRange=zRange)

    

class SpectrumSeriesWithCalibration(SpectrumSeries):
  def __init__(self, axis: Data1D, data:Data2D, calibration: Data1D, metadata=None):
    super().__init__(axis=axis,keys=None,data=data,metadata=metadata)
    self.calibrated = False
    self.calibration = calibration

  def getCalibrationSpectrum(self):
    return Spectrum(self.axis, self.calibration)

  def calibrate(self, references, threshold=10, width=10):
    self.applyAxisTransformation(AutomaticCalibration(self.getCalibrationSpectrum(), references, threshold=threshold, width=width).toTransformation())
    self.calibrated = True
    print("Calibrated")

class BaseSpectrumMap(SpectrumSeriesWithCalibration):
  def __init__(self, axis: Data1D, data:Data2D, mapping: Data3D, calibration: Data1D, metadata=None):
    super().__init__(axis, data, calibration, metadata)
    self.mapping = mapping
    
  def average(self):
    return Spectrum(self.axis, self.data.average())
  
  def getEmptyMap(self, datatype = NUMBER):
    x,y,z = self.mapping.values.shape
    vals = numpy.ndarray(shape=(x,y))
    values = Data2D(vals, datatype)
    return Map(self.mapping, values)

class SparseSpectrumMap(BaseSpectrumMap):
  def __init__(self, axis: Data1D, data: Data2D, mapping:Data3D, mask: Data2D, calibration:Data1D, metadata=None):
    super().__init__(axis,data,mapping,calibration,metadata)
    self.mask = mask #This contains the indexes of the data array where the invidiual spectra are stored or numpy.nan for empty pixels

  def cutMap(self, xMin, xMax, yMin, yMax):
    i1,i2,i3,i4 = self.mapping.cutAndGetIndexRange(xMin,xMax,yMin,yMax)
    self.mask.cutMap(i1,i2,i3,i4)
    self.updateFromMask()
    #the spectra are still there, but they are not referenced anymore. this is okay for most plots, but should be fixed if fits are attempted?
  
  def fitParameterToMap(self, fitter, paramName, paramDatatype):
    map = self.getEmptyMap(paramDatatype)
    x, y = map.data.values.shape
    for i in range(x):
      for j in range(y):
        idx = self.mask.values[i,j]
        result = fitter.results[idx]
        if result==0:
          val = 0
        else:
          val = result.params[paramName].value
        map.data.values[i,j] = val
    return map
    
  def integrate(self):
    return Map(self.mapping, self.data.integrate().to2D(self.mask))
    
  def maximum(self):
    return Map(self.mapping, Data1D(self.axis.values[numpy.argmax(self.data.values,axis=1)],self.axis.datatype).to2D(self.mask))
    
  def updateFromMask(self):
    #This method removes spectra that are not part of the map anymore and updates the mask 
    #TODO I probably need to check for NaN here?
    table = numpy.array(self.mask.values.flatten(),dtype=numpy.int64)
    self.data.values = self.data.values[table,:]
    coordinates = [] #I need to temp store this so I don't accidently "find" a value post-replacement    
    for i,old in enumerate(table):
      coordinates.append(numpy.where(self.mask.values==old))      
    for i,pos in enumerate(coordinates):
      self.mask.values[pos] = i
      
  def export(self, filename): 
    writer = MultiSpectrumWriter(filename)
    writer.addX(self.axis, "Coordinates")
    for x in range(self.mapping.values.shape[0]):
      for y in range(self.mapping.values.shape[1]):
        if not numpy.isnan(self.mask.values[x,y]):
          writer.addY(Data1D(self.data.values[int(self.mask.values[x,y]),:],self.data.datatype), "{0}:{1}".format(self.mapping.values[x,y,0],self.mapping.values[x,y,1]))
    writer.write()

class SpectrumMap(BaseSpectrumMap):
  def __init__(self, axis: Data1D, data:Data3D, mapping:Data3D, calibration: Data1D):
    super().__init__(axis,data,mapping,calibration)

  def cutMap(self, xMin, xMax, yMin, yMax):
    i1,i2,i3,i4 = self.mapping.cutAndGetIndexRange(xMin,xMax,yMin,yMax)
    self.data.cutMap(i1,i2,i3,i4)

  def getClusterMapIdx(self, gmm):
    map = self.getEmptyMap()
    #map.insertFlatData(gmm.predict(self.getDataValues(pca)))
    map.insertFlatData(gmm.labels_)
    return map

  def getClusterIntegratedSpectra(self, gmm):
    map = self.getClusterMapIdx(gmm)
    num = numpy.amax(map.data.values)+1
    data = numpy.zeros(shape=(num,self.data.values.shape[2]))
    for i in range(num):
      cond = numpy.where(map.data.values == i)
      filtered = self.data.values[cond]
      data[i,:] = numpy.sum(filtered, axis=0)
    return SpectrumSeries(self.axis, Data1D(range(num),NUMBER) ,Data2D(data, self.data.datatype))
    
  def export(self, filename):
    writer = MultiSpectrumWriter(filename)
    writer.addX(self.axis, "Coordinates")
    for x in range(self.mapping.values.shape[0]):
      for y in range(self.mapping.values.shape[1]):
        writer.addY(self.data.get1DAt(x,y), "{0}:{1}".format(self.mapping.values[x,y,0],self.mapping.values[x,y,1]))
    writer.write()

  def fit(self, fitter:Fit, filter=None):
    fitter.batchFit(self.axis.values, self.data.flatten(filter=filter))

  def fitDominatingComponents(self, decomp):
    decomp.fit(self.data.flatten())
    return decomp

  def fitParameterToMap(self, fitter, paramName, paramDatatype, filter=None):
    map = self.getEmptyMap(paramDatatype)
    x, y, z = self.data.values.shape
    if filter is not None:
      wasFitted = numpy.zeros_like(self.mapping.values[:,:,0])
      print(wasFitted.shape)
      wasFitted[filter] = 1
      print(wasFitted.shape)
      wasFitted = wasFitted.reshape((x*y,1))
      print(wasFitted.shape)
    vals = numpy.ndarray(shape=(x*y))
    i = 0
    for key in fitter.results.keys():
      if filter is not None:
        while wasFitted[i]==0:
          vals[i] = 0
          i+=1
      result = fitter.results[key]
      if result==0:
        vals[i] = 0
      else:
        vals[i] = result.params[paramName].value
      i+=1
    map.insertFlatData(vals)
    return map
  
  def getDataValues(self, pca=None):
    if pca is not None:
      return pca.transform(self.data.flatten())
    return self.data.flatten()

  def integrate(self):
    return Map(self.mapping, self.data.integrate())

  def maximum(self):
    return Map(self.mapping, Data2D(self.axis.values[numpy.argmax(self.data.values,axis=2)],self.axis.datatype))




class PLE(SpectrumSeriesWithCalibration):
  def __init__(self, axis: Data1D, keys:Data1D, data:Data2D, calibration = None, response = None, metadata=None):
    super().__init__(axis,data,calibration,metadata)
    self.keys = keys
    self.response = response
  
  def applyLampResponseCorrection(self,zeroFloor=False):
    interpolatedResponse = self.response.interpolateResponse(self.keys.values,zeroFloor)
    for i in range(len(self.keys.values)):
      self.data.values[i] /= interpolatedResponse[i]
    print("Lamp Response Correction made")

  
  def calibrateLamp(self,width=2,thresh=1):
    #This assumes the lamp is present in some of the spectra and used to calibrate the entire excitation (keys) axis with a linear fit
    fit = LimitedGaussianFit()
    nominal = []
    fitted = []
    fittedErrs = []
    for i in range(len(self.keys.values)):
      x, y = fit.initializeAutoLimited(self.axis.values,self.data.values[i],self.keys.values[i],width,thresh)
      if type(x) is numpy.ndarray and len(x)>40:
        #print(x,y)
        fit.fit(x,y)
        nominal.append(self.keys.values[i])
        fitted.append(fit.result.params["x0"].value)
        fittedErrs.append(fit.result.params["x0"].stderr)
    nominal = numpy.array(nominal,dtype=numpy.float64)
    fitted = numpy.array(fitted,dtype=numpy.float64)
    calib = CalibrationFit()
    calib.initializeAuto()
    calib.fit(nominal,fitted)#,peakErrs)
    print(calib.result.params)
    transformation = calib.toTransformation()
    self.keys.values = transformation.apply(self.keys.values)
    print("Calibrated Lamp")
    return transformation

  def calibrateLampExplicit(self, width=2, thresh=1):
    #This assumes the lamp is present in ALL spectra and is used to set the excitation (key) to the fitted value for each spectrum
    #The resulting axis may be used to calibrate another PLE measurement which used the same lamp parameters
    #USE WITH CAUTION AND CHECK RESULTS
    fit = GaussianFit()
    for i in range(len(self.keys.values)):
      idxs = numpy.where(numpy.abs(self.axis.values-self.keys.values[i])<=width)[0]
      x, y = self.axis.values[idxs], self.data.values[i,idxs]
      fit.initializeAuto(x,y)
      fit.fit(x,y)
      self.keys.values[i] = fit.result.params["x0"].value
      #print(lamp.keys.values[i], fit.parameters["x0"])
    print("Calibrated Lamp")
  
  def export(self, filename):
    writer = MultiSpectrumWriter(filename)
    writer.addSpectra(self)
    writer.write()
    

  def toPlot(self, log=True):
    from fepydas.constructors.Plots import ContourPlot
    return ContourPlot(self, log=log)

class SpectrumWithIRF(Spectrum):
  def __init__(self, axis: Data1D, data: Data, IRF: Data1D):
    super().__init__(axis,data)
    self.trimIRF(IRF)

  def evaluateConvolutionFit(self, fit):
    return Data1D(fit.evaluateConvolution(self.axis.values, self.IRF.values), self.data.datatype)

  def getExtendedIRF(self):
    data = numpy.zeros(self.data.values.shape)
    for i,x in enumerate(self.IRF.values):
      data[self.IRFStart+i]=x
    return data/data.max()

  def trimIRF(self,IRF):
    self.IRFStart = 0#lastZero+1
    self.IRF = IRF
    self.IRF.trim()
     
  def deconvolve(self,eps=None):
    self.data.deconvolve(self.IRF,eps)

class SpectraWithCommonIRF(SpectrumWithIRF):
  def __init__(self, axis: Data1D, data: Data2D, IRF: Data1D, identifiers: Data1D):
    super().__init__(axis,data,IRF)
    self.keys = identifiers

  def normalize(self, individual=False):
    if individual:
      self.data.normalizeIndividual()
    else:
      self.data.normalize()
