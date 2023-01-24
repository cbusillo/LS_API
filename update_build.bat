@ECHO OFF
REM run these two commands manually
REM winget install --id Git.Git -e --source winget
REM git clone https://github.com/cbusillo/LS_API

tasklist | find /i "python3.exe" && taskkill /im "python3.exe" /F || echo process "python3.exe" not running
cd %~dp0/LS_API

git diff -- update_build.sh --quiet

if %ERRORLEVEL% NEQ 0 (
	echo "Updating files."
	git pull https://github.com/cbusillo/LS_API
	echo "Restarting script."
	%0
	exit
) else (
	git pull https://github.com/cbusillo/LS_API
)
FOR /F "tokens=* USEBACKQ" %%F IN (`python --version`) DO (
SET output=%%F
)

if "%output%" NEQ "Python 3.11.1" (
	winget install -h --silent -e --id Python.Python.3.11
)
%LOCALAPPDATA%\Programs\Python\Python311\scripts\pip install --upgrade pip wheel setuptools

%LOCALAPPDATA%\Programs\Python\Python311\python -m pip install "kivy[base] @ https://github.com/kivy/kivy/archive/master.zip"

%LOCALAPPDATA%\Programs\Python\Python311\scripts\pip install pipreqs
%LOCALAPPDATA%\Programs\Python\Python311\scripts\pip install -U -r requirements.txt

%LOCALAPPDATA%\Programs\Python\Python311\python gui.py