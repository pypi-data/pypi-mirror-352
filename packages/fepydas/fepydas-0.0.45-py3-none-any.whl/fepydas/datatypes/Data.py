#!/usr/bin/python3
import numpy
from scipy.constants import speed_of_light,Planck,elementary_charge

class DataType:
  def __init__(self, name: str, unit:str):
    self.name = name
    self.unit = unit

class Data:
  def __init__(self, values: numpy.ndarray, datatype: DataType, errors = None):
    self.values = values
    self.datatype = datatype
    self.errors = errors

  def normalize(self):
    self.values = self.values / numpy.max(self.values)
  
  def divideBy(self, data):
    self.values = self.values/data

  def append(self, dataToAppend):
    self.values = numpy.concatenate((self.values, dataToAppend), axis=0)

  def applyJacobianTransformation(self, axis):
    jacobian = axis.getJacobian()
    self.values = self.values * jacobian

  def linearAntiBloom(self, values, over, width=1, reverse=False):
    max = numpy.max(values)
    length = len(values)
    if reverse:
      for j in range(length-1,0,-1):
        if j-width > 0:
          if values[j-width] > over:
            values[j] = max
    else:
      for j in range(length-1):
        if j+width < length:
          if values[j+width] > over:
            values[j] = max
    return values

class Data1D(Data):
  def __init__(self, values: numpy.ndarray, datatype: DataType, errors = None):
    super().__init__(values,datatype,errors=errors)

  def antiBloom(self, over, width=1, reverse=False):
    self.values = self.linearAntiBloom(self.values, over, width, reverse)

  def cutAndGetIndexRange(self, min, max):
    idx1, idx2 = self.getIndexRange(min,max)
    self.cut(idx1,idx2)
    return idx1, idx2 

  def getIndexRange(self, min, max):
    idx1 = (numpy.abs(self.values - min)).argmin()
    idx2 = (numpy.abs(self.values - max)).argmin()
    if idx2<idx1:
      temp = idx2
      idx2 = idx1
      idx1 = temp
    return idx1,idx2

  def convertToEnergy(self, unit="eV"):
    self.values = WavelengthToEnergy().apply(self.values*1e-9)
    self.datatype = DataType("Energy","eV")

  def getJacobian(self):
    if self.datatype.unit == "eV":
      factor = elementary_charge
    else:
      factor = 1
    return Planck * speed_of_light/ ((factor*self.values)**2)

  def cut(self, idx1, idx2):
    self.values = self.values[idx1:idx2]
    if self.errors is not None:
      self.errors = self.errors[idx1:idx2]
 
  def shiftValues(self, amount):
    self.values += amount

  def trim(self):
    maxIdx = numpy.argmax(self.values)
    zeroes = numpy.where(self.values==0)[0]
    start = 0
    end = zeroes[numpy.where(zeroes > maxIdx)[0][-1]]
    self.values = self.values[start:end]
    self.values = numpy.array(self.values,dtype=numpy.float64)
    self.values /= self.values.sum()
    
        
  def to2D(self, mask):
    newValues = numpy.full_like(mask.values, numpy.nan, dtype=numpy.float64)
    x,y = mask.values.shape
    for i in range(x):
      for j in range(y):
        if not numpy.isnan(mask.values[i,j]):
          idx = int(mask.values[i,j])
          newValues[i,j] = self.values[idx]
    return Data2D(newValues, self.datatype)

class Data2D(Data):
  def __init__(self, values: numpy.ndarray, datatype: DataType, errors=None):
    super().__init__(values,datatype,errors=errors)

  def antiBloom(self, over, width=1, reverse=False):
    for i in range(self.values.shape[0]):
      self.values[i,:] = self.linearAntiBloom(self.values[i,:], over, width, reverse)
   
  def average(self, despike_method=None, despike_cutoff=1):
    if despike_method == "median":
      median = numpy.median(self.values,axis=0)
      no_spikes = (self.values <= despike_cutoff * median).astype(int)
      return Data1D(numpy.average(self.values,axis=0,weights=no_spikes),self.datatype)
    else:  
      return Data1D(numpy.average(self.values,axis=0),self.datatype)

  def collapse(self, filter=None):
    if filter:
      return Data1D(numpy.sum(self.values[filter],axis=0), self.datatype)
    else:
      return Data1D(numpy.sum(self.values,axis=0),self.datatype)

  def interpSpikes(self, despike_method=None, despike_cutoff=1, interp_method=None):
    if despike_method == "diff":
      diff = numpy.diff(self.values,axis=0,prepend=self.values[0,0])
      filter = numpy.abs(diff)>despike_cutoff
    if interp_method == "avg_0":  
      for i in range(self.values.shape[0]):
        for j in range(self.values.shape[1]):
          if filter[i,j]:
            self.values[i,j]=(self.values[i-1,j]+self.values[i+1,j])/2

  def integrate(self):
    if self.errors is None:
      errors = None
    else:
      errors = numpy.sum(self.errors, axis=1)
    return Data1D(numpy.sum(self.values,axis=1),self.datatype, errors)

  def normalizeIndividual(self):
    maxima = numpy.max(self.values,axis=1)
    self.values = (self.values.T / maxima).T

  def cut(self, idx1, idx2):
    self.values = self.values[:,idx1:idx2]
    if self.errors is not None:
      self.errors = self.errors[:,idx1:idx2]
      
  def cutMap(self, idx1, idx2, idx3, idx4):
    self.values = self.values[idx1:idx2, idx3:idx4]

  def getCrosssectionAt(self, idx):
    return Data1D(self.values[:,idx], self.datatype)
 
  

