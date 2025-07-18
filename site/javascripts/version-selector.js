/**
 * Enhanced Version Selector for FinOps Optimizer Documentation
 * Integrates with Material theme and provides smooth version switching
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        versionsUrl: '../versions.json',
        currentVersion: getCurrentVersion(),
        storageKey: 'finops-docs-version-preference'
    };

    // Get current version from URL
    function getCurrentVersion() {
        const path = window.location.pathname;
        const match = path.match(/\/([^\/]+)\//);
        return match ? match[1] : 'latest';
    }

    // Load versions configuration
    async function loadVersions() {
        try {
            const response = await fetch(CONFIG.versionsUrl);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn('Could not load versions.json, using fallback:', error);
            return getFallbackVersions();
        }
    }

    // Fallback versions if JSON fails to load
    function getFallbackVersions() {
        return [
            { version: 'latest', title: 'Latest (Main)', aliases: ['main'] },
            { version: 'v2.1.0', title: 'v2.1.0 - AI Agents & Real-time Dashboards', aliases: [] },
            { version: 'v2.0.0', title: 'v2.0.0 - Multi-Cloud Support', aliases: [] },
            { version: 'v1.5.0', title: 'v1.5.0 - Oracle Cloud Integration', aliases: [] },
            { version: 'v1.0.0', title: 'v1.0.0 - Initial Release', aliases: [] }
        ];
    }

    // Create version selector HTML
    function createVersionSelector(versions) {
        const currentVersionInfo = versions.find(v => 
            v.version === CONFIG.currentVersion || v.aliases.includes(CONFIG.currentVersion)
        ) || versions[0];

        const selector = document.createElement('div');
        selector.className = 'md-version';
        selector.innerHTML = `
            <div class="md-version__current">
                <span class="md-version__label">Version:</span>
                <span class="md-version__value">${currentVersionInfo.title}</span>
                <svg class="md-version__icon" viewBox="0 0 24 24">
                    <path d="M7 10l5 5 5-5z"/>
                </svg>
            </div>
            <div class="md-version__list">
                ${versions.map(version => `
                    <div class="md-version__item ${version.version === CONFIG.currentVersion ? 'md-version__item--active' : ''}" 
                         data-version="${version.version}">
                        <span class="md-version__title">${version.title}</span>
                        ${version.version === CONFIG.currentVersion ? '<span class="md-version__badge">Current</span>' : ''}
                    </div>
                `).join('')}
            </div>
        `;

        return selector;
    }

    // Add CSS styles
    function addStyles() {
        const styles = `
            .md-version {
                position: relative;
                display: inline-block;
                margin-left: 1rem;
                font-size: 0.8rem;
            }

            .md-version__current {
                display: flex;
                align-items: center;
                padding: 0.5rem 1rem;
                background: var(--md-primary-fg-color--light);
                color: var(--md-primary-bg-color);
                border-radius: 0.2rem;
                cursor: pointer;
                transition: all 0.2s ease;
                user-select: none;
            }

            .md-version__current:hover {
                background: var(--md-primary-fg-color);
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .md-version__label {
                margin-right: 0.5rem;
                opacity: 0.8;
            }

            .md-version__value {
                font-weight: 500;
                margin-right: 0.5rem;
            }

            .md-version__icon {
                width: 1rem;
                height: 1rem;
                fill: currentColor;
                transition: transform 0.2s ease;
            }

            .md-version--open .md-version__icon {
                transform: rotate(180deg);
            }

            .md-version__list {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--md-default-bg-color);
                border: 1px solid var(--md-default-fg-color--lightest);
                border-radius: 0.2rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-0.5rem);
                transition: all 0.2s ease;
                min-width: 300px;
            }

            .md-version--open .md-version__list {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }

            .md-version__item {
                padding: 0.75rem 1rem;
                cursor: pointer;
                transition: background-color 0.2s ease;
                border-bottom: 1px solid var(--md-default-fg-color--lightest);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .md-version__item:last-child {
                border-bottom: none;
            }

            .md-version__item:hover {
                background: var(--md-default-fg-color--lightest);
            }

            .md-version__item--active {
                background: var(--md-primary-fg-color--light);
                color: var(--md-primary-bg-color);
            }

            .md-version__item--active:hover {
                background: var(--md-primary-fg-color);
            }

            .md-version__title {
                font-weight: 500;
            }

            .md-version__badge {
                background: var(--md-accent-fg-color);
                color: var(--md-accent-bg-color);
                padding: 0.2rem 0.5rem;
                border-radius: 1rem;
                font-size: 0.7rem;
                font-weight: 500;
            }

            .md-version__item--active .md-version__badge {
                background: var(--md-primary-bg-color);
                color: var(--md-primary-fg-color);
            }

            /* Mobile responsiveness */
            @media screen and (max-width: 76.1875em) {
                .md-version {
                    margin-left: 0;
                    margin-top: 0.5rem;
                }
                
                .md-version__list {
                    min-width: 250px;
                }
            }

            /* Dark mode adjustments */
            [data-md-color-scheme="slate"] .md-version__list {
                background: var(--md-default-bg-color);
                border-color: var(--md-default-fg-color--light);
            }

            [data-md-color-scheme="slate"] .md-version__item:hover {
                background: var(--md-default-fg-color--light);
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    // Handle version switching
    function switchVersion(targetVersion) {
        const currentPath = window.location.pathname;
        const currentPage = currentPath.split('/').pop() || 'index.html';
        
        // Store user preference
        localStorage.setItem(CONFIG.storageKey, targetVersion);
        
        // Construct new URL
        const baseUrl = window.location.origin;
        const newUrl = `${baseUrl}/finopsoptimizer/${targetVersion}/${currentPage}`;
        
        // Add loading indicator
        showLoadingIndicator();
        
        // Navigate to new version
        window.location.href = newUrl;
    }

    // Show loading indicator
    function showLoadingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'md-version-loading';
        indicator.innerHTML = `
            <div class="md-version-loading__backdrop"></div>
            <div class="md-version-loading__spinner">
                <svg viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                        <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                        <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                    </circle>
                </svg>
                <span>Switching version...</span>
            </div>
        `;
        
        const loadingStyles = `
            .md-version-loading {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .md-version-loading__backdrop {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(2px);
            }
            
            .md-version-loading__spinner {
                position: relative;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 1rem;
                color: var(--md-primary-fg-color);
                background: var(--md-default-bg-color);
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            }
            
            .md-version-loading__spinner svg {
                width: 2rem;
                height: 2rem;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = loadingStyles;
        document.head.appendChild(styleSheet);
        document.body.appendChild(indicator);
    }

    // Initialize version selector
    async function initVersionSelector() {
        // Add styles first
        addStyles();
        
        // Load versions
        const versions = await loadVersions();
        
        // Find header navigation
        const header = document.querySelector('.md-header__inner');
        if (!header) {
            console.warn('Could not find header to insert version selector');
            return;
        }
        
        // Create and insert version selector
        const selector = createVersionSelector(versions);
        header.appendChild(selector);
        
        // Add event listeners
        const current = selector.querySelector('.md-version__current');
        const list = selector.querySelector('.md-version__list');
        const items = selector.querySelectorAll('.md-version__item');
        
        // Toggle dropdown
        current.addEventListener('click', (e) => {
            e.stopPropagation();
            selector.classList.toggle('md-version--open');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            selector.classList.remove('md-version--open');
        });
        
        // Handle version selection
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const version = item.dataset.version;
                if (version !== CONFIG.currentVersion) {
                    switchVersion(version);
                }
                selector.classList.remove('md-version--open');
            });
        });
        
        // Keyboard navigation
        selector.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                selector.classList.remove('md-version--open');
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVersionSelector);
    } else {
        initVersionSelector();
    }

    // Also initialize on navigation for SPA-like behavior
    document.addEventListener('DOMContentLoaded', () => {
        // Re-initialize on instant navigation
        document.addEventListener('DOMContentLoaded', initVersionSelector);
    });

})();