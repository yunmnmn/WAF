import json
import os

# Static data
####################################################################
# All supported configuration properties
CONFIGURATION_PROPERTIES = ['CXXFLAGS', 'DEFINES', 'LINKFLAGS']
# Dictionary connecting all supported IDE's as keys, and supported options
IDE_DICT = dict( 
   msvs = ["msvs2019"],
   xcode6 = [],
   eclipse = []
)
# Array of supported compilers
SUPPORTED_COMPILERS = ["msvc", "gcc"]
# Array of s upported platforms
SUPPORTED_PLATFORMS = ["win", "osx"]

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
# The platforms that are supported
PLATFORMS = {}
# The environments that are supported
ENVIRONMENTS = []
# BuildTargets full data
BUILD_TARGETS = {}

# BuildTarget, target to build for
BUILD_TARGET = ''
# Environment to develop in: msvs2019, eclipse, xcode, etc
IDE = ''
# Compiler to use: msvc, gcc, etc
COMPILER =''

# Helper functions
####################################################################
# Read a json file
def ReadJson(path):
   with open(path) as json_file:
      json_data = json.load(json_file)
      return json_data

# Read all the build settings first
def ReadBuildSettingsData(file_path):
   global THIRD_PARTY_PATH
   global PROJECT_PATH
   # Read the json data
   buildSettingsData = ReadJson(file_path)
   thirdPartyPath =  buildSettingsData['ThirdPartyPath']
   projectsPath =  buildSettingsData['ProjectsPath']

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
def ValidateConfigurationProperty(propertyKey):
   if propertyKey in CONFIGURATION_PROPERTIES:
      return True
   else:
      return False

def ReadConfigurationValues(configurationKey, configurationValue):
   global CONFIGURATIONS
   if configurationKey in CONFIGURATIONS.keys():
      assert False, "key already exists"
   else:
      # Create a new directory entry within the CONFIGURATIONS directory
      CONFIGURATIONS[configurationKey] = {}
      # Check if the property values are valid of the configurations
      for configurationPropertyKey, configurationPropertyValue in configurationValue.items():
         if ValidateConfigurationProperty(configurationPropertyKey):
            CONFIGURATIONS[configurationKey][configurationPropertyKey] = configurationPropertyValue
   return True


# Read configurations file
def ReadConfigurationsData(filePath):
   global CONFIGURATION_GENERIC
   # Read the json data
   configurationData = ReadJson(filePath)

   # Read data generic data first
   # Check if the All configuration exists in the configuration data
   if configurationData['Generic']:
      for configurationGenericKey, configurationGenericValue in configurationData['Generic'].items():
         if ValidateConfigurationProperty(configurationGenericKey):
            CONFIGURATION_GENERIC[configurationGenericKey] = configurationGenericValue 
         else:
            assert False, "Invalid key in configuration data"

   # Add the rest of the configurations (configurations)
   for configurationKey, configurationValue in configurationData['Configurations'].items():
      ReadConfigurationValues(configurationKey, configurationValue)

# Returns a dictionary of flags from the environment, platform and configuration
def GetFlagsFromConfiguration(environment, platform, configuration):
   pass

# Returns an array of configurations from the environment and platform
def GetConfigurationsFromPlatform(environment, platform):
   pass

# Returns an array of platforms from the environment
def GetPlatformsFromEnvironment(environment):
   pass

# Read the BuildTarget values
def ReadBuildTargetsData(filePath):
   global BUILD_TARGETS
   global ENVIRONMENTS
   # Read the json data
   buildTargetsData = ReadJson(filePath)
   # Set the BuildTargets dictionary
   BUILD_TARGETS = buildTargetsData['BuildTargets']
   # Filter out the flags that aren't available
   for environmentKey, environmentValue in BUILD_TARGETS.items():
      # Cache the environments
      ENVIRONMENTS.append(environmentKey)
      for platformKey, platformValue in environmentValue.items():
         for configurationKey, configurationValue in platformValue.items():
            if not ValidateConfigurationProperty(configurationKey):
               configurationValue.pop(configurationKey, None) 

# Read the IDE to use from options
def ReadIdeToolFromOption(optionArgument):
   for ideKey, ideValue in IDE_DICT.items():
      if optionArgument in ideValue:
         return ideKey, ideValue
   assert False, "IDE option isn't valid" 

# Read the compiler to use from options
def ReadCompilerFromOption(optionArgument):
   if optionArgument in SUPPORTED_COMPILERS:
      return optionArgument
   assert False, "Compiler option is not available" 

# Read the compiler to use from options
def ReadEnvironmentFromOption(optionArgument):
   for environment in ENVIRONMENTS:
      if environment.lower() == optionArgument:
         return environment
   assert False, "Environment option is not available" 

# Custom Task Gen functions
####################################################################
from waflib.TaskGen import after_method, before_method, feature, taskgen_method, extension

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

from waflib.Configure import conf 

# Give the path back of the source files depending on the environment
@conf
def GetSourcePathFromEnvironment(bld, sourcePath, sourceFiles):
   # Calculate the relative path
   relativePath = sourcePath + '\\' + 'Platform' + '\\' + bld.env.ENVIRONMENT
   sourceArray = []
   for sourceFile in sourceFiles:
      sourcePath = relativePath + '\\' + sourceFile
      sourceNode = bld.path.find_node(sourcePath)
      # Confirm if the source exists
      assert sourceNode != None, "Source doesn't exist" 
      sourceArray.append(sourcePath)
   return sourceArray

@conf
def GetIncludePathFromEnvironment(bld, includePath):
   relativePath = includePath + '\\' + 'Platform' + '\\' + bld.env.ENVIRONMENT
   includeNode = bld.path.find_node(relativePath)
   assert includeNode != None, "Source doesn't exist" 
   return relativePath