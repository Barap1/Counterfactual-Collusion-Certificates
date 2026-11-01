async (page) => {
  const expected='bdb66f194e5ba4abf1e6b18f20ee4ec6ff44b954ad0adbb19f3685a31cddb687';
  const out='/Users/aarav/Documents/Projects/ApartSprint/ops/reports/final_audit/explorer_release/screenshots/';
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const checks=[];
  await page.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:8766/')?r.continue():r.abort());
  for(const width of [1440,390])for(const theme of ['light','dark']){
    const height=width===390?844:1000;
    await page.setViewportSize({width,height});
    await page.emulateMedia({colorScheme:theme});
    await page.goto('http://127.0.0.1:8766/explorer/index.html?final-provenance='+width+'-'+theme+'#/about');
    await page.waitForFunction(expected=>window.CCC_DATA?.manifest?.manifest_sha256===expected&&document.querySelector('main')?.textContent.includes(expected),expected);
    await page.locator('main p').filter({hasText:'The pack was generated'}).evaluate(el=>{
      const header=document.querySelector('.top');
      const offset=getComputedStyle(header).position==='sticky'?header.getBoundingClientRect().height+16:20;
      window.scrollTo(0,window.scrollY+el.getBoundingClientRect().top-offset);
    });
    const state=await page.evaluate(expected=>{
      const stamp=[...document.querySelectorAll('main .hash')].find(x=>x.textContent===expected);
      const rect=stamp.getBoundingClientRect();
      return {manifest_sha256:window.CCC_DATA.manifest.manifest_sha256,generation_base_commit:window.CCC_DATA.manifest.generator_commit_HEAD,background:getComputedStyle(document.body).backgroundColor,viewport:{width:innerWidth,height:innerHeight},clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,stamp_rect:{top:rect.top,bottom:rect.bottom,left:rect.left,right:rect.right},stamp_fully_visible:rect.top>=0&&rect.bottom<=innerHeight&&rect.left>=0&&rect.right<=innerWidth};
    },expected);
    if(!state.stamp_fully_visible || state.scrollWidth>state.clientWidth+1)throw new Error('Provenance stamp clipped at '+width+' '+theme);
    const file='final_about_provenance_'+width+'_'+theme+'.png';
    await page.screenshot({path:out+file,fullPage:false});
    checks.push({view:'About / Provenance',width,height,theme,file,state});
  }
  return {status:'PASS',checks,errors,scope:'Four fresh provenance views after source-pack sensitivity-note correction; Study view remains byte-identical per post-cold-review-equivalence.json'};
}
