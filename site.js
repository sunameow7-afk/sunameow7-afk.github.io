/* ================================================================
   DTF — site.js   (shared by index.html and dtf.html)
   icons, nav behaviour, starfield, scroll reveal, screenshot lightbox
   ================================================================ */
lucide.createIcons();

/* ---------- nav: solid on scroll + mobile drawer ---------- */
(function () {
  var nav = document.querySelector('.nav');
  if (!nav) return;
  var onScroll = function () { nav.classList.toggle('solid', window.scrollY > 24); };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  var burger = nav.querySelector('.burger');
  if (burger) burger.addEventListener('click', function () { nav.classList.toggle('open'); });
  nav.querySelectorAll('.nav-mobile a').forEach(function (a) {
    a.addEventListener('click', function () { nav.classList.remove('open'); });
  });
})();

/* ---------- re-anchor deep links (#pricing / #showcase) after layout settles ----------
   A cross-page jump like index.html -> dtf.html#pricing scrolls before fonts and images
   finish laying out, which can leave the target off-screen. Re-run it on load. */
(function () {
  var NAV_OFFSET = 96;
  function reanchor() {
    var hash = location.hash;
    if (!hash || hash.length < 2) return;
    var el = document.getElementById(hash.slice(1));
    if (!el) return;
    var y = el.getBoundingClientRect().top + window.scrollY - NAV_OFFSET;
    window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'auto' });
  }
  window.addEventListener('load', reanchor);
  window.addEventListener('hashchange', reanchor);
})();

/* ---------- starfield (very subtle, purple dust) ---------- */
(function () {
  var s = document.getElementById('stars');
  if (!s) return;
  for (var i = 0; i < 46; i++) {
    var d = document.createElement('div');
    d.className = 'star';
    var sz = (Math.random() * 2 + 1).toFixed(1);
    d.style.cssText = 'left:' + (Math.random() * 100).toFixed(2) + '%;top:' + (Math.random() * 100).toFixed(2) +
      '%;width:' + sz + 'px;height:' + sz + 'px;animation-delay:-' + (Math.random() * 3.6).toFixed(2) + 's;' +
      'animation-duration:' + (3 + Math.random() * 3).toFixed(2) + 's';
    s.appendChild(d);
  }
})();

/* ---------- fade-up on scroll ---------- */
(function () {
  var els = document.querySelectorAll('.rv');
  if (!('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  els.forEach(function (el) { io.observe(el); });
})();

/* ---------- screenshot lightbox ---------- */
(function () {
  var lb = document.getElementById('lb');
  if (!lb) return;
  document.querySelectorAll('.shot').forEach(function (fig) {
    fig.addEventListener('click', function () {
      var img = fig.querySelector('img');
      if (!img) return;
      lb.querySelector('img').src = img.src;
      lb.style.display = 'flex';
    });
  });
  lb.addEventListener('click', function () { lb.style.display = 'none'; });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') lb.style.display = 'none';
  });
})();

/* ---------- anti-inspect deterrent: blocks F12 / Ctrl+Shift+I/J/C / Ctrl+U / Ctrl+S / right-click.
   Nothing sensitive lives in these pages — secrets stay server-side. ---------- */
(function () {
  "use strict";
  function b(e) { e.preventDefault(); e.stopPropagation(); return false; }
  document.addEventListener("contextmenu", b);
  document.addEventListener("keydown", function (e) {
    var k = (e.key || "").toLowerCase();
    if (e.key === "F12") return b(e);
    if (e.ctrlKey && e.shiftKey && (k === "i" || k === "j" || k === "c")) return b(e);
    if ((e.ctrlKey || e.metaKey) && (k === "u" || k === "s")) return b(e);
  });
})();
