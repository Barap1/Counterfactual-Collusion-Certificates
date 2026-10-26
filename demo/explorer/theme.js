/* Early, local-only preference restoration. Storage may be unavailable on file://. */
(function () {
  'use strict';
  try { if (localStorage.getItem('ccc-theme') === 'dark') document.documentElement.dataset.theme = 'dark'; } catch (e) { /* light is the default */ }
})();
