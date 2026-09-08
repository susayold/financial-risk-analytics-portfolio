import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const root = process.cwd();
const config = JSON.parse(fs.readFileSync(path.join(root, 'config', 'routes.json'), 'utf8'));
const baseUrl = process.env.BLOCK_F_BASE_URL || 'http://127.0.0.1:8000';
const outDir = path.join(root, 'outputs', 'block-f');
const shotDir = path.join(outDir, 'screenshots');
fs.mkdirSync(path.join(shotDir, 'desktop'), { recursive: true });
fs.mkdirSync(path.join(shotDir, 'mobile'), { recursive: true });

const failures = [];
const diagnostics = [];
const browser = await chromium.launch({ headless: true });

const viewports = [
  { name: 'desktop', width: 1440, height: 1100 },
  { name: 'mobile', width: 390, height: 844 },
];

for (const viewport of viewports) {
  const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
  for (const pageDef of config.primary_pages) {
    const page = await context.newPage();
    const errors = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(`console: ${msg.text()}`); });
    page.on('pageerror', err => errors.push(`pageerror: ${err.message}`));

    const route = pageDef.route === '/' ? '/' : pageDef.route;
    const url = new URL(route.replace(/^\//, ''), `${baseUrl}/`).href;
    const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    if (!response || !response.ok()) failures.push(`${viewport.name} ${pageDef.route}: HTTP failure`);

    const audit = await page.evaluate(() => {
      const viewportMeta = document.querySelector('meta[name="viewport"]');
      const skip = document.querySelector('.skip-link, a[href^="#main"]');
      const noindex = document.querySelector('meta[name="robots"][content*="noindex" i]');
      const body = document.body;
      const html = document.documentElement;
      const maxWidth = Math.max(body.scrollWidth, html.scrollWidth);
      const overflow = maxWidth > window.innerWidth + 2;
      const active = document.querySelector('nav a[aria-current="page"], nav a.active');
      const offenders = overflow ? [...document.querySelectorAll('body *')]
        .map(el => {
          const r = el.getBoundingClientRect();
          return {
            tag: el.tagName.toLowerCase(),
            id: el.id || '',
            className: typeof el.className === 'string' ? el.className : '',
            left: Math.round(r.left),
            right: Math.round(r.right),
            width: Math.round(r.width),
            scrollWidth: el.scrollWidth || 0,
          };
        })
        .filter(x => x.right > window.innerWidth + 2 || x.left < -2 || x.scrollWidth > window.innerWidth + 2)
        .sort((a, b) => Math.max(b.right - window.innerWidth, b.scrollWidth - window.innerWidth) - Math.max(a.right - window.innerWidth, a.scrollWidth - window.innerWidth))
        .slice(0, 12) : [];
      return {
        title: document.title,
        viewport: Boolean(viewportMeta),
        skip: Boolean(skip),
        noindex: Boolean(noindex),
        overflow,
        pageScrollWidth: maxWidth,
        innerWidth: window.innerWidth,
        offenders,
        activeNav: Boolean(active),
      };
    });

    diagnostics.push({ viewport: viewport.name, route: pageDef.route, audit });
    if (!audit.title) failures.push(`${viewport.name} ${pageDef.route}: missing title`);
    if (!audit.viewport) failures.push(`${viewport.name} ${pageDef.route}: missing viewport meta`);
    if (!audit.skip) failures.push(`${viewport.name} ${pageDef.route}: missing skip link`);
    if (audit.noindex) failures.push(`${viewport.name} ${pageDef.route}: unfinished noindex present`);
    if (audit.overflow) failures.push(`${viewport.name} ${pageDef.route}: horizontal overflow (${audit.pageScrollWidth}px > ${audit.innerWidth}px); offenders=${JSON.stringify(audit.offenders.slice(0, 4))}`);
    if (!audit.activeNav) failures.push(`${viewport.name} ${pageDef.route}: active navigation state missing`);
    for (const error of errors) failures.push(`${viewport.name} ${pageDef.route}: ${error}`);

    const slug = pageDef.route === '/' ? 'overview' : pageDef.route.replaceAll('/', '');
    await page.screenshot({ path: path.join(shotDir, viewport.name, `${slug}.png`), fullPage: true });
    await page.close();
  }
  await context.close();
}

await browser.close();

const result = {
  route_tests: failures.some(x => x.includes('HTTP failure')) ? 'FAIL' : 'PASS',
  responsive_qa: failures.some(x => x.includes('horizontal overflow')) ? 'FAIL' : 'PASS',
  accessibility_qa: failures.some(x => x.includes('viewport meta') || x.includes('skip link') || x.includes('active navigation')) ? 'FAIL' : 'PASS',
  visual_qa: failures.some(x => x.includes('console:') || x.includes('pageerror:') || x.includes('noindex')) ? 'FAIL' : 'PASS',
  screenshots: 14,
  failures,
  diagnostics,
};
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'BLOCK_F_BROWSER_QA.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exit(1);
