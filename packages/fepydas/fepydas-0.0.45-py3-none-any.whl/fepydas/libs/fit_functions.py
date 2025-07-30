import numpy
from lmfit import Parameters
def Lorentzian(x, bg=0, I=1, x0=0, fwhm=1):
  if I==0:
    return 0
  t = (x-x0)/(fwhm/2)
  return bg + I / (1+t*t)

def Gaussian(x, bg=0, I=1, x0=0, fwhm=1):
  if I==0:
    return 0
  return I * numpy.exp(- numpy.log(2)*((x-x0)/(fwhm/2))**2)

def Linear(x, a=1, b=0):
  return a*x+b

def Quadratic(x, a=0, b=1, c=0):
  return a*x**2+b*x+c

def Exponential(x, bg=0 ,I=1, x0=0, tau=1, rise=0.001):
  y = numpy.zeros_like(x)
  y+=bg
  decay = numpy.where(x>=x0)

  y[decay]+= I*numpy.exp(-(x[decay]-x0)/tau)*(1-numpy.exp(-(x[decay]-x0)/rise))
#  notDecay = numpy.where(x<x0)
#  y[decay]+= I*numpy.exp(-(x[decay]-x0)/tau)
#  y[notDecay]+= I*numpy.exp(-(x0-x[notDecay])/rise)
  return y


def BiExponential(x, bg=0 , x0=0, I_1=1, tau_1=1, I_2=1, tau_2=1, rise=0.001):
  y = numpy.zeros_like(x)
  y+=bg
  decay = numpy.where(x>=x0)
  y[decay]+= (I_1*numpy.exp(-(x[decay]-x0)/tau_1)+I_2*numpy.exp(-(x[decay]-x0)/tau_2))*(1-numpy.exp(-(x[decay]-x0)/rise))
  #notDecay = numpy.where(x<x0)
  #y[decay]+= I_1*numpy.exp(-(x[decay]-x0)/tau_1)+I_2*numpy.exp(-(x[decay]-x0)/tau_2)
  #y[notDecay]+= (I_1+I_2)*numpy.exp(-(x0-x[notDecay])/rise)
  return y

def TriExponential(x, bg=0 , x0=0, I_1=1, tau_1=1, I_2=1, tau_2=1, I_3=1, tau_3=1, rise=0.001):
  y = numpy.zeros_like(x)
  y+=bg
  decay = numpy.where(x>=x0)
  notDecay = numpy.where(x<x0)
  y[decay]+= I_1*numpy.exp(-(x[decay]-x0)/tau_1)+I_2*numpy.exp(-(x[decay]-x0)/tau_2)+I_3*numpy.exp(-(x[decay]-x0)/tau_3)
  y[notDecay]+= (I_1+I_2+I_3)*numpy.exp(-(x0-x[notDecay])/rise)
  return y


def BiExponentialTail(x, bg=0, I_1=1, tau_1=1, I_2=1, tau_2=1):
  y = bg + I_1*numpy.exp(-(x)/tau_1)+I_2*numpy.exp(-(x)/tau_2)
  return y
