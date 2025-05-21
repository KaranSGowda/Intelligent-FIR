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

        // Initialize
        this.init();
    }

    /**
     * Initialize the voice recorder
     */
    init() {
        // Check if browser supports getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showError('Your browser does not support audio recording. Please use a modern browser like Chrome, Firefox, or Edge.');
            this.disableRecording();
            return;
        }

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
     * Start recording audio from the microphone
     */
    async startRecording() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Create media recorder
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            // Set up event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                // Create audio blob and URL
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

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
            this.mediaRecorder.start();
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
            this.showError(`Could not access microphone: ${error.message}`);
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

        // Clear any existing timer
        this.clearStatusPolling();

        // Set up polling
        this.statusPollTimer = setInterval(() => {
            fetch(`${this.options.statusEndpoint}/${this.taskId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Update UI with status
                    // Determine status type based on progress
                    let statusType = 'transcribing';
                    if (data.status === 'completed') {
                        statusType = 'complete';
                    } else if (data.status === 'failed') {
                        statusType = 'error';
                    }

                    this.updateStatus(data.message, statusType);
                    this.updateProgress(data.progress || 0);

                    // Check if transcription is complete
                    if (data.status === 'completed') {
                        this.clearStatusPolling();
                        this.updateStatus('Transcription complete!', 'complete');
                        this.updateProgress(100);

                        // Set transcription text
                        if (this.transcriptionField && data.result) {
                            this.transcriptionField.value = data.result;

                            // Hide the overlay if it exists
                            const overlay = document.getElementById('transcriptionOverlay');
                            if (overlay) {
                                overlay.style.display = 'none';
                            }

                            // Trigger input event for any listeners
                            this.transcriptionField.dispatchEvent(new Event('input'));
                        }

                        // Call completion callback if provided
                        if (this.options.onTranscriptionComplete) {
                            this.options.onTranscriptionComplete(data.result);
                        }
                    }

                    // Check if transcription failed
                    if (data.status === 'failed') {
                        this.clearStatusPolling();

                        // Format the error message for better readability
                        let errorMessage = data.error || 'Unknown error';
                        if (errorMessage.includes('\n')) {
                            // If the error message contains newlines, format it as HTML
                            const formattedError = errorMessage.split('\n').map(line => {
                                // Bold the error titles
                                if (line.startsWith('Method')) {
                                    return `<strong>${line}</strong>`;
                                }
                                return line;
                            }).join('<br>');

                            // Create a more user-friendly message
                            const userMessage = "Transcription failed. Please try again with clearer audio or in a quieter environment.";

                            // Show the user-friendly message
                            this.showError(userMessage);

                            // Log the detailed error for debugging
                            console.error("Detailed transcription error:", formattedError);
                        } else {
                            // Simple error message
                            this.showError(`Transcription failed: ${errorMessage}`);
                        }
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
        if (this.statusPollTimer) {
            clearInterval(this.statusPollTimer);
            this.statusPollTimer = null;
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
     * Show an error message
     */
    showError(message) {
        this.updateStatus(`Error: ${message}`, 'error');
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
}
