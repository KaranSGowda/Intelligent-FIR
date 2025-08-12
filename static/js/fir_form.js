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


});
