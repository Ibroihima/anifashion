// ── SCROLL REVEAL ──
document.addEventListener('DOMContentLoaded', () => {
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((e, i) => {
        if (e.isIntersecting) {
          setTimeout(() => e.target.classList.add('visible'), i * 80);
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    reveals.forEach(r => observer.observe(r));
  }

  // ── AUTO-HIDE FLASH MESSAGES ──
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(f => {
      f.style.transition = 'opacity 0.5s';
      f.style.opacity = '0';
      setTimeout(() => f.remove(), 500);
    });
  }, 4000);
});
