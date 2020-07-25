import os, sys
from waflib import Scripting
                         
VERSION="2.0.20"

# Set the working directory where the root wscript resides
cwdArgPos = [i for i,x in enumerate(sys.argv) if x == '-cwd']
if cwdArgPos: 
   os.chdir(sys.argv[cwdArgPos[0] + 1])
   # Clear out these arguments as waf will try to process them
   sys.argv.pop(cwdArgPos[0] + 1)
   sys.argv.pop(cwdArgPos[0])

cwd = os.getcwd()

# Set the WAF directory
wafdir = ""
cwdArgPos = [i for i,x in enumerate(sys.argv) if x == '-wrdlib']
if cwdArgPos: 
   wafdir = os.path.normpath(sys.argv[cwdArgPos[0] + 1])
   # Clear out these arguments as waf will try to process them
   sys.argv.pop(cwdArgPos[0] + 1)
   sys.argv.pop(cwdArgPos[0])

# Run the entrypoint of WAF
Scripting.waf_entry_point(cwd, VERSION, wafdir)
