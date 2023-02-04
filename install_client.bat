set APPNAME="Shiny_API"
set PYTHONVERSION=10
set "PYTHONROOT=%LOCALAPPDATA%\Programs\Python"
for /d %%d in (%PYTHONROOT%\Python3%REQVERSION%*) do (set "PYTHONVERSION=%%d" & goto break)
:break
set "PYTHON=%PYTHONVERSION%\python"


tasklist | find /i "python3.exe" && taskkill /im "python3.exe" /F || echo process "python3.exe" not running

%PYTHON% --version
if %errorlevel% NEQ 0 (
	winget install --silent  --accept-package-agreements --accept-source-agreements python3.%PYTHONVERSION%
	echo "Restarting script."
	%0
	exit

)
%PYTHON% -m pip install virtualenv

if not exist %APPNAME% (
	%PYTHON% -m virtualenv %APPNAME%
)

set "VPYTHON=.\%APPNAME%\scripts\python.exe"

%VPYTHON% -m pip install --upgrade pip
%VPYTHON% -m pip install --upgrade %APPNAME%

