/* Development-only browser QA. Requires Playwright; no runtime dependency. HTTP only. */
const {chromium} = require(process.env.CCC_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const base = process.argv[2] || 'http://127.0.0.1:8765/explorer/';
const output = path.resolve(process.argv[3] || 'ops/reports/explorer_redesign/browser');
if (!/^https?:/.test(base)) throw new Error('This QA runner accepts HTTP(S) previews only.');
(async () => {
 await fs.mkdir(output,{recursive:true});
 const browser = await chromium.launch({headless:true});
 const report = {base,started:new Date().toISOString(),checks:[],errors:[],badResponses:[],externalRequests:[],screenshots:[]};
 const routes = ['#/start','#/study','#/twins/P2/2','#/twins/P2/4','#/case/H02_B1','#/about'];
 try {
  for (const width of [1440,768,390,320]) {
   const context = await browser.newContext({viewport:{width,height:960},colorScheme:'dark'});
   const page = await context.newPage();
   page.on('pageerror',e=>report.errors.push(String(e)));
   page.on('response',r=>{if(r.status()>=400) report.badResponses.push({url:r.url(),status:r.status()});});
   await context.route('**/*',route=>{if(new URL(route.request().url()).origin!==new URL(base).origin){report.externalRequests.push(route.request().url());return route.abort();}return route.continue();});
   await page.goto(base,{waitUntil:'load'});
   await page.evaluate(()=>document.fonts.ready);
   assert.equal(await page.locator('html').getAttribute('data-theme'),'light','light default even with dark system preference');
   for (const theme of ['light','dark']) {
    if (theme==='dark') await page.getByRole('button',{name:'Use dark theme'}).click();
    for (const route of routes) {
     await page.goto(base+route,{waitUntil:'load'});
     await page.locator('main h1').waitFor();
     if(route.includes('/case/')) await page.locator('#s-raw').waitFor();
     await page.evaluate(()=>document.fonts.ready);
     const layout = await page.evaluate(()=>({viewport:innerWidth,doc:document.documentElement.scrollWidth,headings:document.querySelectorAll('main h1').length,theme:document.documentElement.dataset.theme,fonts:document.fonts.check('19px "Old Standard TT"'),sideHidden:document.querySelector('.side').hidden}));
     assert.ok(layout.doc<=width+1,`${width} ${theme} ${route} overflow: ${layout.doc}`);
     assert.equal(layout.headings,1); assert.equal(layout.theme,theme); assert.equal(layout.fonts,true);
     assert.equal(layout.sideHidden,!route.includes('/case/'));
     const name = route.replace('#/','').replaceAll('/','_')+'_'+width+'_'+theme+'.png';
     await page.screenshot({path:path.join(output,name),fullPage:true,animations:'disabled'});
     await page.screenshot({path:path.join(output,name.replace('.png','_viewport.png')),fullPage:false,animations:'disabled'});
     report.screenshots.push(name); report.checks.push({width,theme,route,...layout});
    }
   }
   await page.reload();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark','theme persists');
   await context.close();
  }
  const context = await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});
  const page = await context.newPage();
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.goto(base+'#/start');
  assert.deepEqual(await page.locator('.world-result .reward').allTextContents(),['14','14']);
  await page.getByRole('button',{name:'02 Add the cost probe'}).click();
  assert.deepEqual(await page.locator('.world-result .reward').allTextContents(),['29','14']);
  assert.match(await page.locator('.probe-caption').innerText(),/Lowering outsider costs by 10/);
  const motion = await page.locator('.allocation-token').first().evaluate(e=>({transition:getComputedStyle(e).transitionDuration,animation:getComputedStyle(e).animationName,scroll:getComputedStyle(document.documentElement).scrollBehavior}));
  assert.equal(motion.transition,'0s');assert.equal(motion.animation,'none');assert.equal(motion.scroll,'auto');
  await page.screenshot({path:path.join(output,'probe_390_reduced-motion.png'),fullPage:true,animations:'disabled'});report.screenshots.push('probe_390_reduced-motion.png');
  await page.getByRole('button',{name:'01 Shared evidence'}).click();assert.deepEqual(await page.locator('.world-result .reward').allTextContents(),['14','14']);
  await page.goto(base+'#/study');assert.equal(await page.locator('.pair-dot').count(),8);
  await page.getByText('Inspect all eight differences and the underlying cases',{exact:true}).click();assert.equal(await page.locator('main tbody tr').first().isVisible(),true);
  await page.goto(base+'#/twins/P2/2');
  await page.getByRole('button',{name:'I4',exact:true}).press('Enter');
  assert.ok((await page.url()).endsWith('#/twins/P2/4')); assert.equal(await page.evaluate(()=>document.activeElement.dataset.set),'4');
  for(const pair of ['P1','P2','P3','P4','P5','P6']) for(const level of [0,1,2,3,4,5]) {
   await page.goto(base+`#/twins/${pair}/${level}`); assert.equal(await page.locator('#tw-range').inputValue(),String(level));
   assert.equal(await page.locator(`[data-pair][aria-pressed="true"]`).innerText(),pair);
   assert.ok(await page.locator('main').innerText());
  }
  const ids = await page.evaluate(()=>window.CCC_DATA.index.cases.map(c=>c.id));
  for(const id of ids){await page.goto(base+'#/case/'+id);await page.locator('#s-raw').waitFor();assert.equal(await page.locator('#case-select').inputValue(),id);assert.equal(await page.locator('main h1').count(),1);}
  await page.getByLabel('Inspect a case',{exact:true}).selectOption('H02_B1');await page.locator('#s-raw').waitFor();assert.ok((await page.url()).endsWith('#/case/H02_B1'));
  // Exercise disclosures, keyboard focus, internal section links, and invalid-route recovery.
  await page.getByRole('link',{name:'Evidence scope',exact:true}).click();assert.equal(await page.locator('#s-ladder').evaluate(e=>e.closest('details').open),true);
  await page.getByRole('link',{name:'Skip to content',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'main');
  await page.goto(base+'#/case/UNKNOWN');assert.match(await page.locator('[role=status]').first().innerText(),/not in the frozen pack/);
  await page.goto(base+'#/start');
  await page.getByRole('link',{name:'Explore the counterexample',exact:true}).click();assert.equal(await page.evaluate(()=>document.activeElement.id),'counterexample');
  // Audit actual text colors against the background used in each theme.
  report.contrast=[];
  for(const theme of ['light','dark']) {
   if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme-toggle').click();
   const result=await page.evaluate(()=>{
    const rgb=s=>(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);
    const lum=c=>c.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
    const style=getComputedStyle(document.documentElement),bg=lum(rgb(getComputedStyle(document.body).backgroundColor));
    return ['--ink','--muted','--accent','--harm','--unc'].map(key=>{const el=document.createElement('span');el.style.color=style.getPropertyValue(key);document.body.appendChild(el);const l=lum(rgb(getComputedStyle(el).color));el.remove();return {key,ratio:(Math.max(bg,l)+.05)/(Math.min(bg,l)+.05)};});
   });
   result.forEach(r=>assert.ok(r.ratio>=4.5,theme+' '+r.key+' contrast '+r.ratio));report.contrast.push({theme,result});
  }
  report.checks.push({functional:'probe 14/14 → 29/14 and reset; persisted theme; reduced motion; 36 twin states; 21 cases; keyboard and disclosure navigation; invalid case; section anchor; no overflow'});
  await context.close();
  assert.equal(report.errors.length,0);assert.equal(report.badResponses.length,0);assert.equal(report.externalRequests.length,0);
  report.status='PASS';
 } catch(error) {report.status='FAIL';report.failure=error.stack;process.exitCode=1;}
 finally {report.finished=new Date().toISOString();await fs.writeFile(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log(JSON.stringify({status:report.status,checks:report.checks.length,screenshots:report.screenshots.length,failure:report.failure,errors:report.errors,badResponses:report.badResponses,externalRequests:report.externalRequests}));}
})();
