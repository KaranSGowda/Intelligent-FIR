# Language Training Guide for Intelligent-FIR System

## Overview

The Intelligent-FIR system supports multiple languages for speech recognition and UI translation. This guide explains how to train and customize the language functionality.

## Current Supported Languages

The system currently supports the following languages:

### English Variants
- **en-US**: English (US) 🇺🇸
- **en-GB**: English (UK) 🇬🇧  
- **en-IN**: English (India) 🇮🇳

### Indian Languages
- **hi-IN**: Hindi (हिन्दी) 🇮🇳
- **bn-IN**: Bengali (বাংলা) 🇮🇳
- **ta-IN**: Tamil (தமிழ்) 🇮🇳
- **te-IN**: Telugu (తెలుగు) 🇮🇳
- **mr-IN**: Marathi (मराठी) 🇮🇳
- **gu-IN**: Gujarati (ગુજરાતી) 🇮🇳
- **kn-IN**: Kannada (ಕನ್ನಡ) 🇮🇳
- **ml-IN**: Malayalam (മലയാളം) 🇮🇳
- **pa-IN**: Punjabi (ਪੰਜਾਬੀ) 🇮🇳

## How Language Training Works

### 1. Language Configuration (`utils/language_utils.py`)

The language system is configured in `utils/language_utils.py`:

```python
SUPPORTED_LANGUAGES = {
    'hi-IN': {
        'name': 'Hindi',
        'native_name': 'हिन्दी',
        'flag': '🇮🇳',
        'speech_code': 'hi-IN',
        'direction': 'ltr'
    },
    # ... more languages
}
```

### 2. UI Translations

Basic UI translations are stored in the `TRANSLATIONS` dictionary:

```python
TRANSLATIONS = {
    'hi-IN': {
        'file_complaint': 'शिकायत दर्ज करें',
        'record_voice': 'आवाज़ रिकॉर्ड करें',
        'stop_recording': 'रिकॉर्डिंग बंद करें',
        # ... more translations
    }
}
```

### 3. Speech Recognition

Speech recognition uses Google's Speech Recognition API with language-specific codes:

```python
def get_speech_recognition_language(lang_code=None):
    """Get the speech recognition language code."""
    if not lang_code:
        lang_code = get_user_language()
    
    if lang_code in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang_code]['speech_code']
    
    return 'en-US'  # Default to US English
```

## How to Add New Languages

### Step 1: Add Language Configuration

1. Open `utils/language_utils.py`
2. Add your new language to `SUPPORTED_LANGUAGES`:

```python
'new-lang': {
    'name': 'New Language',
    'native_name': 'Native Name',
    'flag': '🏳️',
    'speech_code': 'new-lang',
    'direction': 'ltr'  # or 'rtl' for right-to-left languages
}
```

### Step 2: Add UI Translations

Add translations for your new language in the `TRANSLATIONS` dictionary:

```python
'new-lang': {
    'file_complaint': 'Translation for "File a Complaint"',
    'record_voice': 'Translation for "Record Voice"',
    'stop_recording': 'Translation for "Stop Recording"',
    'transcribing': 'Translation for "Transcribing..."',
    'analyze_legal': 'Translation for "Analyze Legal Sections"',
    'submit': 'Translation for "Submit"',
    'incident_description': 'Translation for "Incident Description"',
    'incident_date': 'Translation for "Incident Date & Time"',
    'incident_location': 'Translation for "Incident Location"',
    'evidence_upload': 'Translation for "Upload Evidence"',
    'language_select': 'Translation for "Select Language"',
    'ready_to_record': 'Translation for "Ready to record"',
    'recording': 'Translation for "Recording... Speak now"',
    'processing': 'Translation for "Processing..."',
    'transcription_complete': 'Translation for "Transcription complete"',
    'transcription_failed': 'Translation for "Transcription failed. Please try again or type manually."',
    'analyzing_legal': 'Translation for "Analyzing applicable IPC sections..."',
    'legal_sections': 'Translation for "Applicable IPC Sections"',
    'confidence': 'Translation for "Confidence"',
    'include_in_fir': 'Translation for "Include in FIR"',
    'no_sections_found': 'Translation for "No applicable IPC sections found. Please review the incident description."'
}
```

### Step 3: Add Multilingual Training Data

For better ML model performance with different languages, add training data in multiple languages:

1. Create a new file `utils/multilingual_training_data.py`:

```python
# Multilingual training data for IPC sections
MULTILINGUAL_TRAINING_DATA = {
    'hi-IN': [
        ("आरोपी ने पीड़ित को चाकू से मार डाला।", ['302']),
        ("आरोपी ने पीड़ित पर हमला किया और चोट पहुंचाई।", ['323']),
        ("आरोपी ने पीड़ित को धोखा दिया।", ['420']),
        # Add more Hindi training examples
    ],
    'ta-IN': [
        ("குற்றவாளி பாதிக்கப்பட்டவரை கத்தியால் கொன்றார்.", ['302']),
        ("குற்றவாளி பாதிக்கப்பட்டவரை தாக்கி காயப்படுத்தினார்.", ['323']),
        ("குற்றவாளி பாதிக்கப்பட்டவரை ஏமாற்றினார்.", ['420']),
        # Add more Tamil training examples
    ],
    # Add more languages
}
```

2. Modify `utils/ml_analyzer.py` to use multilingual training data:

```python
def train_multilingual_model():
    """Train ML model with multilingual data."""
    from utils.multilingual_training_data import MULTILINGUAL_TRAINING_DATA
    
    all_training_data = []
    
    # Combine training data from all languages
    for lang_code, training_data in MULTILINGUAL_TRAINING_DATA.items():
        all_training_data.extend(training_data)
    
    # Add English training data
    from utils.training_data import TRAINING_DATA
    all_training_data.extend(TRAINING_DATA)
    
    # Train the model with combined data
    train_model(all_training_data)
```

