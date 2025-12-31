/**
 * Theme Toggle for The Order of Ethical Technologists
 * Handles dark/light mode with system preference detection
 * No external dependencies - pure vanilla JS
 */
(function() {
  'use strict';

  const STORAGE_KEY = 'oet-theme-preference';
  const THEME_ATTR = 'data-theme';

  /**
   * Get the user's theme preference
   * Priority: localStorage > system preference > light
   */
  function getThemePreference() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return stored;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  /**
   * Apply the theme to the document
   */
  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute(THEME_ATTR, 'dark');
    } else {
      document.documentElement.removeAttribute(THEME_ATTR);
    }

    // Update toggle button state
    const toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-pressed', theme === 'dark');
      toggleBtn.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  /**
   * Toggle between dark and light themes
   */
  function toggleTheme() {
    const current = document.documentElement.getAttribute(THEME_ATTR) === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';

    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  /**
   * Initialize mobile navigation toggle
   */
  function initMobileNav() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
      navToggle.addEventListener('click', function() {
        const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
        navToggle.setAttribute('aria-expanded', !isExpanded);
        navLinks.classList.toggle('is-open');
        navToggle.textContent = isExpanded ? 'Menu' : 'Close';
      });

      // Close menu when clicking a link
      navLinks.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function() {
          navToggle.setAttribute('aria-expanded', 'false');
          navLinks.classList.remove('is-open');
          navToggle.textContent = 'Menu';
        });
      });
    }
  }

  /**
   * Initialize theme system
   */
  function init() {
    // Apply theme immediately to prevent flash
    applyTheme(getThemePreference());

    // Set up toggle button
    const toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', toggleTheme);
    }

    // Initialize mobile navigation
    initMobileNav();

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
      // Only update if user hasn't set a manual preference
      if (!localStorage.getItem(STORAGE_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Also apply theme immediately to prevent flash of wrong theme
  applyTheme(getThemePreference());
})();
