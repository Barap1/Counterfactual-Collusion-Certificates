async (page) => {
  const errors=[];
  page.on('pageerror', e=>errors.push(String(e)));
  const checks={mode:'loopback static server, no external network', cases:[], twins:[], tour:[], links:[], errors};
  await page.route('**/*', route=>route.request().url().startsWith('http://127.0.0.1:8766/') ? route.continue() : route.abort());
  await page.setViewportSize({width:1440,height:1000});
  await page.emulateMedia({colorScheme:'light'});
  await page.goto('http://127.0.0.1:8766/explorer/index.html');
  await page.waitForSelector('.casebtn');
  await page.getByRole('link',{name:'Start here',exact:true}).click();
  for(let i=0;i<4;i++){
    await page.getByRole('group',{name:'Tour steps'}).getByRole('button').nth(i).click();
    checks.tour.push({step:i+1,heading:await page.locator('main h3').first().textContent()});
  }
  for(let i=0;i<3;i++)await page.getByRole('button',{name:'Back',exact:true}).click();
  for(let i=0;i<3;i++)await page.getByRole('button',{name:'Next',exact:true}).click();
  const ids=await page.locator('.casebtn').evaluateAll(xs=>xs.map(x=>x.dataset.id));
  for(const id of ids){
    await page.locator('.casebtn[data-id="'+id+'"]').click();
    await page.waitForFunction(id=>document.querySelector('#top-h')?.textContent.startsWith(id) || (id.startsWith('GateA') && document.querySelector('#top-h')?.textContent.startsWith(id.slice(6))),id);
    const result=await page.evaluate(id=>{
      const C=window.CCC_DATA.cases[id], main=document.querySelector('main');
      if(!C)throw new Error('Missing loaded case '+id);
      const nodes=Array.from(main.querySelectorAll('details > summary'));
      nodes.forEach(s=>{const d=s.parentElement, old=d.open;s.click();if(d.open===old)throw new Error('Details toggle failed');s.click();});
      const links=Array.from(main.querySelectorAll('.sect-nav a'));
      links.forEach(a=>{a.click();if(!document.activeElement.id.startsWith('s-'))throw new Error('Section focus failed');});
      const sel=main.querySelector('#tsel');let n=0;
      if(sel){const d=sel.closest('details');if(d)d.open=true;for(const op of sel.options){sel.value=op.value;sel.dispatchEvent(new Event('change',{bubbles:true}));if(!d.querySelector('.log .rec'))throw new Error('Empty selected transcript');n++;}if(d)d.open=false;}
      const titles=Array.from(main.querySelectorAll('[title]')).map(x=>x.title);
      return {id,status:C.certificate.status,heading:document.querySelector('#top-h').textContent,section_links:links.length,details_toggled:nodes.length,transcripts_selected:n,tooltips:titles.length};
    },id);
    checks.cases.push(result);
  }
  await page.getByRole('link',{name:'Twin worlds',exact:true}).click();
  for(const kind of ['P1','P2','P3','P4','P5','P6']){
    await page.getByRole('button',{name:kind,exact:true}).click();
    for(let i=0;i<6;i++){
      await page.getByRole('button',{name:'I'+i,exact:true}).click();
      const shown=await page.locator('#tw-range').inputValue();
      if(shown!==String(i))throw new Error('Evidence button failed');
      checks.twins.push({kind,set:'I'+i,heading:await page.locator('main h3').first().textContent()});
    }
  }
  await page.locator('#tw-range').focus();
  await page.keyboard.press('Home');
  await page.waitForFunction(()=>document.querySelector('#tw-range').value==='0');
  await page.keyboard.press('ArrowRight');
  await page.waitForFunction(()=>document.querySelector('#tw-range').value==='1');
  checks.slider_keyboard='Home→I0, ArrowRight→I1';
  await page.goto('http://127.0.0.1:8766/explorer/index.html?skip-test#/case/H02_B1');
  await page.waitForSelector('#top-h');
  const beforeSkip=page.url();
  await page.getByRole('link',{name:'Skip to content',exact:true}).focus();
  await page.keyboard.press('Enter');
  if(page.url()!==beforeSkip || await page.evaluate(()=>document.activeElement.id)!=='main')throw new Error('Skip link changed route or failed focus');
  checks.skip_link='Keyboard Enter preserves case route and focuses main';
  await page.locator('#s-chg td[title]').first().hover();
  checks.native_tooltip=await page.locator('#s-chg td[title]').first().getAttribute('title');
  for(const name of ['Study','Concepts & sources']){
    await page.getByRole('link',{name,exact:true}).click();
    await page.waitForFunction(name=>document.querySelector('main h2')?.textContent.includes(name==='Study'?'Study:':'Concepts and sources'),name);
    const ls=await page.locator('main a').evaluateAll(xs=>xs.filter(a=>!a.getAttribute('href').startsWith('#')).map(a=>({text:a.textContent,href:a.href})));
    for(const a of ls){if(!a.href.startsWith('http://127.0.0.1:8766/'))continue;const response=await page.request.get(a.href);checks.links.push({...a,status:response.status()});if(!response.ok())throw new Error('Broken link '+a.href);}
  }
  return checks;
}
