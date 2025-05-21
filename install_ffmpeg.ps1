# PowerShell script to install FFmpeg
# This script downloads FFmpeg, extracts it, and adds it to the PATH

# Create a directory for FFmpeg in the current project folder
$ffmpegDir = ".\ffmpeg"
New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null

Write-Host "Downloading FFmpeg..." -ForegroundColor Green

# Download FFmpeg using direct link to a stable release
$url = "https://github.com/GyanD/codexffmpeg/releases/download/6.0/ffmpeg-6.0-essentials_build.zip"
$output = "$ffmpegDir\ffmpeg.zip"

# Use .NET WebClient for download
$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($url, $output)

Write-Host "Extracting FFmpeg..." -ForegroundColor Green
Expand-Archive -Path $output -DestinationPath $ffmpegDir -Force

# Find the bin directory
$extractedDir = Get-ChildItem -Path $ffmpegDir -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
$binDir = Join-Path -Path $extractedDir.FullName -ChildPath "bin"

# Copy FFmpeg executables to the project's ffmpeg directory
Copy-Item -Path "$binDir\*" -Destination $ffmpegDir -Force

# Clean up the extracted files
Remove-Item -Path $output -Force
Remove-Item -Path $extractedDir.FullName -Recurse -Force

# Create a .bat file to set PATH for the current session
$batContent = @"
@echo off
set PATH=%PATH%;$((Get-Item $ffmpegDir).FullName)
echo FFmpeg added to PATH for this session
echo You can now run the application with: python main.py
"@

Set-Content -Path "run_with_ffmpeg.bat" -Value $batContent

Write-Host "FFmpeg has been installed to $((Get-Item $ffmpegDir).FullName)" -ForegroundColor Green
Write-Host "To run the application with FFmpeg, use the run_with_ffmpeg.bat script" -ForegroundColor Green

# Test if FFmpeg is working
try {
    $env:PATH += ";$((Get-Item $ffmpegDir).FullName)"
    $ffmpegVersion = & "$ffmpegDir\ffmpeg.exe" -version
    Write-Host "FFmpeg is working correctly!" -ForegroundColor Green
    Write-Host $ffmpegVersion[0] -ForegroundColor Cyan
} catch {
    Write-Host "Error testing FFmpeg: $_" -ForegroundColor Red
}
