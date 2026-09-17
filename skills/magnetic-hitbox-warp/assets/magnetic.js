/**
 * Magnetic hitbox — pulls a control's visual toward the cursor while the pointer
 * is inside an enlarged invisible field, and springs it back on exit.
 *
 * Usage:  initMagnetic();                       // all .magnetic hosts
 *         initMagnetic(document.querySelector('nav'));
 * Host:   <span class="magnetic" data-magnetic="6">  (data-magnetic = max pull in px, default 6)
 *
 * Only runs on (hover: hover) and (pointer: fine); silent on touch and under reduced motion.
 * The *field* (host + ::before) is what tracks; the *button* is what moves — the real hit
 * area never moves, so the control can't run away from the cursor.
 */
function initMagnetic(root = document) {
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  if (!fine.matches) return;

  const hosts = root.querySelectorAll('.magnetic');
  hosts.forEach((host) => {
    const target = host.querySelector('.magnetic-target') || host.firstElementChild;
    if (!target) return;
    const maxPull = parseFloat(host.dataset.magnetic) || 6;
    let raf = 0, px = 0, py = 0;

    const move = (e) => {
      if (reduce.matches) return;
      const r = host.getBoundingClientRect();
      // vector from the host's centre, normalised to the host's half-size + reach
      const raw = getComputedStyle(host).getPropertyValue('--magnet-reach').trim();
      const rootPx = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
      const reach = raw.endsWith('rem') ? parseFloat(raw) * rootPx
                  : raw.endsWith('em')  ? parseFloat(raw) * (parseFloat(getComputedStyle(host).fontSize) || rootPx)
                  : parseFloat(raw) || 32;
      const dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2 + reach);
      const dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2 + reach);
      px = Math.max(-1, Math.min(1, dx)) * maxPull;
      py = Math.max(-1, Math.min(1, dy)) * maxPull;
      if (!raf) raf = requestAnimationFrame(apply);
    };
    const apply = () => {
      raf = 0;
      target.style.setProperty('--mx', `${px.toFixed(2)}px`);
      target.style.setProperty('--my', `${py.toFixed(2)}px`);
    };
    const enter = () => { host.classList.add('is-tracking'); };
    const leave = () => {
      host.classList.remove('is-tracking');
      target.style.setProperty('--mx', '0px');
      target.style.setProperty('--my', '0px');
    };

    host.addEventListener('pointerenter', enter);
    host.addEventListener('pointermove', move, { passive: true });
    host.addEventListener('pointerleave', leave);
    // Keyboard users get the visual state without the pull
    target.addEventListener('focus', enter);
    target.addEventListener('blur', leave);
  });

  reduce.addEventListener('change', () => {
    if (reduce.matches) hosts.forEach(h => { const t = h.querySelector('.magnetic-target'); t?.style.removeProperty('--mx'); t?.style.removeProperty('--my'); });
  });
}

if (typeof window !== 'undefined') { window.initMagnetic = initMagnetic; }
if (typeof module !== 'undefined') { module.exports = { initMagnetic }; }
