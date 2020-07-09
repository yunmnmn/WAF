# WAF(WIP)

WAF template used to generate solutions.

- BuildSettings.json: Set the paths of the Project and the ThirdParty
- Configurations.json: Add configurations to the file, and the flags for each configuration. These flags will be applied to all the files. The Generic configuration flags will be applied to all configurations.
- Waf_Bat.settings: Set the WorkingDir(Where the root wscript resides), RootWafDir(where the WafLib resides), PythonPath(path to a python interpeter), and BuildDir(Where the intermediate build artifacts will be stored)

TODO:
- Support for platforms
- Profiler
- Easier integration
- Support for different IDEs
- Update README