// Voice to Text (Experimental) - Standalone JS for use in any page
// Usage: see templates/fir/new.html for HTML structure

(function() {
    // Elements must exist in the DOM
    const voiceInput = document.getElementById('voiceInput');
    const incidentDesc = document.getElementById('incident_description');
    const startBtn = document.getElementById('startVoiceBtn');
    const stopBtn = document.getElementById('stopVoiceBtn');
    const langSelect = document.getElementById('voiceLangSelect');

    if (!voiceInput || !startBtn || !stopBtn || !langSelect) return;

    let recognition;
    let recognizing = false;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        function setRecognitionLanguage() {
            if (recognition) {
                recognition.lang = langSelect.value;
            }
        }
        recognition = new SpeechRecognition();
        setRecognitionLanguage();
        recognition.continuous = false;
        recognition.interimResults = false;

        langSelect.addEventListener('change', function() {
            setRecognitionLanguage();
        });

        recognition.onstart = function() {
            recognizing = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            voiceInput.value = '';
        };
        recognition.onresult = function(event) {
            let transcript = '';
            for (let i = 0; i < event.results.length; ++i) {
                transcript += event.results[i][0].transcript;
            }
            voiceInput.value = transcript;
            // Optionally append to incident description
            if (incidentDesc) {
                incidentDesc.value += (incidentDesc.value ? '\n' : '') + transcript;
            }
        };
        recognition.onerror = function(event) {
            voiceInput.value = 'Error: ' + event.error;
        };
        recognition.onend = function() {
            recognizing = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            // Optionally finalize transcript here if needed
        };

        startBtn.onclick = function() {
            if (!recognizing) recognition.start();
        };
        stopBtn.onclick = function() {
            if (recognizing) recognition.stop();
        };
    } else {
        startBtn.disabled = true;
        stopBtn.disabled = true;
        voiceInput.value = 'Speech recognition not supported in this browser.';
    }
})();


