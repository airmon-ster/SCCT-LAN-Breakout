@echo off
setlocal enabledelayedexpansion

powershell -Command "$PSVersionTable.PSVersion"
powershell -Command "winget install --id Microsoft.Powershell --source winget"
powershell -Command "$PSVersionTable.PSVersion"

REM Check if WinPcap is installed
wmic product where "name like 'WinPcap%%'" get name >nul 2>&1
if %errorlevel% == 0 (
    echo WinPcap detected, uninstalling...
    wmic product where "name like 'WinPcap%%'" call uninstall /nointeractive
    echo WinPcap uninstalled.
) else (
    echo WinPcap is not installed.
)

REM Check if NPCAP is installed
reg query "HKLM\SOFTWARE\WOW6432Node\Npcap" >nul 2>&1
if %errorlevel% == 0 (
    echo NPCAP is already installed.
) else (
    echo NPCAP not found, downloading and installing...
    set npcap_installer=npcap-1.70.exe
    powershell -Command "Invoke-WebRequest -Uri https://nmap.org/npcap/dist/npcap-1.70.exe -OutFile %npcap_installer%"
    
    echo Installing NPCAP...
    start /wait %npcap_installer% /SILENT
    
    echo Cleaning up NPCAP installer...
    del %npcap_installer%
    
    echo NPCAP installation completed.
)

REM Check if WireGuard is installed
reg query "HKLM\SOFTWARE\WireGuard" >nul 2>&1
if %errorlevel% == 0 (
    echo WireGuard is already installed.
) else (
    echo WireGuard not found, downloading and installing...
    set wg_installer=wireguard-installer.msi
    powershell -Command "Invoke-WebRequest -Uri https://download.wireguard.com/windows-client/wireguard-installer.msi -OutFile %wg_installer%"
    
    echo Installing WireGuard...
    start /wait msiexec /i %wg_installer% /quiet
    
    echo Cleaning up WireGuard installer...
    del %wg_installer%
    
    echo WireGuard installation completed.
)


:: Set repository owner and name
set REPO_OWNER="airmon-ster"
set REPO_NAME="SCCT-LAN-Breakout"

:: GitHub API URL to fetch the latest release
set API_URL=https://api.github.com/repos/%REPO_OWNER%/%REPO_NAME%/releases/latest

:: Use PowerShell to fetch the latest release data and parse JSON to get the download URL and file name
for /f "delims=" %%i in ('powershell -Command "try { (Invoke-RestMethod -Uri '%API_URL%' -ErrorAction Stop).assets[0].browser_download_url } catch { Write-Output $_.Exception.Message; exit }"') do set DOWNLOAD_URL=%%i
for /f "delims=" %%j in ('powershell -Command "try { (Invoke-RestMethod -Uri '%API_URL%' -ErrorAction Stop).assets[0].name } catch { Write-Output $_.Exception.Message; exit }"') do set LATEST_RELEASE=%%j

:: Check if download URL is found
if not defined DOWNLOAD_URL (
    echo No download URL found. Exiting.
    exit /b 1
)

:: Read the current release file name from the 'release' file
if exist release (
    set /p CURRENT_RELEASE=<release
) else (
    set CURRENT_RELEASE=NONE
)

:: Print the current and latest release names
echo CURRENT_RELEASE: "%CURRENT_RELEASE%"
echo LATEST_RELEASE: "%LATEST_RELEASE%"

:: Compare the current release with the latest release
if "!CURRENT_RELEASE!" == "!LATEST_RELEASE!" (
    echo Current release is up to date.
) else (
    :: Echo the download URL (for verification)
    echo Download URL: !DOWNLOAD_URL!

    :: Download the zip file using PowerShell
    echo Downloading latest release...
    powershell -Command "Invoke-WebRequest -Uri '!DOWNLOAD_URL!' -OutFile '!LATEST_RELEASE!'"

    :: Unzip the file into the current directory
    echo Extracting the archive...
    powershell -Command "Expand-Archive -Path '!LATEST_RELEASE!' -DestinationPath '.' -Force"

    :: Cleanup
    echo Cleanup done. Removing downloaded zip file...
    del !LATEST_RELEASE!

    :: Update the 'release' file with the new release name
    echo !LATEST_RELEASE!>release

    echo Your folder has been updated.
    timeout /t 3 /nobreak >nul
)


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

REM Install Python Dependencies and Run Python script gui.py
echo checking Python dependencies...
python -m pip install -r %~dp0requirements.txt

echo Current directory is: %cd%
echo Running Python script gui.py...
python %~dp0gui.py