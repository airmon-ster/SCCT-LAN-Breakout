@echo off
setlocal enabledelayedexpansion

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
    exit /b 0
)

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
endlocal
