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
# Array of supported environments
SUPPORTED_ENVIRONMENTS = ["win", "osx"]

# Read and initialize all the confic files
####################################################################
# The path where all third party libraries are
THIRD_PARTY_PATH = ''
# The path where all projects are
PROJECT_PATH = ''
# BuildTargets full data
BUILD_TARGETS = {}

# List of targets that have been added with its wscript
TARGET_LIST = []

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

# Returns a dictionary of flags from the environment, platform and configuration
def GetFlagsFromConfiguration(environment, platform, configuration):
   flags = BUILD_TARGETS[environment][platform][configuration].items()
   return flags

# Returns an array of configurations from the environment and platform
def GetConfigurationsFromPlatform(environment, platform):
   configurations = []
   for configuration in BUILD_TARGETS[environment][platform]:
      configurations.append(configuration)
   return configurations

# Returns an array of platforms from the environment
def GetPlatformsFromEnvironment(environment):
   platforms = []
   for platformKey in BUILD_TARGETS[environment]:
      platforms.append(platformKey)
   return platforms

# Returns an array of environments
def GetEnvironment():
   environments = []
   for environmentKey in BUILD_TARGETS:
      environments.append(environmentKey)
   return environments

# Read the BuildTarget values
def ReadBuildTargetsData(filePath):
   global BUILD_TARGETS

   # Read the json data
   buildTargetsData = ReadJson(filePath)

   # Set the BuildTargets dictionary
   BUILD_TARGETS = buildTargetsData['BuildTargets']

   # Filter out the flags that aren't available
   for environmentValue in BUILD_TARGETS.values():
      for platformValue in environmentValue.values():
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
   for environment in SUPPORTED_ENVIRONMENTS:
      if environment.lower() == optionArgument:
         return environment
   assert False, "Environment option is not available" 

# Custom Task Gen functions
####################################################################
from waflib.TaskGen import after_method, before_method, feature, taskgen_method, extension

# Sets the configuration properties read from json files
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

# Environment(win, osx, linux, etc) related functions
####################################################################
# Give the path back of the source files depending on the environment
from waflib.Configure import conf 

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

# Give the path back of the environment's specific include directory
@conf
def GetIncludePathFromEnvironment(bld, includePath):
   includeArray = []
   relativePath = includePath + '\\' + 'Platform' + '\\' + bld.env.ENVIRONMENT
   includeNode = bld.path.find_node(relativePath)
   assert includeNode != None, "Source doesn't exist" 

   includeArray.append(relativePath)
   return includeArray

# Add the target to a list to verify that it already exists
@conf
def TargetAdded(bld, target):
   if target not in TARGET_LIST:
      TARGET_LIST.append(target)
      return True
   else:
      return False


# Define a target
@conf
def DefineTarget(bld, **kw):
   pass