/**
 * Audio recorder component for recording and transcribing user complaints
 */
class AudioRecorder {
    constructor(options = {}) {
        console.log('AudioRecorder constructor called with options:', options);
        
        this.audioBlob = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.transcribeEndpoint = options.transcribeEndpoint || '/transcribe';
        this.onTranscriptionComplete = options.onTranscriptionComplete || function(text) {};
        this.onRecordingStart = options.onRecordingStart || function() {};
        this.onRecordingStop = options.onRecordingStop || function() {};
        this.onError = options.onError || function(error) {};

        // Language support
        this.languageCode = options.languageCode || function() { return null; };

        // Define DOM elements
        this.recordButton = document.getElementById(options.recordButtonId || 'recordButton');
        this.stopButton = document.getElementById(options.stopButtonId || 'stopButton');
        this.audioElement = document.getElementById(options.audioElementId || 'audioPlayback');
        this.statusElement = document.getElementById(options.statusElementId || 'recordingStatus');
        this.textElement = document.getElementById(options.textElementId || 'incident_description');

        console.log('DOM elements found:');
        console.log('- Record button:', this.recordButton);
        console.log('- Stop button:', this.stopButton);
        console.log('- Audio element:', this.audioElement);
        console.log('- Status element:', this.statusElement);
        console.log('- Text element:', this.textElement);

        this.setupEventListeners();
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        console.log('Record button:', this.recordButton);
        console.log('Stop button:', this.stopButton);
        
        // Check browser compatibility
        this.checkBrowserCompatibility();
        
        if (this.recordButton) {
            this.recordButton.addEventListener('click', () => {
                console.log('Record button clicked');
                this.startRecording();
            });
            console.log('Record button event listener added');
        } else {
            console.error('Record button not found!');
        }

        if (this.stopButton) {
            this.stopButton.addEventListener('click', () => {
                console.log('Stop button clicked');
                this.stopRecording();
            });
            console.log('Stop button event listener added');
        } else {
            console.error('Stop button not found!');
        }
    }

    checkBrowserCompatibility() {
        console.log('Checking browser compatibility...');
        
        // Check for getUserMedia support - more comprehensive check
        const hasModernGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
        const hasLegacyGetUserMedia = !!(navigator.getUserMedia || navigator.webkitGetUserMedia || 
                                        navigator.mozGetUserMedia || navigator.msGetUserMedia);
        const hasGetUserMedia = hasModernGetUserMedia || hasLegacyGetUserMedia;
        
        console.log('Modern getUserMedia support:', hasModernGetUserMedia);
        console.log('Legacy getUserMedia support:', hasLegacyGetUserMedia);
        console.log('Total getUserMedia support:', hasGetUserMedia);
        
        // Check for MediaRecorder support
        const hasMediaRecorder = typeof MediaRecorder !== 'undefined';
        console.log('MediaRecorder support:', hasMediaRecorder);
        
        // Check for secure context (HTTPS)
        const isSecureContext = window.isSecureContext;
        console.log('Secure context (HTTPS):', isSecureContext);
        
        // Check for microphone permissions
        if (navigator.permissions) {
            navigator.permissions.query({ name: 'microphone' }).then(result => {
                console.log('Microphone permission state:', result.state);
            }).catch(err => {
                console.log('Could not check microphone permission:', err);
            });
        }
        
        if (!hasGetUserMedia) {
            console.error('Browser does not support getUserMedia API');
            this.updateStatus('Error: Browser does not support audio recording. Please try Chrome, Firefox, or Edge.');
        } else if (!hasMediaRecorder) {
            console.error('Browser does not support MediaRecorder API');
            this.updateStatus('Error: Browser does not support MediaRecorder API. Please try Chrome, Firefox, or Edge.');
        } else if (!isSecureContext) {
            console.warn('Not in secure context - recording may not work on HTTP');
            this.updateStatus('⚠️ Warning: Recording works best on HTTPS connections. Audio recording may not work properly on HTTP. For better compatibility, use HTTPS.');
        } else {
            console.log('Browser compatibility check passed');
            this.updateStatus('✅ Ready to record (HTTPS detected - optimal compatibility)');
        }
    }

    // Static method to test browser compatibility
    static testBrowserCompatibility() {
        console.log('=== Browser Compatibility Test ===');
        
        const results = {
            getUserMedia: false,
            mediaRecorder: false,
            secureContext: false,
            browser: navigator.userAgent,
            recommendations: []
        };
        
        // Test getUserMedia
        const hasModernGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
        const hasLegacyGetUserMedia = !!(navigator.getUserMedia || navigator.webkitGetUserMedia || 
                                        navigator.mozGetUserMedia || navigator.msGetUserMedia);
        results.getUserMedia = hasModernGetUserMedia || hasLegacyGetUserMedia;
        
        // Test MediaRecorder
        results.mediaRecorder = typeof MediaRecorder !== 'undefined';
        
        // Test secure context
        results.secureContext = window.isSecureContext;
        
        // Generate recommendations
        if (!results.getUserMedia) {
            results.recommendations.push('Switch to Chrome, Firefox, or Edge browser');
        }
        if (!results.mediaRecorder) {
            results.recommendations.push('Update your browser to a newer version');
        }
        if (!results.secureContext) {
            results.recommendations.push('Use HTTPS connection for better compatibility');
        }
        
        console.log('Test Results:', results);
        
        if (results.recommendations.length === 0) {
            console.log('✅ Browser is compatible with audio recording!');
        } else {
            console.log('❌ Browser compatibility issues found:');
            results.recommendations.forEach(rec => console.log('- ' + rec));
        }
        
        return results;
    }

