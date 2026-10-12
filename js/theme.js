/* Theme toggle.
 *
 * No stored choice means the page follows the operating system, which is what
 * the CSS does on its own. Clicking stores an explicit choice on
 * <html data-theme>, and the page then ignores the system setting until the
 * visitor picks the other way.
 *
 * The pre-paint half of this lives inline in each page's <head> so a stored
 * choice applies before the first paint; without it, a visitor who chose dark
 * gets a white flash on every navigation.
 */
(function () {
  var root = document.documentElement;
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;

  // Font Awesome 5's fa-sun is a blunt-toothed ring that reads as a settings
  // cog at this size, so the sun is drawn here instead: solid disc, separated
  // rays. The moon is FA's, which is unambiguous already.
  var SUN =
    '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" ' +
    'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">' +
    '<circle cx="8" cy="8" r="3.05" fill="currentColor" stroke="none"/>' +
    '<path d="M8 .9v2M8 13.1v2M15.1 8h-2M2.9 8h-2' +
    'M13.02 2.98l-1.42 1.42M4.4 11.6l-1.42 1.42' +
    'M13.02 13.02l-1.42-1.42M4.4 4.4L2.98 2.98"/>' +
    '</svg>';
  var MOON = '<i class="fa-solid fa-moon" aria-hidden="true"></i>';

  var media = window.matchMedia('(prefers-color-scheme: dark)');

  function stored() {
    try {
      var v = localStorage.getItem('theme');
      return v === 'dark' || v === 'light' ? v : null;
    } catch (e) {
      return null; // private mode, or site data blocked
    }
  }

  function effective() {
    return stored() || (media.matches ? 'dark' : 'light');
  }

  function render() {
    var dark = effective() === 'dark';
    var label = dark ? 'Switch to light theme' : 'Switch to dark theme';
    btn.innerHTML = dark ? SUN : MOON;
    btn.setAttribute('aria-label', label);
    btn.setAttribute('title', label);
    btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
  }

  btn.addEventListener('click', function () {
    var next = effective() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    render();
  });

  // keep following the system for as long as no explicit choice is stored
  var onSystemChange = function () { if (!stored()) render(); };
  if (media.addEventListener) media.addEventListener('change', onSystemChange);
  else if (media.addListener) media.addListener(onSystemChange);

  render();
})();
