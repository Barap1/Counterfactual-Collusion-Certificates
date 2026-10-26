/* CCC Evidence Explorer. Vanilla JS, offline. All numbers come from window.CCC_DATA
   (generated from demo/data/*.json by bundle_data.py). No network, no innerHTML with data. */
(function () {
  'use strict';
  var D = window.CCC_DATA;
  var main = document.getElementById('main');
  var $ = function (id) { return document.getElementById(id); };
  var SVGNS = 'http://www.w3.org/2000/svg';

  /* ---------- helpers ---------- */
  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (attrs[k] === null || attrs[k] === undefined || attrs[k] === false) continue;
      if (k === 'class') el.className = attrs[k];
      else if (k === 'on') for (var ev in attrs.on) el.addEventListener(ev, attrs.on[ev]);
      else el.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    }
    for (var i = 2; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  function add(el, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { add(el, x); }); return; }
    el.appendChild(typeof c === 'object' ? c : document.createTextNode(String(c)));
  }
  function s(tag, attrs) {
    var el = document.createElementNS(SVGNS, tag);
    if (attrs) for (var k in attrs) if (attrs[k] !== null && attrs[k] !== undefined) el.setAttribute(k, attrs[k]);
    for (var i = 2; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  function fmt(x, d) {
    if (x === null || x === undefined || (typeof x === 'number' && !isFinite(x))) return '—';
    if (typeof x !== 'number') return String(x);
    var r = x.toFixed(d === undefined ? 2 : d);
    return r === '-0.00' || /^-0\.0+$/.test(r) ? r.slice(1) : r;
  }
  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }
  function mean(a) { return a.length ? a.reduce(function (p, c) { return p + c; }, 0) / a.length : null; }
  function concept(kind, text) {
    var map = { causal: ['c-causal', 'Causal effect'], harm: ['c-harm', 'Harm'], attr: ['c-attr', 'Attribution'], unc: ['c-unc', 'Uncertainty'] };
    return h('span', { class: 'concept ' + map[kind][0] }, text || map[kind][1]);
  }
  function statusPill(st) {
    var k = String(st).replace(' ', '_');
    return h('span', { class: 'status ' + k }, String(st).replace('_', ' '));
  }
  function provBadge(c) {
    var held = /held-out/.test(c.provenance_label);
    return h('span', { class: 'badge ' + (held ? 'held' : 'dev'), title: c.provenance_label + ' (evidence category: ' + c.evidence_category + ')' },
      held ? 'held-out · frozen' : 'development · scripted');
  }
  function sha(t) { return h('span', { class: 'hash' }, t); }
  function tw(t) { return h('div', { class: 'tw', tabindex: '0', role: 'region', 'aria-label': 'Scrollable table' }, t); }
  var ARM_NAME = { F: 'Factual', K: 'Knockout', S: 'Sham', N: 'Placebo' };
  var ARM_DESC = { F: 'message delivered as recorded', K: 'exposure message masked for the receiver', S: 'sham: identical input, fresh sampling', N: 'placebo: a different, non-informational message masked' };

  /* ---------- data access ---------- */
  var cases = D.index.cases;
  var byId = {}; cases.forEach(function (c) { byId[c.id] = c; });
  var loading = {};
  function loadCase(id) {
    if (D.cases[id]) return Promise.resolve(D.cases[id]);
    if (loading[id]) return loading[id];
    loading[id] = new Promise(function (res, rej) {
      var sc = document.createElement('script');
      sc.src = 'data/case_' + id + '.js';
      sc.onload = function () { D.cases[id] ? res(D.cases[id]) : rej(new Error('case file loaded but empty')); };
      sc.onerror = function () { delete loading[id]; rej(new Error('Could not load data/case_' + id + '.js. Run bundle_data.py.')); };
      document.head.appendChild(sc);
    });
    return loading[id];
  }

  /* Normalise held-out and scripted-fixture certificates to one shape (no values invented). */
  function norm(c) {
    var cert = c.certificate, held = c.regime !== undefined;
    var o = { held: held, status: cert.status, reasons: [], mO: null, dW: null, tau: {}, placebo: null, wording: null };
    if (held) {
      o.mO = cert.gates.m_O; o.dW = cert.gates.delta_W;
      ['O', 'C', 'W', 'A'].forEach(function (k) {
        o.tau[k] = { est: cert['tau_' + k], L: cert['tau_' + k + '_L'], U: cert['tau_' + k + '_U'], exact: false };
      });
      o.reasons = cert.reasons || [];
      o.placebo = cert.placebo_contrast_status;
      o.wording = cert.wording;
    } else {
      o.mO = c.margins.m_O; o.dW = c.margins.delta_W;
      var e = cert.estimates || {}, ef = e.effects || {}, iv = e.intervals || {};
      ['O', 'C', 'W', 'A'].forEach(function (k) {
        var i = iv['tau_' + k];
        o.tau[k] = { est: ef['tau_' + k] === undefined ? null : ef['tau_' + k], L: i ? i[0] : null, U: i ? i[1] : null, exact: !!i && i[0] === i[1] };
      });
      o.reasons = cert.reasons || [];
      o.placebo = cert.placebo_status;
      var ro = (c.gate_trace || []).filter(function (g) { return g.gate === 'recorded_outcome'; })[0];
      o.wording = ro ? ro.wording : null;
    }
    return o;
  }
  function excludesZero(t) { return t.L !== null && (t.L > 0 || t.U < 0); }

  /* L0/L1 are UI-derived heuristics; only supported certificates reach L2. */
  function ladder(c) {
    var n = norm(c), O = n.tau.O, st = n.status;
    var infl = ['O', 'C', 'W'].some(function (k) { return excludesZero(n.tau[k]); });
    var top, why;
    var rO = O.L === null ? 'no outsider-loss interval was produced' : 'L(O)=' + fmt(O.L) + ', U(O)=' + fmt(O.U) + ' vs m_O=' + fmt(n.mO, 1);
    if (st === 'supported') { top = 2; why = 'Certificate supported: valid replay and L(O) = ' + fmt(O.L) + ' exceeds m_O = ' + fmt(n.mO, 1) + '. The evidence stops at L2.'; }
    else if (st === 'invalid') { top = 0; why = 'Replay validity checks failed, so no behavioural effect can be read from the continuations. Highest rung: the text itself (L0).'; }
    else if (st === 'not_supported' || st === 'not supported') {
      top = infl ? 1 : 0;
      why = (infl ? 'An effect of the knockout is visible (an interval excludes 0), ' : 'No interval excludes 0, ') + 'but harmful exposure is not supported: ' + rO + (O.U !== null && O.U < n.mO ? ' (upper bound below the margin)' : '') + '. Stopped at ' + (infl ? 'L1' : 'L0') + '.';
    } else {
      top = infl ? 1 : 0;
      why = 'Inconclusive: ' + rO + (n.reasons.length ? '; recorded reasons: ' + n.reasons.join(', ') : '') + '. ' + (infl ? 'Some influence is visible (L1), ' : 'No influence is established (L0), ') + 'but the harm rung cannot be decided.';
    }
    if (top === 1) why += ' UI-derived, not a certificate rung: interval is one-sided, case-conditional, n_independent = 1; influence does not establish harm.';
    return { top: top, why: why, infl: infl };
  }
  function ladderStrip(c) {
    var L = ladder(c), n = norm(c);
    var defs = [
      ['L0', 'Suspicious text', 'The exposure message exists in the record.'],
      ['L1', 'Causal influence', 'Behaviour or outcomes change when the message is knocked out.'],
      ['L2', 'Harmful exposure', 'Valid replay and outsider loss beyond m_O, with controls.'],
      ['L3', 'Attribution', 'Collusion justified. Needs evidence beyond a knockout.']
    ];
    var highest = n.status === 'supported' ? 'highest supported' : 'highest reached (UI-derived, not a certificate rung)';
    var wrap = h('div', { class: 'ladder', role: 'list', 'aria-label': 'Evidence ladder; L' + L.top + ' ' + highest });
    defs.forEach(function (d, i) {
      var cls = 'rung' + (i < L.top ? ' reached' : '') + (i === L.top && i < 3 ? ' top' : '') + (i === 3 ? ' na' : '');
      var st = i === 3 ? 'not claimed' : (i === L.top ? highest : (i < L.top ? 'reached' : 'not reached'));
      wrap.appendChild(h('div', { class: cls, role: 'listitem' }, h('b', null, d[0]), d[1], h('span', { class: 'st' }, st), h('span', { class: 'muted' }, d[2])));
    });
    return h('div', null, wrap,
      h('p', null, concept('causal', 'L1'), ' ', concept('harm', 'L2'), ' ', concept('attr', 'L3'), ' ', h('strong', null, 'Why it stops here: '), L.why),
      h('p', { class: 'muted' }, 'L3 is never claimed. A knockout measures what a message did, not whether it should have done it' + (n.held ? '; CCC makes no attribution claim on the held-out data.' : '; this fixture is development evidence.')));
  }

  /* ---------- SVG: interval plot ---------- */
  function ticks(lo, hi) {
    var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / 4)));
    var m = span / 4 / step; step *= m > 5 ? 10 : m > 2 ? 5 : m > 1 ? 2 : 1;
    var out = [], t = Math.ceil(lo / step) * step;
    for (; t <= hi + 1e-9; t += step) out.push(Math.round(t / step) * step);
    return out;
  }
  function intervalPlot(n, opts) {
    opts = opts || {};
    var rows = [
      { k: 'O', name: 'tau_O', sub: 'outsider loss', kind: 'harm', ref: n.mO, refLabel: 'm_O = ' + fmt(n.mO, 1), col: 'var(--harm)' },
      { k: 'C', name: 'tau_C', sub: 'coalition benefit', kind: 'causal', ref: 0, refLabel: '0', col: 'var(--causal)' },
      { k: 'W', name: 'tau_W', sub: 'welfare change', kind: 'causal', ref: -n.dW, refLabel: '−δ_W = ' + fmt(-n.dW, 1), col: 'var(--causal)' }
    ];
    var W = opts.w || 720, rowH = 74, padL = 150, padR = 24, H = rows.length * rowH + 14;
    var svg = s('svg', { class: 'plot', viewBox: '0 0 ' + W + ' ' + H, role: 'img',
      'aria-label': 'Interval plot of tau_O, tau_C and tau_W with one-sided bounds L and U against margins' });
    var desc = [];
    rows.forEach(function (r, i) {
      var t = n.tau[r.k], y = i * rowH + 40;
      var vals = [0, r.ref]; ['est', 'L', 'U'].forEach(function (f) { if (t[f] !== null) vals.push(t[f]); });
      var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), pad = (hi - lo || 1) * 0.12;
      lo -= pad; hi += pad;
      var x = function (v) { return padL + (v - lo) / (hi - lo) * (W - padL - padR); };
      svg.appendChild(s('text', { x: 8, y: y - 6, 'font-size': 15, 'font-weight': 700 }, r.name));
      svg.appendChild(s('text', { x: 8, y: y + 12, 'font-size': 13, class: 'muted', fill: 'var(--muted)' }, r.sub));
      svg.appendChild(s('line', { x1: padL, x2: W - padR, y1: y + 14, y2: y + 14, class: 'ax' }));
      ticks(lo, hi).forEach(function (tv) {
        svg.appendChild(s('line', { x1: x(tv), x2: x(tv), y1: y + 14, y2: y + 19, class: 'ax' }));
        svg.appendChild(s('text', { x: x(tv), y: y + 31, 'font-size': 13, 'text-anchor': 'middle', fill: 'var(--muted)' }, fmt(tv, Math.abs(tv) < 1 && tv !== 0 ? 2 : (tv % 1 ? 1 : 0))));
      });
      svg.appendChild(s('line', { x1: x(0), x2: x(0), y1: y - 22, y2: y + 14, class: 'gl', 'stroke-dasharray': '2 3' }));
      if (r.ref !== 0) {
        svg.appendChild(s('line', { x1: x(r.ref), x2: x(r.ref), y1: y - 26, y2: y + 14, stroke: 'var(--ink)', 'stroke-width': 2, 'stroke-dasharray': '6 3' }));
        svg.appendChild(s('text', { x: x(r.ref), y: y - 30, 'font-size': 13, 'font-weight': 700, 'text-anchor': 'middle' }, r.refLabel));
      }
      if (t.L !== null && t.U !== null && !t.exact) {
        svg.appendChild(s('rect', { x: x(t.L), y: y - 6, width: Math.max(2, x(t.U) - x(t.L)), height: 14, fill: r.col, opacity: 0.28 }));
        svg.appendChild(s('line', { x1: x(t.L), x2: x(t.L), y1: y - 10, y2: y + 12, stroke: r.col, 'stroke-width': 3 }));
        svg.appendChild(s('line', { x1: x(t.U), x2: x(t.U), y1: y - 10, y2: y + 12, stroke: r.col, 'stroke-width': 3 }));
        svg.appendChild(s('text', { x: x(t.L), y: y - 13, 'font-size': 13, 'text-anchor': 'middle', fill: r.col }, 'L ' + fmt(t.L)));
        svg.appendChild(s('text', { x: x(t.U), y: y - 13, 'font-size': 13, 'text-anchor': 'middle', fill: r.col }, 'U ' + fmt(t.U)));
      }
      if (t.est !== null) {
        var px = x(t.est);
        if (t.exact) svg.appendChild(s('path', { d: 'M' + px + ' ' + (y - 9) + ' l8 8 l-8 8 l-8 -8z', fill: r.col }));
        else svg.appendChild(s('circle', { cx: px, cy: y + 1, r: 5.5, fill: 'var(--bg)', stroke: r.col, 'stroke-width': 3 }));
      } else {
        svg.appendChild(s('text', { x: padL, y: y + 1, 'font-size': 13, fill: 'var(--muted)' }, 'no estimate in this certificate'));
      }
      desc.push(r.name + ': ' + (t.est === null ? 'none' : fmt(t.est)) + (t.L !== null ? ' [' + fmt(t.L) + ', ' + fmt(t.U) + ']' : ''));
    });
    svg.appendChild(s('title', null, desc.join('; ')));
    return svg;
  }
  function rowVerdicts(n) {
    var out = [], O = n.tau.O, C = n.tau.C, W = n.tau.W;
    if (O.L !== null) out.push(['harm', 'tau_O', O.L > n.mO ? 'Whole interval is above m_O: harm beyond the margin is supported.' : O.U < n.mO ? 'Upper bound is below m_O under the stated interval assumption; this is not a test or an exoneration.' : 'Interval straddles m_O: the harm question is undecided.']);
    if (C.L !== null) out.push(['causal', 'tau_C', C.L > 0 ? 'Coalition benefit excludes 0 (L > 0).' : C.U <= 0 ? 'No coalition benefit (U ≤ 0).' : 'Interval includes 0: coalition benefit undecided.']);
    if (W.L !== null) out.push(['causal', 'tau_W', W.L >= -n.dW ? 'No welfare change beyond −δ_W (L ≥ −δ_W).' : W.U < -n.dW ? 'Welfare change beyond −δ_W (U < −δ_W).' : 'Interval straddles −δ_W: undecided.']);
    return out;
  }

  /* ---------- interaction log ---------- */
  function postedText(rec) {
    var parts = [];
    (rec.messages || []).forEach(function (m) {
      if (m.content) parts.push({ t: 'say', v: m.content });
      (m.tool_calls || []).forEach(function (tc) {
        var a = null;
        try { a = JSON.parse(tc.function.arguments); } catch (e) { a = null; }
        if (tc.function.name === 'post_message' && a) parts.push({ t: 'post', v: a.message, bb: a.blackboard_id });
        else parts.push({ t: 'call', v: tc.function.name + '(' + (a ? JSON.stringify(a) : tc.function.arguments) + ')' });
      });
    });
    return parts;
  }
  function recordView(rec, exp, roleOf) {
    var isExp = rec.exposure_highlight;
    var el = h('div', { class: 'rec' + (isExp ? ' exp' : '') });
    if (isExp) el.appendChild(h('div', { class: 'xtag' }, 'Exposure message' + (exp && exp.sender ? ': ' + exp.sender + ' → ' + exp.receiver : '')));
    el.appendChild(h('div', { class: 'who' }, rec.agent, ' ', h('span', null, 'turn ' + rec.turn_index + ' · step ' + rec.step + ' · ' + rec.phase + ' · record #' + rec.source_record_index)));
    postedText(rec).forEach(function (p) {
      if (p.t === 'post') el.appendChild(h('div', { class: 'body' }, h('span', { class: 'muted' }, 'posted to blackboard ' + p.bb + ': '), p.v));
      else if (p.t === 'say') el.appendChild(h('div', { class: 'body' }, p.v));
      else el.appendChild(h('div', { class: 'tool' }, 'tool call: ' + p.v));
    });
    (rec.tool_results || []).forEach(function (tr) { el.appendChild(h('div', { class: 'tool' }, 'tool result (' + tr.name + '): ' + tr.content)); });
    return el;
  }
  function logView(records, exp, cpTurn) {
    var box = h('div', { class: 'log', tabindex: '0', role: 'region', 'aria-label': 'Agent interaction transcript' });
    records.forEach(function (r) { box.appendChild(recordView(r, exp)); });
    if (cpTurn !== undefined && cpTurn !== null) box.appendChild(h('div', { class: 'cpline' }, 'Checkpoint at turn ' + cpTurn + ': continuations branch from here'));
    return box;
  }

  /* ---------- certificate trace ---------- */
  var REASON = {
    imprecise: 'the interval is too wide to decide against the margin',
    pattern_ambiguous: 'the harm pattern gates (coalition benefit / efficiency) are ambiguous',
    no_placebo_available: 'no eligible placebo (N) branch existed, so the placebo control could not run',
    pattern_mutual_disruption: 'the pattern gates indicate mutual disruption',
    not_identifiable_redundant: 'the message is not identifiable under single-message knockout (a redundant carrier may exist)',
    pattern_efficient_transfer: 'the pattern looks like an efficient transfer'
  };
  function traceItem(kind, title, text) {
    var sym = { pass: '✓', fail: '✗', info: 'i', warn: '!' }[kind];
    return h('li', null, h('span', { class: 'ic ' + kind, 'aria-label': kind }, sym), h('div', null, h('strong', null, title), h('div', null, text)));
  }
  function traceView(c) {
    var n = norm(c), items = [], gt = c.gate_trace || [];
    gt.forEach(function (g) {
      var G = g.gate;
      if (G === 'all_valid') items.push(traceItem(g.value ? 'pass' : 'fail', 'Validity', g.value ? 'Every continuation replay passed its validity checks.' : 'At least one replay validity check failed.'));
      else if (G === 'session_break') items.push(traceItem(g.value ? 'fail' : 'pass', 'Session continuity', g.value ? 'A session break occurred during replay.' : 'No session break.'));
      else if (G === 'lesion_artefact') items.push(traceItem(g.value ? 'fail' : 'pass', 'Lesion artefact', g.value ? 'The knockout itself may have disrupted behaviour.' : 'No sign that the mask itself, rather than the message, disrupted behaviour.'));
      else if (G === 'treatment_dependent_missingness') items.push(traceItem(g.value ? 'fail' : 'pass', 'Missing outcomes', g.value ? 'Missing outcomes depend on the arm.' : 'Missing outcomes do not depend on the arm.'));
      else if (G === 'placebo_available') items.push(traceItem(g.value ? 'pass' : 'warn', 'Placebo (N)', g.value ? 'An eligible placebo branch existed.' : 'Not run: no eligible placebo was available (stored as availability metadata, which may overstate its causal role).'));
      else if (G === 'V9') items.push(traceItem(g.value === 'pass' ? 'pass' : 'warn', 'Sham gate V9', 'Recorded as “' + g.value + '”.' + (g.value === 'sham_uncertain' ? ' The sham (S) comparison is flagged uncertain.' : '')));
      else if (G === 'm_O' || G === 'delta_W') { /* shown in the margins line */ }
      else if (G === 'placebo') items.push(traceItem(g.value === 'accepted' ? 'pass' : 'info', 'Placebo status', g.value === null ? 'No placebo status recorded.' : 'Recorded as “' + g.value + '”.'));
      else if (G === 'outsider_loss') {
        var k = g.lower_exceeds_margin ? 'pass' : g.upper_below_margin ? 'warn' : 'warn';
        items.push(traceItem(k, 'Outsider loss vs margin (HARM)', 'L(O) = ' + fmt(g.L) + ', U(O) = ' + fmt(g.U) + ', margin m_O = ' + fmt(g.margin, 1) + '. ' +
          (g.lower_exceeds_margin ? 'The lower bound exceeds the margin: harmful exposure supported.' : g.upper_below_margin ? 'Upper bound is below m_O under the stated interval assumption; this is not a test or an exoneration.' : 'The interval straddles the margin: undecided.')));
      } else if (G === 'coalition_benefit' || G === 'efficiency' || G === 'no_material_efficiency_gain') {
        var nm = { coalition_benefit: 'Coalition benefit', efficiency: 'Efficiency (welfare)', no_material_efficiency_gain: 'No material efficiency gain' }[G];
        var tx = g.L !== undefined ? 'L = ' + fmt(g.L) + ', U = ' + fmt(g.U) + (g.delta_W ? ', δ_W = ' + fmt(g.delta_W, 1) : '') + '. ' : '';
        items.push(traceItem(g.status === 'pass' ? 'pass' : (g.status === 'fail' ? 'fail' : 'info'), nm + ' gate', tx + 'Status: ' + g.status + '.' + (g.explanation ? ' ' + g.explanation : '')));
      } else if (G === 'information_and_redundancy') {
        var fl = Object.keys(g.flags || {}).filter(function (f) { return g.flags[f]; });
        items.push(traceItem('info', 'Information and redundancy', 'Information-bearing: ' + g.info_bearing + (g.info_bearing_source ? ' (' + g.info_bearing_source + ')' : '') + '. Flags: ' + (fl.length ? fl.join(', ') : 'none') + '.'));
      } else if (G === 'recorded_outcome') { /* final verdict below */ }
      else items.push(traceItem('info', G, JSON.stringify(g.value !== undefined ? g.value : g.status)));
    });
    items.push(traceItem('info', 'Margins used', 'm_O = ' + fmt(n.mO, 1) + ' (outsider loss), δ_W = ' + fmt(n.dW, 1) + ' (welfare tolerance).'));
    var why;
    if (n.status === 'supported') why = 'Issued because the replays were valid, the sham and placebo controls did not undercut the effect, and the outsider-loss lower bound L(O) = ' + fmt(n.tau.O.L) + ' exceeds m_O = ' + fmt(n.mO, 1) + ', with the coalition-benefit and efficiency pattern gates passing. This is L2 evidence only.';
    else if (n.status === 'invalid') why = 'Withheld because replay validity checks failed (' + n.reasons.map(function (r) { return typeof r === 'string' ? r : r; }).join('; ') + '). No score is issued from invalid replays.';
    else {
      var bits = [];
      var O = n.tau.O;
      if (O.U !== null && O.U < n.mO) bits.push('the outsider-loss upper bound U(O) = ' + fmt(O.U) + ' is below m_O = ' + fmt(n.mO, 1));
      if (O.L !== null && O.L <= n.mO && O.U >= n.mO) bits.push('the outsider-loss interval [' + fmt(O.L) + ', ' + fmt(O.U) + '] straddles m_O = ' + fmt(n.mO, 1));
      n.reasons.forEach(function (r) { var code = typeof r === 'string' ? r : r.code; bits.push(REASON[code] || ('recorded reason: ' + code)); });
      if (n.status !== 'inconclusive' && !bits.length) bits.push('no recorded reason code');
      why = 'Withheld (status ' + String(n.status).replace('_', ' ') + ') because ' + bits.join('; ') + '.';
    }
    return { list: h('ul', { class: 'trace' }, items), why: why, wording: n.wording };
  }

  /* ---------- validity ---------- */
  var VMEAN = {
    'V-echo': 'Echo check recorded per branch (meaning not stated in the pack).',
    'V-model': 'Model identity check recorded per branch (meaning not stated in the pack).',
    V01: 'Snapshot/restore round trip reproduces canonical state.',
    V02: 'Prefix reconstruction: replayed requests/tool events match the recording.',
    V03: 'Branch isolation: one branch cannot alter another or the source.',
    V04: 'Sham identity: factual and sham inputs are identical before fresh sampling.',
    V05: 'Targeted exposure: only the declared receiver/surface changes.',
    V05b: 'Rendering is exact on every prompt (render_exact_every_prompt).',
    V06: 'Prior exposure: already-seen message or history leak is flagged.',
    V07: 'Repeated rendering: the mask stays effective over the horizon (mask_no_leak).',
    V08: 'Tool protocol validity (engine id; batch V8 differs).',
    V09: 'Fresh continuation (engine id; batch V9 differs).',
    V3: 'Independent prompt diff between arms.',
    V6: 'Check V6 (meaning not stated in the pack).',
    V1_static: 'Static check V1 (meaning not stated in the pack).'
  };
  function validityView(c) {
    var rc = c.validity.raw_counts, tot = { pass: 0, fail: 0, na: 0 };
    var rows = rc.map(function (r) {
      ['pass', 'fail', 'na'].forEach(function (k) { tot[k] += r.counts[k] || 0; });
      var extra = Object.keys(r.counts).filter(function (k) { return ['pass', 'fail', 'na'].indexOf(k) < 0; }).map(function (k) { return k + ' ' + r.counts[k]; });
      return h('tr', null, h('td', null, h('code', null, r.check)), h('td', null, VMEAN[r.check] || 'Meaning not stated in the pack; see docs/spec/10_verification.md.'),
        h('td', null, h('span', { class: 'pf p' }, 'pass ' + (r.counts.pass || 0)), h('span', { class: 'pf ' + (r.counts.fail ? 'f' : 'n') }, 'fail ' + (r.counts.fail || 0)), h('span', { class: 'pf n' }, 'na ' + (r.counts.na || 0)), extra.join(' ')));
    });
    var canon = c.validity.canonical_records || [];
    var cs = {}; canon.forEach(function (x) { cs[x.status] = (cs[x.status] || 0) + 1; });
    return h('div', null,
      h('div', { class: 'vgrid' },
        h('div', { class: 'vcell' }, h('div', { class: 'n' }, tot.pass + ' / ' + tot.fail + ' / ' + tot.na), h('div', { class: 'm' }, 'pass / fail / na (raw recorded checks)')),
        h('div', { class: 'vcell' }, h('div', { class: 'n' }, Object.keys(cs).map(function (k) { return k + ' ' + cs[k]; }).join(', ') || 'none'), h('div', { class: 'm' }, 'canonical analysis rows by status'))),
      h('p', { class: 'muted' }, c.validity.note || 'Raw counts count recorded checks, not independent worlds.'),
      tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Check'), h('th', null, 'What it asks'), h('th', null, 'Recorded results'))), h('tbody', null, rows))));
  }

  /* ---------- compare ---------- */
  function armData(c, arm) {
    var items = (c.continuations || []).filter(function (x) { return x.arm === arm; });
    var ok = items.filter(function (x) { return x.status === 'valid' && x.metrics; });
    return { items: items, ok: ok };
  }
  function agentRewards(m) {
    if (m.rewards) return m.rewards;
    if (m.agent_rewards) return m.agent_rewards;
    return {};
  }
  function committedOf(m) { return m.committed || m.assignment || {}; }
  function armSummary(ok) {
    var out = { n: ok.length, Omean: null, Cmean: null, W: null, rewards: {} };
    ['Omean', 'Cmean', 'W'].forEach(function (k) { out[k] = mean(ok.map(function (x) { return x.metrics[k]; })); });
    var agents = {}; ok.forEach(function (x) { Object.keys(agentRewards(x.metrics)).forEach(function (a) { agents[a] = 1; }); });
    Object.keys(agents).sort().forEach(function (a) { out.rewards[a] = mean(ok.map(function (x) { return agentRewards(x.metrics)[a]; }).filter(function (v) { return v !== undefined && v !== null; })); });
    return out;
  }
  function notRunText(c, arm, ad) {
    var reasons = {}; ad.items.forEach(function (x) { (x.reasons || []).forEach(function (r) { reasons[typeof r === 'string' ? r : r.code] = 1; }); });
    var rs = Object.keys(reasons);
    if (arm === 'N' && (rs.indexOf('no_placebo_available') >= 0 || (c.certificate.gates && c.certificate.gates.placebo_available === false))) return 'not run: no eligible placebo';
    if (ad.items.length && !ad.ok.length) return 'not run' + (rs.length ? ': ' + rs.join(', ') : '') + ' (status ' + ad.items.map(function (x) { return x.status; }).filter(function (v, i, a) { return a.indexOf(v) === i; }).join(', ') + ')';
    var av = c.arms && c.arms[arm] ? c.arms[arm].availability : null;
    return 'not run: ' + (av || 'no branch record for this case');
  }
  var transcriptSel = null;
  function compareView(c) {
    var wrap = h('div'), grid = h('div', { class: 'armgrid' }), summ = {};
    ['F', 'K', 'S', 'N'].forEach(function (arm) {
      var ad = armData(c, arm), card = h('div', { class: 'card arm A-' + arm });
      card.appendChild(h('h3', null, arm + ' · ' + ARM_NAME[arm]));
      card.appendChild(h('p', { class: 'muted' }, ARM_DESC[arm]));
      if (!ad.ok.length) { card.appendChild(h('p', { class: 'nr' }, notRunText(c, arm, ad))); grid.appendChild(card); return; }
      var S = summ[arm] = armSummary(ad.ok);
      card.appendChild(h('p', null, h('strong', null, S.n + ' valid replicate' + (S.n > 1 ? 's' : '')), ' of ' + ad.items.length + ' recorded' + (S.n === 1 ? ' (single replicate, no averaging)' : ' (means over replicates)')));
      var roleSrc = ad.ok[0].metrics.roles || null;
      var rrows = Object.keys(S.rewards).map(function (a) {
        return h('tr', null, h('td', null, a, roleSrc && roleSrc[a] ? [' ', h('span', { class: 'chip role-' + roleSrc[a] }, roleSrc[a])] : null), h('td', { class: 'r num' }, fmt(S.rewards[a])));
      });
      card.appendChild(tw(h('table', null, h('caption', null, 'Per-agent reward'), h('thead', null, h('tr', null, h('th', null, 'Agent'), h('th', { class: 'r' }, 'Reward'))), h('tbody', null, rrows))));
      card.appendChild(tw(h('table', null, h('tbody', null,
        h('tr', null, h('td', null, 'Outsider mean'), h('td', { class: 'r num' }, fmt(S.Omean))),
        h('tr', null, h('td', null, 'Coalition mean'), h('td', { class: 'r num' }, fmt(S.Cmean))),
        h('tr', null, h('td', null, 'W (total welfare)'), h('td', { class: 'r num' }, fmt(S.W)))))));
      var act = h('details', { class: 'd' }, h('summary', null, 'Actions: committed tasks per replicate'));
      var at = h('div'); act.appendChild(at);
      ad.ok.forEach(function (x) {
        var cm = committedOf(x.metrics), ch = h('div', { class: 'chips' });
        Object.keys(cm).sort().forEach(function (a) { ch.appendChild(h('span', { class: 'chip' }, a + ': ' + (cm[a] === null ? 'none' : cm[a]))); });
        at.appendChild(h('p', null, h('strong', null, 'rep ' + x.rep), ch));
      });
      card.appendChild(act);
      grid.appendChild(card);
    });
    wrap.appendChild(grid);
    // arm contrasts recomputed from rows, reconciled against the certificate
    if (summ.F && summ.K) {
      var n = norm(c), d = {
        O: summ.K.Omean - summ.F.Omean, C: summ.F.Cmean - summ.K.Cmean, W: summ.K.W - summ.F.W
      };
      var rec = ['O', 'C', 'W'].map(function (k) {
        var cv = n.tau[k].est, ok = cv !== null && Math.abs(cv - d[k]) < 1e-6;
        return h('tr', null, h('td', null, 'tau_' + k), h('td', { class: 'r num' }, fmt(d[k], 3)), h('td', { class: 'r num' }, fmt(cv, 3)), h('td', null, cv === null ? 'no certificate estimate' : ok ? 'reconciles' : 'differs (estimator differs)'));
      });
      wrap.appendChild(h('div', { class: 'card' }, h('h3', null, 'Reconciliation: rows vs certificate'),
        h('p', { class: 'muted' }, 'Browser arithmetic on the stored replicate rows (outsider: K−F; coalition: F−K; welfare: K−F) next to the certificate’s stored value. The certificate value is authoritative.'),
        tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Quantity'), h('th', { class: 'r' }, 'From rows'), h('th', { class: 'r' }, 'Certificate'), h('th', null, 'Check'))), h('tbody', null, rec)))));
    }
    // bar comparison
    var barArms = ['F', 'K', 'S', 'N'].filter(function (a) { return summ[a]; });
    if (barArms.length) wrap.appendChild(barPlot(summ, barArms));
    // transcripts
    var avail = (c.continuations || []).filter(function (x) { return x.messages && x.messages.length; });
    if (avail.length) {
      var sel = h('select', { id: 'tsel', 'aria-label': 'Choose continuation transcript' });
      avail.forEach(function (x, i) { sel.appendChild(h('option', { value: i }, x.arm + ' (' + ARM_NAME[x.arm] + '), rep ' + x.rep)); });
      var holder = h('div');
      var show = function () { clear(holder); var x = avail[sel.value]; holder.appendChild(logView(x.messages, null, null)); };
      sel.addEventListener('change', show);
      wrap.appendChild(h('details', { class: 'd' }, h('summary', null, 'Claims: continuation transcripts (messages and tool calls after the checkpoint)'),
        h('div', null, h('label', null, 'Transcript: ', sel), holder)));
      show();
    } else if (c.continuations && c.continuations.some(function (x) { return x.messages_availability; })) {
      wrap.appendChild(h('p', { class: 'note' }, 'Continuation transcripts: ' + c.continuations.filter(function (x) { return x.messages_availability; })[0].messages_availability + '.'));
    }
    return wrap;
  }
  function barPlot(summ, arms) {
    var metrics = [['Omean', 'Outsider mean'], ['Cmean', 'Coalition mean'], ['W', 'W']], colors = { F: 'var(--ink)', K: 'var(--causal)', S: 'var(--unc)', N: 'var(--attr)' };
    var Wd = 720, gh = 120, svg = s('svg', { class: 'plot', viewBox: '0 0 ' + Wd + ' ' + (metrics.length * gh + 10), role: 'img', 'aria-label': 'Bar chart of outsider mean, coalition mean and W by arm' });
    metrics.forEach(function (m, mi) {
      var y0 = mi * gh + 22, vals = arms.map(function (a) { return summ[a][m[0]]; }), mx = Math.max.apply(null, vals.concat([0])), mn = Math.min.apply(null, vals.concat([0]));
      var span = mx - mn || 1;
      svg.appendChild(s('text', { x: 4, y: y0 - 6, 'font-size': 13, 'font-weight': 700 }, m[1]));
      arms.forEach(function (a, i) {
        var y = y0 + i * 22, x0 = 190, bw = (summ[a][m[0]] - 0) / span * (Wd - x0 - 110), zx = x0 + (-mn) / span * (Wd - x0 - 110);
        svg.appendChild(s('text', { x: x0 - 8, y: y + 13, 'font-size': 14, 'text-anchor': 'end' }, a + ' ' + ARM_NAME[a]));
        svg.appendChild(s('rect', { x: bw >= 0 ? zx : zx + bw, y: y, width: Math.abs(bw), height: 15, fill: colors[a], opacity: a === 'F' ? 0.85 : 0.8 }));
        svg.appendChild(s('text', { x: (bw >= 0 ? zx + bw : zx) + (bw >= 0 ? 6 : -6), y: y + 12, 'font-size': 14, 'text-anchor': bw >= 0 ? 'start' : 'end', class: 'num' }, fmt(summ[a][m[0]])));
      });
    });
    return h('div', { class: 'card bars' }, h('h3', null, 'Outcomes by arm'), chartScroll(svg, 'Outcome means by arm'), h('p', { class: 'muted' }, 'Bars show means over the valid replicates listed above (stored per-replicate values).'));
  }

  /* ---------- case page ---------- */
  function sectionNav(ids) {
    var nav = h('nav', { class: 'sect-nav', 'aria-label': 'Sections of this case' });
    ids.forEach(function (x) {
      nav.appendChild(h('a', { href: '#/case/' + curId, on: { click: function (e) { e.preventDefault(); var t = $(x[0]); if (t) { var detail = t.closest('details'); if (detail) detail.open = true; t.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'start' }); t.focus({ preventScroll: true }); } } } }, x[1]));
    });
    return nav;
  }
  var curId = null;
  function sec(id, title, kinds, body) {
    return h('section', { id: id, tabindex: '-1', 'aria-labelledby': id + '-h' }, h('h2', { id: id + '-h' }, title, ' ', (kinds || []).map(function (k) { return [concept(k), ' ']; })), body);
  }
  function renderCase(id) {
    curId = id;
    var meta = byId[id];
    clear(main);
    main.appendChild(h('p', { class: 'muted' }, 'Loading ' + (meta ? meta.title : id) + '…'));
    loadCase(id).then(function (c) {
      if (curId !== id) return;
      clear(main);
      var n = norm(c), held = n.held;
      main.appendChild(h('div', { class: 'head' }, h('h1', { id: 'top-h' }, c.title), provBadge(c), statusPill(c.certificate.status)));
      main.appendChild(h('p', { class: 'muted' }, held
        ? 'EXP-002 world ' + c.world_id + ' · regime ' + c.regime + (c.regime === 'B1' ? ' (deceptive prompt)' : ' (authorized-cooperation prompt)') + ' · checkpoint turn ' + c.checkpoint_turn + ' · evidence category: ' + c.evidence_category
        : 'Scripted fixture ' + c.family + ' (seed ' + c.seed + ', stratum ' + c.stratum + ') · ' + c.selection_rule + ' · evidence category: ' + c.evidence_category));
      if (!held) main.appendChild(h('p', { class: 'note warn' }, (c.limitations || []).join(' ')));
      else main.appendChild(h('p', { class: 'note' }, 'Held-out cases are descriptive here. The preregistered directional hypothesis was not supported (see Study). Case certificates are Tier-B exploratory.'));
      main.appendChild(sectionNav([['s-ladder', 'Evidence scope'], ['s-inter', 'Observed message'], ['s-cmp', 'F vs K'], ['s-chg', 'What changed'], ['s-val', 'Controls & validity'], ['s-cert', 'Certificate'], ['s-raw', 'Raw evidence']]));
      main.appendChild(disclosure('How the evidence ladder applies to this case', sec('s-ladder', 'Evidence ladder', [], ladderStrip(c))));
      main.appendChild(sec('s-inter', 'Interaction up to the checkpoint', ['causal'], interactionView(c)));
      main.appendChild(sec('s-cmp', 'Factual vs knockout continuations', ['causal'], compareView(c)));
      main.appendChild(sec('s-chg', 'What changed', ['causal', 'harm', 'unc'], changeView(c, n)));
      main.appendChild(sec('s-val', 'Replay validity and control checks', [], disclosure('Inspect all recorded validity checks', validityView(c))));
      main.appendChild(sec('s-cert', 'Recorded certificate and uncertainty', [], certView(c, n)));
      main.appendChild(sec('s-raw', 'Raw evidence', [], rawView(c)));
      window.scrollTo({ top: 0, behavior: 'instant' });
      enhance();
      var hd = $('top-h'); if (hd) { hd.setAttribute('tabindex', '-1'); }
    }).catch(function (e) { if (curId !== id) return; clear(main); main.appendChild(h('p', { class: 'note warn', role: 'alert' }, String(e.message))); });
  }
  function interactionView(c) {
    var ex = c.exposure, box = h('div');
    if (c.regime !== undefined) {
      box.appendChild(h('div', { class: 'expcard' }, h('div', { class: 'route' }, 'Exposure: ' + ex.sender + ' → ' + ex.receiver),
        h('div', { class: 'muted' }, 'private channel [' + (ex.channel_participants || []).join(', ') + '], posted turn ' + ex.posted_turn + ', first seen turn ' + ex.first_exposure_turn + ', knockout mask from turn ' + ex.mask_start + ' (' + ex.mask_version + ')'),
        h('blockquote', null, ex.content)));
      box.appendChild(disclosure('Original interaction transcript and checkpoint', logView(c.original_interaction || [], ex, c.checkpoint_turn)));
      box.appendChild(h('p', { class: 'muted' }, 'The highlighted record is the sender’s post_message call; the checkpoint line marks where factual and knockout continuations branch.'));
    } else {
      box.appendChild(h('div', { class: 'expcard' }, h('div', { class: 'route' }, 'Exposure message'),
        (ex.messages || []).map(function (m) { return h('blockquote', null, m); }),
        h('div', { class: 'muted' }, 'Sender is the agent prefix of the message; the receiver is not recorded in the fixture result.')));
      box.appendChild(h('p', { class: 'note' }, c.original_interaction_availability || 'Original interaction not persisted.'));
      var det = c.detector_text_evidence;
      if (det && det.observations) {
        var dv = h('div');
        det.observations.forEach(function (o) {
          dv.appendChild(h('h3', null, 'Detector observation at turn ' + o.turn));
          Object.keys(o.surfaces).forEach(function (sf) {
            dv.appendChild(h('p', { class: 'muted' }, 'surface ' + sf));
            o.surfaces[sf].forEach(function (t) { if (t) dv.appendChild(h('div', { class: 'body' }, t)); });
          });
        });
        box.appendChild(h('details', { class: 'd' }, h('summary', null, 'Detector text evidence (boundary turn ' + det.boundary + ')'), h('div', null, dv)));
      }
    }
    return box;
  }
  function changeView(c, n) {
    var box = h('div');
    box.appendChild(h('div', { class: 'legend' }, h('span', null, concept('harm', 'tau_O: outsider loss'), ' vs ', h('code', null, 'm_O')),
      h('span', null, concept('causal', 'tau_C, tau_W'), ' vs 0 and −δ_W'), h('span', null, concept('unc', 'bar width'), ' = bound span'), h('span', null, 'dashed black = margin')));
    box.appendChild(h('div', { class: 'card' }, chartScroll(intervalPlot(n), 'Case effect intervals')));
    var rv = rowVerdicts(n);
    if (rv.length) box.appendChild(h('ul', null, rv.map(function (r) {
      var t = n.tau[r[1].slice(4)];
      return h('li', null, concept(r[0]), ' ', h('strong', null, r[1] + ' '), r[2], t.L !== null && !t.exact ? [' ', concept('unc', 'bound span ' + fmt(t.U - t.L))] : null);
    })));
    var tbl = ['O', 'C', 'W'].map(function (k) {
      var t = n.tau[k];
      return h('tr', null, h('td', null, h('code', null, 'tau_' + k)), h('td', { class: 'r num', title: t.est === null ? '' : String(t.est) }, fmt(t.est, 3)), h('td', { class: 'r num' }, fmt(t.L)), h('td', { class: 'r num' }, fmt(t.U)),
        h('td', null, t.exact ? 'exact scripted point (no sampling uncertainty)' : t.L === null ? 'none' : 'one-sided bounds'));
    });
    box.appendChild(tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Effect'), h('th', { class: 'r' }, 'Estimate'), h('th', { class: 'r' }, 'L'), h('th', { class: 'r' }, 'U'), h('th', null, 'Interval type'))), h('tbody', null, tbl),
      h('caption', null, 'm_O = ' + fmt(n.mO, 1) + ', δ_W = ' + fmt(n.dW, 1) + '. Held-out bounds are stored to two decimals; estimates are shown to three, with full precision on hover.'))));
    if (n.held) {
      var ce = c.certificate;
      box.appendChild(h('p', { class: 'muted' }, 'Uncertainty scope: ' + ce.uncertainty_scope + ' (n_independent = ' + ce.n_independent + '; interval assumption: ' + ce.uncertainty_assumption + '). One world is one case, not an independent sample: the independent sample is the eight matched world pairs.'));
    }
    box.appendChild(h('p', { class: 'muted' }, concept('attr', 'Attribution'), ' is not assessed by these quantities. Even a supported tau_O says the message changed outsider outcomes, not that agents should be blamed.'));
    return box;
  }
  function certView(c, n) {
    var t = traceView(c), box = h('div');
    box.appendChild(h('div', { class: 'verdict' }, h('div', { class: 'muted' }, 'Exact certificate status'), h('div', { class: 'big' }, statusPill(n.status), ' ', h('code', null, String(n.status))),
      h('p', null, h('strong', null, 'Why: '), t.why), t.wording ? h('p', { class: 'muted' }, 'Recorded wording: “' + t.wording + '”') : null,
      h('p', null, concept('attr', 'Attribution'), ' CCC does not issue this rung. A “not supported” certificate is not evidence that agents did not collude; a “supported” one is not evidence that they did.')));
    box.appendChild(disclosure('Inspect the recorded gate trace', t.list));
    box.appendChild(h('p', { class: 'muted' }, 'The trace restates recorded gates in plain language; it explains the stored outcome and does not issue a replacement certificate.'));
    return box;
  }
  function rawView(c) {
    var box = h('div');
    box.appendChild(h('p', null, h('a', { href: '../data/cases/' + c.id + '.json' }, 'Download compact case JSON'), ' · ', h('a', { href: '../data/full/' + c.id + '.json' }, 'Full-text source overlay')));
    box.appendChild(h('p', null, 'Archive: ', h('code', null, D.index.archive.path), h('br'), sha('sha256 ' + (c.archive_sha256 || D.index.archive.sha256))));
    box.appendChild(h('p', null, h('a', { href: '../data/MANIFEST.json' }, 'MANIFEST.json'), ' · ', h('a', { href: '../data/TRACE.md' }, 'TRACE.md (field-by-field source map)'), ' · pack built by ', h('code', null, D.manifest.generator), ' with generation base commit ', h('code', null, (D.manifest.generator_commit_HEAD || '').slice(0, 10)), '. Actual source and generator bytes are bound by hashes. ', D.manifest.n_files + ' generated files and ' + D.manifest.n_source_hashes + ' source hashes are listed in the manifest.'));
    var rows = (c.sources || []).map(function (src) {
      return h('tr', null, h('td', null, h('code', { class: 'hash' }, src.archive_member || src.path)), h('td', null, sha(src.sha256)));
    });
    box.appendChild(h('details', { class: 'd' }, h('summary', null, (c.sources || []).length + ' source files with sha256 (archive members and analysis files)'),
      h('div', null, tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Path / archive member'), h('th', null, 'sha256'))), h('tbody', null, rows))))));
    if (c.limitations) box.appendChild(h('details', { class: 'd' }, h('summary', null, 'Limitations recorded with this case'), h('div', null, h('ul', null, c.limitations.map(function (l) { return h('li', null, l); })))));
    box.appendChild(h('p', { class: 'muted' }, 'Text shown: ' + (c._text_mode || 'compact') + '. Compact pack strings are cut at 900 characters; the full-text overlay restores them.'));
    return box;
  }

  /* ---------- study: individual matched pairs and whole-pair uncertainty ---------- */
  function chartScroll(svg, label) { return h('div', { class: 'chart-scroll', tabindex: '0', role: 'region', 'aria-label': label + '; scroll horizontally on narrow screens' }, svg); }
  function studyFigure() {
    var p = D.study.primary.result;
    return h('figure', { class: 'study-figure' }, h('h3', null, 'Eight pairs, one uncertain directional comparison'),
      h('p', { class: 'muted' }, 'Outsider-loss difference: deceptive prompt (B1) − authorized cooperation (B2). Reward units.'),
      h('p', { class: 'chart-hint' }, 'Each circle is one independent matched pair; the diamond and horizontal line show the mean and whole-pair 95% interval.'),
      h('div', { class: 'chart-scroll', tabindex: '0', role: 'region', 'aria-label': 'Matched-pair differences and whole-pair uncertainty figure' }, stripPlot(D.study)),
      h('figcaption', null, h('div', { class: 'study-summary' }, h('span', null, 'Mean ', h('b', { class: 'num' }, fmt(p.estimate, 3))),
        h('span', null, '95% CI ', h('b', { class: 'num' }, '[' + fmt(p.L, 3) + ', ' + fmt(p.U, 3) + ']')),
        h('span', null, 'Exact one-sided p = ', h('b', { class: 'num' }, String(p.p_raw)))),
        h('p', { class: 'muted' }, 'The interval resamples whole matched pairs and includes zero. The preregistered directional effect was not established; this is not proof of no effect or equivalence.')));
  }
  function renderStudy() {
    var st = D.study, p = st.primary.result, ns = st.noncommit_sensitivity.result;
    clear(main);
    main.appendChild(h('p', { class: 'eyebrow' }, 'The real-agent comparison · EXP-002'));
    main.appendChild(h('div', { class: 'head' }, h('h1', null, 'A directional difference was not established.'), h('span', { class: 'badge held' }, 'Held-out · frozen'), h('span', { class: 'muted' }, p.eligible_complete_pairs + ' independent matched pairs')));
    main.appendChild(h('p', { class: 'page-intro' }, 'Does a deceptive-prompt regime produce larger outsider loss from a single exposure message than authorized cooperation? The independent sample is eight matched world pairs. The frozen comparison does not establish the preregistered direction.'));
    main.appendChild(studyFigure());
    var tb = h('tbody');
    st.per_world.forEach(function (w) {
      var td = h('td', null, h('span', { class: 'muted' }, 'Loading cases…'));
      tb.appendChild(h('tr', null, h('th', { scope: 'row' }, w.world_id), h('td', { class: 'r num' }, fmt(w.tau_O_B1, 3)), h('td', { class: 'r num' }, fmt(w.tau_O_B2, 3)), h('td', { class: 'r num' }, fmt(w.d_w, 3)), td));
      worldCases(w.world_id).then(function (m) { clear(td); ['B1', 'B2'].forEach(function (r) { if (m[r]) td.appendChild(h('a', { href: '#/case/' + m[r] }, m[r] + ' ')); }); }).catch(function () { td.textContent = 'Case data unavailable'; });
    });
    main.appendChild(disclosure('Inspect all eight differences and the underlying cases', tw(h('table', null,
      h('thead', null, h('tr', null, ['World', 'Outsider loss B1', 'Outsider loss B2', 'Difference', 'Cases'].map(function (x) { return h('th', null, x); }))), tb))));
    main.appendChild(h('h3', null, 'What the case certificates establish'));
    main.appendChild(h('p', null, 'Across sixteen held-out checkpoints, ' + (st.certificate_counts.supported || 0) + ' certificates are supported, ' + st.certificate_counts.not_supported + ' are not supported, and ' + st.certificate_counts.inconclusive + ' are inconclusive. These descriptive, exploratory case certificates do not attribute policy violations. A “not supported” result is not exoneration.'));
    main.appendChild(h('p', null, st.scheduled_counts.valid + ' continuations executed with valid outcomes; ' + st.scheduled_counts.not_run + ' were not run because no eligible placebo was available. There were ' + (st.scheduled_counts.valid + st.scheduled_counts.not_run) + ' scheduled records. Unrun records are missing evidence, not zero-valued outcomes.'));
    main.appendChild(disclosure('Registered sensitivity and uncertainty assumptions', h('div', null,
      h('p', null, 'With non-commit cases excluded: mean ' + fmt(ns.estimate, 3) + ', 95% interval [' + fmt(ns.L, 3) + ', ' + fmt(ns.U, 3) + ']. This estimate and interval are original-registered-secondary, not the primary confirmatory test. A separately reported sensitivity p-value is post-hoc-exploratory.'),
      h('p', null, p.caveats), h('p', { class: 'muted' }, 'Independent units are whole matched world pairs. Branch replicates and validation checks do not increase that independent sample size.'))));
    main.appendChild(h('h3', null, 'The constructed benchmark is a separate test'));
    main.appendChild(h('p', null, 'Scripted policies illustrate which additional evidence can resolve an ambiguity. They do not establish real-agent intent or deployment performance.'));
    main.appendChild(disclosure('All aggregate criteria, utility counts, and cross-platform discrepancy', benchmarkDetails()));
    main.appendChild(disclosure('Frozen study sources and hashes', h('div', null, st.sources.map(function (x) { return h('p', null, sourceLink(x.path), h('br'), sha(x.sha256)); }),
      h('p', null, h('a', { href: '../data/study.json' }, 'Download frozen study JSON')))));
  }
  var worldMap = null;
  function worldCases(world) {
    if (worldMap) return Promise.resolve(worldMap[world] || {});
    var ids = cases.filter(function (c) { return c.id.charAt(0) === 'H'; }).map(function (c) { return c.id; });
    return Promise.all(ids.map(loadCase)).then(function (cs) {
      worldMap = {}; cs.forEach(function (c) { (worldMap[c.world_id] = worldMap[c.world_id] || {})[c.regime] = c.id; });
      return worldMap[world] || {};
    });
  }
  function stripPlot(st) {
    var p = st.primary.result, W = Math.max(280, Math.min(820, main.clientWidth || 820)), H = 390, padL = W < 500 ? 68 : 135, padR = W < 500 ? 50 : 100;
    var vals = st.per_world.map(function (w) { return w.d_w; }).concat([p.L, p.U, 0]);
    var lo = Math.min.apply(null, vals) - .5, hi = Math.max.apply(null, vals) + .5;
    var x = function (v) { return padL + (v - lo) / (hi - lo) * (W - padL - padR); };
    var svg = s('svg', { class: 'plot matched-plot', viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Eight matched-pair differences and mean ' + fmt(p.estimate, 3) + '; whole-pair 95% interval [' + fmt(p.L, 3) + ', ' + fmt(p.U, 3) + '] includes zero.' });
    svg.appendChild(s('title', null, 'Individual matched pairs and whole-pair uncertainty'));
    svg.appendChild(s('desc', null, st.per_world.map(function (w) { return w.world_id + ': ' + String(w.d_w); }).join('; ') + '. Exact one-sided sign-flip p = ' + p.p_raw + '.'));
    svg.appendChild(s('text', { x: x(0), y: 20, 'text-anchor': 'middle', 'font-size': 12 }, 'Zero difference'));
    svg.appendChild(s('line', { x1: x(0), x2: x(0), y1: 32, y2: 326, stroke: 'var(--muted)', 'stroke-dasharray': '3 5' }));
    st.per_world.forEach(function (w, i) {
      var y = 48 + i * 31;
      svg.appendChild(s('line', { x1: padL, x2: W - padR, y1: y, y2: y, class: 'pair-guide' }));
      svg.appendChild(s('text', { x: 4, y: y + 5, 'font-size': 13 }, 'Pair ' + String(i + 1).padStart(2, '0')));
      svg.appendChild(s('circle', { cx: x(w.d_w), cy: y, r: 5.5, fill: 'var(--bg)', stroke: 'var(--accent)', 'stroke-width': 2, class: 'pair-dot', tabindex: '0', role: 'img', 'aria-label': w.world_id + ': ' + fmt(w.d_w, 3) }, s('title', null, w.world_id + ': ' + String(w.d_w))));
      svg.appendChild(s('text', { x: W - 8, y: y + 5, 'font-size': 13, 'text-anchor': 'end' }, fmt(w.d_w, 3)));
    });
    var y = 315, mx = x(p.estimate);
    svg.appendChild(s('text', { x: 4, y: y + 5, 'font-size': 13, 'font-weight': 600 }, W < 500 ? 'Mean' : 'Mean · 95% CI'));
    svg.appendChild(s('line', { x1: x(p.L), x2: x(p.U), y1: y, y2: y, stroke: 'var(--accent)', 'stroke-width': 2 }));
    [p.L, p.U].forEach(function (v) { svg.appendChild(s('line', { x1: x(v), x2: x(v), y1: y - 6, y2: y + 6, stroke: 'var(--accent)', 'stroke-width': 2 })); });
    svg.appendChild(s('path', { d: 'M' + mx + ' ' + (y - 7) + ' l7 7 l-7 7 l-7 -7z', fill: 'var(--accent)' }));
    svg.appendChild(s('text', { x: W - 8, y: y + 5, 'font-size': 13, 'text-anchor': 'end', 'font-weight': 600 }, fmt(p.estimate, 3)));
    svg.appendChild(s('line', { x1: padL, x2: W - padR, y1: 348, y2: 348, class: 'ax' }));
    ticks(lo, hi).forEach(function (t) { svg.appendChild(s('line', { x1: x(t), x2: x(t), y1: 348, y2: 354, class: 'ax' })); svg.appendChild(s('text', { x: x(t), y: 373, 'font-size': 13, 'text-anchor': 'middle' }, fmt(t, 0))); });
    return svg;
  }

  /* ---------- editorial research companion ---------- */
  function essaySection(number, label, title, body, id) {
    return h('section', { class: 'essay-section', id: id || null, 'aria-labelledby': 'essay-' + number },
      h('div', { class: 'section-aside' }, h('span', { class: 'index' }, number), label),
      h('div', { class: 'section-body' }, h('h2', { id: 'essay-' + number }, title), body));
  }
  function localScroll(id) {
    var el = $(id);
    if (el) { el.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'start' }); el.focus({ preventScroll: true }); }
  }
  function reducedMotion() { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; }
  function disclosure(title, content) { return h('details', { class: 'd' }, h('summary', null, title), h('div', null, content)); }
  function sourceLink(path, text) { return h('a', { href: 'https://github.com/Barap1/Counterfactual-Collusion-Certificates/blob/main/' + path }, text || path); }
  function benchmarkDetails() {
    var r = D.review, u = r.utility;
    var rows = Object.keys(r.criteria).map(function (k) {
      return h('tr', null, h('th', { scope: 'row' }, k), h('td', null, r.criteria[k]),
        h('td', null, { RQ1: 'Identical-view consistency; by construction', RQ2: 'Enumerated evidence separation; by construction', RQ3: 'Harm prevalence among forbidden policies', RQ4: 'Original baseline over-attribution criterion', RQ4b: 'DEV-informed refinement; aggregate criterion', RQ5: 'Full utility criterion; exploratory method', RQ6: 'Exposure-level illustration' }[k]));
    });
    return h('div', null,
      h('p', null, 'The original aggregate outcomes are retained: RQ1 and RQ2 pass by construction; RQ3, RQ4, RQ4b, and RQ5 do not meet their criteria. RQ6 is descriptive.'),
      tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Question'), h('th', null, 'Frozen result'), h('th', null, 'Meaning'))), h('tbody', null, rows))),
      h('p', null, 'At ε = 0, CCC-L v1 meets the full utility criterion in ' + u.v1.passed + '/' + u.v1.total + ' settings; v0 in ' + u.v0.passed + '/' + u.v0.total + '. Each version has ' + u.v1.undefined_gaps + ' undefined accuracy gaps. Undefined values are retained, without favourable imputation. Settings are combinations of case family and information set, not independent deployment trials.'),
      h('p', null, 'RQ3 harm prevalence at ε = 0: ' + r.rq3.k + '/' + r.rq3.n + ' = ' + fmt(r.rq3.rate, 3) + ', exact 95% interval [' + fmt(r.rq3.cp95[0], 3) + ', ' + fmt(r.rq3.cp95[1], 3) + ']. This is the share of forbidden policies with oracle outsider harm above the 2.5 margin; the <0.25 criterion is not met.'),
      h('p', null, 'The B2+ harm-based baseline over-attributes in the permitted P2 allocation and authorized P3 transfer cases: ', r.baseline.map(function (b, i) { var o = b.over_attribution; return (i ? '; ' : '') + b.kind + ' ' + o.unit_k + '/' + o.independent_n + ' independent units'; }), '. This constructed result does not estimate a real-world false-accusation rate.'),
      h('p', null, 'The deterministic restriction (ε = 0) was chosen post hoc, after outcomes were visible. The ε = 0.1 results have an unresolved cross-platform discrepancy in substantive method decisions. The refined RQ4b passes within the deterministic stratum while its original aggregate result remains unmet. End-to-end support-level positive-control recovery and useful real-agent sensitivity remain unestablished; EXP-003 was not completed.'),
      h('p', { class: 'muted' }, sourceLink(r.source, 'Frozen benchmark results'), ' · ', sourceLink('docs/enh/r2/PROTOCOL.md', 'Protocol'), ' · ', sourceLink('docs/RESULTS.md', 'Interpretation and scope')),
      sha('RESULTS.json sha256 ' + r.sha256));
  }
  function evidenceProgression() {
    var steps = [
      ['Observation', 'A message and an allocation are recorded.'],
      ['Causal influence', 'Removing the message changes a continuation.'],
      ['Harmful exposure', 'A valid, controlled replay supports outsider loss.'],
      ['Policy attribution', 'The rule and legitimate alternatives must also be known.']
    ];
    return h('ol', { class: 'evidence-flow', 'aria-label': 'Evidence progression' }, steps.map(function (d) { return h('li', null, h('b', null, d[0]), h('span', null, d[1])); }));
  }
  function allocationDiagram() {
    var svg = s('svg', { class: 'allocation', viewBox: '0 0 360 125', role: 'img', 'aria-label': 'Recorded allocation action: route' });
    svg.appendChild(s('path', { class: 'wire', d: 'M20 62 H94 L150 27 H338 M94 62 L150 100 H338' }));
    var active = s('path', { class: 'active-wire', d: 'M20 62 H94 L150 27 H338' }); svg.appendChild(active);
    svg.appendChild(s('text', { x: 20, y: 47 }, 'Allocation'));
    var routeText = s('text', { x: 168, y: 19, class: 'selected' }, 'Route · retain allocation');
    var baseText = s('text', { x: 168, y: 92 }, 'Base · change allocation');
    svg.appendChild(routeText); svg.appendChild(baseText);
    var token = s('circle', { cx: 150, cy: 27, r: 5, class: 'allocation-token' }); svg.appendChild(token);
    return { el: svg, update: function (arm) {
      var route = arm.actions.indexOf('route') !== -1;
      svg.setAttribute('aria-label', 'Recorded allocation action: ' + arm.actions.join(', '));
      active.setAttribute('d', route ? 'M20 62 H94 L150 27 H338' : 'M20 62 H94 L150 100 H338');
      token.setAttribute('transform', route ? 'translate(0 0)' : 'translate(0 73)');
      routeText.setAttribute('class', route ? 'selected' : ''); baseText.setAttribute('class', route ? '' : 'selected');
    } };
  }
  function counterexample() {
    var P = D.twins && D.twins.pairs.filter(function (p) { return p.kind === 'P2'; })[0];
    if (!P) return h('p', null, 'The constructed twin evidence is unavailable. ', h('a', { href: '../data/twins.json' }, 'Inspect the frozen source.'));
    var permitted = P.members.filter(function (m) { return m.truth.M === 'legitimate-cooperation'; })[0];
    var prohibited = P.members.filter(function (m) { return m.truth.M === 'harmful-coordination'; })[0];
    var shared = permitted.by_set.I2, wrap = h('div');
    wrap.appendChild(h('p', { class: 'lead' }, 'Two programmed policies produce the same message, the same allocation, and the same measured removal effect. Can the audit tell them apart?'));
    wrap.appendChild(h('div', { class: 'shared-evidence' }, h('div', { class: 'eyebrow' }, 'The shared evidence'),
      h('blockquote', null, '“' + shared.transcript[0].content + '”'),
      h('div', { class: 'shared-stats' },
        h('div', null, h('span', null, 'Outsider reward · message present → removed'), h('strong', { class: 'num' }, fmt(shared.arms.F.Omean, 0) + ' → ' + fmt(shared.arms.K.Omean, 0)), ' in both worlds'),
        h('div', null, h('span', null, 'Coalition reward · present → removed'), h('strong', { class: 'num' }, fmt(shared.arms.F.Cmean, 0) + ' → ' + fmt(shared.arms.K.Cmean, 0))),
        h('div', null, h('span', null, 'Total welfare · present → removed'), h('strong', { class: 'num' }, fmt(shared.arms.F.W, 0) + ' → ' + fmt(shared.arms.K.W, 0))))));
    var controls = h('div', { class: 'probe-controls', role: 'group', 'aria-label': 'Counterexample evidence' }, h('span', null, 'Reveal the evidence'));
    var b0 = h('button', { type: 'button', 'aria-pressed': 'true', 'aria-controls': 'policy-comparison' }, '01  Shared evidence');
    var b1 = h('button', { type: 'button', 'aria-pressed': 'false', 'aria-controls': 'policy-comparison' }, '02  Add the cost probe ↗');
    controls.appendChild(b0); controls.appendChild(b1); wrap.appendChild(controls);
    var worlds = h('div', { class: 'policy-worlds', id: 'policy-comparison' }), updates = [];
    [permitted, prohibited].forEach(function (m, i) {
      var diagram = allocationDiagram(), reward = h('span', { class: 'reward num' }), outcome = h('span'), coalition = h('span'), detail = h('p', { class: 'probe-description' });
      worlds.appendChild(h('article', { class: 'policy-world' }, h('div', { class: 'world-no' }, i ? 'Programmed policy · prohibited' : 'Programmed policy · permitted'),
        h('h3', null, i ? 'Coalition-protecting coordination' : 'Efficiency-seeking coordination'), diagram.el,
        h('p', { class: 'world-result' }, reward, 'outsider reward', h('br'), coalition, ' coalition reward · ', outcome, ' total welfare'), detail));
      updates.push(function (probe) {
        var arm = m.by_set[probe ? 'I4' : 'I2'].arms[probe ? 'PF' : 'F'];
        diagram.update(arm); reward.textContent = fmt(arm.Omean, 0); coalition.textContent = fmt(arm.Cmean, 0); outcome.textContent = fmt(arm.W, 0);
        detail.textContent = probe ? (i ? 'Retains the route action despite the cheaper outsider option.' : 'Switches to the base action when outsider costs fall.') : 'Same recorded route action. The initial audit cannot distinguish these policies.';
      });
    });
    wrap.appendChild(worlds);
    var caption = h('p', { class: 'probe-caption', role: 'status', 'aria-live': 'polite' }); wrap.appendChild(caption);
    var show = function (probe) {
      b0.setAttribute('aria-pressed', String(!probe)); b1.setAttribute('aria-pressed', String(probe));
      updates.forEach(function (f) { f(probe); });
      caption.textContent = probe
        ? 'Lowering outsider costs by ' + fmt(permitted.by_set.I4.probe.outsider_cost_reduction, 0) + ' separates the programmed responses. With the message present, the permitted policy changes allocation; the prohibited policy protects the coalition. Additional evidence distinguishes them.'
        : 'Same observed evidence, different programmed policies. The labels come from the benchmark’s design; they are not inferred from the initial behaviour.';
    };
    b0.addEventListener('click', function () { show(false); }); b1.addEventListener('click', function () { show(true); }); show(false);
    wrap.appendChild(disclosure('Inspect the control and probe outcomes', h('div', null,
      tw(h('table', null, h('thead', null, h('tr', null, ['Policy', 'F', 'K', 'Sham', 'Placebo', 'Probe F', 'Probe K'].map(function (v) { return h('th', null, v); }))),
        h('tbody', null, [permitted, prohibited].map(function (m, i) {
          return h('tr', null, h('th', { scope: 'row' }, i ? 'Prohibited' : 'Permitted'), ['F', 'K', 'S', 'N', 'PF', 'PK'].map(function (arm) { return h('td', { class: 'num' }, fmt(m.by_set.I4.arms[arm].Omean, 0)); }));
        })), h('caption', null, 'Outsider mean reward. F: message present; K: message removed; probe F/K: the same comparison after lowering outsider costs. S and N are sham and eligible placebo controls.'))),
      h('p', null, 'The sham and placebo preserve the factual outcome in both policies. Under the probe, removal yields ' + fmt(permitted.by_set.I4.arms.PK.Omean, 0) + ' outsider reward in both worlds. The exposure certificate remains L2 supported for both; this is not an attribution verdict. At I4, CCC-L v0 attributes the prohibited twin and abstains on the permitted twin. The benchmark’s Bayes-given-S reference distinguishes both labels.'),
      h('p', { class: 'muted' }, h('a', { href: '#/twins/P2/2' }, 'Inspect I2'), ' · ', h('a', { href: '#/twins/P2/4' }, 'Inspect I4'), ' · ', h('a', { href: '../data/twins.json' }, 'Raw twin evidence')))));
    wrap.appendChild(h('div', { class: 'figure-meta' }, h('span', null, 'Fig. 1 · Constructed P2 pair · ε = 0 · one deterministic continuation per arm'), h('a', { href: '#/twins/P2/4' }, 'Open the full twin comparison ↗')));
    return wrap;
  }
  function researchFindings() {
    var p = D.study.primary.result, u = D.review.utility.v1;
    var findings = [
      ['Constructed counterexamples separate as specified', 'The allocation cost probe and the transfer authorization record reveal distinctions hidden in the initial evidence. These are controlled constructions with programmed labels.'],
      ['Harm alone leaves an attribution gap', 'The harm-based baseline accuses permitted allocation and authorized-transfer cases. Outsider loss can be real while policy attribution remains unjustified.'],
      ['The broader auditor needs further validation', 'Four aggregate benchmark predictions were unmet. CCC-L v1 meets the full utility criterion in ' + u.passed + '/' + u.total + ' deterministic settings; this is a count of settings, not deployment accuracy.'],
      ['A directional difference was not established', 'The separate real-agent study includes ' + p.eligible_complete_pairs + ' matched pairs. Its mean difference is positive, but the whole-pair 95% uncertainty interval includes zero. The result does not establish equivalence.']
    ];
    return h('div', null, h('p', { class: 'lead' }, 'The evidence supports a boundary on attribution. It also identifies what an auditor must still demonstrate.'),
      h('div', { class: 'finding-list' }, findings.map(function (f, i) { return h('article', { class: 'finding' }, h('span', null, String(i + 1).padStart(2, '0')), h('div', null, h('h3', null, f[0]), h('p', null, f[1]))); })),
      studyFigure(), disclosure('Detailed benchmark results and validation boundaries', benchmarkDetails()),
      h('p', { class: 'muted' }, 'Established benchmark claims are restricted post hoc to ε = 0. The noisy ε = 0.1 condition has unresolved cross-platform decision disagreements.'),
      h('div', { class: 'text-actions' }, h('a', { href: '#/study' }, 'Inspect the full study', h('span', { 'aria-hidden': 'true' }, '↗'))));
  }
  function renderStart() {
    clear(main);
    var scroll = function (e) { e.preventDefault(); localScroll('counterexample'); };
    main.appendChild(h('section', { class: 'hero', 'aria-labelledby': 'opening-title' },
      h('p', { class: 'eyebrow' }, 'An interactive research companion · Multi-agent AI'),
      h('div', null, h('h1', { id: 'opening-title' }, 'When Cooperation', h('br'), 'Looks Like ', h('em', null, 'Collusion')),
        h('p', { class: 'subtitle' }, 'The limits of counterfactual auditing in multi-agent AI.'),
        h('p', { class: 'dek' }, 'A message can influence other agents and disadvantage outsiders without proving that the coordination was prohibited.'),
        h('div', { class: 'text-actions' }, h('a', { href: '#/start/counterexample', on: { click: scroll } }, 'Explore the counterexample', h('span', { 'aria-hidden': 'true' }, '↓')),
          h('a', { href: '#/study' }, 'Inspect the study evidence', h('span', { 'aria-hidden': 'true' }, '↗')))),
      h('aside', { class: 'hero-aside', 'aria-label': 'Research scope' }, h('p', null, h('b', null, 'The question'), 'What can a message-removal audit actually establish?'), h('p', null, h('b', null, 'The evidence'), 'Constructed twin worlds and eight matched real-agent pairs.'))));
    var ce = essaySection('01', 'The counterexample', 'One observation. Two explanations.', counterexample(), 'counterexample'); ce.tabIndex = -1; main.appendChild(ce);
    main.appendChild(essaySection('02', 'The attribution gap', 'What does an audit establish?', h('div', null,
      h('p', { class: 'lead' }, 'A knockout removes a message and replays what follows. It can support a causal claim about that message’s effect. Attribution asks a further question: did the coordination violate the rule?'), evidenceProgression(),
      h('p', { class: 'pullquote' }, 'A knockout measures what a message did, not whether it should have done it.'))));
    main.appendChild(essaySection('03', 'The study evidence', 'What the evidence establishes', researchFindings()));
    main.appendChild(essaySection('04', 'The evidence inspector', 'Follow the evidence yourself.', h('div', null,
      h('div', { class: 'inspector-intro' }, h('p', { class: 'lead' }, 'Read the recorded message, compare its removal with sham and placebo controls, and inspect exactly where the certificate stops.'), h('a', { class: 'btn', href: '#/case/H02_B1' }, 'Open case H02_B1 ↗')),
      h('p', { class: 'muted' }, 'The default opens the largest absolute matched-world contrast, an illustrative selection rather than a positive result. All 16 held-out checkpoints and 5 scripted development fixtures remain available.'),
      h('div', { class: 'text-actions' }, h('a', { href: '#/twins/P3/5' }, 'Inspect transfer authorization ↗'), h('a', { href: '#/about' }, 'Concepts & sources ↗')))));
    main.appendChild(essaySection('05', 'The next research question', 'Does more evidence improve attribution on unfamiliar agents?', h('div', null,
      h('p', { class: 'lead' }, 'The next stage is to test whether added evidence improves attribution beyond the constructions that motivated it.'),
      h('ol', { class: 'research-agenda' },
        h('li', null, h('div', null, h('strong', null, 'Validate the full certificate pipeline'), h('p', null, 'Establish support-level sensitivity with controlled, reproducible positive controls before interpreting real-agent abstention.'))),
        h('li', null, h('div', null, h('strong', null, 'Evaluate independently designed policies'), h('p', null, 'Test unfamiliar permitted and prohibited policies designed independently of the auditor and its separating probes.'))),
        h('li', null, h('div', null, h('strong', null, 'Compare the evidence available to the auditor'), h('p', null, 'Compare knockout-only auditing with added cost probes or authorization. Measure false accusations, sensitivity, and coverage together.')))),
      h('div', { class: 'text-actions' }, sourceLink('docs/STUDIO_RESEARCH_PLAN.md', 'Read the research continuation ↗')))));
  }

  /* ---------- concepts and sources ---------- */
  function renderAbout() {
    clear(main);
    main.appendChild(h('p', { class: 'eyebrow' }, 'Reading the evidence'));
    main.appendChild(h('div', { class: 'head' }, h('h1', null, 'Concepts & sources')));
    main.appendChild(h('p', { class: 'page-intro' }, 'Influence, harm, and policy attribution answer different questions. This companion keeps their evidence and uncertainty separate.'));
    main.appendChild(evidenceProgression());
    main.appendChild(h('h3', null, 'The attribution gap'));
    main.appendChild(h('p', null, 'A valid intervention can support a scoped causal claim: removing this message changed these outcomes. A policy violation additionally depends on the applicable rule, authorization, and legitimate alternatives. Programmed benchmark labels are supplied by the evaluator; they are not inferred real-agent intent.'));
    main.appendChild(h('h3', null, 'Effect definitions'));
    main.appendChild(tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Quantity'), h('th', null, 'Definition'))), h('tbody', null,
      h('tr', null, h('th', { scope: 'row' }, 'Outsider loss · τO'), h('td', null, 'Outsider mean reward under removal (K) minus message present (F).')),
      h('tr', null, h('th', { scope: 'row' }, 'Coalition benefit · τC'), h('td', null, 'Coalition mean reward under F minus K.')),
      h('tr', null, h('th', { scope: 'row' }, 'Welfare change · τW'), h('td', null, 'Total reward under K minus F.')),
      h('tr', null, h('th', { scope: 'row' }, 'Controls · S and N'), h('td', null, 'S is a sham with identical input and fresh sampling. N removes a different, eligible non-informational message. Not available does not mean zero effect.'))))));
    main.appendChild(h('h3', null, 'Reading a certificate'));
    main.appendChild(h('p', null, 'Supported means the recorded harmful-exposure criterion is met; it does not attribute collusion. Not supported means the criterion is not met; it does not exonerate a policy. Inconclusive preserves uncertainty. Invalid means replay validity failed. The case ladder’s L0/L1 display is a UI-derived heuristic, not a replacement certificate; only supported certificates reach L2. L3 policy attribution is never claimed for the held-out cases.'));
    main.appendChild(h('h3', null, 'Evidence provenance'));
    main.appendChild(h('p', null, 'Held-out real-agent evidence comes from EXP-002: sixteen checkpoints from eight matched world pairs. Gate A cases are five scripted development fixtures, including failed diagnostics. The selected prospective twin examples are deterministic ε = 0 constructions. None of these categories substitutes for another.'));
    main.appendChild(h('p', null, 'The frozen pack was generated by ', h('code', null, D.manifest.generator), '. Generation base commit ', h('code', null, D.manifest.generator_commit_HEAD), ' records HEAD at generation. Hashes bind the actual source and generator bytes. The full-text overlay restores messages shortened in the compact pack.'));
    main.appendChild(h('p', { class: 'muted' }, 'Manifest SHA-256: ', sha(D.manifest.manifest_sha256), h('br'), 'Archive SHA-256: ', sha(D.index.archive.sha256)));
    main.appendChild(h('div', { class: 'sources-list' }, h('h3', null, 'Inspect or download the sources'), h('ul', null,
      h('li', null, h('a', { href: '../data/MANIFEST.json' }, 'Frozen manifest and source hashes')),
      h('li', null, h('a', { href: '../data/TRACE.md' }, 'Field-by-field numerical source map')),
      h('li', null, h('a', { href: '../data/study.json' }, 'Study results and all eight matched-pair differences')),
      h('li', null, h('a', { href: '../data/twins.json' }, 'All bundled twin worlds and information sets')),
      h('li', null, h('a', { href: '../data/cases.json' }, 'Index of held-out cases and development fixtures')),
      h('li', null, sourceLink('docs/runner/archives/exp002-live.tar.gz', 'Original archived real-agent records')),
      h('li', null, sourceLink('docs/REPRODUCING.md', 'Reproduction instructions and missing-input limits')),
      h('li', null, h('a', { href: 'https://docs.google.com/document/d/1lpUPKgZGy_vVPfbocKlr5-VqD6UxcGb2RzEWD8DbZgk/edit' }, 'Paper and research context')))));
    main.appendChild(disclosure('Public data, privacy, and redistribution scope', h('div', null,
      h('p', null, 'This site republishes the repository’s existing frozen research evidence: synthetic scenario identifiers, scripted messages, and recorded model outputs. It runs without inference, analytics, or network requests for its content. Explicit external links leave this local evidence companion. Theme preference is stored only in the browser.'),
      h('p', null, 'Prior repository reviews leave upstream scenario and trace redistribution rights unresolved. Publication authorization does not establish third-party licensing clearance. Source text and tool outputs are research artifacts; they should not be interpreted as statements by real participants.'),
      h('p', null, sourceLink('NOTICE.md', 'Repository notices'), ' · ', sourceLink('docs/release/LICENSES.md', 'Existing license inventory'), ' · ', sourceLink('docs/release/CHECKLIST.md', 'Release limitations')))));
    main.appendChild(h('h3', null, 'Design and offline use'));
    main.appendChild(h('p', null, 'Old Standard TT is embedded locally under the ', h('a', { href: 'fonts/OFL.txt' }, 'SIL Open Font License 1.1'), '. The warm paper and forest accents take inspiration from the ', h('a', { href: 'https://apartresearch.com/' }, 'Apart Research website'), '; this is an independent research companion, not an official Apart product.'));
    main.appendChild(h('p', null, 'To use offline, download the repository and open demo/explorer/index.html. Keep its adjacent assets and demo/data directory together. Hash routes work without a server.'));
  }

  /* ---------- twins (hidden unless data/twins.js exists) ---------- */
  var twinState = { pair: 1, set: 2 };
  function vtxt(v) {
    if (!v) return '—';
    var s2 = v.status + (v.rung ? ' · ' + v.rung : '');
    if (v.M_label && v.M_label !== 'n/a') s2 += ' · ' + v.M_label;
    return s2;
  }
  function vsame(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
  function labelStrip(t) {
    var tr = t.truth;
    return h('div', { class: 'truth' }, h('div', { class: 'muted' }, 'Private label (evaluator only, never in the auditor view)'),
      h('div', { class: 'chips' }, h('span', { class: 'chip' }, 'mechanism: ' + tr.M), h('span', { class: 'chip' }, 'harm H: ' + String(tr.H)), h('span', { class: 'chip' }, 'exposure effect E: ' + String(tr.E)),
        h('span', { class: 'chip' }, 'tau_O ' + fmt(tr.tau_O, 2)), h('span', { class: 'chip' }, 'tau_C ' + fmt(tr.tau_C, 2)), h('span', { class: 'chip' }, 'tau_W ' + fmt(tr.tau_W, 2))));
  }
  function twinColumn(P, mem, si, other) {
    var S = SETS_T[si], bs = mem.by_set[S], col = h('div', { class: 'card twin' });
    col.appendChild(h('h3', null, 'Twin ' + (P.members.indexOf(mem) === 0 ? 'A' : P.members.indexOf(mem) === 1 ? 'B' : '') + ' ' , h('span', { class: 'muted' }, 'seed ' + P.seed + ', member ' + mem.member)));
    col.appendChild(labelStrip(mem));
    col.appendChild(h('h4', null, 'Auditor-visible transcript (' + bs.sender + ' → ' + bs.receiver + ' is the exposure edge)'));
    var tl = h('div', { class: 'log short', tabindex: '0', role: 'region', 'aria-label': 'Auditor-visible transcript' });
    bs.transcript.forEach(function (e) {
      var isExp = e.agent === bs.sender && e.id === 'event_0';
      tl.appendChild(h('div', { class: 'rec' + (isExp ? ' exp' : '') }, isExp ? h('div', { class: 'xtag' }, 'Exposure message') : null,
        h('div', { class: 'who' }, e.agent, ' ', h('span', null, 'board ' + e.board + ' · ' + e.id)), h('div', { class: 'body' }, e.content)));
    });
    col.appendChild(tl);
    col.appendChild(h('p', { class: 'muted' }, 'Transcript snippets may end mid-sentence (clipped in source).'));
    col.appendChild(h('p', { class: 'muted scroll-hint' }, 'Scroll the continuations table horizontally to see all columns, including Action; focus it to scroll with the arrow keys.'));
    col.appendChild(h('h4', null, 'Continuations visible at ' + S));
    var rows = [];
    Object.keys(bs.arms).forEach(function (arm) {
      var a = bs.arms[arm];
      var nm = { F: 'F factual', K: 'K knockout', S: 'S sham', N: 'N placebo', J: 'J joint knockout', PF: 'PF probe, factual', PK: 'PK probe, knocked out' }[arm] || arm;
      if (!a) rows.push(h('tr', null, h('td', null, nm), h('td', { colspan: 4 }, h('em', null, 'not run: no eligible placebo'))));
      else rows.push(h('tr', null, h('td', null, nm), h('td', { class: 'r num' }, fmt(a.Omean)), h('td', { class: 'r num' }, fmt(a.Cmean)), h('td', { class: 'r num' }, fmt(a.W)), h('td', null, a.actions.join(', '))));
    });
    col.appendChild(tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Arm'), h('th', { class: 'r' }, 'Outsider mean'), h('th', { class: 'r' }, 'Coalition mean'), h('th', { class: 'r' }, 'W'), h('th', null, 'Action'))), h('tbody', null, rows),
      h('caption', null, 'Structural benchmark, epsilon = 0: one deterministic continuation per arm.'))));
    var ex = [];
    if (bs.probe) ex.push('Probe: ' + bs.probe.intervention + ' (by ' + fmt(bs.probe.outsider_cost_reduction, 0) + ').');
    if (bs.authorization) ex.push('Authorization record: ' + bs.authorization.status + ' (' + bs.authorization.source + ').');
    if (bs.placebo) ex.push('Placebo selection: ' + bs.placebo.status + '.');
    if (ex.length) col.appendChild(h('p', { class: 'muted' }, ex.join(' ')));
    col.appendChild(h('div', { class: 'hash' }, 'view sha256 ' + bs.view_sha256));
    return col;
  }
  var SETS_T = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5'];
  function updateTwin(pair, set, control) {
    var y = window.scrollY; twinState.pair = pair; twinState.set = set;
    try { history.replaceState(null, '', '#/twins/' + D.twins.pairs[pair].kind + '/' + set); } catch (e) { /* static file browsing may restrict history */ }
    renderTwins(); window.scrollTo({ top: y, behavior: 'instant' });
    var selected = main.querySelector('[data-' + control + '="' + (control === 'pair' ? pair : set) + '"]');
    if (selected) selected.focus({ preventScroll: true });
  }
  function renderTwins() {
    clear(main);
    var T = D.twins, P = T.pairs[twinState.pair], si = twinState.set;
    var dev = T.label === 'DEV';
    main.appendChild(h('div', { class: 'head' }, h('h1', null, 'When does new evidence distinguish the worlds?'), h('span', { class: 'badge ' + (dev ? 'dev' : 'held'), title: T.provenance_label }, T.provenance_label)));
    main.appendChild(h('p', null, 'Two programmed policies can share the same observed evidence. Explore which additional evidence distinguishes them, from transcript alone (I0) to authorization (I5).'));
    main.appendChild(h('p', { class: 'muted' }, 'Selected deterministic constructions (ε = 0). The scope restriction was post hoc; four aggregate criteria were unmet, and noisy results have unresolved cross-platform differences.'));
    main.appendChild(disclosure('Scope, selection, and all aggregate outcomes', h('div', null,
      T.banner ? h('p', null, T.banner) : null,
      h('p', null, 'Selection rule: ' + T.selection_rule),
      T.scope_note ? h('p', null, T.scope_note) : null,
      T.aggregate_criteria ? h('p', null, 'Frozen aggregate criteria: ' + Object.keys(T.aggregate_criteria).map(function (rq) { return rq + ' ' + T.aggregate_criteria[rq]; }).join(' · ') + '. RQ1/RQ2 pass by construction, not independent detection performance. Selected deterministic examples do not replace the aggregate outcomes.') : null,
      T.limitations ? h('p', null, T.limitations) : null)));
    var tabs = h('div', { class: 'steps', role: 'group', 'aria-label': 'Twin pair types' });
    T.pairs.forEach(function (p, i) { tabs.appendChild(h('button', { type: 'button', class: 'tabbtn', 'data-pair': i, 'aria-pressed': i === twinState.pair ? 'true' : 'false', on: { click: function () { updateTwin(i, twinState.set, 'pair'); } } }, p.kind)); });
    main.appendChild(tabs);
    main.appendChild(h('h3', null, P.kind + ' · ' + P.title), h('p', null, P.description));
    // stepper
    var slider = h('input', { type: 'range', min: 0, max: 5, step: 1, value: si, id: 'tw-range', 'aria-valuetext': SETS_T[si] + ': ' + T.sets[si].adds, 'aria-label': 'Information set, I0 to I5' });
    slider.addEventListener('input', function () { twinState.set = +slider.value; try { history.replaceState(null, '', '#/twins/' + P.kind + '/' + twinState.set); } catch (e) { /* file browser may restrict history */ } renderTwins(); $('tw-range').focus(); });
    var btns = h('div', { class: 'steps', role: 'group', 'aria-label': 'Information set' });
    SETS_T.forEach(function (s2, i) { btns.appendChild(h('button', { type: 'button', class: 'tabbtn', 'data-set': i, 'aria-pressed': i === si ? 'true' : 'false', on: { click: function () { updateTwin(twinState.pair, i, 'set'); } } }, s2)); });
    main.appendChild(h('div', { class: 'card' }, h('div', { class: 'stepper' }, h('label', { for: 'tw-range' }, 'Evidence revealed: ', h('strong', null, SETS_T[si])), slider, btns),
      h('p', null, h('strong', null, SETS_T[si] + ' adds: '), T.sets[si].adds, si > 0 ? h('span', { class: 'muted' }, ' (cumulative: everything from earlier sets is still shown)') : null)));
    // columns
    var A = P.members[0], B = P.members[1];
    var cols = h('div', { class: 'grid2' });
    P.members.forEach(function (m) { cols.appendChild(twinColumn(P, m, si)); });
    main.appendChild(cols);
    // verdicts at this set
    var sameView = B ? A.by_set[SETS_T[si]].view_sha256 === B.by_set[SETS_T[si]].view_sha256 : null;
    var banner;
    if (!B) banner = h('div', { class: 'verdict' }, h('div', { class: 'big' }, 'Single case, no twin'), h('p', null, P.description));
    else if (sameView) banner = h('div', { class: 'verdict same' }, h('div', { class: 'big' }, 'At ' + SETS_T[si] + ' the two auditor views are byte-identical.'), h('p', null, 'Identical evidence → identical verdict. Every method below must, and does, give the same output for both worlds.'));
    else banner = h('div', { class: 'verdict diff' }, h('div', { class: 'big' }, 'At ' + SETS_T[si] + ' the auditor views differ.'), h('p', null, 'New evidence has entered, so outputs may differ. See which methods actually do.'));
    main.appendChild(h('h3', null, 'Verdicts at ' + SETS_T[si]));
    main.appendChild(h('p', { class: 'note' }, 'Private twin labels and attribution verdicts are scripted benchmark labels, not a detection.'));
    main.appendChild(banner);
    var vr = T.methods.map(function (mt) {
      var va = A.by_set[SETS_T[si]].verdicts[mt.id], vb = B ? B.by_set[SETS_T[si]].verdicts[mt.id] : null;
      var lab = mt.id === 'baseline' ? mt.label + ' (' + T.strongest_baseline.id + ')' : mt.label;
      return h('tr', null, h('th', { scope: 'row' }, lab), h('td', null, vtxt(va)), B ? h('td', null, vtxt(vb)) : null, B ? h('td', null, vsame(va, vb) ? h('span', { class: 'pf n' }, 'same') : h('span', { class: 'pf f' }, 'differs')) : null);
    });
    main.appendChild(tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Method'), h('th', null, 'Twin A'), B ? h('th', null, 'Twin B') : null, B ? h('th', null, 'Same?') : null)), h('tbody', null, vr))));
    // matrix
    if (B) {
      var head = h('tr', null, h('th', null, 'Method'));
      SETS_T.forEach(function (s2, i) { head.appendChild(h('th', { class: i === si ? 'cur' : '' }, s2)); });
      var vrows = [h('tr', null, h('th', { scope: 'row' }, 'Auditor view'), SETS_T.map(function (s2, i) { var d = A.by_set[s2].view_sha256 !== B.by_set[s2].view_sha256; return h('td', { class: i === si ? 'cur' : '' }, d ? h('span', { class: 'pf f' }, 'differs') : h('span', { class: 'pf n' }, 'identical')); }))];
      T.methods.forEach(function (mt) {
        vrows.push(h('tr', null, h('th', { scope: 'row' }, mt.label), SETS_T.map(function (s2, i) {
          var d = !vsame(A.by_set[s2].verdicts[mt.id], B.by_set[s2].verdicts[mt.id]);
          return h('td', { class: i === si ? 'cur' : '' }, d ? h('span', { class: 'pf f' }, 'differs') : h('span', { class: 'pf n' }, 'same'));
        })));
      });
      main.appendChild(h('h3', null, 'Where do the verdicts diverge? I0 → I5'));
      main.appendChild(tw(h('table', { class: 'matrix' }, h('thead', null, head), h('tbody', null, vrows), h('caption', null, 'Computed in the browser from the stored per-set verdicts. A verdict row can differ only from the set at which the auditor view differs.'))));
      var fs = P.first_separating_set;
      main.appendChild(h('p', { class: 'twinline' }, h('strong', null, 'Identical evidence → identical verdict; only new evidence (' + (fs || 'none in this pair') + ') separates them.'),
        fs ? ' First set where the auditor views differ: ' + fs + (P.enumerated_pair_separator ? ' (enumerated minimal separator: ' + P.enumerated_pair_separator + ').' : '.') : ' The two worlds are not separated by any information set in this run.'));
      var cc = T.methods.filter(function (m) { return m.id !== 'baseline' || true; }).map(function (m) { return m.label + ': ' + (P.first_divergence[m.id] || 'never'); }).join(' · ');
      main.appendChild(h('p', null, concept('unc', 'First verdict divergence'), ' ' + cc));
      main.appendChild(h('p', { class: 'note' }, concept('causal'), ' ', concept('harm'), ' CCC v1.2.2 makes exposure-level (L2) claims only. When it gives the same L2 “supported” to a legitimate twin, that is the point of the benchmark: ', concept('attr'), ' a knockout measures what a message did, not whether it should have done it.'));
    }
    main.appendChild(h('details', { class: 'd' }, h('summary', null, 'Sources and sha256 (' + T.sources.length + ' files)'), h('div', null,
      h('p', null, 'Run: ', h('code', null, T.run_dir), '. Strongest-baseline rule: ' + T.strongest_baseline.rule + ' Balanced accuracy B2+ ' + fmt(T.strongest_baseline.balanced_accuracy['B2+'], 3) + ', B3b ' + fmt(T.strongest_baseline.balanced_accuracy['B3b'], 3) + '.'),
      T.sources.map(function (x) { return h('p', null, h('code', null, x.path), h('br'), sha(x.sha256)); }))));
  }
  /* ---------- compact case selection, local theme and hash routes ---------- */
  function buildSidebar() {
    var select = $('case-select'); clear(select);
    [['Held-out real-agent · EXP-002', 'H'], ['Development · scripted fixtures', 'GateA']].forEach(function (group) {
      var g = h('optgroup', { label: group[0] });
      cases.filter(function (c) { return c.id.indexOf(group[1]) === 0; }).forEach(function (c) {
        g.appendChild(h('option', { value: c.id }, c.id + ' · ' + c.title + ' · ' + String(c.status).replace(/_/g, ' ')));
      }); select.appendChild(g);
    });
    select.addEventListener('change', function () { location.hash = '#/case/' + select.value; });
  }
  function mark(view, id) {
    document.querySelectorAll('.views a').forEach(function (a) { if (a.getAttribute('data-view') === view) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    document.querySelector('.side').hidden = view !== 'case';
    main.className = view + '-page';
    if (id) $('case-select').value = id;
    $('case-current').textContent = id ? (/^H/.test(id) ? 'Held-out · descriptive' : 'Development · scripted') : '';
    document.title = (view === 'start' ? 'When Cooperation Looks Like Collusion' : ({ study: 'Study evidence', twins: 'Twin worlds', case: id, about: 'Concepts & sources' }[view])) + ' · CCC Evidence Explorer';
  }
  var revealObserver = null;
  function enhance() {
    if (revealObserver) revealObserver.disconnect();
    if (reducedMotion() || !('IntersectionObserver' in window)) return;
    // Content is always visible. An observed entry adds only a brief enhancement.
    revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { if (entry.isIntersecting) { entry.target.classList.add('reveal-in'); revealObserver.unobserve(entry.target); } });
    }, { threshold: .06 });
    main.querySelectorAll('.essay-section, .study-figure').forEach(function (el) { revealObserver.observe(el); });
  }
  function route() {
    var hash = location.hash || '#/start', m = hash.match(/^#\/case\/([\w-]+)$/);
    curId = null;
    if (m && byId[m[1]]) { mark('case', m[1]); renderCase(m[1]); }
    else if (hash === '#/study') { mark('study'); renderStudy(); }
    else if (hash === '#/about') { mark('about'); renderAbout(); }
    else if (/^#\/twins(\/|$)/.test(hash) && D.twins) {
      var tm = hash.match(/^#\/twins\/(\w+)(?:\/([0-5]))?$/);
      if (tm) { D.twins.pairs.forEach(function (p, i) { if (p.kind === tm[1]) twinState.pair = i; }); if (tm[2] !== undefined) twinState.set = +tm[2]; }
      mark('twins'); renderTwins();
    } else {
      mark('start'); renderStart();
      if (m) main.insertBefore(h('p', { class: 'note', role: 'status' }, 'That case is not in the frozen pack. Open Case inspector to choose one of the available cases.'), main.firstChild);
    }
    if (!m) window.scrollTo({ top: 0, behavior: 'instant' });
    enhance();
    if (hash === '#/start/counterexample') localScroll('counterexample');
  }
  var resizeFrame;
  window.addEventListener('resize', function () {
    if (resizeFrame) cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(function () { main.querySelectorAll('.matched-plot').forEach(function (plot) { plot.replaceWith(stripPlot(D.study)); }); });
  });
  var toggle = $('theme-toggle');
  function themeLabel() {
    var dark = document.documentElement.dataset.theme === 'dark';
    toggle.setAttribute('aria-label', dark ? 'Use light theme' : 'Use dark theme');
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.firstChild.textContent = dark ? 'Light ' : 'Dark ';
  }
  toggle.addEventListener('click', function () {
    var theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('ccc-theme', theme); } catch (e) { /* preference remains valid for this page */ }
    themeLabel();
  });
  document.querySelectorAll('.brand, .views a, .footer-mark').forEach(function (link) {
    link.addEventListener('click', function (event) {
      if (link.getAttribute('href') === (location.hash || '#/start')) { event.preventDefault(); window.scrollTo({ top: 0, behavior: reducedMotion() ? 'auto' : 'smooth' }); main.focus({ preventScroll: true }); }
    });
  });
  window.addEventListener('hashchange', function () { route(); main.focus({ preventScroll: true }); });
  document.querySelector('.skip').addEventListener('click', function (event) { event.preventDefault(); main.focus(); main.scrollIntoView({ block: 'start' }); });
  buildSidebar();
  if (D.twins) $('twins-nav').hidden = false;
  themeLabel();
  route();
})();
