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
      svg.appendChild(s('text', { x: 8, y: y + 12, 'font-size': 12, class: 'muted', fill: 'var(--muted)' }, r.sub));
      svg.appendChild(s('line', { x1: padL, x2: W - padR, y1: y + 14, y2: y + 14, class: 'ax' }));
      ticks(lo, hi).forEach(function (tv) {
        svg.appendChild(s('line', { x1: x(tv), x2: x(tv), y1: y + 14, y2: y + 19, class: 'ax' }));
        svg.appendChild(s('text', { x: x(tv), y: y + 31, 'font-size': 11, 'text-anchor': 'middle', fill: 'var(--muted)' }, fmt(tv, Math.abs(tv) < 1 && tv !== 0 ? 2 : (tv % 1 ? 1 : 0))));
      });
      svg.appendChild(s('line', { x1: x(0), x2: x(0), y1: y - 22, y2: y + 14, class: 'gl', 'stroke-dasharray': '2 3' }));
      if (r.ref !== 0) {
        svg.appendChild(s('line', { x1: x(r.ref), x2: x(r.ref), y1: y - 26, y2: y + 14, stroke: 'var(--ink)', 'stroke-width': 2, 'stroke-dasharray': '6 3' }));
        svg.appendChild(s('text', { x: x(r.ref), y: y - 30, 'font-size': 11, 'font-weight': 700, 'text-anchor': 'middle' }, r.refLabel));
      }
      if (t.L !== null && t.U !== null && !t.exact) {
        svg.appendChild(s('rect', { x: x(t.L), y: y - 6, width: Math.max(2, x(t.U) - x(t.L)), height: 14, fill: r.col, opacity: 0.28 }));
        svg.appendChild(s('line', { x1: x(t.L), x2: x(t.L), y1: y - 10, y2: y + 12, stroke: r.col, 'stroke-width': 3 }));
        svg.appendChild(s('line', { x1: x(t.U), x2: x(t.U), y1: y - 10, y2: y + 12, stroke: r.col, 'stroke-width': 3 }));
        svg.appendChild(s('text', { x: x(t.L), y: y - 13, 'font-size': 11, 'text-anchor': 'middle', fill: r.col }, 'L ' + fmt(t.L)));
        svg.appendChild(s('text', { x: x(t.U), y: y - 13, 'font-size': 11, 'text-anchor': 'middle', fill: r.col }, 'U ' + fmt(t.U)));
      }
      if (t.est !== null) {
        var px = x(t.est);
        if (t.exact) svg.appendChild(s('path', { d: 'M' + px + ' ' + (y - 9) + ' l8 8 l-8 8 l-8 -8z', fill: r.col }));
        else svg.appendChild(s('circle', { cx: px, cy: y + 1, r: 5.5, fill: 'var(--bg)', stroke: r.col, 'stroke-width': 3 }));
      } else {
        svg.appendChild(s('text', { x: padL, y: y + 1, 'font-size': 12, fill: 'var(--muted)' }, 'no estimate in this certificate'));
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
        svg.appendChild(s('text', { x: x0 - 8, y: y + 13, 'font-size': 12, 'text-anchor': 'end' }, a + ' ' + ARM_NAME[a]));
        svg.appendChild(s('rect', { x: bw >= 0 ? zx : zx + bw, y: y, width: Math.abs(bw), height: 15, fill: colors[a], opacity: a === 'F' ? 0.85 : 0.8 }));
        svg.appendChild(s('text', { x: (bw >= 0 ? zx + bw : zx) + (bw >= 0 ? 6 : -6), y: y + 12, 'font-size': 12, 'text-anchor': bw >= 0 ? 'start' : 'end', class: 'num' }, fmt(summ[a][m[0]])));
      });
    });
    return h('div', { class: 'card bars' }, h('h3', null, 'Outcomes by arm'), svg, h('p', { class: 'muted' }, 'Bars show means over the valid replicates listed above (stored per-replicate values).'));
  }

  /* ---------- case page ---------- */
  function sectionNav(ids) {
    var nav = h('nav', { class: 'sect-nav', 'aria-label': 'Sections of this case' });
    ids.forEach(function (x) {
      nav.appendChild(h('a', { href: '#/case/' + curId, on: { click: function (e) { e.preventDefault(); var t = $(x[0]); if (t) { t.scrollIntoView({ behavior: 'smooth', block: 'start' }); t.focus({ preventScroll: true }); } } } }, x[1]));
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
      main.appendChild(h('div', { class: 'head' }, h('h2', { id: 'top-h' }, c.title), provBadge(c), statusPill(c.certificate.status)));
      main.appendChild(h('p', { class: 'muted' }, held
        ? 'EXP-002 world ' + c.world_id + ' · regime ' + c.regime + (c.regime === 'B1' ? ' (deceptive prompt)' : ' (authorized-cooperation prompt)') + ' · checkpoint turn ' + c.checkpoint_turn + ' · evidence category: ' + c.evidence_category
        : 'Scripted fixture ' + c.family + ' (seed ' + c.seed + ', stratum ' + c.stratum + ') · ' + c.selection_rule + ' · evidence category: ' + c.evidence_category));
      if (!held) main.appendChild(h('p', { class: 'note warn' }, (c.limitations || []).join(' ')));
      else main.appendChild(h('p', { class: 'note' }, 'Held-out data are descriptive here. The preregistered confirmatory result is a null (see Study). Case certificates are Tier-B exploratory.'));
      main.appendChild(sectionNav([['s-ladder', 'Ladder'], ['s-inter', 'Interaction'], ['s-cmp', 'F vs K'], ['s-chg', 'What changed'], ['s-val', 'Validity'], ['s-cert', 'Certificate'], ['s-raw', 'Raw evidence']]));
      main.appendChild(sec('s-ladder', 'Evidence ladder', ['causal', 'harm', 'attr'], ladderStrip(c)));
      main.appendChild(sec('s-inter', 'Interaction up to the checkpoint', ['causal'], interactionView(c)));
      main.appendChild(sec('s-cmp', 'Factual vs knockout continuations', ['causal'], compareView(c)));
      main.appendChild(sec('s-chg', 'What changed', ['causal', 'harm', 'unc'], changeView(c, n)));
      main.appendChild(sec('s-val', 'Validity checks', [], validityView(c)));
      main.appendChild(sec('s-cert', 'Certificate and gate trace', ['harm', 'attr'], certView(c, n)));
      main.appendChild(sec('s-raw', 'Raw evidence', [], rawView(c)));
      window.scrollTo(0, 0);
      var hd = $('top-h'); if (hd) { hd.setAttribute('tabindex', '-1'); }
    }).catch(function (e) { clear(main); main.appendChild(h('p', { class: 'note warn' }, String(e.message))); });
  }
  function interactionView(c) {
    var ex = c.exposure, box = h('div');
    if (c.regime !== undefined) {
      box.appendChild(h('div', { class: 'expcard' }, h('div', { class: 'route' }, 'Exposure: ' + ex.sender + ' → ' + ex.receiver),
        h('div', { class: 'muted' }, 'private channel [' + (ex.channel_participants || []).join(', ') + '], posted turn ' + ex.posted_turn + ', first seen turn ' + ex.first_exposure_turn + ', knockout mask from turn ' + ex.mask_start + ' (' + ex.mask_version + ')'),
        h('blockquote', null, ex.content)));
      box.appendChild(logView(c.original_interaction || [], ex, c.checkpoint_turn));
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
    box.appendChild(h('div', { class: 'card' }, intervalPlot(n)));
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
    box.appendChild(h('h3', null, 'Gate trace'));
    box.appendChild(t.list);
    box.appendChild(h('p', { class: 'muted' }, 'The trace restates recorded gates in plain language; it explains the stored outcome and does not issue a replacement certificate.'));
    return box;
  }
  function rawView(c) {
    var box = h('div');
    box.appendChild(h('p', null, 'Archive: ', h('code', null, D.index.archive.path), h('br'), sha('sha256 ' + (c.archive_sha256 || D.index.archive.sha256))));
    box.appendChild(h('p', null, h('a', { href: '../data/MANIFEST.json' }, 'MANIFEST.json'), ' · ', h('a', { href: '../data/TRACE.md' }, 'TRACE.md (field-by-field source map)'), ' · pack built by ', h('code', null, D.manifest.generator), ' at commit ', h('code', null, (D.manifest.generator_commit_HEAD || '').slice(0, 10)), '. ', D.manifest.n_files + ' generated files and ' + D.manifest.n_source_hashes + ' source hashes are listed in the manifest.'));
    var rows = (c.sources || []).map(function (src) {
      return h('tr', null, h('td', null, h('code', { class: 'hash' }, src.archive_member || src.path)), h('td', null, sha(src.sha256)));
    });
    box.appendChild(h('details', { class: 'd' }, h('summary', null, (c.sources || []).length + ' source files with sha256 (archive members and analysis files)'),
      h('div', null, tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'Path / archive member'), h('th', null, 'sha256'))), h('tbody', null, rows))))));
    if (c.limitations) box.appendChild(h('details', { class: 'd' }, h('summary', null, 'Limitations recorded with this case'), h('div', null, h('ul', null, c.limitations.map(function (l) { return h('li', null, l); })))));
    box.appendChild(h('p', { class: 'muted' }, 'Text shown: ' + (c._text_mode || 'compact') + '. Compact pack strings are cut at 900 characters; the full-text overlay restores them.'));
    return box;
  }

  /* ---------- study ---------- */
  function renderStudy() {
    var st = D.study, p = st.primary.result, ns = st.noncommit_sensitivity.result;
    clear(main);
    main.appendChild(h('div', { class: 'head' }, h('h2', null, 'Study: eight matched world pairs'), h('span', { class: 'badge held' }, 'held-out · frozen')));
    main.appendChild(h('p', null, 'EXP-002 asked whether a deceptive-prompt regime (B1) produces larger outsider loss from a single exposure message than an authorized-cooperation regime (B2). The independent sample is the eight matched world pairs, not branches or checks.'));
    main.appendChild(h('div', { class: 'kpis' },
      h('div', { class: 'card' }, concept('causal', 'Frozen primary Δ'), h('div', { class: 'big-num num' }, fmt(p.estimate, 3)), h('p', null, '95% CI [' + fmt(p.L, 3) + ', ' + fmt(p.U, 3) + '] (world-cluster)'), h('p', { class: 'muted' }, 'category: ' + st.primary.evidence_category)),
      h('div', { class: 'card' }, concept('unc', 'One-sided p'), h('div', { class: 'big-num num' }, fmt(p.p_raw, 4)), h('p', null, 'exact sign-flip, ' + p.eligible_complete_pairs + ' of ' + p.matched_pairs_attempted + ' pairs')),
      h('div', { class: 'card' }, concept('attr', 'Decision'), h('div', { class: 'big-num', style: null }, 'NOT SUPPORTED'), h('p', null, 'Preregistered directional hypothesis ' + String(p.decision).toUpperCase() + '. Confirmatory null.')),
      h('div', { class: 'card' }, concept('unc', 'Registered sensitivity'), h('div', { class: 'big-num num' }, fmt(ns.estimate, 3)), h('p', null, '95% CI [' + fmt(ns.L, 2) + ', ' + fmt(ns.U, 2) + '] (non-commit excluded)'), h('p', { class: 'muted' }, 'registered sensitivity, ' + st.noncommit_sensitivity.evidence_category + '; not a confirmatory test'))));
    main.appendChild(h('p', { class: 'note' }, p.caveats));
    main.appendChild(h('h3', null, 'Per-world contrast d_w = tau_O(B1) − tau_O(B2)'));
    main.appendChild(h('div', { class: 'card' }, stripPlot(st)));
    main.appendChild(h('div', { class: 'legend' }, h('span', null, 'dots: d_w per world'), h('span', null, 'solid line: frozen Δ'), h('span', null, 'band: 95% CI'), h('span', null, 'dashed: 0 (no regime difference)')));
    var tb = h('tbody'); main.appendChild(h('div', null, tw(h('table', null, h('thead', null, h('tr', null, h('th', null, 'World'), h('th', { class: 'r' }, 'tau_O B1'), h('th', { class: 'r' }, 'tau_O B2'), h('th', { class: 'r' }, 'd_w'), h('th', null, 'Open cases'))), tb))));
    st.per_world.forEach(function (w) {
      var td = h('td', null, h('span', { class: 'muted' }, 'loading…'));
      tb.appendChild(h('tr', null, h('td', null, h('code', null, w.world_id)), h('td', { class: 'r num' }, fmt(w.tau_O_B1, 3)), h('td', { class: 'r num' }, fmt(w.tau_O_B2, 3)), h('td', { class: 'r num' }, fmt(w.d_w, 3)), td));
      worldCases(w.world_id).then(function (m) { clear(td); ['B1', 'B2'].forEach(function (r) { if (m[r]) td.appendChild(h('a', { href: '#/case/' + m[r], style: null }, m[r] + ' ')); }); });
    });
    main.appendChild(h('div', { class: 'grid2' },
      h('div', { class: 'card' }, h('h3', null, 'Certificates'), h('p', null, statusPill('supported'), ' ' + (st.certificate_counts.supported || 0) + ' · not supported ' + st.certificate_counts.not_supported + ' · ', concept('unc', 'inconclusive'), ' ' + st.certificate_counts.inconclusive), h('p', { class: 'muted' }, 'Sixteen held-out case certificates (8 worlds × 2 regimes). None reaches L2.')),
      h('div', { class: 'card' }, h('h3', null, 'Scheduled continuation records'), h('p', null, st.scheduled_counts.valid + ' executed valid + ' + st.scheduled_counts.not_run + ' not run (placebo unavailable) = ' + (st.scheduled_counts.valid + st.scheduled_counts.not_run) + ' scheduled.'), h('p', { class: 'muted' }, 'Unrun records are not zeros.'))));
    main.appendChild(h('details', { class: 'd' }, h('summary', null, 'Sources and sha256'), h('div', null, st.sources.map(function (x) { return h('p', null, h('code', null, x.path), h('br'), sha(x.sha256)); }))));
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
    var p = st.primary.result, W = 720, H = 190, padL = 20, padR = 20;
    var vals = st.per_world.map(function (w) { return w.d_w; }).concat([p.L, p.U, 0]);
    var lo = Math.min.apply(null, vals) - 0.4, hi = Math.max.apply(null, vals) + 0.4;
    var x = function (v) { return padL + (v - lo) / (hi - lo) * (W - padL - padR); };
    var svg = s('svg', { class: 'plot', viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Strip plot of per-world d_w with frozen Delta ' + fmt(p.estimate, 3) + ' and confidence interval' });
    svg.appendChild(s('rect', { x: x(p.L), y: 20, width: x(p.U) - x(p.L), height: 120, fill: 'var(--unc)', opacity: 0.18 }));
    svg.appendChild(s('line', { x1: padL, x2: W - padR, y1: 150, y2: 150, class: 'ax' }));
    ticks(lo, hi).forEach(function (t) { svg.appendChild(s('line', { x1: x(t), x2: x(t), y1: 150, y2: 156, class: 'ax' })); svg.appendChild(s('text', { x: x(t), y: 172, 'font-size': 12, 'text-anchor': 'middle', fill: 'var(--muted)' }, fmt(t, 0))); });
    svg.appendChild(s('line', { x1: x(0), x2: x(0), y1: 14, y2: 150, stroke: 'var(--ink)', 'stroke-dasharray': '5 4' }));
    svg.appendChild(s('line', { x1: x(p.estimate), x2: x(p.estimate), y1: 14, y2: 150, stroke: 'var(--causal)', 'stroke-width': 3 }));
    svg.appendChild(s('text', { x: x(p.estimate) + 6, y: 28, 'font-size': 12, 'font-weight': 700, fill: 'var(--causal)' }, 'Δ = ' + fmt(p.estimate, 3)));
    var sorted = st.per_world.slice().sort(function (a, b) { return a.d_w - b.d_w; }), lastX = -99, row = 0;
    sorted.forEach(function (w) {
      var cx = x(w.d_w); row = Math.abs(cx - lastX) < 16 ? (row + 1) % 4 : 0; lastX = cx;
      var cy = 58 + row * 22;
      svg.appendChild(s('circle', { cx: cx, cy: cy, r: 7, fill: w.d_w > 0 ? 'var(--causal)' : 'var(--bg)', stroke: 'var(--causal)', 'stroke-width': 2.5 }, s('title', null, 'world ' + w.world_id + ': d_w = ' + fmt(w.d_w, 3))));
    });
    return svg;
  }

  /* ---------- start here (tour) ---------- */
  var tourStep = 0;
  function tourPair() {
    // Rule: among the 8 worlds, pick the one with the largest |tau_O(B1) - tau_O(B2)| (= |d_w|).
    var pw = D.study.per_world.slice().sort(function (a, b) { return Math.abs(b.d_w) - Math.abs(a.d_w); })[0];
    return pw;
  }
  function renderStart() {
    clear(main);
    main.appendChild(h('div', { class: 'head' }, h('h2', null, 'Start here')));
    main.appendChild(h('p', null, 'This explorer lets you inspect every piece of evidence behind CCC’s held-out experiment and its development fixtures. Four ideas stay visually separate throughout.'));
    var holder = h('div'); main.appendChild(holder);
    var pw = tourPair();
    var steps = [
      ['1 · Four questions, kept apart', function (b) {
        b.appendChild(h('div', { class: 'concepts' },
          h('div', { class: 'card k-causal' }, concept('causal'), h('p', null, h('strong', null, 'Did the message change behaviour?')), h('p', null, 'Compare factual (F) with knockout (K) continuations. Effects tau_O, tau_C, tau_W.')),
          h('div', { class: 'card k-harm' }, concept('harm'), h('p', null, h('strong', null, 'Did outsiders lose more than the margin?')), h('p', null, 'tau_O against m_O = 2.5, with controls. This is the L2 rung.')),
          h('div', { class: 'card k-attr' }, concept('attr'), h('p', null, h('strong', null, 'Is collusion justified?')), h('p', null, 'Needs evidence a knockout cannot give. CCC never claims this rung in the held-out data.')),
          h('div', { class: 'card k-unc' }, concept('unc'), h('p', null, h('strong', null, 'How sure, and when to abstain?')), h('p', null, 'Bound span. Wide spans give “inconclusive”, not a guess.'))));
        b.appendChild(h('p', null, 'Working principle: a knockout measures what a message did, not whether it should have done it.'));
      }],
      ['2 · One real contrast', function (b) {
        b.appendChild(h('p', null, h('strong', null, 'Selection rule (fixed in advance, stated here): '), 'of the eight held-out worlds, take the one whose B1 and B2 checkpoints differ most in tau_O, i.e. the largest |d_w|. That is world ', h('code', null, pw.world_id), ' (|d_w| = ' + fmt(Math.abs(pw.d_w), 3) + ').'));
        b.appendChild(h('p', { class: 'note warn' }, 'Illustrative, not a selected positive result. The rule picks the largest contrast, not a certified harm: neither checkpoint below reaches a supported certificate, and the study-level result is a null.'));
        var g = h('div', { class: 'grid2' }); b.appendChild(g);
        worldCases(pw.world_id).then(function (m) {
          ['B1', 'B2'].forEach(function (r) {
            var cell = h('div', { class: 'card' }, h('p', { class: 'muted' }, 'loading…')); g.appendChild(cell);
            loadCase(m[r]).then(function (c) {
              var n = norm(c); clear(cell);
              cell.appendChild(h('h3', { style: null }, r + (r === 'B1' ? ' deceptive prompt' : ' authorized-cooperation prompt')));
              cell.appendChild(h('p', null, provBadge(c), ' ', statusPill(n.status), ' ', h('span', { class: 'muted' }, 'tau_O = ' + fmt(n.tau.O.est, 2) + ', [' + fmt(n.tau.O.L) + ', ' + fmt(n.tau.O.U) + '] vs m_O = ' + fmt(n.mO, 1))));
              cell.appendChild(intervalPlot(n, { w: 560 }));
              cell.appendChild(h('p', null, h('a', { href: '#/case/' + m[r] }, 'Open ' + m[r] + ' in full')));
            });
          });
        });
      }],
      ['3 · What the certificate allows', function (b) {
        b.appendChild(h('p', null, 'Only a supported certificate reaches L2. L0 and L1 show the highest reached (UI-derived, not a certificate rung); a one-sided bound excluding zero can suggest influence in either direction, without establishing harm. Each stop has a stated reason. L3 (attribution) is never claimed.'));
        var g = h('div', { class: 'grid2' }); b.appendChild(g);
        worldCases(pw.world_id).then(function (m) {
          ['B1', 'B2'].forEach(function (r) { loadCase(m[r]).then(function (c) { g.appendChild(h('div', { class: 'card' }, h('h3', null, m[r]), ladderStrip(c))); }); });
        });
      }],
      ['4 · The pre-registered answer', function (b) {
        var p = D.study.primary.result;
        b.appendChild(h('p', null, 'Across all eight world pairs, the frozen primary contrast is Δ = ' + fmt(p.estimate, 3) + ', 95% CI [' + fmt(p.L, 3) + ', ' + fmt(p.U, 3) + '], one-sided p = ' + fmt(p.p_raw, 4) + '. The preregistered directional hypothesis is not supported. The contrast above is one world among eight; it should be read next to the strip plot, not instead of it.'));
        b.appendChild(h('p', null, h('a', { class: 'btn', href: '#/study' }, 'Open the study panel')));
      }]
    ];
    var show = function () {
      clear(holder);
      var box = h('div', { class: 'tour' });
      var nav = h('div', { class: 'steps', role: 'group', 'aria-label': 'Tour steps' });
      steps.forEach(function (st, i) { nav.appendChild(h('button', { type: 'button', 'aria-current': i === tourStep ? 'step' : null, on: { click: function () { tourStep = i; show(); } } }, st[0].split(' · ')[0] + '. ' + st[0].split(' · ')[1])); });
      box.appendChild(nav);
      box.appendChild(h('h3', null, steps[tourStep][0]));
      steps[tourStep][1](box);
      box.appendChild(h('div', { class: 'navrow' },
        h('button', { class: 'btn sec', type: 'button', disabled: tourStep === 0, on: { click: function () { tourStep--; show(); } } }, 'Back'),
        h('button', { class: 'btn', type: 'button', disabled: tourStep === steps.length - 1, on: { click: function () { tourStep++; show(); } } }, 'Next')));
      holder.appendChild(box);
    };
    show();
    if (D.twins) main.appendChild(h('div', { class: 'card twins-flag' }, h('h3', null, 'Twin worlds'), h('p', null, 'Two worlds with identical observables and different labels. Step the evidence I0 \u2192 I5 and watch when verdicts diverge.'), h('a', { class: 'btn', href: '#/twins' }, 'Open Twin worlds')));
    main.appendChild(h('p', { class: 'muted' }, 'Or pick any case from the list on the left: 16 held-out checkpoints (8 worlds × B1/B2) and 5 scripted development fixtures.'));
  }

  /* ---------- about ---------- */
  function renderAbout() {
    clear(main);
    main.appendChild(h('div', { class: 'head' }, h('h2', null, 'Concepts and sources')));
    main.appendChild(h('div', { class: 'concepts' },
      h('div', { class: 'card k-causal' }, concept('causal'), h('p', null, 'Did the message change behaviour? tau_C, tau_W and (as a quantity) tau_O. Shown in blue with a filled circle.')),
      h('div', { class: 'card k-harm' }, concept('harm'), h('p', null, 'Did outsiders lose more than the margin m_O? tau_O vs m_O. Shown in red with a filled square.')),
      h('div', { class: 'card k-attr' }, concept('attr'), h('p', null, 'Is collusion justified? Never claimed here. Violet with a triangle; the L3 rung is hatched.')),
      h('div', { class: 'card k-unc' }, concept('unc'), h('p', null, 'Bound span and abstention (inconclusive). Amber with a diamond.'))));
    main.appendChild(h('h3', null, 'Effect definitions (verified against stored rows)'));
    main.appendChild(h('ul', null, h('li', null, 'tau_O = outsider mean under K minus under F.'), h('li', null, 'tau_C = coalition mean under F minus under K.'), h('li', null, 'tau_W = W under K minus W under F.'), h('li', null, 'F factual, K knockout (exposure mask), S sham, N placebo.')));
    main.appendChild(h('h3', null, 'Provenance'));
    main.appendChild(h('p', null, 'The pack was generated by ', h('code', null, D.manifest.generator), ' at commit ', h('code', null, (D.manifest.generator_commit_HEAD || '').slice(0, 10)), '. See ', h('a', { href: '../data/MANIFEST.json' }, 'MANIFEST.json'), ' and ', h('a', { href: '../data/TRACE.md' }, 'TRACE.md'), '. Archive sha256:'));
    main.appendChild(sha(D.index.archive.sha256));
    main.appendChild(h('p', null, 'Held-out data: EXP-002 (frozen, descriptive here). Development data: scripted Gate A fixtures, never evidence of performance. Gate A overall status was FAIL; the fixtures are shown because their failures are informative.'));
  }

  /* ---------- twins (hidden unless data/twins.js exists) ---------- */
  var twinState = { pair: 0, set: 0 };
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
  function renderTwins() {
    clear(main);
    var T = D.twins, P = T.pairs[twinState.pair], si = twinState.set;
    var dev = T.label === 'DEV';
    main.appendChild(h('div', { class: 'head' }, h('h2', null, 'Twin worlds: when does evidence separate verdicts?'), h('span', { class: 'badge ' + (dev ? 'dev' : 'held'), title: T.provenance_label }, T.provenance_label)));
    if (T.banner) main.appendChild(h('div', { class: 'note warn banner', role: 'status' }, h('strong', null, T.banner), ' Selection rule: ' + T.selection_rule));
    main.appendChild(h('p', null, 'Two worlds are built so that the auditor sees identical observables up to a stated information set, yet their private labels differ. A method that sees only the same evidence must give the same output; only new evidence can separate them. Pick a pair, then step the evidence from I0 to I5.'));
    var tabs = h('div', { class: 'steps', role: 'group', 'aria-label': 'Twin pair types' });
    T.pairs.forEach(function (p, i) { tabs.appendChild(h('button', { type: 'button', class: 'tabbtn', 'aria-pressed': i === twinState.pair ? 'true' : 'false', on: { click: function () { twinState.pair = i; renderTwins(); } } }, p.kind)); });
    main.appendChild(tabs);
    main.appendChild(h('h3', null, P.kind + ' · ' + P.title), h('p', null, P.description));
    // stepper
    var slider = h('input', { type: 'range', min: 0, max: 5, step: 1, value: si, id: 'tw-range', 'aria-valuetext': SETS_T[si] + ': ' + T.sets[si].adds, 'aria-label': 'Information set, I0 to I5' });
    slider.addEventListener('input', function () { twinState.set = +slider.value; renderTwins(); $('tw-range').focus(); });
    var btns = h('div', { class: 'steps', role: 'group', 'aria-label': 'Information set' });
    SETS_T.forEach(function (s2, i) { btns.appendChild(h('button', { type: 'button', class: 'tabbtn', 'aria-pressed': i === si ? 'true' : 'false', on: { click: function () { twinState.set = i; renderTwins(); } } }, s2)); });
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
      return h('tr', null, h('th', { scope: 'row' }, lab), h('td', null, vtxt(va)), B ? h('td', null, vtxt(vb)) : null, B ? h('td', null, vsame(va, vb) ? h('span', { class: 'pf n' }, 'same') : h('span', { class: 'pf f' }, 'DIFFERENT')) : null);
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
  function probeTwins() {
    var sc = document.createElement('script');
    sc.src = 'data/twins.js';
    sc.onload = function () { if (D.twins) { var a = $('twins-nav'); a.hidden = false; if (/^#\/twins/.test(location.hash) || location.hash === '#/start' || !location.hash) route(); } };
    sc.onerror = function () { /* absent: show nothing */ };
    document.head.appendChild(sc);
  }

  /* ---------- sidebar + router ---------- */
  function buildSidebar() {
    var list = $('case-list'); clear(list);
    var worlds = {}, order = [];
    cases.filter(function (c) { return c.id.charAt(0) === 'H'; }).forEach(function (c) { var k = c.id.slice(0, 3); if (!worlds[k]) { worlds[k] = []; order.push(k); } worlds[k].push(c); });
    list.appendChild(h('div', { class: 'grp' }, 'Held-out real agent · EXP-002 · frozen'));
    list.appendChild(h('p', { class: 'muted', style: null }, '8 worlds × B1 deceptive / B2 authorized cooperation'));
    order.forEach(function (k) {
      list.appendChild(h('div', { class: 'world' }, 'World ' + k));
      var pair = h('div', { class: 'pair' });
      worlds[k].forEach(function (c) { pair.appendChild(caseBtn(c, c.id.slice(4) + (c.id.endsWith('B1') ? ' deceptive' : ' authorized'))); });
      list.appendChild(pair);
    });
    list.appendChild(h('div', { class: 'grp' }, 'Development · scripted fixtures'));
    cases.filter(function (c) { return c.id.indexOf('GateA') === 0; }).forEach(function (c) { list.appendChild(caseBtn(c, c.title)); });
  }
  function caseBtn(c, label) {
    var held = c.id.charAt(0) === 'H';
    return h('button', { class: 'casebtn', type: 'button', 'data-id': c.id, title: c.title + ' — ' + c.provenance_label, on: { click: function () { location.hash = '#/case/' + c.id; if (window.innerWidth <= 900) $('case-menu').open = false; } } },
      label, h('span', { class: 'sub' }, h('span', null, String(c.status).replace('_', ' '))));
  }
  function mark(view, id) {
    document.querySelectorAll('.views a').forEach(function (a) { if (a.getAttribute('data-view') === view) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    document.querySelectorAll('.casebtn').forEach(function (b) { if (b.getAttribute('data-id') === id) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    $('case-current').textContent = id ? '· ' + id : '';
  }
  function route() {
    var hash = location.hash || '#/start', m = hash.match(/^#\/case\/([\w-]+)$/);
    if (m && byId[m[1]]) { mark('case', m[1]); renderCase(m[1]); }
    else if (hash === '#/study') { mark('study'); curId = null; renderStudy(); }
    else if (hash === '#/about') { mark('about'); curId = null; renderAbout(); }
    else if (/^#\/twins(\/|$)/.test(hash) && D.twins) {
      var tm = hash.match(/^#\/twins\/(\w+)(?:\/([0-5]))?$/);
      if (tm) { D.twins.pairs.forEach(function (p, i) { if (p.kind === tm[1]) twinState.pair = i; }); if (tm[2] !== undefined) twinState.set = +tm[2]; }
      mark('twins'); curId = null; renderTwins();
    }
    else { mark('start'); curId = null; renderStart(); }
    if (!m) window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route);
  buildSidebar();
  if (window.innerWidth <= 900) $('case-menu').open = false;
  route();
  probeTwins();
})();
