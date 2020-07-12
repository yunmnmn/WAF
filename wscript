from wafextension import project_configure

# Used to create the build configuration variants
from waflib.Build import BuildContext, CleanContext, InstallContext, UninstallContext

# Static data
####################################################################
# All wscript modules used
WSCRIPT_MODULES = ['msvs', 'msvc']

# Read and initialize all the confic files
####################################################################
# Read all the BuildTarget settings, and set all the global variables
project_configure.ReadBuildTargetsData('Configurations.json')
# Read all the build settings, and set all the global variables
project_configure.ReadBuildSettingsData('BuildSettings.json')
# Read all the configurations, and set all the global variables
project_configure.ReadConfigurationsData('Configurations.json')

# Create the build configuration commands
####################################################################
for configurationKey in project_configure.CONFIGURATIONS:
   for y in (BuildContext, CleanContext, InstallContext, UninstallContext):
      name = y.__name__.replace('Context','').lower()
      class tmp(y): 
         cmd = name + '_' + configurationKey.lower()
         variant = configurationKey

from wafextension import msvs_wrapper

# WAF specific code from here
####################################################################
# Recurses through subfolders to find wscripts
def recurse_subfolders(ctx):
   # Recurse the ThirdParty and Project directories
   ctx.recurse(dirs = project_configure.THIRD_PARTY_PATH, mandatory = False)
   ctx.recurse(dirs = project_configure.PROJECT_PATH, mandatory = False)

def options(opt):
   opt.load('msvc')
   opt.load('msvs')

   opt.add_option('--environment', action='store', default='', dest='environment')
   opt.add_option('--ide', action='store', default='', dest='ide')
   opt.add_option('--compiler', action='store', default='', dest='compiler')

   # Recurse through all the subfolders, calling the wscripts
   recurse_subfolders(opt)

def configure(cnf):
   # Read the IDE to use
   ideTool, ideOption = project_configure.ReadIdeToolFromOption(cnf.options.ide)
   cnf.env.IDE = ideOption
   cnf.load(ideTool)

   # Read the compiler to use
   compilerTool = project_configure.ReadCompilerFromOption(cnf.options.compiler)
   cnf.env.COMPILER = compilerTool
   cnf.load(compilerTool)
   
   # Read the Environment to use
   environment = project_configure.ReadEnvironmentFromOption(cnf.options.environment)
   cnf.env.ENVIRONMENT = environment

   # Make the copy of the environment
   defaultEnv = cnf.env 

   # Set the properties per configuration that are read from the json file
   for configurationKey, configurationValue in project_configure.CONFIGURATIONS.items():
      # Set the configuration specific properties
      cnf.setenv(configurationKey.lower(), defaultEnv)

      # Set the configuration specific properties
      for propertyKey, propertyValue in configurationValue.items():
         cnf.env.append_unique(propertyKey, propertyValue) 

      # Set the generic configuration properties
      for genericPropertyKey, genericPropertyValue in project_configure.CONFIGURATION_GENERIC.items():
         cnf.env.append_unique(genericPropertyKey, genericPropertyValue) 

   # Recurse through all the subfolders, calling the wscripts
   recurse_subfolders(cnf)

def build(bld):
   # Disable the generic clean, build and install commands
   if not bld.variant and not bld.cmd == 'msvs2019':
      bld.fatal('call "waf build_debug", "waf build_release" or "waf build_releasewithsymbols", and try "waf --help"')

   # Recurse through all the subfolders, calling the wscripts
   recurse_subfolders(bld)