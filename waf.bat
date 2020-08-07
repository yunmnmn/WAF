@ECHO OFF

REM Name of the waf proxy file
SET WAF_PROXY=/waf_proxy.py

REM Get current directory
SET WAF_ROOT_DIR=%~dp0
REM remove the trailing slash
IF %WAF_ROOT_DIR:~-1%==\ SET WAF_ROOT_DIR=%WAF_ROOT_DIR:~0,-1%

REM Read the settings variables
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "WorkingDir" WAFSettings.ini') do SET WORKING_DIR=%%C
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "RootWafLibDir" WAFSettings.ini') do SET ROOT_WAF_LIB_DIR=%%C
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "PythonPath" WAFSettings.ini') do SET PYTHON_PATH=%%C
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "BuildDir" WAFSettings.ini') do SET BUILD_DIR=%%C
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "AppName" WAFSettings.ini') do SET APPNAME=%%C

FOR /F "tokens=1,2*" %%A in ('findstr /I /N "Environment" WAFSettings.ini') do SET ENVIRONMENT=%%C
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "IDE" WAFSettings.ini') do SET IDE=%%C
FOR /F "tokens=1,2*" %%A in ('findstr /I /N "Compiler" WAFSettings.ini') do SET COMPILER=%%C

CALL :NORMALIZEPATH %WORKING_DIR% WORKING_DIR_ABS
CALL :NORMALIZEPATH %ROOT_WAF_LIB_DIR% ROOT_WAF_LIB_DIR_ABS
CALL :NORMALIZEPATH %PYTHON_PATH% PYTHON_PATH_ABS
CALL :NORMALIZEPATH %BUILD_DIR% BUILD_DIR_ABS

REM Set the path to the waf proxy
SET WAF_PROXY_SCRIPT=%ROOT_WAF_LIB_DIR_ABS%%WAF_PROXY%

REM Check if the python is available
IF NOT EXIST %PYTHON_PATH_ABS% GOTO pythonNotFound
REM Check if the working directory exists
IF NOT EXIST %WORKING_DIR_ABS% GOTO workingDirNotFound
REM Check if the waf lib root directory is set
IF NOT EXIST %ROOT_WAF_LIB_DIR_ABS% GOTO wafRootLibDirNotFound
REM REM Check if the python waf_proxy script is available
IF NOT EXIST %WAF_PROXY_SCRIPT% GOTO wafProxyScriptNotFound 

CALL "%PYTHON_PATH_ABS%" "%WAF_PROXY_SCRIPT%"  "-wrdlib" "%ROOT_WAF_LIB_DIR_ABS%" "-cwd" "%WORKING_DIR_ABS%" "--environment=%ENVIRONMENT%" "--ide=%IDE%" "--compiler=%COMPILER%" "--out=%BUILD_DIR_ABS%" "--appname=%APPNAME%" "--wrd=%WAF_ROOT_DIR%" "--no-lock-in-top" "--no-lock-in-run" %*
EXIT /B

:pythonNotFound
ECHO Unable to locate python.
EXIT /B

:workingDirNotFound
ECHO Unable to find the working directory.
EXIT /B

:wafRootDirNotFound
ECHO Unable to locate Waf root directory.
EXIT /B

:wafRootLibDirNotFound
ECHO Unable to locate Waf lib root directory.
EXIT /B

:wafProxyScriptNotFound
ECHO Unable to locate the Waf_Proxy script. It needs to be available at the root of the Waf directory.
EXIT /B

REM Helper function to convert relative path to absolute. Absolute stays absolute
:NORMALIZEPATH
   SET RETVAL=%~dpfn1
   REM remove trailing spaces
   IF %RETVAL:~-1%==" " SET RETVAL=%RETVAL:~0,-1%
   REM remove trailing slashes
   IF %RETVAL:~-1%==\ SET RETVAL=%RETVAL:~0,-1%
   SET %~2=%RETVAL%
   REM For debugging purposes
   REM ECHO %RETVAL%
   EXIT /B
