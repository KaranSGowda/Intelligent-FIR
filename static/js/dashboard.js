/**
 * Enhanced Dashboard JavaScript for Intelligent FIR System
 * Modern interactive features and user experience improvements
 */

class DashboardManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        // Call individual search and filter functions instead of the missing combined function
        this.setupSearch();
        this.setupFilters();
        this.setupRealTimeUpdates();
        this.setupAccessibility();
        this.setupPerformanceOptimizations();
    }

    setupEventListeners() {
        // Card hover effects
        this.setupCardInteractions();
        
        // Search functionality
        this.setupSearch();
        
        // Filter functionality
        this.setupFilters();
        
        // Loading states
        this.setupLoadingStates();
        
        // Keyboard navigation
        this.setupKeyboardNavigation();
    }

    setupCardInteractions() {
        const cards = document.querySelectorAll('.complaint-card');
        
        cards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', (e) => {
                this.animateCardHover(card, true);
            });
            
            card.addEventListener('mouseleave', (e) => {
                this.animateCardHover(card, false);
            });
            
            // Add click effects
            card.addEventListener('click', (e) => {
                if (!e.target.closest('a, button')) {
                    const viewLink = card.querySelector('a[href*="view_fir"]');
                    if (viewLink) {
                        viewLink.click();
                    }
                }
            });
            
            // Add focus effects for accessibility
            card.addEventListener('focus', (e) => {
                this.animateCardFocus(card, true);
            });
            
            card.addEventListener('blur', (e) => {
                this.animateCardFocus(card, false);
            });
        });
    }

    animateCardHover(card, isHovering) {
        if (isHovering) {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
            
            // Add shimmer effect
            this.addShimmerEffect(card);
        } else {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            
            // Remove shimmer effect
            this.removeShimmerEffect(card);
        }
    }

    animateCardFocus(card, isFocused) {
        if (isFocused) {
            card.style.outline = '2px solid var(--embassy-primary)';
            card.style.outlineOffset = '2px';
        } else {
            card.style.outline = 'none';
        }
    }

    addShimmerEffect(card) {
        const shimmer = document.createElement('div');
        shimmer.className = 'shimmer-effect';
        shimmer.style.cssText = `
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            animation: shimmer 1.5s ease-in-out;
            pointer-events: none;
            z-index: 1;
        `;
        
        card.style.position = 'relative';
        card.appendChild(shimmer);
        
        // Remove shimmer after animation
        setTimeout(() => {
            this.removeShimmerEffect(card);
        }, 1500);
    }

    removeShimmerEffect(card) {
        const shimmer = card.querySelector('.shimmer-effect');
        if (shimmer) {
            shimmer.remove();
        }
    }

    setupSearch() {
        const searchInput = document.getElementById('search-complaints');
        if (!searchInput) return;

        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        // Add search suggestions
        this.setupSearchSuggestions(searchInput);
    }

    performSearch(query) {
        const cards = document.querySelectorAll('.complaint-card');
        const resultsContainer = document.querySelector('.complaints-section .row');
        
        if (!query.trim()) {
            cards.forEach(card => {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease-in-out';
            });
            return;
        }

        let visibleCount = 0;
        
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            if (matches) {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease-in-out';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Show no results message
        this.showNoResultsMessage(visibleCount === 0);
    }

    showNoResultsMessage(show) {
        let noResults = document.querySelector('.no-results-message');
        
        if (show) {
            if (!noResults) {
                noResults = document.createElement('div');
                noResults.className = 'no-results-message col-12 text-center py-5';
                noResults.innerHTML = `
                    <div class="no-results-icon mb-3">
                        <i class="fas fa-search fa-3x text-muted"></i>
                    </div>
                    <h4 class="text-muted">No complaints found</h4>
                    <p class="text-muted">Try adjusting your search terms</p>
                `;
                document.querySelector('.complaints-section .row').appendChild(noResults);
            }
            noResults.style.display = 'block';
        } else if (noResults) {
            noResults.style.display = 'none';
        }
    }

    setupSearchSuggestions(searchInput) {
        const suggestions = [
            'theft', 'assault', 'fraud', 'harassment', 'accident',
            'draft', 'filed', 'investigation', 'closed'
        ];

        searchInput.addEventListener('focus', () => {
            this.showSearchSuggestions(searchInput, suggestions);
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                this.hideSearchSuggestions();
            }, 200);
        });
    }

    showSearchSuggestions(input, suggestions) {
        this.hideSearchSuggestions();
        
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        suggestionsContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid var(--embassy-border);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            max-height: 200px;
            overflow-y: auto;
        `;

        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            item.style.cssText = `
                padding: 0.75rem 1rem;
                cursor: pointer;
                border-bottom: 1px solid var(--embassy-border);
                transition: background-color 0.2s;
            `;
            
            item.addEventListener('mouseenter', () => {
                item.style.backgroundColor = 'var(--embassy-section-bg)';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.backgroundColor = 'transparent';
            });
            
            item.addEventListener('click', () => {
                input.value = suggestion;
                input.focus();
                this.performSearch(suggestion);
                this.hideSearchSuggestions();
            });
            
            suggestionsContainer.appendChild(item);
        });

        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(suggestionsContainer);
    }

    hideSearchSuggestions() {
        const suggestions = document.querySelector('.search-suggestions');
        if (suggestions) {
            suggestions.remove();
        }
    }

    setupFilters() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = button.dataset.filter;
                this.applyFilter(filter);
                
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }

    applyFilter(filter) {
        const cards = document.querySelectorAll('.complaint-card');
        
        cards.forEach(card => {
            if (filter === 'all' || card.classList.contains(filter)) {
                card.style.display = 'block';
                card.style.animation = 'fadeIn 0.3s ease-in-out';
            } else {
                card.style.display = 'none';
            }
        });
    }

    setupLoadingStates() {
        // Add loading states for buttons
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                if (button.classList.contains('btn-loading')) return;
                
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                button.classList.add('btn-loading');
                button.disabled = true;
                
                // Reset after a delay (simulate loading)
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.classList.remove('btn-loading');
                    button.disabled = false;
                }, 2000);
            });
        });
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals or clear search
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('search-complaints');
                if (searchInput && document.activeElement === searchInput) {
                    searchInput.value = '';
                    this.performSearch('');
                    searchInput.blur();
                }
            }
            
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.getElementById('search-complaints');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }

    initializeAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'slideUp 0.6s ease-out forwards';
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe cards and stats
        document.querySelectorAll('.complaint-card, .stat-card').forEach(el => {
            observer.observe(el);
        });
    }

    setupRealTimeUpdates() {
        // Simulate real-time updates
        setInterval(() => {
            this.updateStats();
        }, 30000); // Update every 30 seconds
    }

    updateStats() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(stat => {
            const currentValue = parseInt(stat.textContent);
            const newValue = currentValue + Math.floor(Math.random() * 3);
            
            // Animate the number change
            this.animateNumberChange(stat, currentValue, newValue);
        });
    }

    animateNumberChange(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    setupAccessibility() {
        // Add ARIA labels
        const cards = document.querySelectorAll('.complaint-card');
        cards.forEach((card, index) => {
            card.setAttribute('role', 'button');
            card.setAttribute('tabindex', '0');
            card.setAttribute('aria-label', `Complaint ${index + 1}. Click to view details.`);
        });

        // Add skip links
        this.addSkipLinks();
    }

    addSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--embassy-primary);
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    setupPerformanceOptimizations() {
        // Lazy load images
        this.setupLazyLoading();
        
        // Debounce scroll events
        this.debounceScrollEvents();
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }

    debounceScrollEvents() {
        let scrollTimeout;
        
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                // Handle scroll-based animations
                this.handleScrollAnimations();
            }, 16); // ~60fps
        });
    }

    handleScrollAnimations() {
        // Add parallax effect to stats
        const stats = document.querySelector('.dashboard-stats');
        if (stats) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            stats.style.transform = `translateY(${rate}px)`;
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .btn-loading {
        pointer-events: none;
    }
    
    .filter-btn.active {
        background-color: var(--embassy-primary);
        color: white;
    }
    
    .complaint-card {
        cursor: pointer;
    }
    
    .complaint-card:focus {
        outline: 2px solid var(--embassy-primary);
        outline-offset: 2px;
    }
`;
document.head.appendChild(style);
