/**
 * main.js  –  Shared utilities across all pages
 * Handles: navbar scroll effect, star generation, mobile menu, tab init
 */

// ─── Generate Stars ───────────────────────────────────────────
function generateStars() {
  const container = document.getElementById('stars');
  if (!container) return;

  for (let i = 0; i < 160; i++) {
    const star = document.createElement('div');
    const size = Math.random() * 2.2 + 0.5;
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    const opacity = Math.random() * 0.7 + 0.1;
    const duration = Math.random() * 4 + 2;
    const delay = Math.random() * 5;

    Object.assign(star.style, {
      position: 'absolute',
      width:  `${size}px`,
      height: `${size}px`,
      borderRadius: '50%',
      background: `rgba(255,255,255,${opacity})`,
      left:  `${x}%`,
      top:   `${y}%`,
      animation: `starTwinkle ${duration}s ease-in-out ${delay}s infinite`,
      boxShadow: size > 1.8
        ? `0 0 ${size * 2}px rgba(255,255,255,0.6)`
        : 'none'
    });

    container.appendChild(star);
  }

  // Inject keyframe if not present
  if (!document.getElementById('star-keyframe')) {
    const style = document.createElement('style');
    style.id = 'star-keyframe';
    style.textContent = `
      @keyframes starTwinkle {
        0%, 100% { opacity: var(--op, 0.4); transform: scale(1); }
        50%       { opacity: calc(var(--op, 0.4) * 0.3); transform: scale(0.7); }
      }`;
    document.head.appendChild(style);
  }
}

// ─── Navbar: scroll glass effect ─────────────────────────────
function initNavbar() {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 30);
  }, { passive: true });
}

// ─── Mobile nav toggle ────────────────────────────────────────
function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const links  = document.querySelector('.nav-links');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    links.classList.toggle('open');
    toggle.textContent = links.classList.contains('open') ? '✕' : '☰';
  });

  // Close on link click
  links.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.textContent = '☰';
    });
  });
}

// ─── Animate numbers (stat counters) ─────────────────────────
function animateNumber(el, target, suffix = '') {
  const isFloat = target % 1 !== 0;
  const duration = 1200;
  const start = performance.now();

  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = isFloat
      ? (eased * target).toFixed(1)
      : Math.floor(eased * target);
    el.textContent = current + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function initStatCounters() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const raw = el.textContent.trim();
        const num = parseFloat(raw.replace('%', '').replace(',', ''));
        if (!isNaN(num)) {
          const suffix = raw.includes('%') ? '%' : '';
          animateNumber(el, num, suffix);
        }
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.stat-value, .mc-val').forEach(el => {
    observer.observe(el);
  });
}

// ─── Card hover tilt effect ───────────────────────────────────
function initCardTilt() {
  const cards = document.querySelectorAll('.feature-card, .stat-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width  - 0.5;
      const y = (e.clientY - rect.top)  / rect.height - 0.5;
      card.style.transform =
        `translateY(-6px) rotateX(${y * -6}deg) rotateY(${x * 6}deg)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
}

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  generateStars();
  initNavbar();
  initMobileNav();
  initStatCounters();
  initCardTilt();
});
