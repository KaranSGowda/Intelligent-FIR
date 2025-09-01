/**
 * Language selector functionality for the Intelligent FIR System
 * Handles loading available languages and setting the user's preferred language
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize language selector
    initLanguageSelector();
});

/**
 * Initialize the language selector dropdown
 */
function initLanguageSelector() {
    // Get language menu elements
    const languageMenu = document.getElementById('languageMenu');
    const currentLanguageText = document.getElementById('currentLanguage');
    
    if (!languageMenu || !currentLanguageText) return;
    
    // Fetch available languages from the API
    fetch('/api/speech/languages')
        .then(response => response.json())
        .then(data => {
            // Clear loading indicator
            languageMenu.innerHTML = '';
            
            // Update current language display
            if (data.current) {
                const currentLang = data.languages.find(lang => lang.code === data.current);
                if (currentLang) {
                    currentLanguageText.innerHTML = `${currentLang.flag} ${currentLang.native_name}`;
                }
            }
            
            // Add languages to dropdown
            data.languages.forEach(lang => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.className = 'dropdown-item language-option';
                a.href = '#';
                a.setAttribute('data-lang-code', lang.code);
                a.innerHTML = `${lang.flag} ${lang.native_name} <span class="text-muted">(${lang.name})</span>`;
                
                // Highlight current language
                if (data.current === lang.code) {
                    a.classList.add('active');
                    a.setAttribute('aria-current', 'true');
                }
                
                // Add click event to set language
                a.addEventListener('click', function(e) {
                    e.preventDefault();
                    setLanguage(lang.code, lang.flag, lang.native_name);
                });
                
                li.appendChild(a);
                languageMenu.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading languages:', error);
            languageMenu.innerHTML = '<li><div class="dropdown-item text-danger">Error loading languages</div></li>';
        });
}

/**
 * Set the user's preferred language
 * @param {string} langCode - The language code to set
 * @param {string} flag - The flag emoji for the language
 * @param {string} name - The native name of the language
 */
function setLanguage(langCode, flag, name) {
    // Update UI
    const currentLanguageText = document.getElementById('currentLanguage');
    if (currentLanguageText) {
        currentLanguageText.innerHTML = `${flag} ${name}`;
    }
    
    // Highlight active language in dropdown
    const languageOptions = document.querySelectorAll('.language-option');
    languageOptions.forEach(option => {
        if (option.getAttribute('data-lang-code') === langCode) {
            option.classList.add('active');
            option.setAttribute('aria-current', 'true');
        } else {
            option.classList.remove('active');
            option.removeAttribute('aria-current');
        }
    });
    
    // Save language preference to server
    fetch('/api/user/set-language', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: langCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload page to apply language changes
            window.location.reload();
        } else {
            console.error('Error setting language:', data.error);
        }
    })
    .catch(error => {
        console.error('Error setting language:', error);
    });
}

/**
 * Get the current language code
 * @returns {string} The current language code
 */
function getCurrentLanguage() {
    // Try to get from data attribute
    const currentLanguageText = document.getElementById('currentLanguage');
    if (currentLanguageText && currentLanguageText.getAttribute('data-lang-code')) {
        return currentLanguageText.getAttribute('data-lang-code');
    }
    
    // Default to English (India)
    return 'en-IN';
}

// Make functions available globally
window.getCurrentLanguage = getCurrentLanguage;
window.setLanguage = setLanguage;