### Step 4: Test the New Language

1. Restart the application
2. Go to the language selector dropdown
3. Select your new language
4. Test speech recognition and UI translations

## Training Speech Recognition for Better Accuracy

### 1. Language-Specific Speech Recognition Settings

Modify `utils/speech_recognition.py` to add language-specific recognition parameters:

```python
def _recognize_google(self, audio, language=None):
    """Enhanced wrapper for Google Speech Recognition with language-specific settings."""
    
    # Language-specific recognition configurations
    language_configs = {
        'hi-IN': {
            'energy_threshold': 150,
            'pause_threshold': 0.6,
            'phrase_threshold': 0.3
        },
        'ta-IN': {
            'energy_threshold': 120,
            'pause_threshold': 0.7,
            'phrase_threshold': 0.4
        },
        # Add more language-specific configurations
    }
    
    # Apply language-specific settings
    if language and language in language_configs:
        config = language_configs[language]
        self.recognizer.energy_threshold = config['energy_threshold']
        self.recognizer.pause_threshold = config['pause_threshold']
        self.recognizer.phrase_threshold = config['phrase_threshold']
```

### 2. Improve Recognition with Multiple Attempts

The system already tries multiple recognition attempts with different settings:

```python
# Multiple recognition attempts with different configurations
recognition_configs = [
    {'language': language, 'show_all': False},
    {'language': language, 'energy_threshold': 50, 'show_all': False},
    {'language': language, 'energy_threshold': 300, 'show_all': False},
    # Fallback to base language
    {'language': base_language, 'show_all': False},
    # Fallback to other Indian languages
    {'language': 'hi-IN', 'show_all': False},
    {'language': 'en-IN', 'show_all': False},
]
```

## Training the ML Model for Multilingual IPC Classification

### 1. Create Language-Specific IPC Keywords

Add language-specific keywords for better IPC section classification:

```python
# In utils/ml_analyzer.py
MULTILINGUAL_IPC_KEYWORDS = {
    'hi-IN': {
        '302': ['मार डाला', 'हत्या', 'कत्ल', 'मौत'],
        '323': ['मारपीट', 'हमला', 'चोट', 'आक्रमण'],
        '420': ['धोखा', 'फरेब', 'छल', 'धोखाधड़ी'],
        # Add more Hindi keywords
    },
    'ta-IN': {
        '302': ['கொன்றார்', 'கொலை', 'மரணம்'],
        '323': ['தாக்குதல்', 'காயம்', 'வன்முறை'],
        '420': ['ஏமாற்று', 'மோசடி', 'வஞ்சகம்'],
        # Add more Tamil keywords
    }
}
```

### 2. Enhance Keyword-Based Analysis

Modify the keyword analysis to use multilingual keywords:

```python
def multilingual_keyword_analysis(text, language='en-IN'):
    """Analyze text using language-specific keywords."""
    from utils.ml_analyzer import MULTILINGUAL_IPC_KEYWORDS
    
    result = {}
    
    if language in MULTILINGUAL_IPC_KEYWORDS:
        keywords = MULTILINGUAL_IPC_KEYWORDS[language]
        
        for section, section_keywords in keywords.items():
            matches = []
            for keyword in section_keywords:
                if keyword.lower() in text.lower():
                    matches.append(keyword)
            
            if matches:
                result[section] = {
                    'confidence': len(matches) / len(section_keywords),
                    'matched_keywords': matches
                }
    
    return result
```

## Best Practices for Language Training

### 1. Data Quality
- Use authentic, real-world complaint descriptions
- Include regional variations and dialects
- Ensure proper grammar and spelling in each language

### 2. Coverage
- Cover all major IPC sections (302, 307, 323, 376, 420, etc.)
- Include both simple and complex descriptions
- Add variations in sentence structure and vocabulary

### 3. Testing
- Test with native speakers
- Validate speech recognition accuracy
- Check UI translation completeness
- Verify IPC classification accuracy

### 4. Performance Optimization
- Use language-specific recognition parameters
- Implement fallback mechanisms
- Cache frequently used translations
- Optimize ML model for each language

## Troubleshooting Common Issues

### 1. Speech Recognition Not Working
- Check if the language code is supported by Google Speech Recognition
- Verify microphone permissions
- Test with HTTPS (required for audio recording)
- Check browser compatibility

### 2. Poor Translation Quality
- Review and improve translation accuracy
- Add missing translations
- Consider using professional translation services
- Test with native speakers

### 3. ML Model Performance Issues
- Increase training data for the specific language
- Add more language-specific keywords
- Tune model parameters for the language
- Consider separate models for different languages

## Running Training Scripts

### Train with New Language Data

```bash
# Train the comprehensive model with multilingual data
python scripts/train_comprehensive_model.py

# Train with specific language data
python scripts/train_with_new_cases.py

# Analyze training data coverage
python scripts/analyze_training_data.py
```

### Test Language Functionality

```bash
# Test speech recognition
python scripts/test_voice_transcription.py

# Test language selection
python scripts/test_language_functionality.py
```

## Conclusion

The language training system in Intelligent-FIR is designed to be extensible and maintainable. By following this guide, you can:

1. Add new languages easily
2. Improve speech recognition accuracy
3. Enhance UI translations
4. Train better ML models for multilingual IPC classification
5. Provide a better user experience for speakers of different languages

Remember to test thoroughly with native speakers and continuously improve the training data based on real-world usage patterns. 