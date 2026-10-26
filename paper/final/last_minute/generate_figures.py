#!/usr/bin/env python3
"""Publication figures from frozen data and the independent boundary audit.

Requires an existing matplotlib + Pillow installation; never downloads fonts.
Run after analyze_boundary.py. SVG retains editable text and embeds OFL fonts.
"""
import base64
import html
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager
from matplotlib.patches import Rectangle, FancyArrowPatch
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FONTS = ROOT/'paper/v2/fonts'
for name in ('Regular', 'Bold', 'Italic'):
    fontManager.addfont(str(FONTS/f'OldStandard-{name}.ttf'))
plt.rcParams.update({'svg.fonttype':'none', 'font.family':'Old Standard TT',
                     'pdf.fonttype':42, 'savefig.facecolor':'white'})
INK, MUTED, LINE = '#20312e', '#5d6663', '#cbd3cf'
GREEN, RUST, PALE = '#285b4b', '#955b43', '#f1f5f2'


class Figure:
    def __init__(self, name, height, title, description):
        self.name, self.w, self.h = name, 468, height
        self.title, self.description = title, description
        self.fig = plt.figure(figsize=(self.w/72, self.h/72), dpi=144)
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(0,self.w), ylim=(self.h,0))
        self.ax.set_axis_off()
        self.texts = []

    def text(self, x, y, value, size=10, weight='Regular', color=INK, ha='left'):
        assert size >= 8
        font = FontProperties(fname=str(FONTS/f'OldStandard-{weight}.ttf'), size=size,
                              weight='bold' if weight=='Bold' else 'normal',
                              style='italic' if weight=='Italic' else 'normal')
        artist = self.ax.text(x,y,value,fontproperties=font,color=color,ha=ha,va='baseline')
        self.texts.append((artist, value, size))

    def rect(self, x,y,w,h,fill='white',edge=LINE):
        self.ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor=edge,linewidth=.65))

    def line(self,x,y,x2,y2,color=LINE,width=.65):
        self.ax.plot([x,x2],[y,y2],color=color,linewidth=width)

    def arrow(self,x,y,x2,y2,color=MUTED):
        self.ax.add_patch(FancyArrowPatch((x,y),(x2,y2),arrowstyle='-|>',
                                         mutation_scale=9,color=color,linewidth=.8))

    def save(self):
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        bounds = self.fig.bbox
        boxes = []
        for artist, value, size in self.texts:
            b = artist.get_window_extent(renderer)
            assert b.x0 >= bounds.x0-1 and b.x1 <= bounds.x1+1, ('horizontal clip',value)
            assert b.y0 >= bounds.y0-1 and b.y1 <= bounds.y1+1, ('vertical clip',value)
            boxes.append({'text':value,'font_pt':size,'bbox_pixels':list(b.bounds)})
        self.fig.savefig(OUT/f'{self.name}.svg',metadata={'Date':None,'Title':self.title,
                                                       'Description':self.description})
        # Matplotlib's SVG keeps live text but does not package fonts. Embed the
        # repository's unmodified OFL fonts to make the intended face portable.
        path = OUT/f'{self.name}.svg'
        svg = path.read_text()
        rules = []
        for face,weight,style in [('Regular','normal','normal'),('Bold','bold','normal'),('Italic','normal','italic')]:
            data = base64.b64encode((FONTS/f'OldStandard-{face}.ttf').read_bytes()).decode()
            rules.append(f"@font-face{{font-family:'Old Standard TT';font-weight:{weight};font-style:{style};src:url(data:font/ttf;base64,{data}) format('truetype')}}")
        svg = svg.replace('<defs>', '<defs>\n<style type="text/css">'+''.join(rules)+'</style>',1)
        svg = svg.replace('<svg ', '<svg role="img" aria-labelledby="figure-title figure-description" ',1)
        svg = svg.replace('<defs>', '<title id="figure-title">'+html.escape(self.title)+'</title>\n<desc id="figure-description">'+html.escape(self.description)+'</desc>\n<defs>',1)
        path.write_text('\n'.join(line.rstrip() for line in svg.splitlines())+'\n')
        self.fig.savefig(OUT/f'{self.name}.png',dpi=300)
        self.fig.savefig(OUT/f'{self.name}.pdf',metadata={'CreationDate':None,'ModDate':None,
                                                      'Title':self.title})
        im = Image.open(OUT/f'{self.name}.png')
        assert im.width == 1950 and abs(im.height - self.h/72*300) < 2
        assert all(abs(v-300)<.1 for v in im.info['dpi'])
        ns={'s':'http://www.w3.org/2000/svg'}
        doc=ET.parse(path).getroot()
        assert doc.findall('.//s:text',ns) and not doc.findall('.//s:image',ns)
        # Text overlap checking excludes intentionally separate text lines only
        # when their boxes do not intersect; every pair is checked geometrically.
        overlaps=[]
        for i,(a,va,_) in enumerate(self.texts):
            for b,vb,_ in self.texts[i+1:]:
                aa,bb=a.get_window_extent(renderer),b.get_window_extent(renderer)
                if min(aa.x1,bb.x1)-max(aa.x0,bb.x0) > 1 and min(aa.y1,bb.y1)-max(aa.y0,bb.y0) > 1:
                    overlaps.append([va,vb])
        assert not overlaps, overlaps
        plt.close(self.fig)
        return {'title':self.title,'description':self.description,'width_pt':468,
                'height_pt':self.h,'minimum_text_pt':min(s for _,_,s in self.texts),
                'png_pixels':list(im.size),'png_dpi':list(im.info['dpi']),
                'svg_text_elements':len(doc.findall('.//s:text',ns)),
                'text_bounds_checked':True,'text_overlaps':overlaps,'text_boxes':boxes}


