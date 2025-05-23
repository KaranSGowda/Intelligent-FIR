/**
 * Voice Recorder and Transcription Module
 *
 * This module provides functionality for recording audio from the user's microphone,
 * uploading it to the server for transcription, and displaying the transcription results.
 */

class VoiceRecorder {
    constructor(options = {}) {
        // Configuration options
        this.options = {
            recordButtonId: options.recordButtonId || 'recordButton',
            stopButtonId: options.stopButtonId || 'stopButton',
            audioPlayerId: options.audioPlayerId || 'audioPlayer',
            transcriptionFieldId: options.transcriptionFieldId || 'transcriptionField',
            statusElementId: options.statusElementId || 'recordingStatus',
            progressBarId: options.progressBarId || 'transcriptionProgress',
            languageSelectorId: options.languageSelectorId || 'languageSelector',
            maxRecordingTime: options.maxRecordingTime || 300, // 5 minutes
            uploadEndpoint: options.uploadEndpoint || '/api/speech/upload',
            statusEndpoint: options.statusEndpoint || '/api/speech/status',
            languagesEndpoint: options.languagesEndpoint || '/api/speech/languages',
            statusPollInterval: options.statusPollInterval || 1000, // 1 second
            onTranscriptionComplete: options.onTranscriptionComplete || null,
            onError: options.onError || null,
            showAudioPlayer: options.showAudioPlayer !== undefined ? options.showAudioPlayer : true,
            autoUpload: options.autoUpload !== undefined ? options.autoUpload : true
        };

        // DOM elements
        this.recordButton = document.getElementById(this.options.recordButtonId);
        this.stopButton = document.getElementById(this.options.stopButtonId);
        this.audioPlayer = document.getElementById(this.options.audioPlayerId);
        this.transcriptionField = document.getElementById(this.options.transcriptionFieldId);
        this.statusElement = document.getElementById(this.options.statusElementId);
        this.progressBar = document.getElementById(this.options.progressBarId);
        this.languageSelector = document.getElementById(this.options.languageSelectorId);

        // Recording state
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingTimer = null;
        this.audioBlob = null;
        this.audioUrl = null;
        this.taskId = null;
        this.statusPollTimer = null;

        // Initialize retry button
        this.retryButton = document.getElementById('retryTranscription');
        if (this.retryButton) {
            this.retryButton.addEventListener('click', () => this.retryTranscription());
        }

        // Initialize
        this.init();
    }

    /**
     * Initialize the voice recorder
     */
    init() {
        // Check browser compatibility in detail
        this.checkBrowserCompatibility();

        // Set up event listeners
        if (this.recordButton) {
            this.recordButton.addEventListener('click', () => this.startRecording());
        }

        if (this.stopButton) {
            this.stopButton.addEventListener('click', () => this.stopRecording());
            this.stopButton.disabled = true;
        }

        // Load available languages
        if (this.languageSelector) {
            this.loadLanguages();
        }

        // Initialize UI
        this.updateStatus('Ready to record', '');
        this.updateProgress(0);
    }

    /**
     * Check browser compatibility for audio recording
     * Provides detailed error messages for different compatibility issues
     */
    checkBrowserCompatibility() {
        // Check if browser supports basic audio APIs
        if (!window.AudioContext && !window.webkitAudioContext) {
            this.showError('Your browser does not support the Web Audio API. Please use a modern browser like Chrome, Firefox, or Edge.');
            this.disableRecording();
            return false;
        }

        // Check if browser supports MediaDevices API
        if (!navigator.mediaDevices) {
            this.showError('Your browser does not support the MediaDevices API. This could be because you\'re using an older browser or the page is not being served over HTTPS.');
            this.disableRecording();
            return false;
        }

        // Check if browser supports getUserMedia
        if (!navigator.mediaDevices.getUserMedia) {
            this.showError('Your browser does not support getUserMedia. Please use a modern browser like Chrome (49+), Firefox (36+), Edge (79+), or Safari (14.1+).');
            this.disableRecording();
            return false;
        }

        // Check if browser supports MediaRecorder
        if (!window.MediaRecorder) {
            this.showError('Your browser does not support the MediaRecorder API. Please use a modern browser like Chrome (49+), Firefox (25+), Edge (79+), or Safari (14.1+).');
            this.disableRecording();
            return false;
        }

        // Check if browser supports WebM with Opus codec
        let isWebmOpusSupported = false;
        try {
            isWebmOpusSupported = MediaRecorder.isTypeSupported('audio/webm;codecs=opus');
        } catch (e) {
            // MediaRecorder.isTypeSupported might throw in some browsers
            isWebmOpusSupported = false;
        }

        if (!isWebmOpusSupported) {
            console.warn('WebM with Opus codec is not supported. Will try to use default codec.');
        }

        return true;
    }

