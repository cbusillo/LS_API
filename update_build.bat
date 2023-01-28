REM @ECHO OFF
REM run these two commands manually
REM winget install --id Git.Git -e --source winget
REM close window and open new
REM git clone https://github.com/cbusillo/LS_API

set REQVERSION=11
set "PYTHONROOT=%LOCALAPPDATA%\Programs\Python\Python3%REQVERSION%"
for /d %%d in (%PYTHONROOT%\Python311*) do (set "PYTHONVERSION=%%d" & goto break)
:break

set "PIP=%PYTHONVERSION%\scripts\pip"
set "PYTHON=%PYTHONVERSION%\python"
echo %PIP%
echo %PYTHON%

tasklist | find /i "python3.exe" && taskkill /im "python3.exe" /F || echo process "python3.exe" not running
cd /D %~dp0

git remote update
git diff origin/main --quiet update_build.bat
if %errorlevel% NEQ 0 (
	echo "Updating files."
	git pull https://github.com/cbusillo/LS_API
	echo "Restarting script."
	%0
	exit
) else (
	git pull https://github.com/cbusillo/LS_API
)

%PYTHON% --version
if %errorlevel% NEQ 0 (
	winget install -h --silent -a X64 -e --id Python.Python.3.%REQVERSION%
	echo "Restarting script."
	%0
	exit
)
%PIP% install virtualenv

if not exist .venv/ (
	%PYTHON% -m virtualenv .venv
)

REM .venv\scripts\activate.bat
%PIP% install -U -r requirements.txt


%PIP% install --upgrade pip wheel setuptools

%PIP% install -U -r requirements.txt


%PIP% install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/


%PYTHON% gui.py