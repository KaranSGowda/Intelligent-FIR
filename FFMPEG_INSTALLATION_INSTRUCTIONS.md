# FFmpeg Installation Instructions

## Why You Need FFmpeg

The Intelligent FIR System uses FFmpeg for audio processing, which is required for the voice transcription feature to work properly. Without FFmpeg, you'll see the error:

```
Transcription failed: All transcription methods failed
```

## Installation Instructions

### For Windows:

1. **Download FFmpeg**:
   - Go to [FFmpeg.org](https://ffmpeg.org/download.html)
   - Click on "Windows" under "Get packages & executable files"
   - Download a Windows build (e.g., from gyan.dev)
   - Direct link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

2. **Extract and Set Up**:
   - Extract the ZIP file to a location like `C:\ffmpeg`
   - Add the `bin` folder to your system PATH:
     - Right-click on "This PC" → Properties
     - Click "Advanced system settings"
     - Click "Environment Variables"
     - Under "System variables", find "Path" and click "Edit"
     - Click "New" and add the path to the bin folder (e.g., `C:\ffmpeg\bin`)
     - Click "OK" on all dialogs

3. **Verify Installation**:
   - Open a new Command Prompt
   - Type `ffmpeg -version`
   - You should see version information if FFmpeg is correctly installed

### For Linux (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install ffmpeg
```

### For macOS:

```bash
brew install ffmpeg
```

## After Installing FFmpeg

After installing FFmpeg:

1. Restart your computer to ensure the PATH changes take effect
2. Restart the Intelligent FIR System application
3. Try using the voice recording feature again

## Troubleshooting

If you still encounter issues after installing FFmpeg:

1. Make sure you've restarted your computer after adding FFmpeg to the PATH
2. Verify FFmpeg is correctly installed by running `ffmpeg -version` in a command prompt
3. Check if there are any firewall or antivirus settings blocking the application from accessing your microphone
4. Try using a different browser (Chrome or Firefox are recommended)
5. Try recording shorter audio clips (10-15 seconds) first

## Alternative Solution

If you can't install FFmpeg or continue to have issues, you can still use the system by typing your statements manually instead of using voice recording.