    /**
     * Start recording audio from the microphone
     */
    async startRecording() {
        try {
            // Hide any previous error messages
            const errorContainer = document.getElementById('errorContainer');
            if (errorContainer) {
                errorContainer.style.display = 'none';
            }

            // Update status to show we're requesting microphone access
            this.updateStatus('Requesting microphone access...', 'transcribing');

            // Request microphone access with high-quality audio constraints
            let stream;
            try {
                // First try with high-quality settings
                stream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        channelCount: 2,
                        sampleRate: 44100,
                        sampleSize: 16
                    }
                });
                console.log('Using high-quality audio settings');
            } catch (highQualityError) {
                console.warn('Failed to get high-quality audio, trying with basic settings:', highQualityError);

                // If high-quality fails, try with basic settings
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        audio: true
                    });
                    console.log('Using basic audio settings');
                } catch (basicError) {
                    // If both fail, show a detailed error message
                    let errorMessage = 'Could not access microphone. ';

                    if (basicError.name === 'NotAllowedError' || basicError.name === 'PermissionDeniedError') {
                        errorMessage += 'You denied permission to use the microphone. Please allow microphone access in your browser settings and try again.';
                    } else if (basicError.name === 'NotFoundError' || basicError.name === 'DevicesNotFoundError') {
                        errorMessage += 'No microphone was found on your device. Please connect a microphone and try again.';
                    } else if (basicError.name === 'NotReadableError' || basicError.name === 'TrackStartError') {
                        errorMessage += 'Your microphone is busy or not available. Please close other applications that might be using your microphone.';
                    } else if (basicError.name === 'OverconstrainedError') {
                        errorMessage += 'The requested audio settings are not supported by your device.';
                    } else if (basicError.name === 'TypeError' || basicError.name === 'TypeError') {
                        errorMessage += 'Audio recording is not supported in this browser or context. Make sure you\'re using HTTPS.';
                    } else {
                        errorMessage += `Error: ${basicError.message}`;
                    }

                    throw new Error(errorMessage);
                }
            }

            // Determine the best supported MIME type
            let mimeType = 'audio/webm;codecs=opus';
            let fallbackMimeType = 'audio/webm';

            // Check if the preferred MIME type is supported
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                console.warn(`${mimeType} is not supported, trying fallback`);

                if (MediaRecorder.isTypeSupported(fallbackMimeType)) {
                    console.log(`Using fallback MIME type: ${fallbackMimeType}`);
                    mimeType = fallbackMimeType;
                } else {
                    console.warn('Fallback MIME type not supported, using browser default');
                    mimeType = '';  // Let the browser choose
                }
            }

            // Create media recorder with appropriate settings
            const recorderOptions = mimeType ? { mimeType, audioBitsPerSecond: 128000 } : {};
            this.mediaRecorder = new MediaRecorder(stream, recorderOptions);
            this.audioChunks = [];

            // Set up event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                // Create audio blob and URL
                const blobType = mimeType || 'audio/webm';
                this.audioBlob = new Blob(this.audioChunks, { type: blobType });

                if (this.options.showAudioPlayer && this.audioPlayer) {
                    this.audioUrl = URL.createObjectURL(this.audioBlob);
                    this.audioPlayer.src = this.audioUrl;
                    this.audioPlayer.style.display = 'block';
                }

                // Auto upload if enabled
                if (this.options.autoUpload) {
                    this.uploadAudio();
                }
            };

            // Start recording
            this.mediaRecorder.start(1000);  // Collect data every second
            this.isRecording = true;
            this.recordingStartTime = Date.now();

            // Update UI
            if (this.recordButton) this.recordButton.disabled = true;
            if (this.stopButton) this.stopButton.disabled = false;

            // Get selected language
            let languageInfo = '';
            if (this.languageSelector && this.languageSelector.value) {
                const selectedOption = this.languageSelector.options[this.languageSelector.selectedIndex];
                const langCode = this.languageSelector.value;
                languageInfo = ` in ${selectedOption.textContent.split(' ')[0]} ${langCode.split('-')[0]}`;
            }

            this.updateStatus(`Recording${languageInfo}... (click Stop when finished)`, 'recording');

            // Set up recording timer
            this.startRecordingTimer();

        } catch (error) {
            this.showError(`Microphone access error: ${error.message}`);
            console.error('Recording error:', error);
        }
    }

    /**
     * Stop recording audio
     */
    stopRecording() {
        if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
            return;
        }

        // Stop the media recorder
        this.mediaRecorder.stop();
        this.isRecording = false;

        // Stop all audio tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());

        // Clear recording timer
        this.clearRecordingTimer();

        // Update UI
        if (this.recordButton) this.recordButton.disabled = false;
        if (this.stopButton) this.stopButton.disabled = true;
        this.updateStatus('Recording stopped, processing...', 'transcribing');
    }

    /**
     * Upload the recorded audio for transcription
     */
    uploadAudio() {
        if (!this.audioBlob) {
            this.showError('No audio recorded');
            return;
        }

        // Create form data
        const formData = new FormData();
        formData.append('audio', this.audioBlob, 'recording.webm');

        // Add language if selected
        if (this.languageSelector && this.languageSelector.value) {
            formData.append('language', this.languageSelector.value);
            console.log(`Using language: ${this.languageSelector.value}`);
        }

        // Update UI
        this.updateStatus('Uploading audio for transcription...', 'transcribing');
        this.updateProgress(10);

        // Send to server
        fetch(this.options.uploadEndpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Store task ID for polling
            this.taskId = data.task_id;

            // Update UI
            this.updateStatus(`Transcription in progress: ${data.status.message}`, 'transcribing');
            this.updateProgress(data.status.progress || 15);

            // Start polling for status
            this.startStatusPolling();
        })
        .catch(error => {
            this.showError(`Error uploading audio: ${error.message}`);
        });
    }

    /**
     * Poll the server for transcription status
     */
    startStatusPolling() {
        if (!this.taskId) return;

        this.clearStatusPolling();  // Clear any existing polling

        // Start polling the status endpoint
        this.statusPollingInterval = setInterval(() => {
            fetch(`${this.options.statusEndpoint}/${this.taskId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Update progress bar
                    if (data.progress !== undefined) {
                        this.updateProgress(data.progress);
                    }

                    // Update status message
                    if (data.message) {
                        this.updateStatus(data.message, data.status);
                    }

                    // Check if transcription is complete
                    if (data.status === 'completed') {
                        this.clearStatusPolling();
                        this.updateStatus('Transcription complete!', 'complete');
                        this.updateProgress(100);

                        // Set transcription text
                        if (this.transcriptionField && data.result) {
                            this.transcriptionField.value = data.result;
                            this.transcriptionField.dispatchEvent(new Event('input'));
                        }

                        // Call completion callback if provided
                        if (this.options.onTranscriptionComplete) {
                            this.options.onTranscriptionComplete(data.result);
                        }
                    }

                    // Handle transcription failure
                    if (data.status === 'failed') {
                        this.clearStatusPolling();

                        // Keep the audio recording available for retry
                        if (this.audioBlob) {
                            const audioUrl = URL.createObjectURL(this.audioBlob);
                            if (this.audioPlayer) {
                                this.audioPlayer.src = audioUrl;
                                this.audioPlayer.style.display = 'block';
                            }
                        }

                        // Show retry button if it exists
                        const retryButton = document.getElementById('retryTranscription');
                        if (retryButton) {
                            retryButton.style.display = 'block';
                        }

                        // Show user-friendly error message
                        this.showError('Could not transcribe audio. Please try speaking more clearly or try again.');
                    }
                })
                .catch(error => {
                    this.clearStatusPolling();
                    this.showError(`Error checking transcription status: ${error.message}`);
                });
        }, this.options.statusPollInterval);
    }

    /**
     * Clear the status polling timer
     */
    clearStatusPolling() {
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
            this.statusPollingInterval = null;
        }
    }

    /**
     * Start the recording timer
     */
    startRecordingTimer() {
        // Clear any existing timer
        this.clearRecordingTimer();

        // Set up timer to stop recording after max time
        this.recordingTimer = setTimeout(() => {
            if (this.isRecording) {
                this.stopRecording();
                this.updateStatus('Maximum recording time reached');
            }
        }, this.options.maxRecordingTime * 1000);
    }

    /**
     * Clear the recording timer
     */
    clearRecordingTimer() {
        if (this.recordingTimer) {
            clearTimeout(this.recordingTimer);
            this.recordingTimer = null;
        }
    }

    /**
     * Update the status message
     */
    updateStatus(message, statusType = '') {
        if (this.statusElement) {
            this.statusElement.textContent = message;

            // Update status container class based on status type
            const statusContainer = this.statusElement.closest('.status-container');
            if (statusContainer) {
                // Remove all status classes
                statusContainer.classList.remove('status-recording', 'status-transcribing', 'status-complete', 'status-error');

                // Add appropriate status class
                if (statusType) {
                    statusContainer.classList.add(`status-${statusType}`);
                }

                // Update icon based on status
                const statusIcon = statusContainer.querySelector('.status-icon');
                if (statusIcon) {
                    statusIcon.className = 'fas status-icon';

                    // Add appropriate icon class
                    switch (statusType) {
                        case 'recording':
                            statusIcon.classList.add('fa-microphone');
                            break;
                        case 'transcribing':
                            statusIcon.classList.add('fa-cog', 'fa-spin');
                            break;
                        case 'complete':
                            statusIcon.classList.add('fa-check-circle');
                            break;
                        case 'error':
                            statusIcon.classList.add('fa-exclamation-circle');
                            break;
                        default:
                            statusIcon.classList.add('fa-info-circle');
                    }
                }
            }
        }
    }

    /**
     * Update the progress bar
     */
    updateProgress(percent) {
        if (this.progressBar) {
            // Ensure percent is a valid number between 0 and 100
            const validPercent = Math.max(0, Math.min(100, parseInt(percent) || 0));

            // Update progress bar width
            this.progressBar.style.width = `${validPercent}%`;
            this.progressBar.setAttribute('aria-valuenow', validPercent);

            // Update percentage text if it exists
            const percentageElement = document.getElementById('statusPercentage');
            if (percentageElement) {
                percentageElement.textContent = `${validPercent}%`;
            }
        }
    }

    /**
     * Show an error message with detailed troubleshooting information
     */
    showError(message) {
        // Update error container
        const errorContainer = document.getElementById('errorContainer');
        const errorMessage = document.getElementById('errorMessage');

        if (errorContainer && errorMessage) {
            // Parse the error message for specific cases
            let displayMessage = message;
            let errorType = 'error';
            let troubleshootingSteps = [];

            // Determine error type and provide specific troubleshooting steps
            if (message.includes('Could not detect clear speech') || message.includes('Could not transcribe audio')) {
                displayMessage = 'Could not transcribe your speech.';
                errorType = 'warning';
                troubleshootingSteps = [
                    'Speak louder and more clearly',
                    'Move to a quieter environment',
                    'Check your microphone settings',
                    'Speak at a moderate pace',
                    'Position the microphone closer to your mouth',
                    'Try typing your statement instead (see below)'
                ];

                // Show manual text input option
                this.showManualTextInput();
            } else if (message.includes('Network') || message.includes('API error')) {
                displayMessage = 'Connection issue detected.';
                errorType = 'network';
                troubleshootingSteps = [
                    'Check your internet connection',
                    'Ensure you have a stable connection',
                    'Try again in a few moments',
                    'If the problem persists, try refreshing the page',
                    'Try typing your statement instead (see below)'
                ];

                // Show manual text input option
                this.showManualTextInput();
            } else if (message.includes('microphone') || message.includes('audio')) {
                if (message.includes('denied permission') || message.includes('NotAllowedError')) {
                    displayMessage = 'Microphone access denied.';
                    errorType = 'permission';
                    troubleshootingSteps = [
                        'Click the padlock icon in your browser\'s address bar',
                        'Make sure microphone access is set to "Allow"',
                        'Refresh the page after changing permissions',
                        'Check your system privacy settings for microphone access',
                        'Try typing your statement instead (see below)'
                    ];

                    // Show manual text input option
                    this.showManualTextInput();
                } else if (message.includes('not found') || message.includes('NotFoundError')) {
                    displayMessage = 'No microphone detected.';
                    errorType = 'hardware';
                    troubleshootingSteps = [
                        'Connect a microphone to your device',
                        'If using a headset, make sure it\'s properly connected',
                        'Check if your microphone is recognized in your system settings',
                        'Try using a different microphone if available',
                        'Try typing your statement instead (see below)'
                    ];

                    // Show manual text input option
                    this.showManualTextInput();
                } else if (message.includes('busy') || message.includes('NotReadableError')) {
                    displayMessage = 'Your microphone is busy or not available.';
                    errorType = 'busy';
                    troubleshootingSteps = [
                        'Close other applications that might be using your microphone',
                        'Check if another browser tab is using your microphone',
                        'Restart your browser',
                        'If using a headset, try unplugging and reconnecting it',
                        'Try typing your statement instead (see below)'
                    ];

                    // Show manual text input option
                    this.showManualTextInput();
                } else {
                    displayMessage = 'Microphone access error.';
                    errorType = 'error';
                    troubleshootingSteps = [
                        'Make sure your browser has permission to use the microphone',
                        'Check if your microphone is working properly',
                        'Try using a different browser (Chrome, Firefox, or Edge)',
                        'Restart your browser',
                        'Make sure you\'re using a secure connection (HTTPS)',
                        'Try typing your statement instead (see below)'
                    ];

                    // Show manual text input option
                    this.showManualTextInput();
                }
            } else if (message.includes('browser') || message.includes('support')) {
                displayMessage = 'Browser compatibility issue.';
                errorType = 'compatibility';
                troubleshootingSteps = [
                    'Use a modern browser like Chrome, Firefox, or Edge',
                    'Update your browser to the latest version',
                    'Make sure JavaScript is enabled in your browser',
                    'Try disabling browser extensions that might interfere with audio recording',
                    'Try using an incognito/private browsing window',
                    'Try typing your statement instead (see below)'
                ];

                // Show manual text input option
                this.showManualTextInput();
            }

            // Build the error message HTML
            let messageHTML = `<strong>${displayMessage}</strong>`;

            // Add original error message in small text if it's different from the display message
            if (displayMessage !== message && !troubleshootingSteps.length) {
                messageHTML += `<br><small class="text-muted">${message}</small>`;
            }

            // Add troubleshooting steps if available
            if (troubleshootingSteps.length > 0) {
                messageHTML += '<br><br><strong>Please try:</strong><ol>';
                troubleshootingSteps.forEach(step => {
                    messageHTML += `<li>${step}</li>`;
                });
                messageHTML += '</ol>';
            }

            // Update the error message
            errorMessage.innerHTML = messageHTML;
            errorContainer.style.display = 'block';

            // Add error type class
            errorContainer.className = `error-container error-${errorType}`;

            // Show retry button for transcription errors
            if (message.includes('transcription') || message.includes('speech') || message.includes('Network') ||
                message.includes('microphone') && this.audioBlob) {
                if (this.retryButton) {
                    this.retryButton.style.display = 'block';

                    // Add hint text under retry button
                    let hintText = document.getElementById('retryHint');
                    if (!hintText) {
                        hintText = document.createElement('p');
                        hintText.id = 'retryHint';
                        hintText.className = 'text-muted small mt-2';
                        this.retryButton.parentNode.appendChild(hintText);
                    }

                    // Update hint text based on error type
                    if (errorType === 'warning') {
                        hintText.textContent = 'Tip: Try speaking more slowly and clearly, and make sure you are in a quiet environment';
                    } else if (errorType === 'network') {
                        hintText.textContent = 'Tip: Check your internet connection before retrying';
                    } else if (errorType === 'permission') {
                        hintText.textContent = 'Tip: Allow microphone access in your browser settings before retrying';
                    } else if (errorType === 'hardware') {
                        hintText.textContent = 'Tip: Make sure your microphone is properly connected before retrying';
                    } else if (errorType === 'busy') {
                        hintText.textContent = 'Tip: Close other applications using your microphone before retrying';
                    } else if (errorType === 'compatibility') {
                        hintText.textContent = 'Tip: Try using a different browser like Chrome or Firefox';
                    } else {
                        hintText.textContent = 'Tip: Try speaking more slowly and clearly when retrying';
                    }
                }
            }
        }

        // Keep the audio player visible if we have a recording
        if (this.audioBlob && this.audioPlayer) {
            const audioUrl = URL.createObjectURL(this.audioBlob);
            this.audioPlayer.src = audioUrl;
            this.audioPlayer.style.display = 'block';

            // Add playback speed controls if not already present
            if (!document.getElementById('playbackControls')) {
                const controlsDiv = document.createElement('div');
                controlsDiv.id = 'playbackControls';
                controlsDiv.className = 'mt-2';

                const speedSelect = document.createElement('select');
                speedSelect.className = 'form-control form-control-sm d-inline-block w-auto';
                speedSelect.innerHTML = `
                    <option value="0.75">0.75x Speed</option>
                    <option value="1" selected>Normal Speed</option>
                    <option value="1.25">1.25x Speed</option>
                    <option value="1.5">1.5x Speed</option>
                `;

                speedSelect.addEventListener('change', (e) => {
                    this.audioPlayer.playbackRate = parseFloat(e.target.value);
                });

                controlsDiv.appendChild(speedSelect);
                this.audioPlayer.parentNode.insertBefore(controlsDiv, this.audioPlayer.nextSibling);
            }
        }

        // Update status and progress
        this.updateStatus(message, 'error');
        this.updateProgress(0);
        console.error(message);

        if (this.options.onError) {
            this.options.onError(message);
        }
    }

    /**
     * Disable recording functionality
     */
    disableRecording() {
        if (this.recordButton) this.recordButton.disabled = true;
        if (this.stopButton) this.stopButton.disabled = true;
    }

    /**
     * Load available languages from the server
     */
    loadLanguages() {
        if (!this.languageSelector) return;

        // Show loading state
        this.languageSelector.innerHTML = '<option value="" disabled selected>Loading languages...</option>';

        // Fetch languages from server
        fetch(this.options.languagesEndpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Clear loading option
                this.languageSelector.innerHTML = '';

                // Check if speech recognition is available
                if (data.speech_recognition && !data.speech_recognition.available) {
                    // Speech recognition is not available
                    this.showSpeechRecognitionError(data.speech_recognition.missing_packages);
                    this.disableRecording();
                }

                // Add languages to dropdown
                if (data.languages) {
                    data.languages.forEach(lang => {
                        const option = document.createElement('option');
                        option.value = lang.code;
                        option.textContent = `${lang.flag} ${lang.native_name} (${lang.name})`;

                        // Set current language as selected
                        if (data.current === lang.code) {
                            option.selected = true;
                        }

                        this.languageSelector.appendChild(option);
                    });
                } else {
                    // Fallback if no languages returned
                    this.addDefaultLanguages();
                }
            })
            .catch(error => {
                console.error(`Error loading languages: ${error.message}`);
                this.addDefaultLanguages();
            });
    }

    /**
     * Add default languages to the selector as fallback
     */
    addDefaultLanguages() {
        if (!this.languageSelector) return;

        // Clear any existing options
        this.languageSelector.innerHTML = '';

        // Add default languages
        const defaultLanguages = [
            { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
            { code: 'en-GB', name: 'English (UK)', flag: '🇬🇧' },
            { code: 'en-IN', name: 'English (India)', flag: '🇮🇳' },
            { code: 'hi-IN', name: 'Hindi', flag: '🇮🇳' },
            { code: 'bn-IN', name: 'Bengali', flag: '🇮🇳' },
            { code: 'ta-IN', name: 'Tamil', flag: '🇮🇳' },
            { code: 'te-IN', name: 'Telugu', flag: '🇮🇳' },
            { code: 'mr-IN', name: 'Marathi', flag: '🇮🇳' },
            { code: 'gu-IN', name: 'Gujarati', flag: '🇮🇳' },
            { code: 'kn-IN', name: 'Kannada', flag: '🇮🇳' },
            { code: 'ml-IN', name: 'Malayalam', flag: '🇮🇳' },
            { code: 'pa-IN', name: 'Punjabi', flag: '🇮🇳' }
        ];

        defaultLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = `${lang.flag} ${lang.name}`;

            // Default to English (India)
            if (lang.code === 'en-IN') {
                option.selected = true;
            }

            this.languageSelector.appendChild(option);
        });
    }

    /**
     * Show speech recognition error
     */
    showSpeechRecognitionError(missingPackages) {
        let errorMessage = "Speech recognition is not available on the server.";

        if (missingPackages && missingPackages.length > 0) {
            errorMessage += ` Missing packages: ${missingPackages.join(', ')}`;
        }

        this.showError(errorMessage);
    }

    /**
     * Clean up resources
     */
    destroy() {
        this.clearRecordingTimer();
        this.clearStatusPolling();

        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }

        if (this.audioUrl) {
            URL.revokeObjectURL(this.audioUrl);
        }
    }

    /**
     * Show manual text input option as a fallback
     */
    showManualTextInput() {
        // Check if manual input container already exists
        let manualInputContainer = document.getElementById('manualInputContainer');

        // If it doesn't exist, create it
        if (!manualInputContainer) {
            manualInputContainer = document.createElement('div');
            manualInputContainer.id = 'manualInputContainer';
            manualInputContainer.className = 'manual-input-container mt-4 p-3 border rounded';

            // Create heading
            const heading = document.createElement('h5');
            heading.textContent = 'Type Your Statement';
            heading.className = 'mb-3';

            // Create text area
            const textArea = document.createElement('textarea');
            textArea.id = 'manualTextInput';
            textArea.className = 'form-control mb-3';
            textArea.rows = 4;
            textArea.placeholder = 'Type your statement here instead of using voice recording...';

            // Create submit button
            const submitButton = document.createElement('button');
            submitButton.textContent = 'Use This Text';
            submitButton.className = 'btn btn-primary';
            submitButton.addEventListener('click', () => this.useManualText());

            // Assemble container
            manualInputContainer.appendChild(heading);
            manualInputContainer.appendChild(textArea);
            manualInputContainer.appendChild(submitButton);

            // Add to page - try to find the best location
            const transcriptionField = document.getElementById(this.options.transcriptionFieldId);
            if (transcriptionField && transcriptionField.parentNode) {
                transcriptionField.parentNode.insertBefore(manualInputContainer, transcriptionField.nextSibling);
            } else {
                // Fallback - add after error container
                const errorContainer = document.getElementById('errorContainer');
                if (errorContainer && errorContainer.parentNode) {
                    errorContainer.parentNode.insertBefore(manualInputContainer, errorContainer.nextSibling);
                } else {
                    // Last resort - add to body
                    document.body.appendChild(manualInputContainer);
                }
            }
        } else {
            // If it exists, just make sure it's visible
            manualInputContainer.style.display = 'block';
        }
    }

    /**
     * Use the manually entered text instead of voice transcription
     */
    useManualText() {
        const manualTextInput = document.getElementById('manualTextInput');
        if (!manualTextInput || !manualTextInput.value.trim()) {
            alert('Please enter some text first.');
            return;
        }

        // Get the text
        const text = manualTextInput.value.trim();

        // Update the transcription field
        if (this.transcriptionField) {
            this.transcriptionField.value = text;
            this.transcriptionField.dispatchEvent(new Event('input'));
        }

        // Update status
        this.updateStatus('Manual text entered successfully', 'complete');
        this.updateProgress(100);

        // Hide error container if it exists
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }

        // Call completion callback if provided
        if (this.options.onTranscriptionComplete) {
            this.options.onTranscriptionComplete(text);
        }
    }

    /**
     * Retry transcription with the existing audio
     */
    retryTranscription() {
        if (!this.audioBlob) {
            this.showError('No audio recording available to retry');
            return;
        }

        // Hide error container and retry button
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.style.display = 'none';
        }
        if (this.retryButton) {
            this.retryButton.style.display = 'none';
        }

        // Hide hint text if it exists
        const hintText = document.getElementById('retryHint');
        if (hintText) {
            hintText.style.display = 'none';
        }

        // Show transcribing status
        this.updateStatus('Retrying transcription...', 'transcribing');
        this.updateProgress(0);

        // Create a new FormData and append the existing audio
        const formData = new FormData();
        formData.append('audio', this.audioBlob, 'recording.webm');

        // Add language if available
        if (this.languageSelector) {
            formData.append('language', this.languageSelector.value);
        }

        // Add retry attempt count to help server optimize processing
        this.retryCount = (this.retryCount || 0) + 1;
        formData.append('retry_attempt', this.retryCount.toString());

        // Upload the audio again with retry flag
        fetch(this.options.uploadEndpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.task_id) {
                this.taskId = data.task_id;
                this.startStatusPolling();
            } else {
                throw new Error('No task ID received from server');
            }
        })
        .catch(error => {
            this.showError(`Error retrying transcription: ${error.message}`);
        });
    }
}
