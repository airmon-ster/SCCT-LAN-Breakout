@echo off
REM Check for Python installation
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python is installed.
) else (
    echo Python is not installed. Downloading and installing Python...
    
    set downloadURL=https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe
    set installer=python-latest.exe
    
    echo Downloading Python installer...
    powershell -Command "Invoke-WebRequest -Uri %downloadURL% -OutFile %installer%"
    
    echo Installing Python...
    start /wait %installer% /quiet InstallAllUsers=1 PrependPath=1
    
    echo Cleaning up...
    del %installer%
    
    echo Python installation completed. Verifying installation...
    python --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Python has been successfully installed and added to PATH.
    ) else (
        echo Failed to install Python or add it to PATH.
    )
)

REM Set the working directory to the location of the batch file
cd /d %~dp0

@REM REM Launch Microsoft Edge with specified parameters
@REM echo Launching Microsoft Edge...
@REM start msedge --disable-pinch --guest --disable-extensions --app=http://127.0.0.1:8000

REM Install Python Dependencies and Run Python script gui.py
echo checking Python dependencies...
python -m pip install -r %~dp0requirements.txt

echo Current directory is: %cd%
echo Running Python script gui.py...
python %~dp0gui.py

@REM REM Create a Desktop Shortcut
@REM powershell -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('%UserProfile%\Desktop\Run Script.lnk'); $Shortcut.TargetPath = '%~dp0run.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"
