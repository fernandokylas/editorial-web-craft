/**
 * Choreographed section entrance with GSAP.
 *
 * Requires gsap (and ScrollTrigger for below-fold sections):
 *   <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
 *   <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
 *
 * Markup contract — mark what should animate, in reading order:
 *   <section data-entrance>
 *     <aside data-reveal="rail">…</aside>
 *     <div>
 *       <h2 data-reveal="title">…</h2>
 *       <p data-reveal>…</p>   <li data-reveal>…</li>   <!-- copy: staggered -->
 *     </div>
 *   </section>
 *
 * CSS contract — hide only when a script can run, so no-JS users see content:
 *   @media (scripting: enabled) { [data-reveal] { visibility: hidden; } }
 *   and, in case GSAP itself fails to load, entranceAll() reveals everything.
 *
 * Usage:
 *   entranceAll();                         // every [data-entrance]; first plays on load, rest on scroll
 *   entrance(document.querySelector('.hero'), { scroll: false }).play();
 */

const DEFAULTS = {
  ease: 'power4.out',
  duration: 1.1,
  stagger: 0.05,        // 30–70ms is the band that reads as one continuous flow
  railX: -15,
  titleY: 25,
  copyY: 15,
  scroll: true,         // play when the section enters the viewport
  scrollStart: 'top 80%',
};

function entrance(section, opts = {}) {
  const o = { ...DEFAULTS, ...opts };
  const rail = section.querySelectorAll('[data-reveal="rail"]');
  const title = section.querySelectorAll('[data-reveal="title"]');
  const copy = section.querySelectorAll('[data-reveal=""], [data-reveal="copy"]');

  const tl = gsap.timeline({
    paused: true,
    defaults: { ease: o.ease, duration: o.duration },
    // Leave the DOM clean afterwards: no inline transforms fighting later CSS :hover
    onComplete: () => gsap.set([...rail, ...title, ...copy], { clearProps: 'transform' }),
  });

  if (rail.length)  tl.from(rail,  { autoAlpha: 0, x: o.railX, duration: o.duration + 0.2 }, 0);
  if (title.length) tl.from(title, { autoAlpha: 0, y: o.titleY }, 0.15);
  if (copy.length)  tl.from(copy,  { autoAlpha: 0, y: o.copyY, stagger: o.stagger }, 0.3);

  if (o.scroll && window.ScrollTrigger) {
    ScrollTrigger.create({ trigger: section, start: o.scrollStart, once: true, onEnter: () => tl.play() });
  } else if (o.scroll && 'IntersectionObserver' in window) {
    // ScrollTrigger missing: don't strand below-fold sections in their paused state
    const io = new IntersectionObserver((es) => es.forEach(e => { if (e.isIntersecting) { tl.play(); io.disconnect(); } }),
                                        { rootMargin: '0px 0px -20% 0px' });
    io.observe(section);
  }
  return tl;
}

function entranceAll(opts = {}) {
  const sections = [...document.querySelectorAll('[data-entrance]')];
  if (!window.gsap) {                      // CDN blocked or failed: content must still show
    document.querySelectorAll('[data-reveal]').forEach(el => { el.style.visibility = 'visible'; });
    return null;
  }
  if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  const mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    const tls = sections.map((s, i) => entrance(s, { ...opts, scroll: i > 0 }));
    if (tls[0]) tls[0].play();          // above-the-fold section plays immediately
    return () => tls.forEach(t => t.kill());
  });
  mm.add('(prefers-reduced-motion: reduce)', () => {
    // No motion: just make everything visible.
    gsap.set('[data-reveal]', { autoAlpha: 1 });
  });
  return mm;
}

if (typeof module !== 'undefined') module.exports = { entrance, entranceAll };
if (typeof window !== 'undefined') Object.assign(window, { entrance, entranceAll });
