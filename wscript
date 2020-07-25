from wafextension import project_configure
from waflib.Build import BuildContext, CleanContext, InstallContext, UninstallContext
from wafextension import msvs_wrapper
from waflib import Configure

from waflib import Context

# TODO: Fix dependencies
from waflib.Tools import c_preproc
#c_preproc.go_absolute = True

# Name of the app
APPNAME = ''

def create_variant(ctx):
   CreateConfigurations(ctx)

def CreateConfigurations(ctx):
   # Read and initialize all the confic files
   ####################################################################
   # Read all the BuildTarget settings, and set all the global variables
   project_configure.ReadBuildTargetsData(ctx.options.wrd + "\\" + 'Configurations.json')
   # Read all the build settings, and set all the global variables
   project_configure.ReadBuildSettingsData(ctx.options.wrd + "\\" + 'BuildSettings.json')
   # Create the build configuration commands
   ####################################################################
   # Create WAF configurations(e.g cmd = clean_win_x64_debug, variant = win_x64_debug)
   for environmentKey, environmentValue in project_configure.BUILD_TARGETS.items():
      for platformKey, platformValue in environmentValue.items():
         for configurationKey in platformValue:
            variantName = environmentKey.lower() + '_' + platformKey.lower() + '_' + configurationKey.lower()
            for y in (BuildContext, CleanContext, InstallContext, UninstallContext):
               className = y.__name__.replace('Context','').lower()
               class tmp(y):  
                  cmd = className + '_' + variantName
                  variant = variantName

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
   opt.add_option('--appname', action='store', default='', dest='appname')
   opt.add_option('--wrd', action='store', default='', dest='wrd')

   # Recurse through all the subfolders, calling the wscripts
   recurse_subfolders(opt)

def configure(cnf):
   CreateConfigurations(cnf)

   # Read the IDE to use
   ideTool, ideOption = project_configure.ReadIdeToolFromOption(cnf.options.ide)
   cnf.env.IDE = ideOption
   cnf.load(ideTool)

   # Read the compiler to use
   compilerTool = project_configure.ReadCompilerFromOption(cnf.options.compiler)
   cnf.env.COMPILER = compilerTool
   cnf.load(compilerTool)

   # Set the WafRootDir
   cnf.env.WafRootDir = cnf.options.wrd

   # test, TODO
   cnf.load('msvcdeps')

   # Read the Environment to use
   environment = project_configure.ReadEnvironmentFromOption(cnf.options.environment)
   cnf.env.ENVIRONMENT = environment

   # Read the appname
   global APPNAME
   APPNAME = cnf.options.appname

   # Make the copy of the environment
   defaultEnv = cnf.env 

   # Set the properties per configuration that are read from the json file
   for environmentKey, environmentValue in project_configure.BUILD_TARGETS.items():
      for platformKey, platformValue in environmentValue.items():
         for configurationKey, configurationValue in platformValue.items():
            variant = environmentKey.lower() + '_' + platformKey.lower() + '_' + configurationKey.lower()
            cnf.setenv(variant, defaultEnv)
            for propertyKey, propertyValue in configurationValue.items():
               cnf.env.append_unique(propertyKey, propertyValue) 

   msvs_wrapper.CreateMsvs(cnf)

   # Recurse through all the subfolders, calling the wscripts
   recurse_subfolders(cnf)

def build(bld):
   # Disable the generic clean, build and install commands
   if not bld.variant and not bld.cmd == 'msvs2019':
      bld.fatal('call "waf build_debug", "waf build_release" or "waf build_releasewithsymbols", and try "waf --help"')

   # Recurse through all the subfolders, calling the wscripts
   recurse_subfolders(bld)