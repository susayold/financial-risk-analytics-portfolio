document.documentElement.classList.add('js');

const slides = [...document.querySelectorAll('.slide')];
const railItems = [...document.querySelectorAll('.rail-item')];
const railProgress = document.querySelector('.rail-line i');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (window.lucide) window.lucide.createIcons();

function activate(id) {
  railItems.forEach(item => item.classList.toggle('is-active', item.dataset.slide === id));
  document.body.classList.toggle('hero-active', id === 'hero');
  const index = Math.max(0, slides.findIndex(slide => slide.id === id));
  if (railProgress) railProgress.style.height = `${slides.length > 1 ? (index / (slides.length - 1)) * 100 : 0}%`;
}

const observer = new IntersectionObserver(entries => {
  const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (visible) activate(visible.target.id);
}, {threshold: [.35, .55, .75]});
slides.forEach(slide => observer.observe(slide));

const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add('is-visible');
    revealObserver.unobserve(entry.target);
  });
}, {threshold: .12, rootMargin: '0px 0px -8% 0px'});
document.querySelectorAll('.reveal, .reveal-group').forEach(element => revealObserver.observe(element));

function goTo(index) {
  const safeIndex = Math.max(0, Math.min(slides.length - 1, index));
  slides[safeIndex]?.scrollIntoView({behavior: reducedMotion ? 'auto' : 'smooth', block: 'start'});
}

document.addEventListener('keydown', event => {
  const tag = event.target?.tagName?.toLowerCase();
  if (['input', 'textarea', 'select'].includes(tag) || event.target?.isContentEditable) return;
  const activeId = railItems.find(item => item.classList.contains('is-active'))?.dataset.slide;
  const activeIndex = Math.max(0, slides.findIndex(slide => slide.id === activeId));
  const index = activeIndex;
  if (['ArrowDown', 'PageDown', ' ', 'ArrowRight'].includes(event.key)) { event.preventDefault(); goTo(index + 1); }
  if (['ArrowUp', 'PageUp', 'ArrowLeft'].includes(event.key)) { event.preventDefault(); goTo(index - 1); }
  if (event.key === 'Home') { event.preventDefault(); goTo(0); }
  if (event.key === 'End') { event.preventDefault(); goTo(slides.length - 1); }
});

railItems.forEach(item => item.addEventListener('click', () => activate(item.dataset.slide)));
activate('hero');
