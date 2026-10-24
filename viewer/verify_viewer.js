// Offline structural and JavaScript smoke checks. No browser or network.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const payload=html.match(/<script id="evidence" type="application\/json">([\s\S]*?)<\/script>/)[1];
const evidence=JSON.parse(payload);
const script=html.match(/<script>\n([\s\S]*?)<\/script>/)[1];
const nodes={};
for(const id of ['tier','case','selection','content','evidence']){
 let content=''; nodes[id]={value:id==='tier'?'real':'',textContent:id==='evidence'?payload:'',listeners:{},addEventListener(type,fn){this.listeners[type]=fn},
 get innerHTML(){return content},set innerHTML(value){content=value;if(id==='case'){const match=value.match(/value="([^"]+)"/);this.value=match?match[1]:''}}};
}
const ctx=vm.createContext({document:{getElementById:id=>{assert(nodes[id],id);return nodes[id]}},console});
vm.runInContext(script,ctx);
assert.equal(nodes.case.value,'0');assert(evidence.selection.includes('lexicographically first'));
assert(nodes.content.innerHTML.includes(evidence.cases[0].id));
for(let i=0;i<evidence.cases.length;i++){
 nodes.case.value=String(i);nodes.case.listeners.change();const output=nodes.content.innerHTML;
 for(const label of ['Audited exposure E*','Harm, utility and uncertainty','Validity checks','Provenance','Omean'])assert(output.includes(label),`${i}: ${label}`);
 assert(!output.includes('[object Object]'));
}
nodes.tier.value='fixture';nodes.tier.listeners.change();assert(evidence.cases[Number(nodes.case.value)].kind.startsWith('Synthetic'));
nodes.tier.value='real';nodes.tier.listeners.change();assert.equal(nodes.case.value,'0');
assert(!/<(?:script|link|img|iframe)[^>]+(?:src|href)=/i.test(html));
assert(!/\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon|importScripts)\s*\(/.test(script));
assert(html.includes("connect-src 'none'"));assert(html.includes('prefers-color-scheme:dark'));assert(html.includes('max-width:650px'));
const real=evidence.cases.filter(c=>c.kind.startsWith('Real'));
assert.equal(real[0].id,real.map(c=>c.id).sort()[0]);
for(const c of real)for(const arm of ['F','S','K','N'])assert(c.arms[arm].diff);
const report={status:'pass',case_renders:evidence.cases.length,real_cases:real.length,fixture_cells:evidence.cases.length-real.length,default:real[0].id,
 html_sha256:crypto.createHash('sha256').update(html).digest('hex'),
 checks:['all case rendering functions executed with minimal DOM stub','both evidence tier controls switch and reset case selection','offline resource and network API checks','CSP, responsive and color scheme rules present'],
 limitation:'Not a browser layout or visual test. Headless Chrome screenshot skipped per user instruction; director render pending.'};
fs.writeFileSync(__dirname+'/verification.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
