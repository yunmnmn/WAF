import os, re, sys

from waflib.extras import msvs
from waflib import Logs, Context, Utils
from wafextension import project_configure

PROJECT_2019_TEMPLATE=r'''<?xml version="1.0" encoding="UTF-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0"
   xmlns="http://schemas.microsoft.com/developer/msbuild/2003">

   <ItemGroup Label="ProjectConfigurations">
      ${for b in project.build_properties}
      <ProjectConfiguration Include="${b.configuration}|${b.platform}">
         <Configuration>${b.configuration}</Configuration>
         <Platform>${b.platform}</Platform>
      </ProjectConfiguration>
      ${endfor}
   </ItemGroup>

   <PropertyGroup Label="Globals">
      <ProjectGuid>{${project.uuid}}</ProjectGuid>
      <Keyword>MakeFileProj</Keyword>
      <ProjectName>${project.name}</ProjectName>
   </PropertyGroup>
   <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />

   ${for b in project.build_properties}
   <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='${b.configuration}|${b.platform}'" Label="Configuration">
      <ConfigurationType>Makefile</ConfigurationType>
      <OutDir>${b.outdir}</OutDir>
      <PlatformToolset>${project.platform_toolset_ver}</PlatformToolset>
   </PropertyGroup>
   ${endfor}

   <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
   <ImportGroup Label="ExtensionSettings">
   </ImportGroup>

   ${for b in project.build_properties}
   <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='${b.configuration}|${b.platform}'">
      <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
   </ImportGroup>
   ${endfor}

   ${for b in project.build_properties}
   <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='${b.configuration}|${b.platform}'">
      <NMakeBuildCommandLine>${xml:project.get_build_command(b)}</NMakeBuildCommandLine>
      <NMakeReBuildCommandLine>${xml:project.get_rebuild_command(b)}</NMakeReBuildCommandLine>
      <NMakeCleanCommandLine>${xml:project.get_clean_command(b)}</NMakeCleanCommandLine>
      <NMakeIncludeSearchPath>${xml:b.includes_search_path}</NMakeIncludeSearchPath>
      <NMakePreprocessorDefinitions>${xml:b.preprocessor_definitions};$(NMakePreprocessorDefinitions)</NMakePreprocessorDefinitions>
      <IncludePath>${xml:b.includes_search_path}</IncludePath>
      <ExecutablePath>$(ExecutablePath)</ExecutablePath>

      ${if getattr(b, 'output_file', None)}
      <NMakeOutput>${xml:b.output_file}</NMakeOutput>
      ${endif}
      ${if getattr(b, 'deploy_dir', None)}
      <RemoteRoot>${xml:b.deploy_dir}</RemoteRoot>
      ${endif}
   </PropertyGroup>
   ${endfor}

   ${for b in project.build_properties}
      ${if getattr(b, 'deploy_dir', None)}
   <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='${b.configuration}|${b.platform}'">
      <Deploy>
         <DeploymentType>CopyToHardDrive</DeploymentType>
      </Deploy>
   </ItemDefinitionGroup>
      ${endif}
   ${endfor}

   <ItemGroup>
      ${for x in project.source}
      <${project.get_key(x)} Include='${x.win32path()}' />
      ${endfor}
   </ItemGroup>
   <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
   <ImportGroup Label="ExtensionTargets">
   </ImportGroup>
</Project>
'''

class vsnode_target_custom(msvs.vsnode_target):
   def __init__(self,ctx,node):
      msvs.vsnode_target.__init__(self,ctx,node)
      self.is_active=True
   def collect_properties(self):
      msvs.vsnode_project.collect_properties(self)
      for x in self.build_properties:
         x.outdir = self.path.parent.win32path()
         x.preprocessor_definitions = ''
         x.includes_search_path = ''
         try:
            tsk=self.tg.link_task
         except AttributeError:
            pass
         else:
            x.output_file = self.get_build_dir(x, tsk.outputs[0])

            # Store the absolute paths for intellisense
            includeArray = [includePath.abspath() for includePath in self.tg.includes_nodes]
            x.includes_search_path = ';'.join(includeArray)

            # Set the defines in the configuration for the project
            defineArray = [define for define in self.tg.defines]
            x.preprocessor_definitions = ';'.join(defineArray)

   def get_build_dir(self, buildProperty, default_build_node):
      relative_path = default_build_node.path_from(self.ctx.bldnode)
      out_dir = self.ctx.out_dir + '\\' + self.ctx.env.ENVIRONMENT + '_' + buildProperty.platform + '_' + buildProperty.configuration + '\\' + relative_path
      return out_dir

   def write(self):
      Logs.debug('msvs: creating %r',self.path)
      template1=msvs.compile_template(PROJECT_2019_TEMPLATE)
      proj_str=template1(self)
      proj_str=msvs.rm_blank_lines(proj_str)
      self.path.stealth_write(proj_str)
      template2=msvs.compile_template(msvs.FILTER_TEMPLATE)
      filter_str=template2(self)
      filter_str=msvs.rm_blank_lines(filter_str)
      tmp=self.path.parent.make_node(self.path.name+'.filters')
      tmp.stealth_write(filter_str)
   
   def get_waf(self):
      return 'cd /d "%s" & %s' % (self.ctx.env.WafRootDir, getattr(self.ctx, 'waf_command', 'waf.bat'))

   def CreateArgumentFromProps(self, props):
      return self.ctx.env.ENVIRONMENT + '_' + props.platform.lower() + '_' + props.configuration.lower()

   def get_build_params(self, props):
      """
      Override the default to add the target name
      """
      opt = '--execsolution=%s' % self.ctx.get_solution_node().win32path()
      if getattr(self, 'tg', None):
         opt += " --targets=%s" % self.tg.name
      buildArgument = self.CreateArgumentFromProps(props)
      #TODO HARDCODED
      return (self.get_waf(), "create_variant", buildArgument, opt)
   
   # TODO Clean this
   def get_build_params2(self, props):
      """
      Override the default to add the target name
      """
      opt = '--execsolution=%s' % self.ctx.get_solution_node().win32path()
      if getattr(self, 'tg', None):
         opt += " --targets=%s" % self.tg.name
      buildArgument = self.CreateArgumentFromProps(props)
      return (self.get_waf(), buildArgument, "create_variant", buildArgument, opt)

   def get_build_command(self, props):
      return "%s %s build_%s %s" % self.get_build_params(props)

   def get_clean_command(self, props):
      #TODO: one too many comment create_variant
      return "%s %s clean_%s %s" % self.get_build_params(props)

   def get_rebuild_command(self, props):
      return "%s clean_%s %s build_%s %s" % self.get_build_params2(props)

