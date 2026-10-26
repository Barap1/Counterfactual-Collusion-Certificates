/* HTTP(S) deployment smoke test; development-only Playwright dependency. */
const {chromium}=require(process.env.CCC_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
const base=process.argv[2],output=process.argv[3];
if(!/^https?:/.test(base))throw new Error('HTTP(S) deployment URL required');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:960},reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[],responses=[];
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('response',r=>{if(r.status()>=400)responses.push({url:r.url(),status:r.status()});});
 const report={base,checked:new Date().toISOString(),errors,responses};
 try{
  await page.goto(base+'#/study');await page.locator('main h1').waitFor();
  assert.ok((await page.url()).includes('/demo/explorer/#/study'),'root preserves existing hash deep links');
  assert.equal(await page.locator('.pair-dot').count(),8);
  await page.goto(base+'#/start');await page.locator('#opening-title').waitFor();
  await page.getByRole('button',{name:'02 Add the cost probe'}).click();assert.deepEqual(await page.locator('.world-result .reward').allTextContents(),['29','14']);
  await fs.mkdir(output,{recursive:true});await page.locator('#counterexample').screenshot({path:path.join(output,'counterexample-probe.png'),animations:'disabled'});
  await page.getByRole('link',{name:'CCC Evidence Explorer — Start',exact:true}).click();
  assert.equal(await page.evaluate(()=>window.scrollY),0,'same-route brand link returns to the opening');
  await fs.mkdir(output,{recursive:true});await page.screenshot({path:path.join(output,'desktop.png'),animations:'disabled'});
  await page.goto(base+'#/about');await page.locator('main h1').waitFor();
  const downloads=await page.locator('main a').evaluateAll(links=>links.map(a=>a.href).filter(h=>h.includes('/demo/data/')||h.endsWith('/fonts/OFL.txt')));
  report.downloads=[];
  for(const url of downloads){const r=await context.request.get(url);assert.equal(r.status(),200,url);report.downloads.push({url,status:r.status()});}
  await page.goto(base+'#/case/H02_B1');await page.locator('#s-raw').waitFor();assert.equal(await page.locator('#case-select option').count(),21);
  const compact=await page.getByRole('link',{name:'Download compact case JSON'}).getAttribute('href');const raw=await context.request.get(new URL(compact,page.url()).href);assert.equal(raw.status(),200);assert.equal((await raw.json()).id,'H02_B1');
  await page.goto(base+'#/twins/P3/5');await page.locator('#tw-range').waitFor();assert.equal(await page.locator('#tw-range').inputValue(),'5');assert.match(await page.locator('main').innerText(),/Authorization record/);
  await page.setViewportSize({width:390,height:844});await page.goto(base+'#/study');await page.locator('.pair-dot').first().waitFor();
  await page.getByRole('button',{name:'Use dark theme'}).click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(output,'mobile-study-dark.png'),animations:'disabled'});
  await page.locator('.study-figure').screenshot({path:path.join(output,'mobile-study-figure.png'),animations:'disabled'});
  assert.equal(errors.length,0);assert.equal(responses.length,0);report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=e.stack;process.exitCode=1;}
 finally{await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log(JSON.stringify(report));}
})();
