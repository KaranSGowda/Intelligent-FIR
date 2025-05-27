@echo off
echo ===== Intelligent FIR System =====
echo Setting up environment...

set PATH=%PATH%;K:\IntelligentFirSystem\Intelligent-FIR\ffmpeg
echo FFmpeg added to PATH for this session

echo Starting application...
python main.py
