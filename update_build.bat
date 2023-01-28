REM @ECHO OFF
REM run these two commands manually
REM winget install --id Git.Git -e --source winget
REM close window and open new
REM git clone https://github.com/cbusillo/LS_API


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

if not exist "%PROGRAMFILES%\Microsoft Visual Studio\2022\Community" (
	winget install --id=Microsoft.VisualStudio.2022.BuildTools  -e
	winget install Microsoft.VisualStudio.2022.Community --silent --override "--wait --quiet --add ProductLang En-us --add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended"
	echo "Restarting script."
	%0
	exit
)

set REQVERSION=11
set "PYTHONROOT=%LOCALAPPDATA%\Programs\Python"
for /d %%d in (%PYTHONROOT%\Python3%REQVERSION%*) do (set "PYTHONVERSION=%%d" & goto break)
:break

set "PIP=%PYTHONVERSION%\scripts\pip"
set "PYTHON=%PYTHONVERSION%\python"
echo %PIP%
echo %PYTHON%

tasklist | find /i "python3.exe" && taskkill /im "python3.exe" /F || echo process "python3.exe" not running


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


%PIP% uninstall kivy
%PIP% install "kivy[base] @ https://github.com/kivy/kivy/archive/master.zip"


%PYTHON% gui.py