def CreateMsvs(cnf):
   class msvs_2019(msvs.msvs_generator):
      cmd = 'msvs2019'
      numver = '12.00'
      vsver = '2019'
      platforms = project_configure.GetPlatformsFromEnvironment(cnf.env.ENVIRONMENT)
      configurations = [configurationKey for configurationKey in project_configure.GetConfigurationsFromPlatform(cnf.env.ENVIRONMENT, platforms[0])]
      platform_toolset_ver = 'v142'
      vsnode_target = vsnode_target_custom

      def init(self):
         if not getattr(self, 'projects_dir', None):
            self.projects_dir = self.bldnode.make_node('Solution/.depproj')
            self.projects_dir.mkdir()

         if not getattr(self, 'configurations', None):
            self.configurations = ['Release'] # LocalRelease, RemoteDebug, etc
         if not getattr(self, 'platforms', None):
            self.platforms = ['Win32']
         if not getattr(self, 'all_projects', None):
            self.all_projects = []
         if not getattr(self, 'project_extension', None):
            self.project_extension = '.vcxproj'
         if not getattr(self, 'projects_dir', None):
            self.projects_dir = self.srcnode.make_node('.depproj')
            self.projects_dir.mkdir()

         # bind the classes to the object, so that subclass can provide custom generators
         if not getattr(self, 'vsnode_vsdir', None):
            self.vsnode_vsdir = msvs.vsnode_vsdir
         if not getattr(self, 'vsnode_target', None):
            self.vsnode_target = msvs.vsnode_target
         if not getattr(self, 'vsnode_build_all', None):
            self.vsnode_build_all = msvs.vsnode_build_all
         if not getattr(self, 'vsnode_install_all', None):
            self.vsnode_install_all = msvs.vsnode_install_all

      def get_solution_node(self):
         solution_name = getattr(self, 'solution_name', None)
         if not solution_name:
            solution_name = 'Solution/'+ getattr(Context.g_module, Context.APPNAME, 'project') + '.sln'
         if os.path.isabs(solution_name):
            self.solution_node = self.root.make_node(solution_name)
         else:
            self.solution_node = self.bldnode.make_node(solution_name)
         return self.solution_node

      def add_aliases(self):
         """
         Add a specific target that emulates the "make all" necessary for Visual studio when pressing F7
         We also add an alias for "make install" (disabled by default)
         """
         base = getattr(self, 'projects_dir', None) or self.tg.path

         node_project = base.make_node('build_all_projects' + self.project_extension) # Node
         p_build = self.vsnode_build_all(self, node_project)
         p_build.collect_properties()
         self.all_projects.append(p_build)

         node_project = base.make_node('install_all_projects' + self.project_extension) # Node
         p_install = self.vsnode_install_all(self, node_project)
         p_install.collect_properties()
         self.all_projects.append(p_install)
      

#TODO
from waflib.TaskGen import after_method, before_method, feature
@feature('cxxprogram', 'cxxshlib', 'cprogram', 'cshlib', 'cxx', 'c')
@after_method('apply_incpaths')
def set_pdb_flags(self):            
   if not 'msvc' in (self.env.CC_NAME, self.env.CXX_NAME):
      return  

   #  if not self.bld.is_option_true('generate_debug_info'):
   #      return

    # find the last debug symbol type of [/Z7, /Zi, /ZI] applied in cxxflags.
   last_debug_option = ''
   for opt in reversed(self.env['CXXFLAGS']):
      if opt in ['/Z7', '/Zi', '/ZI']:
         last_debug_option = opt
         break

   if last_debug_option in ['/Zi', '/ZI']:
      for t in getattr(self, 'compiled_tasks', []):
         pdb_folder = self.path.get_bld().make_node(t.inputs[0].name + '_' + "vc.pdb")
         pdb_cxxflag = '/Fd{}'.format(pdb_folder.abspath())
         t.env.append_value('CXXFLAGS', pdb_cxxflag)
         t.env.append_value('CFLAGS', pdb_cxxflag)

      # Make sure the PDB folder exists
      # pdb_folder.mkdir()
    
      # Add CXX and C Flags

      #   # Add PDB also to Precompiled header.  pch_task is not in compiled_tasks
      #   if getattr(self, 'pch_task', None):
      #       self.pch_task.env.append_value('CXXFLAGS', pdb_cxxflag)
      #       self.pch_task.env.append_value('CFLAGS', pdb_cxxflag)
