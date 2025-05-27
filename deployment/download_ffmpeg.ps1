# PowerShell script to download and install FFmpeg

# Create a directory for FFmpeg
$ffmpegDir = "$env:USERPROFILE\ffmpeg"
New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null
Set-Location $ffmpegDir

Write-Host "Downloading FFmpeg..." -ForegroundColor Green

# Download FFmpeg using a more reliable method
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$output = "$ffmpegDir\ffmpeg.zip"

# Use .NET WebClient for download
$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($url, $output)

Write-Host "Extracting FFmpeg..." -ForegroundColor Green
Expand-Archive -Path $output -DestinationPath $ffmpegDir -Force

# Find the bin directory
$binDir = Get-ChildItem -Path $ffmpegDir -Filter "bin" -Recurse -Directory | Select-Object -First 1 -ExpandProperty FullName

# Add to PATH for current session
$env:Path += ";$binDir"

# Add to PATH permanently
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User)

Write-Host "FFmpeg has been installed to $binDir" -ForegroundColor Green
Write-Host "FFmpeg has been added to your PATH" -ForegroundColor Green
Write-Host "Please restart your application for the changes to take effect" -ForegroundColor Green

# Test if FFmpeg is working
try {
    $ffmpegVersion = & "$binDir\ffmpeg.exe" -version
    Write-Host "FFmpeg is working correctly!" -ForegroundColor Green
    Write-Host $ffmpegVersion[0] -ForegroundColor Cyan
} catch {
    Write-Host "Error testing FFmpeg: $_" -ForegroundColor Red
}

# Clean up
Remove-Item -Path $output -Force