class Data3D(Data):
  def __init__(self, values: numpy.ndarray, datatype: DataType):
    super().__init__(values,datatype)

  def collapse(self, filter=None):
    print(filter)
    if filter is not None:
      return Data1D(numpy.sum(self.flatten()[filter],axis=0), self.datatype)
    else:
      return Data1D(numpy.sum(self.flatten(),axis=0),self.datatype)

  def cutMap(self, xMin, xMax, yMin, yMax):
    self.values = self.values[xMin:xMax,yMin:yMax,:]

  def flatten(self, filter=None):
    if filter is None:
      x,y,z = self.values.shape
      return self.values.reshape(x*y,z)
    else:
      return self.values[filter].reshape(len(filter[0]),self.values.shape[2])


  def getIndexRange(self, xMin, xMax, yMin, yMax):
    idx1 = (numpy.abs(self.values[:,0,0] - xMin)).argmin(axis=0)
    idx2 = (numpy.abs(self.values[:,0,0] - xMax)).argmin(axis=0)
    idx3 = (numpy.abs(self.values[0,:,1] - yMin)).argmin(axis=0)
    idx4 = (numpy.abs(self.values[0,:,1] - yMax)).argmin(axis=0)  
    return idx1,idx2,idx3,idx4

  def get1DAt(self,x,y):
    return Data1D(self.values[x,y,:], self.datatype)

  def cutAndGetIndexRange(self, xMin, xMax, yMin, yMax):
    i1,i2,i3,i4 = self.getIndexRange(xMin,xMax,yMin,yMax)
    self.cutMap(i1,i2,i3,i4)
    return i1,i2,i3,i4

  def integrate(self):
    return Data2D(numpy.sum(self.values, axis=2), self.datatype)

  def average(self):
    return Data1D(numpy.average(self.values, axis=(0,1)), self.datatype)

  def extractAxes(self):
    y = self.values[0,:,1]
    x = self.values[:,0,0]
    return Data1D(x, self.datatype), Data1D(y, self.datatype)
  
  def cut(self, idx1, idx2):
    self.values = self.values[:,:,idx1:idx2]

  def normalizeIndividual(self):
    maxima = numpy.max(self.values,axis=2)
    self.values = (self.values.T / maxima.T).T

class DataTransformation():
  def __init__(self, transformation, newUnit):
    self.transformation = transformation
    self.newUnit = newUnit

  def apply(self, oldAxis):
    newValues = self.transformation.apply(oldAxis.values)
    if oldAxis.errors is not None:
      errors = oldAxis.errors / oldAxis.values * newValues
    else:
      errors = None
    return Data1D(self.transformation.apply(oldAxis.values), self.newUnit, errors)

class ArrheniusTransformation(DataTransformation):
  def __init__(self):
    super().__init__(Transformation(self.reciprocal,{}),DataType("1/T","1/K"))

  def reciprocal(self, values):
    return 1/values
    
class Transformation():
  def __init__(self, function, parameterDict):
    self.function = function
    self.params = parameterDict

  def apply(self, values):
    if values is None: return None
    return self.function(values,**self.params)

class WavelengthToEnergy(Transformation):
  def __init__(self, unit="eV"):
    params = {}
    if unit=="eV":
      params["factor"]=1/elementary_charge
    else:
      params["factor"]=1
    super().__init__(self.wavelengthToEnergy, params)

  def wavelengthToEnergy(self, values, factor):
    return factor * Planck * speed_of_light / values
    
