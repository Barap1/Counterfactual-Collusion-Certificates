#!/usr/bin/env python3
"""Dependency-free final provenance, headline and vector/raster artifact checks."""
from collections import Counter
import base64
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def main():
    audit=read(OUT/'boundary_audit.json')
    figure=read(OUT/'figure_provenance.json')
    hashes={**audit['sources'], **figure['sources']}
    for path, expected in hashes.items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==expected, path
    results=read(ROOT/'docs/enh/r2/run_par/RESULTS.json')
    rows=[r for r in results['tables']['T5'] if r['epsilon']==0]
    accusations={r['kind']:[r['over_attribution']['unit_k'],r['over_attribution']['independent_n']] for r in rows}
    assert accusations=={'P2':[200,200],'P3':[200,200],'P6':[0,200],'benign-cooperation':[0,100]}
    selected=[r for r in results['rq']['RQ5']['pair_attribution'] if r['epsilon']==0]
    assert {(r['kind'],r['set'],r['k'],r['n']) for r in selected}=={('P2','I4',200,200),('P3','I5',200,200)}
    failed=[k for k,v in results['rq'].items() if v['status']=='fail']
    assert failed==['RQ3','RQ4','RQ4b','RQ5']
    effects=read(ROOT/'docs/analysis/exp002_heldout_v3/effects_study.json')
    primary=next(r for r in effects if r['effect']=='Delta_total')
    assert primary['estimate']==1.354325711018898
    assert [primary['L'],primary['U']]==[-0.01954964911635066,2.8336288730243204]
    assert primary['p_raw']==.0703125
    fresh=read(OUT/'checks/headline.json')
    assert len(fresh['pairs'])==8 and math.isclose(fresh['Delta'],primary['estimate'],abs_tol=2e-14)
    assert fresh['sign_flip']=={'denominator':256,'numerator':18,'p':.0703125}
    cert=read(ROOT/'docs/analysis/exp002_heldout_v3/checkpoint_certificates.json')
    assert Counter(r['status'] for r in cert)==Counter({'supported':0,'not_supported':11,'inconclusive':5})
    # Compare the newly rerun bootstrap receipt with the canonical interval.
    bootstrap=read(OUT/'checks/bootstrap.json')
    assert all(abs(a-b)<2e-14 for a,b in zip(bootstrap['ci'],[primary['L'],primary['U']]))
    strata=read(ROOT/'docs/enh/r2/RESULTS_BY_STRATUM.json')
    platform={eps:{k:v for k,v in data.items() if not isinstance(v,(list,dict))}
              for eps,data in strata['platform_audit'].items()}
    graphics=[]
    ns={'s':'http://www.w3.org/2000/svg'}
    for stem, info in figure['graphics'].items():
        for ext, expected in info['outputs'].items():
            assert sha256((OUT/f'{stem}.{ext}').read_bytes()).hexdigest()==expected
        svg=ET.parse(OUT/f'{stem}.svg').getroot()
        texts=svg.findall('.//s:text',ns)
        assert svg.find('s:title',ns) is not None and svg.find('s:desc',ns) is not None
        assert len(texts)==info['svg_text_elements']
        sizes=[float(re.search(r'font-size:\s*([\d.]+)px',e.get('style')).group(1)) for e in texts]
        assert min(sizes)>=8 and min(sizes)==info['minimum_text_pt']
        assert any('font-weight: 700' in e.get('style','') for e in texts)
        assert not svg.findall('.//s:script',ns) and not svg.findall('.//s:foreignObject',ns)
        assert not svg.findall('.//s:image',ns)
        source=(OUT/f'{stem}.svg').read_text()
        assert source.count('@font-face')==3 and 'data:font/ttf;base64,' in source
        embedded=re.findall(r'data:font/ttf;base64,([A-Za-z0-9+/=]+)',source)
        assert len(embedded)==3
        for payload, face in zip(embedded, ('Regular','Bold','Italic')):
            assert base64.b64decode(payload)==(ROOT/f'paper/v2/fonts/OldStandard-{face}.ttf').read_bytes()
        data=(OUT/f'{stem}.png').read_bytes()
        assert data[:8]==b'\x89PNG\r\n\x1a\n'
        offset=8; dimensions=None; dpi=None
        while offset<len(data):
            length=struct.unpack('>I',data[offset:offset+4])[0]
            tag=data[offset+4:offset+8]; payload=data[offset+8:offset+8+length]
            if tag==b'IHDR': dimensions=list(struct.unpack('>II',payload[:8]))
            if tag==b'pHYs':
                x,y,unit=struct.unpack('>IIB',payload)
                assert unit==1
                dpi=[x*.0254,y*.0254]
            offset+=length+12
        assert dimensions==info['png_pixels'] and dimensions[0]==1950
        assert dpi and all(abs(d-300)<.1 for d in dpi)
        assert info['text_bounds_checked'] and not info['text_overlaps']
        # The existing broad document-ID rule can match random fragments of a
        # public font's base64. Verify exact font bytes, then audit the remaining
        # text with that same rule. Never suppress or overwrite its original log.
        candidates=re.compile(r'''(?<![A-Za-z0-9_-])(/d/|["'])?([A-Za-z0-9_-]{44})(?![A-Za-z0-9_-])''')
        def id_flags(text):
            count=0
            for m in candidates.finditer(text):
                prefix, token=m.groups()
                suspect=(prefix=='/d/' or
                         (prefix in ('"',"'") and any(c.isupper() for c in token) and any(c.islower() for c in token) and any(c.isdigit() for c in token)) or
                         (token.startswith('1') and re.search(r'[G-Zg-z_-]',token)))
                count+=bool(suspect)
            return count
        stripped=re.sub(r'data:font/ttf;base64,[A-Za-z0-9+/=]+','verified-public-font',source)
        assert id_flags(stripped)==0
        graphics.append(dict(stem=stem,minimum_font_pt=min(sizes),png_pixels=dimensions,dpi=dpi,
                             embedded_fonts_exactly_match_tracked_OFL_sources=True,
                             document_id_pattern_candidates_inside_font_payloads=id_flags(source),
                             document_id_pattern_candidates_outside_font_payloads=id_flags(stripped)))
    receipt=dict(status='PASS',frozen_and_derived_input_hashes_verified=len(hashes),
                 deterministic_accusations=accusations,designed_pair_attribution=selected,
                 aggregate_failures=failed,utility=audit['composite_utility'],
                 primary={k:primary[k] for k in ('estimate','L','U','p_raw')},
                 real_agent_certificates=dict(Counter(r['status'] for r in cert)),
                 platform_overlap_record_rechecked=platform,graphics=graphics,
                 scope='Hashes and published arithmetic/artifact checks; no model reruns, new sensitivity claim, fresh clean-install verification or live-Doc layout validation.')
    (OUT/'checks/delivery_verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','frozen_and_derived_input_hashes_verified','aggregate_failures','graphics')},indent=2))


if __name__=='__main__':
    main()
