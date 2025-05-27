/**
 * FIR Form functionality
 * Handles form submission, voice recording, and evidence uploads
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load transcription from multiple sources
    const descriptionInput = document.getElementById('incident_description');
    if (descriptionInput) {
        // Try to get transcription from different sources in order of preference
        const transcription =
            sessionStorage.getItem('voiceTranscription') ||
            localStorage.getItem('voiceTranscription') ||
            document.getElementById('transcription')?.value || '';

        if (transcription && transcription.trim() !== '') {
            descriptionInput.value = transcription;
            // Clear storage after successful load
            sessionStorage.removeItem('voiceTranscription');
            localStorage.removeItem('voiceTranscription');
        }
    }

    // Load languages for the recording dropdown
    const recordingLanguage = document.getElementById('recordingLanguage');
    if (recordingLanguage) {
        loadLanguages(recordingLanguage);
    }

    // Initialize the voice recorder
    const recorder = new AudioRecorder({
        transcribeEndpoint: '/new',
        recordButtonId: 'recordButton',
        stopButtonId: 'stopButton',
        audioElementId: 'audioPlayback',
        statusElementId: 'recordingStatus',
        languageCode: function() {
            // Get selected language from dropdown
            if (recordingLanguage && recordingLanguage.value) {
                return recordingLanguage.value;
            }
            return null; // Will use default language
        },
        onTranscriptionComplete: function(text, audioPath) {
            // Update form with transcription
            const transcriptionInput = document.getElementById('transcription');
            const descriptionInput = document.getElementById('incident_description');

            if (transcriptionInput && text) {
                transcriptionInput.value = text;
            }

            // Also populate the incident description if it's empty
            if (descriptionInput && text && !descriptionInput.value.trim()) {
                descriptionInput.value = text;
            }

            // Show transcription
            const transcriptionDisplay = document.getElementById('transcriptionDisplay');
            if (transcriptionDisplay) {
                if (text) {
                    // Show the transcription
                    transcriptionDisplay.textContent = text;
                    transcriptionDisplay.parentElement.classList.remove('d-none');

                    // If we received processing time info, show it
                    if (audioPath && audioPath.processing_time) {
                        const processingInfo = document.createElement('small');
                        processingInfo.className = 'text-muted d-block mt-1';
                        processingInfo.textContent = `Processing time: ${audioPath.processing_time}`;
                        transcriptionDisplay.parentElement.appendChild(processingInfo);
                    }
                } else {
                    transcriptionDisplay.textContent = 'Transcription failed. Please type your complaint manually.';
                    transcriptionDisplay.parentElement.classList.remove('d-none');
                    transcriptionDisplay.classList.add('text-warning');
                }
            }

            // Enable the submit button
            const submitButton = document.getElementById('submitFIR');
            if (submitButton) {
                submitButton.disabled = false;
            }

            // If we have an audio path, store it for form submission
            const audioPathInput = document.getElementById('audio_path');
            if (audioPathInput && audioPath) {
                audioPathInput.value = audioPath;
            }
        },
        onError: function(error) {
            console.error('Recorder error:', error);

            // Show a user-friendly error message
            const isTimeout = error.message && error.message.includes('timed out');

            if (isTimeout) {
                showAlert('The audio was recorded successfully, but the automatic transcription process timed out. ' +
                    'This can happen with longer recordings or when the server is busy. ' +
                    'You can still submit your complaint by typing it manually.', 'warning');

                // Focus on the incident description field to encourage manual entry
                const descriptionInput = document.getElementById('incident_description');
                if (descriptionInput) {
                    descriptionInput.focus();
                }
            } else {
                showAlert('Audio recording issue: There was a problem processing your audio. ' +
                    'You can still submit your complaint by typing it manually.', 'warning');
            }

            // Enable the submit button even if recording failed
            const submitButton = document.getElementById('submitFIR');
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });

    // Handle evidence file uploads
    const evidenceUpload = document.getElementById('evidenceUpload');
    const evidencePreview = document.getElementById('evidencePreview');

    if (evidenceUpload && evidencePreview) {
        evidenceUpload.addEventListener('change', function(e) {
            // Clear existing previews
            evidencePreview.innerHTML = '';

            // Create previews for each file
            Array.from(this.files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const imgContainer = document.createElement('div');
                        imgContainer.className = 'evidence-preview-item mb-2';

                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'img-thumbnail';
                        img.style.maxHeight = '150px';

                        imgContainer.appendChild(img);
                        evidencePreview.appendChild(imgContainer);
                    };
                    reader.readAsDataURL(file);
                } else {
                    // For non-image files, just show the filename
                    const fileContainer = document.createElement('div');
                    fileContainer.className = 'evidence-preview-item mb-2';
                    fileContainer.innerHTML = `<span class="badge bg-info">${file.name}</span>`;
                    evidencePreview.appendChild(fileContainer);
                }
            });

            // Show the preview section
            document.getElementById('evidencePreviewSection').classList.remove('d-none');
        });
    }

    // Handle image analysis
    const analyzeImageButton = document.getElementById('analyzeImageButton');
    if (analyzeImageButton) {
        analyzeImageButton.addEventListener('click', async function() {
            const evidenceUpload = document.getElementById('evidenceUpload');
            if (!evidenceUpload || !evidenceUpload.files || evidenceUpload.files.length === 0) {
                showAlert('Please select an image to analyze first', 'warning');
                return;
            }

            // Get the first image file
            const file = Array.from(evidenceUpload.files).find(f => f.type.startsWith('image/'));
            if (!file) {
                showAlert('Please select a valid image file', 'warning');
                return;
            }

            try {
                // Show loading state
                analyzeImageButton.disabled = true;
                analyzeImageButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';

                // Create form data
                const formData = new FormData();
                formData.append('image', file);

                // Send to server for analysis
                const response = await fetch('/fir/analyze_image', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                // Display the analysis
                const analysisResult = document.getElementById('imageAnalysisResult');
                if (analysisResult) {
                    analysisResult.textContent = data.analysis;
                    document.getElementById('imageAnalysisSection').classList.remove('d-none');
                }

                // Update description if it's empty
                const descriptionInput = document.getElementById('incident_description');
                if (descriptionInput && !descriptionInput.value.trim()) {
                    descriptionInput.value = data.analysis;
                }

            } catch (error) {
                console.error('Image analysis error:', error);
                showAlert('Error during image analysis: ' + error.message, 'danger');
            } finally {
                // Reset button state
                analyzeImageButton.disabled = false;
                analyzeImageButton.textContent = 'Analyze Image';
            }
        });
    }

    // Legal section analysis
    const analyzeLegalButton = document.getElementById('analyzeLegalButton');
    if (analyzeLegalButton) {
        analyzeLegalButton.addEventListener('click', function() {
            const description = document.getElementById('incident_description').value.trim();
            if (!description) {
                showAlert('Please provide an incident description to analyze', 'warning');
                return;
            }

            analyzeLegalSections(description);
        });
    }

    // Global function to analyze legal sections
    window.analyzeLegalSections = async function(text) {
        try {
            // Show loading state
            const legalSectionsContainer = document.getElementById('legalSectionsContainer');
            if (legalSectionsContainer) {
                legalSectionsContainer.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Analyzing applicable IPC sections...</p></div>';
                legalSectionsContainer.classList.remove('d-none');
            }

            // Send to server for analysis
            const response = await fetch('/fir/analyze_legal_sections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Display the analysis
            displayLegalSections(data.sections);

        } catch (error) {
            console.error('Legal section analysis error:', error);

            const legalSectionsContainer = document.getElementById('legalSectionsContainer');
            if (legalSectionsContainer) {
                legalSectionsContainer.innerHTML = `<div class="alert alert-danger">Error analyzing legal sections: ${error.message}</div>`;
            }
        }
    };

    // Function to display legal sections
    function displayLegalSections(sections) {
        const legalSectionsContainer = document.getElementById('legalSectionsContainer');
        if (!legalSectionsContainer) return;

        if (!sections || sections.length === 0) {
            legalSectionsContainer.innerHTML = '<div class="alert alert-info">No applicable IPC sections found. Please review the incident description.</div>';
            return;
        }

        // Sort sections by confidence (highest first)
        sections.sort((a, b) => b.confidence - a.confidence);

        let html = '<div class="card mb-4"><div class="card-header bg-primary text-white"><h5 class="mb-0">Applicable IPC Sections</h5></div><div class="card-body p-0"><div class="list-group list-group-flush">';

        sections.forEach(section => {
            const confidenceClass = section.confidence > 0.7 ? 'text-success' : (section.confidence > 0.4 ? 'text-warning' : 'text-danger');
            const confidencePercentage = Math.round(section.confidence * 100);

            html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="mb-0">Section ${section.section_code}: ${section.section_name}</h5>
                    <span class="badge bg-light ${confidenceClass}">Confidence: ${confidencePercentage}%</span>
                </div>
                <p class="mb-1">${section.section_description || 'No description available'}</p>
                <p class="mb-0 text-muted small">${section.relevance || 'No relevance information available'}</p>

                <input type="checkbox" name="legal_sections" value="${section.section_code}"
                       id="section_${section.section_code}" class="form-check-input mt-2" checked>
                <label for="section_${section.section_code}" class="form-check-label ms-2">Include in FIR</label>
            </div>`;
        });

        html += '</div></div></div>';

        legalSectionsContainer.innerHTML = html;
        legalSectionsContainer.classList.remove('d-none');
    }

    // Form validation before submission
    const firForm = document.getElementById('firForm');
    if (firForm) {
        firForm.addEventListener('submit', function(e) {
            const description = document.getElementById('incident_description').value.trim();

            if (!description) {
                e.preventDefault();
                showAlert('Please provide an incident description', 'warning');
            }

            // Check if legal sections have been analyzed
            const legalSectionsContainer = document.getElementById('legalSectionsContainer');
            if (legalSectionsContainer && legalSectionsContainer.classList.contains('d-none')) {
                // If we have a description but haven't analyzed legal sections, do it now
                if (description) {
                    analyzeLegalSections(description);
                }
            }
        });
    }

    // Helper function to show alerts
    function showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        alertContainer.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }

    /**
     * Load available languages into the dropdown
     * @param {HTMLSelectElement} selectElement - The select element to populate
     */
    function loadLanguages(selectElement) {
        fetch('/api/speech/languages')
            .then(response => response.json())
            .then(data => {
                // Clear loading option
                selectElement.innerHTML = '';

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

                        selectElement.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading languages:', error);
                selectElement.innerHTML = '<option value="en-IN">English (India)</option>';
            });
    }
});
