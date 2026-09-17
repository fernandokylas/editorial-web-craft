/**
 * Inertia planes — JS fallback for parallax on browsers without scroll-driven
 * animations, plus the IntersectionObserver that triggers `.arrive` elements.
 *
 * This never touches the main scroll position. Native scrolling stays native:
 * find-in-page, keyboard paging, scroll restoration and assistive tech all work.
 * Only decorative planes are moved, and they lerp toward their target so the
 * motion has weight without ever lagging the content.
 *
 * Markup:  <section class="kinetic-section">
 *            <div class="parallax-meta-bg" data-plane="0.3">01</div>
 *            <div class="kinetic-content">… <p class="arrive">…</p> …</div>
 *          </section>
 */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const supportsSDA = CSS.supports('animation-timeline: view()');

  // 1. Scroll-cued arrivals (CSS does the easing; we only flip the class)
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.1 });
  const arrivals = document.querySelectorAll('.arrive');
  arrivals.forEach(el => reduce.matches ? el.classList.add('is-in') : io.observe(el));
  // Anything sitting in the last few percent of a page that can't scroll further would never cross
  // the observer's margin — reveal what's left once the page is at (or near) its end.
  const revealTail = () => {
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4)
      arrivals.forEach(el => el.classList.add('is-in'));
  };
  addEventListener('scroll', revealTail, { passive: true });
  addEventListener('load', revealTail);

  // 2. Parallax planes — only where the CSS version isn't available
  if (supportsSDA || reduce.matches) return;

  const planes = [...document.querySelectorAll('[data-plane]')].map(el => ({
    el, factor: parseFloat(el.dataset.plane) || 0.3, current: 0, target: 0,
    section: el.closest('.kinetic-section') || el.parentElement,
  }));
  if (!planes.length) return;

  const LERP = 0.12;             // 0 = never arrives, 1 = no smoothing; ~0.1–0.15 reads as weight
  let ticking = false;

  function measure() {
    const vh = window.innerHeight;
    for (const p of planes) {
      const r = p.section.getBoundingClientRect();
      const progress = (vh - r.top) / (vh + r.height);          // 0 entering → 1 leaving
      p.target = (progress - 0.5) * 0.8 * vh * p.factor;        // −0.4vh·f at entry → +0.4vh·f at exit, same as the CSS keyframes
    }
  }
  function frame() {
    let moving = false;
    for (const p of planes) {
      p.current += (p.target - p.current) * LERP;
      if (Math.abs(p.target - p.current) > 0.05) moving = true;
      p.el.style.transform = `translate3d(0, ${p.current.toFixed(2)}px, 0)`;
    }
    ticking = moving;
    if (moving) requestAnimationFrame(frame);
  }
  function onScroll() {
    measure();
    if (!ticking) { ticking = true; requestAnimationFrame(frame); }
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll, { passive: true });
  onScroll();

  reduce.addEventListener('change', () => {
    if (reduce.matches) planes.forEach(p => { p.el.style.transform = ''; });
  });
})();
