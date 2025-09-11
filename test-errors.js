const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  // Capture console messages
  page.on('console', msg => {
    console.log(`[${msg.type()}]`, msg.text());
  });
  
  page.on('pageerror', error => {
    console.log('[ERROR]', error.message);
  });
  
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(2000);
  
  const content = await page.evaluate(() => document.getElementById('root')?.innerHTML || 'No content');
  console.log('\nRoot content:', content.substring(0, 200));
  
  await browser.close();
})();