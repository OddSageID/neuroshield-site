/**
 * Theme Initialization - Prevents Flash of Unstyled Content (FOUC)
 *
 * This script MUST be loaded synchronously in <head> (no defer/async)
 * to apply the theme class before the body renders.
 *
 * Order of Ethical Technologists
 */
(function() {
  'use strict';

  var STORAGE_KEY = 'oet-theme-preference';
  var DARK_CLASS = 'dark-mode';

  // Check stored preference first, then system preference
  var stored = localStorage.getItem(STORAGE_KEY);
  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (stored === 'dark' || (!stored && prefersDark)) {
    document.documentElement.classList.add(DARK_CLASS);
  }
})();
