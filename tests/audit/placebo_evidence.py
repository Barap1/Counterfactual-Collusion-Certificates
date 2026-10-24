"""Explicit synthetic N_m evidence for pure decision unit tests (no native claim)."""
from ccc.audit.placebo import RULE

SELECTION = {'status':'accepted', 'rule':RULE, 'M_star':['unit-chatter']}

def bind(branches):
    for row in branches.get('N', []):
        row['placebo_control'] = {'label':'N_m', 'M_star':['unit-chatter']}
        row['checks'] = [{'id':'V05b','name':'placebo_render_exact_every_prompt','status':'pass',
                          'details':{'arm':'N','m_star':['unit-chatter'],'receiver_prompts':1}}]
    return branches