def main():
    audit=json.loads((OUT/'boundary_audit.json').read_text())
    tw=json.loads((ROOT/'paper/v2/figures/fig_twins_audit.json').read_text())['plotted_values']
    a,b=(tw['members'][m]['outcomes_outsider'] for m in ('A','B'))
    assert a['F']==b['F']==14 and a['K']==b['K']==19
    assert a['PF']==14 and b['PF']==29 and a['PK']==b['PK']==29
    assert audit['component_deletion_controls']['P2_delete_PF']=={'pairs':200,'still_distinct':0}
    v=Figure('figure_A_same_evidence',278,'Same Evidence, Different Policies',
             'Constructed P2 allocation twins: identical messages and baseline replay rewards, separated by the designed cost probe. No real-agent performance claim.')
    v.text(5,17,'Same evidence, different policies',15,'Bold')
    v.text(5,32,'Constructed allocation twins  ·  P2  ·  deterministic  ·  seed 19693329',9.5,color=MUTED)
    v.rect(5,43,458,35,PALE,PALE)
    v.text(234,64,'“Please allocate the contested task to our dispatch team.”',11,'Italic',ha='center')
    for x,title,rule,color in [(5,'Permitted policy','Allocate by efficiency',GREEN),
                                (249,'Prohibited policy','Protect the coalition allocation',RUST)]:
        v.text(x+107,97,title,12,'Bold',color,ha='center')
        v.text(x+107,111,rule,9.5,color=MUTED,ha='center')
        v.text(x+107,139,'14 → 19',22,'Bold',ha='center')
        v.text(x+107,154,'Outsider reward: message shown → removed',9,ha='center')
    v.line(5,165,463,165)
    v.text(234,182,'I4 cost probe: lower each outsider’s task cost by 10',11,'Bold',ha='center')
    for x,reward,action,color in [(112,29,'Cedes the task',GREEN),(356,14,'Retains the task',RUST)]:
        v.arrow(x,187,x,198,color)
        v.text(x,223,str(reward),25,'Bold',color,ha='center')
        v.text(x,239,action+' · factual probe reward (PF)',9.5,ha='center')
    v.text(234,256,'Probe knockout reward (PK): 29 in both worlds',9.5,color=MUTED,ha='center')
    v.line(5,263,463,263)
    v.text(234,275,'Same through I3; removing PF restores ambiguity in all 200 P2 pairs.',9.5,ha='center')
    outputs={'figure_A_same_evidence':v.save()}

    # Every displayed audit count is checked against the independent reduction.
    def cell(kind,level):
        return next(r for r in audit['cells'] if (r['kind'],r['level'])==(kind,level))
    def pair(kind,level):
        return next(r for r in audit['pairs'] if (r['kind'],r['level'])==(kind,level))
    assert cell('P1','I3')['ambiguous_negative_answers']==200
    assert cell('P6','I4')['abstained']==400
    assert pair('P6','I4')['both_globally_identifiable']==200
    assert pair('P4','I1')['pair_distinct']==200 and pair('P4','I1')['both_globally_identifiable']==0
    assert pair('P2','I4')['v1_correct_both']==pair('P3','I5')['v1_correct_both']==200
    assert all(cell('relayed-harmful',s)['globally_identifiable_members']==0 for s in LEVELS[1:])
    effects=json.loads((ROOT/'docs/analysis/exp002_heldout_v3/effects_study.json').read_text())
    primary=next(r for r in effects if r['effect']=='Delta_total')
    assert round(primary['estimate'],3)==1.354 and primary['p_raw']==.0703125
    v=Figure('figure_B_evidence_establishes',405,'What Evidence Actually Establishes',
             'Actual evidence access I1-I5, constructed benchmark successes and failures, and the distinct unresolved eight-pair real-agent contrast. All deterministic restrictions are post hoc.')
    v.text(5,17,'What evidence actually establishes',15,'Bold')
    v.text(5,32,'More evidence can resolve a named ambiguity; it does not validate an auditor.',10,color=MUTED)
    for x,title,requires in [(5,'Influence','I1: factual + knockout'),
                             (161,'Harmful exposure','I2: controls + harm gates'),
                             (317,'Policy attribution','I3–I5: separating evidence')]:
        v.line(x,46,x+146,46,GREEN,1.5)
        v.text(x+73,63,title,11.5,'Bold',ha='center')
        v.text(x+73,78,requires,9,ha='center')
    v.text(5,101,'EVIDENCE ADDED',9,'Bold',MUTED)
    v.text(166,101,'WHAT THE FROZEN RECORDS SHOW',9,'Bold',MUTED)
    rows=[
        ('I1','Single-message knockout K',[
            'B2+ accuses legitimate P2/P3: 200/200 each.',
            'P6: 0/200; benign cooperation: 0/100.']),
        ('I2','Sham S and placebo N',[
            'CCC exposure supported on legitimate P2/P3:',
            '200/200 each. Their attribution remains unresolved.']),
        ('I3','Joint same-sender removal J',[
            'P1 separates 200/200 pairs; 200 negative answers',
            'still admit a prohibited relay alternative.']),
        ('I4','Task-cost probe PF and PK',[
            'P2: correct attribution on 200/200 pairs.',
            'P6: identifiable; CCC-L abstains on all 400 members.']),
        ('I5','External authorization record',[
            'P3: correct attribution on 200/200 pairs.',
            'The record defines permission; separation is designed.']),
    ]
    for i,(level,addition,lines) in enumerate(rows):
        y=111+i*37
        v.line(5,y,463,y)
        v.text(5,y+15,level,11,'Bold',GREEN)
        v.text(27,y+15,addition,8.8)
        v.text(166,y+14,lines[0],9.5)
        v.text(166,y+28,lines[1],9.5)
    v.line(5,296,463,296)
    v.text(5,311,'Pair separation ≠ global attribution',10.5,'Bold')
    v.text(5,325,'P4/I1: 200/200 pairs differ; neither label is globally identifiable.',9.5)
    v.text(5,339,'Relay cases: 0/100 identifiable at I1–I5. Full utility: 2/84 settings.',9.5)
    v.rect(5,350,458,38,PALE,PALE)
    v.text(14,365,'Separate language-model study: directional contrast not established',10.5,'Bold')
    v.text(14,380,'8 pairs; contrast = 1.354; 95% interval [−0.020, 2.834]; p = 0.0703125.',10)
    v.text(234,401,'Deterministic scope is post hoc; noisy-platform divergence remains unresolved.',9,color=MUTED,ha='center')
    outputs['figure_B_evidence_establishes']=v.save()
    provenance={'classification':'Frozen-data graphics; new boundary checks are post-hoc-exploratory.',
                'insertion_width':'468 pt = 6.5 inches; do not shrink below 6.5 inches for the stated text sizes.',
                'fonts':'Unmodified Old Standard TT from paper/v2/fonts; embedded in SVG; OFL.txt remains at that source path.',
                'sources':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in
                           [OUT/'boundary_audit.json',OUT/'analyze_boundary.py',Path(__file__).resolve(),
                            ROOT/'paper/v2/figures/fig_twins_audit.json',
                            ROOT/'docs/analysis/exp002_heldout_v3/effects_study.json']},
                'graphics':outputs}
    for stem in outputs:
        outputs[stem]['outputs']={ext:sha256((OUT/f'{stem}.{ext}').read_bytes()).hexdigest() for ext in ('svg','png','pdf')}
    (OUT/'figure_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({k:{a:v[a] for a in ('width_pt','height_pt','minimum_text_pt','png_pixels','png_dpi','svg_text_elements','text_bounds_checked','text_overlaps')} for k,v in outputs.items()},indent=2))


LEVELS=tuple(f'I{i}' for i in range(6))
if __name__=='__main__':
    main()