class VacuumCorrection(Transformation):
  def __init__(self, temperature=20, pressure=101325, humidity=0, co2=610):
    params = {}
    params["temperature"]=temperature
    params["pressure"]=pressure
    params["humidity"]=humidity
    params["co2"]=co2
    super().__init__(self.convertWavelength, params)
    
  def convertWavelength(self, values, temperature, pressure, humidity, co2):
    return values * self.n(values/1000, temperature, pressure, humidity, co2)
  
  def Z(self, T,p,xw): #compressibility
    t=T-273.15
    a0 = 1.58123e-6   #K·Pa^-1
    a1 = -2.9331e-8   #Pa^-1
    a2 = 1.1043e-10   #K^-1·Pa^-1
    b0 = 5.707e-6     #K·Pa^-1
    b1 = -2.051e-8    #Pa^-1
    c0 = 1.9898e-4    #K·Pa^-1
    c1 = -2.376e-6    #Pa^-1
    d  = 1.83e-11     #K^2·Pa^-2
    e  = -0.765e-8    #K^2·Pa^-2
    return 1-(p/T)*(a0+a1*t+a2*t**2+(b0+b1*t)*xw+(c0+c1*t)*xw**2) + (p/T)**2*(d+e*xw**2)
  
  def n(self, λ,t,p,h,xc):
    # λ: wavelength, 0.3 to 1.69 μm 
    # t: temperature, -40 to +100 °C
    # p: pressure, 80000 to 120000 Pa
    # h: fractional humidity, 0 to 1
    # xc: CO2 concentration, 0 to 2000 ppm
    σ = 1/λ           #μm^-1
    T= t + 273.15     #Temperature °C -> K
    R = 8.314510      #gas constant, J/(mol·K)
    k0 = 238.0185     #μm^-2
    k1 = 5792105      #μm^-2
    k2 = 57.362       #μm^-2
    k3 = 167917       #μm^-2
    w0 = 295.235      #μm^-2
    w1 = 2.6422       #μm^-2
    w2 = -0.032380    #μm^-4
    w3 = 0.004028     #μm^-6
    A = 1.2378847e-5  #K^-2
    B = -1.9121316e-2 #K^-1
    C = 33.93711047
    D = -6.3431645e3  #K
    α = 1.00062
    β = 3.14e-8       #Pa^-1,
    γ = 5.6e-7        #°C^-2
    #saturation vapor pressure of water vapor in air at temperature T
    if(t>=0):
        svp = numpy.exp(A*T**2 + B*T + C + D/T) #Pa
    else:
        svp = 10**(-2663.5/T+12.537)
    #enhancement factor of water vapor in air
    f = α + β*p + γ*t**2
    #molar fraction of water vapor in moist air
    xw = f*h*svp/p
    #refractive index of standard air at 15 °C, 101325 Pa, 0% humidity, 450 ppm CO2
    nas = 1 + (k1/(k0-σ**2)+k3/(k2-σ**2))*1e-8
    #refractive index of standard air at 15 °C, 101325 Pa, 0% humidity, xc ppm CO2
    naxs = 1 + (nas-1) * (1+0.534e-6*(xc-450))
    #refractive index of water vapor at standard conditions (20 °C, 1333 Pa)
    nws = 1 + 1.022*(w0+w1*σ**2+w2*σ**4+w3*σ**6)*1e-8
    Ma = 1e-3*(28.9635 + 12.011e-6*(xc-400)) #molar mass of dry air, kg/mol
    Mw = 0.018015                            #molar mass of water vapor, kg/mol
    Za = self.Z(288.15, 101325, 0)                #compressibility of dry air
    Zw = self.Z(293.15, 1333, 1)                  #compressibility of pure water vapor
    #Eq.4 with (T,P,xw) = (288.15, 101325, 0)
    ρaxs = 101325*Ma/(Za*R*288.15)           #density of standard air
    #Eq 4 with (T,P,xw) = (293.15, 1333, 1)
    ρws  = 1333*Mw/(Zw*R*293.15)             #density of standard water vapor
    # two parts of Eq.4: ρ=ρa+ρw
    ρa   = p*Ma/(self.Z(T,p,xw)*R*T)*(1-xw)       #density of the dry component of the moist air    
    ρw   = p*Mw/(self.Z(T,p,xw)*R*T)*xw           #density of the water vapor component
    nprop = 1 + (ρa/ρaxs)*(naxs-1) + (ρw/ρws)*(nws-1)
    return nprop


class Response():
  def __init__(self, input: Data1D, values: Data1D):
    self.input = input
    self.values = values 

  def interpolateResponse(self, inputValues: numpy.ndarray, zeroFloor=False):
    if zeroFloor:
      self.values.values -= numpy.amin(self.values.values)*0.9
    return numpy.interp(inputValues, self.input.values, self.values.values)
