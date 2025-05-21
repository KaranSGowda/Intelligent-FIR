@echo off
echo Setting up FFmpeg for Intelligent FIR System...

:: Create directories
mkdir %USERPROFILE%\ffmpeg
cd %USERPROFILE%\ffmpeg

:: Download FFmpeg
echo Downloading FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"

:: Extract the zip file
echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '%USERPROFILE%\ffmpeg' -Force"

:: Find the bin directory
for /d %%i in (%USERPROFILE%\ffmpeg\ffmpeg-*) do set FFMPEG_DIR=%%i

:: Add to PATH temporarily for this session
set PATH=%PATH%;%FFMPEG_DIR%\bin

:: Add to PATH permanently
echo Adding FFmpeg to PATH...
setx PATH "%PATH%;%FFMPEG_DIR%\bin"

echo FFmpeg has been set up successfully!
echo Please restart your command prompt and the Intelligent FIR System application.

pause
