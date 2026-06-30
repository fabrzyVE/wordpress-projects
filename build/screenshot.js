// Render a standalone page HTML and capture full-page + per-section screenshots
// for pixel-perfect QC against the Figma design PNGs.
// Usage: node screenshot.js <slug> [width]
const { chromium } = require(process.env.PW_PATH || 'playwright');
const path = require('path');
const fs = require('fs');

const SECTION_NAMES = ['hero','intro','levels','env','team','insurance','expect','impact','faq','final','nearby'];
const ROOT = path.resolve(__dirname, '..');

(async () => {
  const slug = process.argv[2];
  const width = parseInt(process.argv[3] || '1280', 10);
  if (!slug) { console.error('need slug'); process.exit(1); }
  const htmlPath = path.join(ROOT, 'pages', `${slug}.html`);
  const outDir = path.join(ROOT, 'qc', slug);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height: 1000 }, deviceScaleFactor: 2 });
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(500);

  await page.screenshot({ path: path.join(outDir, '00-full.png'), fullPage: true });

  const sections = await page.$$('.av-loc > section');
  for (let i = 0; i < sections.length; i++) {
    const name = SECTION_NAMES[i] || `s${i}`;
    const nn = String(i + 1).padStart(2, '0');
    try {
      await sections[i].scrollIntoViewIfNeeded();
      await page.waitForTimeout(120);
      await sections[i].screenshot({ path: path.join(outDir, `${nn}-${name}.png`) });
    } catch (err) {
      console.error(`section ${name} failed: ${err.message}`);
    }
  }
  await browser.close();
  console.log(`shot ${slug}: ${sections.length} sections -> qc/${slug}/`);
})();
