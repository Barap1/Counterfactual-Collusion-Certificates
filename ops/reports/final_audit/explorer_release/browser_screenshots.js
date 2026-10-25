async (page) => {
  const out='/Users/aarav/Documents/Projects/ApartSprint/ops/reports/final_audit/explorer_release/screenshots/';
  const base='http://127.0.0.1:8766/explorer/index.html';
  const checks=[];
  for(const width of [1440,390])for(const theme of ['light','dark']){
    await page.setViewportSize({width,height:width===390?844:1000});
    await page.emulateMedia({colorScheme:theme});
    for(const view of ['start','study','twins/P2/4','twins/P3/5','case/H02_B1','case/GateA_A1','about']){
      await page.goto(base+'?qa='+encodeURIComponent(width+'-'+theme+'-'+view)+'#/'+view);
      if(view.startsWith('case/'))await page.waitForSelector('#top-h');
      else if(view.startsWith('twins/'))await page.waitForFunction(view=>document.querySelector('#tw-range')?.value===view.slice(-1)&&document.querySelector('main h3')?.textContent.startsWith(view.split('/')[1]),view);
      else await page.waitForFunction(view=>document.querySelector('main h2')?.textContent.startsWith({start:'Start here',study:'Study:',about:'Concepts and sources'}[view]),view);
      const state=await page.evaluate(()=>({viewport:innerWidth,client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,theme:getComputedStyle(document.body).backgroundColor,head:document.querySelector('main h2').textContent,menu_open:document.querySelector('#case-menu').open,visible_nav:[...document.querySelectorAll('.views a')].map(x=>({text:x.textContent,rect:{x:x.getBoundingClientRect().x,y:x.getBoundingClientRect().y,width:x.getBoundingClientRect().width,height:x.getBoundingClientRect().height}}))}));
      const file=view.replaceAll('/','_')+'_'+width+'_'+theme+'.png';
      await page.screenshot({path:out+file,fullPage:false});
      checks.push({view,width,theme,file,state});
      if(state.scroll>state.client+1)throw new Error('Horizontal page overflow '+view+' '+width);
      if(view.startsWith('twins/')){
        await page.locator('main .grid2').first().scrollIntoViewIfNeeded();
        const file2=view.replaceAll('/','_')+'_evidence_'+width+'_'+theme+'.png';
        await page.screenshot({path:out+file2,fullPage:false});
        checks.push({view:view+'/evidence',width,theme,file:file2});
      }
      if(width===390 && view==='case/H02_B1'){
        if(!await page.locator('#case-menu').evaluate(x=>x.open))await page.locator('#case-menu > summary').click();
        await page.locator('.casebtn[data-id="H01_B2"]').click();
        await page.waitForFunction(()=>document.querySelector('#top-h')?.textContent.startsWith('H01_B2'));
        if(await page.locator('#case-menu').evaluate(x=>x.open))throw new Error('Mobile selector did not close');
      }
    }
  }
  return checks;
}
