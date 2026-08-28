document.documentElement.classList.add('js');
const ids = ['intro','journey','architecture','target','temporal','features','bridge','risks','economics','evidence'];
const links = [...document.querySelectorAll('.navlinks a')];
const railItems = [...document.querySelectorAll('.rail-item')];
const railProgress = document.querySelector('.rail-progress');

function setActiveSection(id) {
  railItems.forEach(item => item.classList.toggle('is-active', item.dataset.section === id));
  document.body.classList.toggle('rail-dark', id === 'intro' || id === 'journey');
  links.forEach(link => link.removeAttribute('aria-current'));
  const link = document.querySelector(`.navlinks a[href="#${id}"]`);
  if (link) link.setAttribute('aria-current', 'location');
}

const sectionObserver = new IntersectionObserver(entries => {
  const entry = entries.filter(item => item.isIntersecting).sort((a,b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (entry) setActiveSection(entry.target.id);
}, {rootMargin:'-25% 0px -60% 0px', threshold:[.12,.25]});
ids.forEach(id => { const element = document.getElementById(id); if (element) sectionObserver.observe(element); });

const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add('is-visible');
    revealObserver.unobserve(entry.target);
  });
}, {threshold:.16, rootMargin:'0px 0px -8% 0px'});
document.querySelectorAll('.reveal, .reveal-group').forEach(element => revealObserver.observe(element));

function updateRailProgress() {
  if (!railProgress) return;
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const ratio = scrollable > 0 ? scrollTop / scrollable : 0;
  railProgress.style.height = `${Math.min(100, Math.max(0, ratio * 100))}%`;
}
window.addEventListener('scroll', updateRailProgress, {passive:true});
updateRailProgress();
setActiveSection('intro');


