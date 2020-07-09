import json
import os

# Static data
####################################################################
# All supported configuration properties
CONFIGURATION_PROPERTIES = ['CXXFLAGS', 'DEFINES', 'LINKFLAGS']

# Read and initialize all the confic files
####################################################################
# The path where all third party libraries are
THIRD_PARTY_PATH = ''
# The path where all projects are
PROJECT_PATH = ''
# The generic configuration which will hold properties that will be appliec to all configurations
CONFIGURATION_GENERIC = {}
# The configurations that are supported
CONFIGURATIONS = {}

# Helper functions
####################################################################
# Read a json file
def read_json(path):
   with open(path) as json_file:
      json_data = json.load(json_file)
      return json_data

# Read all the build settings first
def readBuildSettingsData(file_path):
   global THIRD_PARTY_PATH
   global PROJECT_PATH
   # Read the json data
   buildData = read_json(file_path)
   thirdPartyPath =  buildData['ThirdPartyPath']
   projectsPath =  buildData['ProjectsPath']

   # Read the third party path
   if os.path.isabs(thirdPartyPath):
      THIRD_PARTY_PATH = thirdPartyPath
   else:
     THIRD_PARTY_PATH = os.path.normpath(os.path.abspath(os.path.curdir) + "\\" + thirdPartyPath)
   # Read the projects path
   if os.path.isabs(projectsPath):
      PROJECT_PATH = os.path.normpath(projectsPath)
   else:
     PROJECT_PATH = os.path.normpath(os.path.abspath(os.path.curdir) + "\\" + projectsPath)

# Check if the property key is valid
def valid_configuration_property(propertyKey):
   if propertyKey in CONFIGURATION_PROPERTIES:
      return True
   else:
      # TODO: Throw exception
      assert False, "There is an invalid configuration property in the data" 

def read_configuration_values(configurationKey, configurationValue):
   global CONFIGURATIONS
   if configurationKey in CONFIGURATIONS.keys():
      assert False, "key already exists"
   else:
      # Create a new directory entry within the CONFIGURATIONS directory
      CONFIGURATIONS[configurationKey] = {}
      # Check if the property values are valid of the configurations
      for configurationPropertyKey, configurationPropertyValue in configurationValue.items():
         if valid_configuration_property(configurationPropertyKey):
            CONFIGURATIONS[configurationKey][configurationPropertyKey] = configurationPropertyValue
   return True

# Read configurations file
def readConfigurationsData(file_path):
   global CONFIGURATION_GENERIC
   # Read the json data
   configurationData = read_json(file_path)

   # Read data generic data first
   # Check if the All configuration exists in the configuration data
   if configurationData['Generic']:
      for configurationGenericKey, configurationGenericValue in configurationData['Generic'].items():
         if valid_configuration_property(configurationGenericKey):
            CONFIGURATION_GENERIC[configurationGenericKey] = configurationGenericValue 
         else:
            assert False, "Invalid key in configuration data"

   # Add the rest of the configurations (configurations)
   for configurationKey, configurationValue in configurationData['Configurations'].items():
      read_configuration_values(configurationKey, configurationValue)

from waflib.TaskGen import after_method, before_method, feature, taskgen_method, extension

# Custom Task Gen functions
####################################################################

# Sets the configuration properties read from json files
@taskgen_method
def get_configuration_vars(self):
   _vars = set()
   for x in self.features:
      if x in CONFIGURATION_PROPERTIES:
         _vars |= CONFIGURATION_PROPERTIES[x]
   return _vars

@feature('c', 'cxx')
@before_method('propagate_uselib_vars')
def propegate_configuration_vars(self):
   configurationKey = self.bld.variant
   if configurationKey:
      configuration_env = self.bld.all_envs[configurationKey.lower()]
      #_vars = self.get_configuration_vars()
      _vars = CONFIGURATION_PROPERTIES 
      env = self.env
      app = env.append_value
      for var in _vars:
         val = configuration_env[var]
         if val:
            app(var, self.to_list(val))