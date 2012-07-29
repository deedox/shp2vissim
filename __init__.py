"""
"""
def name(): 
  return "zlyTools" 
def description():
  return "tools created by zhangliye for academic purpose"
def version(): 
  return "Version 1.0.1" 
  
def qgisMinimumVersion():
  return "1.0"
  
def icon():
  return ""
  
def classFactory(iface): 
  # load GdalTools class from file GdalTools
  from ZlyTools import ZlyTools 
  return ZlyTools(iface)

