#!/usr/bin/env python3
"""Generate original editable SVGs and matching vector PDFs from frozen CCC records.
No worlds, models, network or experiment code are run. Requires reportlab and Poppler.
"""
from pathlib import Path
import json,hashlib,html,subprocess,math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[4]; OUT=ROOT/'paper/final/figures'
FONT=ROOT/'paper/v2/fonts'
for name,file in [('OST','OldStandard-Regular.ttf'),('OSTB','OldStandard-Bold.ttf'),('OSTI','OldStandard-Italic.ttf')]:pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
INK='#193025';GREEN='#194b37';GREY='#726d66';LINE='#d5dbd6';PALE='#f2f5f2';BLUE='#355b79';WHITE='#ffffff'
manifest={}
class V:
 def __init__(self,name,w,h,alt):
  self.name=name;self.w=w;self.h=h;self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(alt)}</title><rect width="100%" height="100%" fill="white"/>'];self.c=canvas.Canvas(str(OUT/(name+'.pdf')),pagesize=(w,h),invariant=1);self.c.setTitle(alt);self.c.setAuthor('Aarav Patel');self.rect(0,0,w,h,WHITE,None)
 def col(self,c):return tuple(int(c[i:i+2],16)/255 for i in (1,3,5))
 def rect(self,x,y,w,h,fill=WHITE,stroke=LINE,r=0):
  self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width=".65"/>');self.c.setLineWidth(.65)
  if fill:self.c.setFillColorRGB(*self.col(fill))
  if stroke:self.c.setStrokeColorRGB(*self.col(stroke))
  self.c.roundRect(x,self.h-y-h,w,h,r,stroke=bool(stroke),fill=bool(fill))
 def line(self,x,y,x2,y2,color=LINE,width=.6,dash=False):
  self.svg.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="3 3"' if dash else '')+'/>');self.c.setStrokeColorRGB(*self.col(color));self.c.setLineWidth(width);self.c.setDash([3,3] if dash else []);self.c.line(x,self.h-y,x2,self.h-y2);self.c.setDash([])
 def text(self,x,y,t,size=10,font='OST',color=INK,anchor='start'):
  weight='bold' if font=='OSTB' else 'normal';style='italic' if font=='OSTI' else 'normal';self.svg.append(f'<text x="{x}" y="{y}" font-family="Old Standard TT, serif" font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{color}" text-anchor="{anchor}">{html.escape(t)}</text>');self.c.setFont(font,size);self.c.setFillColorRGB(*self.col(color));{'start':self.c.drawString,'middle':self.c.drawCentredString,'end':self.c.drawRightString}[anchor](x,self.h-y,t)
 def dot(self,x,y,r=3,color=GREEN):
  self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>');self.c.setFillColorRGB(*self.col(color));self.c.circle(x,self.h-y,r,fill=1,stroke=0)
 def arrow(self,x,y,x2,y2,color=INK):
  self.line(x,y,x2,y2,color,1);a=math.atan2(y2-y,x2-x)
  for z in [-.5,.5]:self.line(x2,y2,x2-5*math.cos(a+z),y2-5*math.sin(a+z),color,1)
 def save(self):
  self.svg.append('</svg>');(OUT/(self.name+'.svg')).write_text('\n'.join(self.svg));self.c.showPage();self.c.save();subprocess.run(['pdftoppm','-scale-to-x',str(round(self.w/72*300)),'-scale-to-y','-1','-singlefile','-png',str(OUT/(self.name+'.pdf')),str(OUT/self.name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def source(p):
 q=ROOT/p;return {'path':p,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
# Read the existing audited exhibit, with explicit frozen provenance.
twinp='paper/v2/figures/fig_twins_audit.json';tw=json.loads((ROOT/twinp).read_text())['plotted_values'];assert tw['seed']==19693329
A=tw['members']['A']['outcomes_outsider'];B=tw['members']['B']['outcomes_outsider'];assert A['F']==B['F']==14 and A['K']==B['K']==19 and A['PF']==14 and B['PF']==29 and A['PK']==B['PK']==29
v=V('fig1_twins',468,194,'Constructed allocation twins: identical replay evidence; an incentive probe separates specified policies.')
v.text(0,12,'SAME OBSERVATIONS',10,'OSTB');v.text(468,12,'DIFFERENT PROGRAMMED RESPONSES',10,'OSTB',anchor='end')
v.rect(0,23,468,39,PALE,None,3);v.text(234,39,'“Please allocate the contested task to our dispatch team.”',11,'OSTI',anchor='middle');v.text(234,54,'Same allocation · outsider reward F = S = N = 14; K = 19',10,anchor='middle')
v.rect(0,77,212,62);v.rect(256,77,212,62);v.text(12,94,'Forbidden coordination',12,'OSTB');v.text(268,94,'Efficiency-motivated cooperation',12,'OSTB');v.text(12,109,'Protect the coalition allocation',10);v.text(268,109,'Allocate according to efficiency',10);v.text(12,127,'Before probe: retain task',10);v.text(268,127,'Before probe: retain task',10)
v.text(234,73,'↓',12,anchor='middle');v.arrow(106,141,106,154);v.arrow(362,141,362,154)
v.text(234,151,'I4: outsider cost lowered by 10',10,'OSTB',anchor='middle');v.text(106,169,'Retain task · outsider reward 14',10,'OSTB',anchor='middle');v.text(362,169,'Cede task · outsider reward 29',10,'OSTB',anchor='middle')
v.line(0,179,468,179);v.text(234,191,'Knockout: influence and exposure harm. Attribution: unresolved until separating evidence.',9.5,anchor='middle');v.save()
manifest['fig1_twins']={'sources':[source(twinp),source('figures/enh/prospective/fig_twins.json')],'values':tw,'schematic':True,'alt':'Two scripted allocation mechanisms share the dispatch message and outsider rewards 14 factual,19 knockout. Lowering outsider cost by10 leads forbidden policy to keep the task, reward14, and efficiency policy to yield, reward29.','caption':'Constructed P2 twins, seed19693329. Extra evidence separates the specified policies, not arbitrary real agents.'}
# Exact proportions and intervals from the frozen report.
rp='docs/enh/r2/run_par/RESULTS.json';r=json.loads((ROOT/rp).read_text());rows=[z for z in r['tables']['T5'] if z['epsilon']==0];print('T5 kinds',[z['kind'] for z in rows])
labels={'P2':'Efficiency allocation (P2)','P3':'Authorized transfer (P3)','P6':'Information-bearing (P6)','benign-cooperation':'Benign cooperation'}
plot=[]
for z in rows:
 kind=z['kind'];a=z['over_attribution'];plot.append({'kind':kind,'label':labels.get(kind,'Benign cooperation'),'k':a['unit_k'],'n':a['independent_n'],'ci':a['unit_cp95']})
assert [(a['k'],a['n']) for a in plot]==[(200,200),(200,200),(0,200),(0,100)]
v=V('fig2_accusations',468,133,'B2+ legitimate-member accusation rates at identical I1 evidence: scenario-dependent failures.')
x=lambda p:202+p*170
for k in [0,.5,1]:v.line(x(k),15,x(k),105,LINE,.5);v.text(x(k),121,f'{k:.0%}',9,anchor='middle')
for i,a in enumerate(plot):
 y=27+i*23;v.text(0,y+3,a['label'],10.5);lo,hi=a['ci'];v.line(x(lo),y,x(hi),y,GREEN,2);v.line(x(lo),y-3,x(lo),y+3,GREEN,1);v.line(x(hi),y-3,x(hi),y+3,GREEN,1);v.dot(x(a['k']/a['n']),y,3,GREEN);v.text(468,y+3,f"{a['k']}/{a['n']}",10.5,'OSTB',anchor='end')
v.text(287,132,'Accusation rate · exact 95% interval',9.5,anchor='middle');v.save();manifest['fig2_accusations']={'sources':[source(rp)],'selector':'tables.T5 rows epsilon==0; over_attribution.unit_k/independent_n/unit_cp95','values':plot,'alt':'Accusation rate100% for legitimate P2/P3 with200units each;0% for P6 n200 and benign n100; exact confidence intervals.','caption':'Original all-class baseline prediction failed; effects are scenario-dependent.'}
# Matched world contrasts: original file order retained; no post-hoc highlights.
dp='docs/analysis/exp002_heldout_v2/figure_data/fig_delta_by_world.json';data=json.loads((ROOT/dp).read_text());ep='docs/analysis/exp002_heldout_v3/effects_study.json';effects=json.loads((ROOT/ep).read_text());agg=next(z for z in effects if z['effect']=='Delta_total');assert len(data)==8
v=V('fig3_real_agents',468,169,'Original real-agent matched-world effects with aggregate uncertainty crossing zero.')
x=lambda a:62+(a+1.5)/7.5*262
for tick in [-1,0,1,2,3,4,5]:
 v.line(x(tick),12,x(tick),118,LINE if tick else GREY,.55 if tick else 1,dash=bool(tick==0));v.text(x(tick),135,str(tick),9,anchor='middle')
for i,z in enumerate(data):
 y=17+i*11;v.text(0,y+3,f'Pair {i+1}',9.5);v.dot(x(z['d_w']),y,2.7,BLUE)
v.line(0,109,468,109);y=119;v.text(0,y+3,'Mean',10,'OSTB');v.line(x(agg['L']),y,x(agg['U']),y,GREEN,2.4);v.line(x(agg['L']),y-4,x(agg['L']),y+4,GREEN,1);v.line(x(agg['U']),y-4,x(agg['U']),y+4,GREEN,1);v.dot(x(agg['estimate']),y,4,GREEN)
v.text(347,29,'Delta = 1.354',12,'OSTB');v.text(347,46,'95% CI [−0.020, 2.834]',9.5);v.text(347,63,'n = 8 matched pairs',10);v.text(347,80,'One-sided p = 0.0703',10);v.text(347,101,'Directional hypothesis',9.5);v.text(347,115,'not supported',11,'OSTB');v.text(193,151,'Prompt-regime contrast in outsider effect (task reward units)',10,anchor='middle');v.text(193,165,'Cooperation larger  ←  0  →  Deceptive prompts larger',9.5,color=GREY,anchor='middle');v.save()
manifest['fig3_real_agents']={'sources':[source(dp),source(ep)],'values':{'pairs':data,'primary':agg,'signflip_numerator':18,'signflip_denominator':256},'alt':'Eight pair contrasts range from−1.086to5.259. Mean1.354 with95%interval−.020to2.834 crosses zero; one-sided p.0703.','caption':'Preregistered primary directional hypothesis not supported. No post-hoc highlights.'}
# Original non-evidentiary banner. More graphical, same font and palette.
v=V('ccc_banner',900,245,'CCC: Counterfactual Collusion Certificates. What changed is not yet who colluded.')
v.rect(0,0,900,245,WHITE,None);v.line(0,0,900,0,GREEN,5);v.text(32,67,'CCC',48,'OSTB');v.text(32,100,'Counterfactual Collusion Certificates',23,'OSTB');v.text(32,138,'What changed? What can we attribute?',19);v.text(32,193,'Evidence standards for AI-agent collusion audits',13,color=GREY);v.text(32,218,'Constructed counterexamples · controlled replay · explicit uncertainty',12,color=GREY)
v.line(563,28,563,221,LINE,1)
v.rect(592,38,261,48,PALE,None,3);v.text(723,58,'Same message + allocation',14,'OSTB',anchor='middle');v.text(723,76,'Two constructed mechanisms',11,anchor='middle')
v.arrow(723,90,723,112,GREEN);v.text(723,134,'Add an incentive probe',13,'OSTI',anchor='middle')
v.line(654,148,790,148,GREEN,1);v.arrow(654,148,654,165,GREEN);v.arrow(790,148,790,165,GREEN)
v.text(654,184,'Coalition rule',12,'OSTB',anchor='middle');v.text(790,184,'Efficiency rule',12,'OSTB',anchor='middle');v.text(654,206,'Keeps task',12,anchor='middle');v.text(790,206,'Yields task',12,anchor='middle');v.save()
assets=ROOT/'docs/assets';assets.mkdir(exist_ok=True)
for ext in ['svg','png']:(assets/('ccc_banner.'+ext)).write_bytes((OUT/('ccc_banner.'+ext)).read_bytes())
manifest['ccc_banner']={'schematic':True,'data':'Non-evidentiary identity graphic; no numeric claims.','source':'original Vector primitives in src/generate.py'}
v=V('evidence_flow',900,186,'Four different audit claims, each requiring its own evidence; no automatic implication.')
labels=[('Suspicious content','What does the message say?','Transcript'),('Causal influence','What changes when it is removed?','Valid controlled replay'),('Harmful exposure','Who loses, and by how much?','Outsider, coalition, welfare gates'),('Collusion attribution','What policy was violated?','Separating behavior or authority')]
for i,(title,question,evidence) in enumerate(labels):
 x=i*225+8;v.rect(x,24,209,118,WHITE,LINE,3);v.text(x+12,49,title,15,'OSTB');v.text(x+12,72,question,11);v.line(x+12,85,x+196,85);v.text(x+12,105,'Requires',10,'OSTI',GREY);v.text(x+12,125,evidence,10.5)
v.text(450,16,'DISTINCT CLAIMS. SEPARATE REQUIREMENTS.',11,'OSTB',anchor='middle');v.text(450,169,'Incomplete evidence leaves attribution unresolved. A prior claim does not automatically prove the next.',12,anchor='middle');v.save()
for ext in ['svg','png']:(assets/('evidence_flow.'+ext)).write_bytes((OUT/('evidence_flow.'+ext)).read_bytes())
manifest['evidence_flow']={'schematic':True,'data':'Four claim definitions, not empirical observations.','source':'original Vector primitives in src/generate.py'}
(OUT/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Wrote',list(manifest))