    async startRecording() {
        try {
            console.log('Starting recording...');
            
            // Check if mediaDevices is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.log('Modern getUserMedia not supported, trying legacy APIs...');
                // Try older browser APIs
                const getUserMedia = navigator.getUserMedia ||
                                    navigator.webkitGetUserMedia ||
                                    navigator.mozGetUserMedia ||
                                    navigator.msGetUserMedia;

                if (!getUserMedia) {
                    throw new Error('Browser does not support audio recording. Please try a different browser like Chrome, Firefox, or Edge.');
                }

                // Use the older API with a promise wrapper
                this.stream = await new Promise((resolve, reject) => {
                    getUserMedia({ audio: true }, resolve, reject);
                });
            } else {
                console.log('Using modern getUserMedia API...');
                // Modern API - request microphone access
                try {
                    this.stream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        } 
                    });
                } catch (mediaError) {
                    console.log('Modern getUserMedia failed, trying with basic audio config...');
                    // Fallback to basic audio configuration
                    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                }
            }

            console.log('Microphone access granted, creating MediaRecorder...');
            this.updateStatus('Recording... Speak now');

            // Create media recorder with fallback for unsupported mime types
            try {
                this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'audio/webm' });
                console.log('Using audio/webm format');
            } catch (e) {
                console.log('audio/webm not supported, trying audio/mp4...');
                // If audio/webm is not supported, try audio/mp4
                try {
                    this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'audio/mp4' });
                    console.log('Using audio/mp4 format');
                } catch (e2) {
                    console.log('Using default MediaRecorder format');
                    // If that fails too, use the default
                    this.mediaRecorder = new MediaRecorder(this.stream);
                }
            }

            this.audioChunks = [];

            // Set up event handlers
            this.mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    console.log('Audio chunk received, size:', event.data.size);
                }
            });

            this.mediaRecorder.addEventListener('stop', () => {
                console.log('Recording stopped, processing audio...');
                // Determine the best mime type to use
                const mimeType = this.mediaRecorder.mimeType || 'audio/webm';
                this.audioBlob = new Blob(this.audioChunks, { type: mimeType });
                console.log('Audio blob created, size:', this.audioBlob.size);

                // Create URL for audio playback
                if (this.audioElement) {
                    this.audioElement.src = URL.createObjectURL(this.audioBlob);
                    this.audioElement.classList.remove('d-none');
                }

                // Transcribe the audio
                this.transcribeAudio();
            });

            // Start recording with a timeslice to get data periodically
            this.mediaRecorder.start(1000); // Get data every second
            this.isRecording = true;
            console.log('Recording started successfully');

            // Update UI
            if (this.recordButton) this.recordButton.disabled = true;
            if (this.stopButton) this.stopButton.disabled = false;

            this.onRecordingStart();
        } catch (error) {
            console.error('Recording error:', error);

            // Provide a more user-friendly error message
            let errorMessage = error.message;
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage = 'Microphone access denied. Please allow microphone access in your browser settings and try again.';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage = 'No microphone found. Please connect a microphone and try again.';
            } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                errorMessage = 'Could not access microphone. It may be in use by another application. Please close other applications using the microphone.';
            } else if (error.name === 'SecurityError') {
                errorMessage = 'Recording is only available on secure (HTTPS) connections. Please use HTTPS or localhost.';
            } else if (error.name === 'TypeError' && error.message.includes('getUserMedia')) {
                errorMessage = 'Cannot access microphone. This browser may not support recording or requires HTTPS. Please try Chrome, Firefox, or Edge.';
            } else if (error.message.includes('Browser does not support')) {
                errorMessage = error.message; // Keep the original message for browser compatibility errors
            } else {
                errorMessage = 'Recording failed: ' + error.message + '. Please try again or use a different browser.';
            }

            this.updateStatus('Error: ' + errorMessage);
            this.onError(error);
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.updateStatus('Processing audio...');

        // Stop recording
        this.mediaRecorder.stop();
        this.isRecording = false;

        // Stop all tracks in the stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }

        // Update UI
        if (this.recordButton) this.recordButton.disabled = false;
        if (this.stopButton) this.stopButton.disabled = true;

        this.onRecordingStop();
    }

    async transcribeAudio() {
        if (!this.audioBlob) {
            this.updateStatus('No audio recorded');
            return;
        }

        // Define variables in the outer scope so they're accessible in all try/catch blocks
        let progressInterval;
        let timeoutId;

        try {
            this.updateStatus('Transcribing audio... This may take up to a minute.');

            // Set up a progress indicator
            let dots = 0;
            progressInterval = setInterval(() => {
                dots = (dots + 1) % 4;
                this.updateStatus(`Transcribing audio${'.'.repeat(dots)} This may take up to a minute.`);
            }, 1000);

            // Create form data with audio file
            const formData = new FormData();

            // Get the mime type from the recorder or use a default
            const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
            const fileExtension = mimeType.includes('mp4') ? 'mp4' : 'webm';

            formData.append('audio', this.audioBlob, `recording.${fileExtension}`);
            formData.append('transcribe', 'true');

            // Add language code if available
            const langCode = typeof this.languageCode === 'function' ? this.languageCode() : this.languageCode;
            if (langCode) {
                formData.append('language', langCode);
                this.updateStatus(`Transcribing audio in ${langCode}...`);
            }

            try {
                // Create a promise that will reject after a timeout
                const timeoutPromise = new Promise((_, reject) => {
                    timeoutId = setTimeout(() => {
                        reject(new Error('Transcription request timed out'));
                    }, 120000); // 120 second timeout (2 minutes) - increased from 60 seconds
                });

                // Create the fetch promise
                const fetchPromise = fetch(this.transcribeEndpoint, {
                    method: 'POST',
                    body: formData
                });

                // Race the fetch against the timeout
                const response = await Promise.race([fetchPromise, timeoutPromise]);

                // Clear the timeout and progress indicator
                clearTimeout(timeoutId);
                clearInterval(progressInterval);

                if (!response.ok) {
                    if (response.status === 500) {
                        // For server errors, try to get the error message from the response
                        const errorData = await response.json().catch(() => ({}));
                        if (errorData && errorData.message) {
                            throw new Error(errorData.message);
                        } else {
                            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
                        }
                    } else {
                        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
                    }
                }

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                // Check for warnings or processing time info
                if (data.warning) {
                    this.updateStatus('Transcription completed with warnings: ' + data.warning);
                } else if (data.processing_time) {
                    this.updateStatus(`Transcription complete (${data.processing_time})`);
                } else {
                    this.updateStatus('Transcription complete');
                }

                // Update the text area with the transcription
                if (this.textElement && data.transcription) {
                    this.textElement.value = data.transcription;

                    // Trigger input event to update character count if needed
                    const event = new Event('input', { bubbles: true });
                    this.textElement.dispatchEvent(event);

                    // Focus on the text element to allow immediate editing
                    this.textElement.focus();

                    // Trigger the legal section analysis if available
                    if (typeof analyzeLegalSections === 'function') {
                        analyzeLegalSections(data.transcription);
                    }
                }

                // Pass all the data to the callback
                this.onTranscriptionComplete(data.transcription, {
                    path: data.audio_path,
                    processing_time: data.processing_time,
                    warning: data.warning
                });
            } catch (fetchError) {
                // Clean up timers
                if (timeoutId) clearTimeout(timeoutId);
                if (progressInterval) clearInterval(progressInterval);
                throw fetchError;
            }
        } catch (error) {
            // Clean up any remaining timers
            if (timeoutId) clearTimeout(timeoutId);
            if (progressInterval) clearInterval(progressInterval);

            // Check if this is a timeout error
            const isTimeout = error.message && error.message.includes('timed out');

            if (isTimeout) {
                this.updateStatus('Transcription timed out. Your audio has been recorded but automatic transcription is taking too long. Please type manually.');

                // For timeout errors, we still want to make the audio available and provide a partial transcription
                this.onTranscriptionComplete('Audio recorded successfully, but transcription timed out. Please type your complaint manually.', {
                    path: this.audioBlob ? URL.createObjectURL(this.audioBlob) : '',
                    processing_time: 'Timed out after 2 minutes',
                    warning: 'Transcription process took too long. The audio has been saved but could not be automatically transcribed.'
                });
            } else {
                this.updateStatus('Transcription error: ' + error.message);

                // For other errors, still make the audio available
                if (this.audioElement) {
                    this.onTranscriptionComplete('', {
                        path: this.audioBlob ? URL.createObjectURL(this.audioBlob) : '',
                        warning: 'Error during transcription: ' + error.message
                    });
                }
            }

            // Report the error to the error handler
            this.onError(error);
        }
    }

    updateStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
        console.log('Recorder status:', message);
    }

    reset() {
        this.audioBlob = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.audioElement) {
            this.audioElement.src = '';
        }

        if (this.recordButton) this.recordButton.disabled = false;
        if (this.stopButton) this.stopButton.disabled = true;

        this.updateStatus('Ready to record');
    }
}
