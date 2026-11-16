/* interactive-deck-story engine 1.0.1 — core renderers; topic renderers are injected at the TOPIC RENDERERS marker by build_story.py */
(function () {
"use strict";
var STORY = JSON.parse(document.getElementById("story-data").textContent);
var META = STORY.meta, SC = STORY.scenes, STRAT = STORY.strategies;
var W = 1600, H = 900, NS = "http://www.w3.org/2000/svg";
var RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var COLORS = {avoid:"#34D399", hide:"#38BDF8", reduce:"#A78BFA", steady:"#FBBF24", measure:"#C7D2EC",
  teal:"#00B39F", tealhi:"#2CE5CB", client:"#38BDF8", azure:"#7C8FE0", foundry:"#00B39F"};
var stage = document.getElementById("stage"), viewport = document.getElementById("viewport");
var G = null, cur = -1, beat = 0, cameFrom = null, autoplay = null;
var IDX = {}; SC.forEach(function (s, i) { IDX[s.id] = i; });
Object.keys(STRAT || {}).forEach(function (k) { if (STRAT[k].color) COLORS[k] = STRAT[k].color; });
var HUB = (SC.filter(function (s) { return s.type === "map"; })[0] || {}).id;
function slideLabel(s, pre) { if (!s.slide) return ""; var l = [].concat(s.slide); return pre + (l.length > 1 ? "slides " + l.join(", ") : "slide " + l[0]); }
function LBL(k, d) { return (META.labels && META.labels[k]) || d; }

/* ------------------------------------------------------------------ helpers */
function el(tag, a) {
  var e = document.createElement(tag); a = a || {};
  Object.keys(a).forEach(function (k) {
    var v = a[k]; if (v === null || v === undefined || v === false) return;
    if (k === "class") e.className = v; else if (k === "style") e.style.cssText = v;
    else if (k === "text") e.textContent = v; else if (k === "html") e.innerHTML = v;
    else if (k.slice(0, 2) === "on" && typeof v === "function") e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  });
  for (var i = 2; i < arguments.length; i++) add(e, arguments[i]);
  return e;
}
function add(e) {
  for (var i = 1; i < arguments.length; i++) {
    var c = arguments[i];
    if (c === null || c === undefined || c === false) continue;
    if (Array.isArray(c)) { c.forEach(function (x) { add(e, x); }); continue; }
    e.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
  }
}
function sv(tag, a, parent) {
  var e = document.createElementNS(NS, tag); a = a || {};
  Object.keys(a).forEach(function (k) {
    var v = a[k]; if (v === null || v === undefined) return;
    if (k === "text") e.textContent = v; else if (k === "class") e.setAttribute("class", v);
    else if (k.slice(0, 2) === "on" && typeof v === "function") e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  });
  if (parent) parent.appendChild(e);
  return e;
}
function px(x, y, w, h) { return "left:" + x + "px;top:" + y + "px;" + (w != null ? "width:" + w + "px;" : "") + (h != null ? "height:" + h + "px;" : ""); }
function box(x, y, w, h, cls, b, d, extra) {
  var e = el("div", {class: "box " + (cls || ""), style: px(x, y, w, h) + (d ? "--d:" + d + "s;" : "") + (extra || "")});
  if (b !== undefined && b !== null) e.setAttribute("data-b", b);
  return e;
}
function chip(k) { return el("span", {class: "chip c-" + k, style: COLORS[k] ? "color:" + COLORS[k] : null, text: (STRAT[k] || {label: k}).label}); }
function clickable(e, fn, label) {
  e.classList.add("click"); e.setAttribute("tabindex", "0"); e.setAttribute("role", "button");
  if (label) e.setAttribute("aria-label", label);
  e.addEventListener("click", function (ev) { if (ev.target.closest(".dive,.walk,a")) return; fn(ev); });
  e.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); ev.stopPropagation(); fn(ev); } });
  return e;
}
function wire(svg, d, b, del, cls) {
  return sv("path", {d: d, class: "wire " + (cls || ""), pathLength: "1", "data-b": b === null ? null : String(b), style: del ? "--d:" + del + "s" : null}, svg);
}
function curve(x1, y1, x2, y2) { var mx = (x1 + x2) / 2; return "M" + x1 + "," + y1 + " C" + mx + "," + y1 + " " + mx + "," + y2 + " " + x2 + "," + y2; }
function later(fn, ms) { var t = setTimeout(fn, ms); G && G.timers.push(t); return t; }
function every(fn, ms) { var t = setInterval(fn, ms); G && G.intervals.push(t); return t; }
function links(list) { var f = document.createDocumentFragment(); (list || []).forEach(function (s, i) { if (i) f.appendChild(document.createTextNode("  ·  ")); f.appendChild(el("a", {href: s.url, target: "_blank", rel: "noopener", text: s.label})); }); return f; }

/* ------------------------------------------------------------------ particles */
function flow(path, o) {
  o = o || {}; var f = {path: path, layer: o.layer || G.pt, color: o.color || COLORS.tealhi, every: o.every || 900, speed: o.speed || 260, r: o.r || 4, when: o.when, acc: Math.random() * (o.every || 900), burst: o.burst || 1};
  G.flows.push(f); return f;
}
function spawn(path, layer, color, speed, r, done) {
  if (RM || !G) return;
  var L = path.getTotalLength(); if (!L) return;
  var c = sv("circle", {r: r || 4, fill: color || COLORS.tealhi, filter: "url(#glow)"}, layer || G.pt);
  G.parts.push({c: c, path: path, L: L, s: 0, v: speed || 260, done: done});
}
var last = performance.now();
function tick(now) {
  var dt = Math.min(60, now - last); last = now;
  if (G && !RM) {
    G.flows.forEach(function (f) {
      if (f.when && !f.when()) return;
      f.acc += dt;
      if (f.acc >= f.every) { f.acc = 0; for (var b = 0; b < f.burst; b++) (function (k) { setTimeout(function () { if (G && G.flows.indexOf(f) >= 0) spawn(f.path, f.layer, f.color, f.speed, f.r); }, k * 110); })(b); }
    });
    for (var i = G.parts.length - 1; i >= 0; i--) {
      var p = G.parts[i]; p.s += p.v * dt / 1000;
      if (p.s >= p.L) { p.c.remove(); G.parts.splice(i, 1); if (p.done) p.done(); continue; }
      var pt = p.path.getPointAtLength(p.s);
      p.c.setAttribute("cx", pt.x.toFixed(1)); p.c.setAttribute("cy", pt.y.toFixed(1));
      p.c.setAttribute("opacity", Math.max(0, Math.min(1, p.s / 24, (p.L - p.s) / 24)).toFixed(2));
    }
  }
  requestAnimationFrame(tick);
}

/* ------------------------------------------------------------------ drawer, notes, toast */
var drawer = document.getElementById("drawer"), notesEl = document.getElementById("notes"), railEl = document.getElementById("rail");
function openDrawer(o) {
  var body = drawer.querySelector(".body"); body.innerHTML = "";
  add(body, el("div", {class: "dk", text: o.kicker || ""}));
  var h = el("h2", {text: o.title || ""}); add(body, h);
  if (o.preview) add(h, el("span", {class: "badge", style: "margin-inline-start:10px;vertical-align:4px", text: "PREVIEW"}));
  if (o.tag) add(body, chip(o.tag));
  if (o.body) add(body, el("p", {text: o.body}));
  if (o.list) add(body, el("ul", {}, o.list.map(function (t) { return el("li", {text: t}); })));
  if (o.src && o.src.length) add(body, el("div", {class: "srcs"}, el("div", {class: "h-sm", text: "Sources"}), o.src.map(function (s) { return el("a", {href: s.url, target: "_blank", rel: "noopener", text: s.label + " ↗"}); })));
  if (o.go && IDX[o.go] !== undefined) {
    add(body, el("div", {class: "act"}, el("button", {class: "tb primary", text: "Open " + SC[IDX[o.go]].short + "  ›", onclick: function () { closeDrawer(); go(o.go, {from: o.from, focus: o.focus}); }})));
  }
  drawer.classList.add("open"); drawer.setAttribute("aria-hidden", "false");
  setTimeout(function () { drawer.querySelector(".x").focus({preventScroll: true}); }, 50);
}
function closeDrawer() { drawer.classList.remove("open"); drawer.setAttribute("aria-hidden", "true"); }
drawer.querySelector(".x").addEventListener("click", closeDrawer);
function setNotes() {
  var s = SC[cur]; var p = notesEl.querySelector("p"); p.innerHTML = "";
  var txt = s.notes || "";
  var parts = txt.split("A likely question:");
  add(p, parts[0]);
  if (parts[1]) { add(p, el("br")); add(p, el("br")); add(p, el("b", {text: "Likely question: "})); add(p, parts[1].trim()); }
}
function toggle(elm, btn, force) {
  var on = force !== undefined ? force : !elm.classList.contains("open");
  elm.classList.toggle("open", on); if (btn) btn.setAttribute("aria-pressed", on ? "true" : "false");
}
var toastT;
function toast(t, ms) { var e = document.getElementById("toast"); e.textContent = t; e.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(function () { e.classList.remove("on"); }, ms || 1600); }

/* ------------------------------------------------------------------ scene chrome */
function chrome(s, root) {
  add(root, el("div", {class: "kicker", text: s.kicker}));
  add(root, el("h1", {class: "title", text: s.title}));
  add(root, el("p", {class: "subtitle", text: s.subtitle}));
  if (s.tags && s.tags.length) add(root, el("div", {class: "tags"}, s.tags.map(chip)));
  var src = el("span", {class: "src"}, (s.sources && s.sources.length ? "Sources: " : ""), links(s.sources));
  add(root, el("div", {class: "foot"}, src, el("span", {text: META.footer + slideLabel(s, " · deck ")})));
  if (s.preview) add(root, el("div", {class: "pnote", text: META.previewNote}));
}

/* ------------------------------------------------------------------ renderers */
var R = {};

R.title = function (s, root, svg) {
  add(root, el("div", {class: "hero-k", text: META.kicker}));
  add(root, el("div", {class: "hero-bar"}));
  add(root, el("h1", {class: "hero-t", text: META.title}));
  add(root, el("p", {class: "hero-s", text: META.subtitle}));
  add(root, el("div", {class: "hero-go"},
    el("button", {class: "tb primary", text: "Start the story  ›", onclick: function () { next(); }}),
    (HUB ? el("button", {class: "tb", text: LBL("jumpHub", "Jump to the main decision tree"), onclick: function () { go(HUB); }}) : null)));
  add(root, el("div", {class: "hero-keys", html: "<kbd>→</kbd> or <kbd>Space</kbd> next step &nbsp; <kbd>←</kbd> back &nbsp; <kbd>M</kbd> main tree &nbsp; <kbd>C</kbd> chapters &nbsp; <kbd>N</kbd> presenter notes &nbsp; <kbd>W</kbd> walk a tree &nbsp; <kbd>F</kbd> full screen"}));
  var toc = el("div", {class: "toc"}, el("div", {class: "h-sm", text: "In this story"}));
  s.chapters.forEach(function (c) { add(toc, el("button", {onclick: function () { go(c[2]); }}, el("b", {text: c[0]}), el("span", {text: c[1]}))); });
  add(root, toc);
  add(root, el("div", {class: "hero-meta"}, el("span", {text: "Paired deck: " + META.deck}), el("span", {text: "Facts checked " + META.checked})));
  // decorative token stream
  var p = sv("path", {d: "M70,792 C500,760 900,820 1530,780", fill: "none", stroke: "rgba(0,179,159,.25)", "stroke-width": 1.5}, svg);
  flow(p, {every: 260, speed: 420, r: 3});
  var p2 = sv("path", {d: "M70,804 C600,840 1000,770 1530,806", fill: "none", stroke: "rgba(56,189,248,.18)", "stroke-width": 1.2}, svg);
  flow(p2, {every: 520, speed: 300, r: 2.5, color: COLORS.hide});
};

R.turn = function (s, root, svg) {
  add(root, el("div", {class: "barlab", style: px(70, 196), text: s.barLabel || "ONE USER TURN — ILLUSTRATIVE PROPORTIONS"}));
  var mk = s.marker;
  var bar = el("div", {class: "box turnbar", style: px(70, 224, 1460, 58), "data-b": "0"});
  var x = 0, ftx = 0;
  s.bar.forEach(function (b, i) {
    var w = b[1] * 1460;
    add(bar, el("div", {class: "seg " + b[2], style: px(x + 2, 0, w - 4, 58) + "--d:" + (i * .55) + "s" + (b[3] ? ";background:" + b[3] : ""), text: b[0]}));
    if (mk && (b[2] === mk.after || i === mk.after)) ftx = x + w;
    x += w;
  });
  add(root, bar);
  if (mk) add(root, el("div", {class: "ftmark", style: px(70 + ftx - 6, 290) + "--d:2.6s", "data-b": "0", text: "▲ " + mk.text}));
  s.cards.forEach(function (c, i) {
    var col = i % 3, row = Math.floor(i / 3);
    var b = box(70 + col * 495, 340 + row * 186, 470, 168, "card src-card", 1, (i * .08).toFixed(2));
    add(b, el("div", {class: "n", text: "0" + (i + 1)}), el("h3", {text: c.t}), el("p", {text: c.d}),
      el("div", {class: "lev"}, el("span", {text: s.leverLabel || "MAIN LEVER"}), c.lever), chip(c.tag));
    clickable(b, function () { openDrawer({kicker: s.cardKicker || "Cause", title: c.t, body: c.detail, tag: c.tag, src: c.src, go: c.go}); }, c.t);
    add(root, b);
  });
  var band = s.principle && el("div", {class: "band", style: "top:722px", "data-b": "2"}, el("span", {class: "h-sm", text: s.principleLabel || "DESIGN PRINCIPLE"}), el("span", {text: s.principle}));
  add(root, band);
  s.beats = 2;
};

R.map = function (s, root, svg) {
  var Q = s.questions, nQ = Q.length, qx = 400, qw = 420, qh = nQ >= 5 ? 84 : 104, LAST = nQ + 1;
  var pQ = nQ > 1 ? Math.min(120, (456 - qh) / (nQ - 1)) : 0, tQ = (nQ - 1) * pQ + qh, yQ = 268 + (456 - tQ) / 2;
  var ys = Q.map(function (q, i) { return yQ + i * pQ; });
  var rx = 70, ry = 404, rw = 260, rh = 140;
  // measure + govern bands
  if (s.measure) {
    var mb = el("div", {class: "mband", style: "top:196px", "data-b": "0"}, el("b", {text: s.measure.t}), el("span", {text: s.measure.d}), el("span", {class: "go", text: "Open ›"}));
    clickable(mb, function () { go(s.measure.go, {from: mb}); }, s.measure.t); add(root, mb);
  }
  if (s.govern) {
    var gb = el("div", {class: "mband", style: "top:752px", "data-b": String(LAST)}, el("b", {text: s.govern.t}), el("span", {text: s.govern.d}), el("span", {class: "go", text: "Open ›"}));
    clickable(gb, function () { go(s.govern.go, {from: gb}); }, s.govern.t); add(root, gb);
  }
  // root
  var rn = box(rx, ry, rw, rh, "node-root", 0);
  add(rn, el("h3", {text: s.root.t}), el("p", {text: s.root.d}));
  add(root, rn);
  var orderEl = s.order ? el("div", {class: "order", "data-b": String(LAST)}, el("b", {text: s.orderLabel || "WHY THIS ORDER"}), s.order) : null;
  if (orderEl) add(root, orderEl);
  if (s.measure) wire(svg, "M398,217 L" + (rx + rw / 2) + ",217 L" + (rx + rw / 2) + "," + ry, 0, .2);
  if (s.govern) wire(svg, "M" + (rx + rw / 2) + "," + (ry + rh) + " L" + (rx + rw / 2) + ",772 L398,772", LAST, 0);
  var qEls = [], qWires = [], leafEls = [], leafWires = [];
  Q.forEach(function (q, i) {
    var k = q.k, col = COLORS[k];
    var w = wire(svg, curve(rx + rw, ry + rh / 2, qx, ys[i] + qh / 2), 0, .3 + i * .15);
    qWires.push(w);
    var n = box(qx, ys[i], qw, qh, "card qnode", 0, (.35 + i * .15).toFixed(2), "--k:" + col + ";");
    add(n, el("div", {class: "lab", text: (i + 1) + " · " + STRAT[k].label.toUpperCase()}), el("h3", {text: q.q}), el("p", {text: q.d}), el("span", {class: "cnt", text: q.leaves.length + " " + (s.leafWord || "levers")}));
    clickable(n, function () { G.manual = i; if (beat < 1) beat = 1; applyBeat(); }, q.q);
    qEls.push(n); add(root, n);
    var n2 = q.leaves.length, pitch = 88, lh = 76, top = 496 - (n2 * pitch - (pitch - lh)) / 2;
    leafEls[i] = []; leafWires[i] = [];
    q.leaves.forEach(function (lf, j) {
      var ly = top + j * pitch;
      var lw = wire(svg, curve(qx + qw, ys[i] + qh / 2, 930, ly + lh / 2), null, j * .07);
      lw.style.stroke = col; lw.style.opacity = 0; leafWires[i].push(lw);
      var tgt = SC[IDX[lf.go]];
      var L = box(930, ly, 600, lh, "card leaf", null, (j * .07).toFixed(2), "--k:" + col + ";");
      add(L, el("h4", {text: lf.t}), el("div", {class: "to", text: "Deep dive: " + (tgt ? tgt.short : lf.go)}));
      var dv = el("button", {class: "dive", "aria-label": "Open " + (tgt ? tgt.short : ""), text: "›", onclick: function (ev) { ev.stopPropagation(); go(lf.go, {from: L, focus: lf.focus}); }});
      add(L, dv);
      clickable(L, function () { openDrawer({kicker: STRAT[k].label + " · " + q.q, title: lf.t, body: lf.detail, tag: k, src: lf.src, go: lf.go, focus: lf.focus, from: L}); }, lf.t);
      leafEls[i].push(L); add(root, L);
      var fl = flow(lw, {color: col, every: 1300 + j * 140, speed: 320, r: 3.5, when: function () { return G.active === i; }});
    });
    flow(w, {color: col, every: 1500, speed: 260, r: 3.5, when: function () { return G.active === i || (G.active === null && beat >= 0); }});
  });
  var hint = el("div", {class: "map-hint", style: "top:470px", text: "Press → to unfold each question, or select one"});
  add(root, hint);
  add(root, el("div", {class: "edit-note", text: META.editorial}));
  G.active = null;
  function setActive(i, user) {
    G.active = i;
    qEls.forEach(function (e, j) { e.classList.toggle("act", j === i); e.classList.toggle("mute", i !== null && j !== i); });
    qWires.forEach(function (w, j) { w.classList.toggle("dim", i !== null && j !== i); });
    leafEls.forEach(function (arr, j) { arr.forEach(function (L) { L.classList.toggle("show", j === i); }); });
    leafWires.forEach(function (arr, j) { arr.forEach(function (w) { w.style.opacity = j === i ? 1 : 0; w.classList.toggle("on", j === i); }); });
    hint.style.opacity = (i === null && beat < LAST) ? 1 : 0;
    if (orderEl) orderEl.style.visibility = i === null ? "visible" : "hidden";
  }
  G.onBeat = function (b) {
    var a = (G.manual !== null && G.manual !== undefined) ? G.manual : ((b >= 1 && b <= nQ) ? b - 1 : null);
    G.manual = null; setActive(a);
    if (b === LAST) hint.textContent = "Select any question to unfold it again";
  };
  G.setActive = setActive;
  s.beats = LAST;
};

R.path = function (s, root, svg) {
  var nH = s.hops.length, chain = s.chain || nH, cx = [], CY = 292, w = 150, hgt = 76, d = 36, LASTB = Math.floor((nH - 1) / 2) + 2;
  s.hops.forEach(function (h, i) { cx.push(70 + (1460 / nH) * (i + .5)); });
  // wires first (behind cubes)
  var ws = [];
  for (var i = 0; i < chain - 1; i++) ws.push(wire(svg, "M" + cx[i] + "," + CY + " L" + cx[i + 1] + "," + CY, 0, .3 + i * .2, "on"));
  ws.forEach(function (p, i) { flow(p, {every: 900, speed: 240, r: 4, color: COLORS.tealhi}); });
  if (s.loop) {
    var lp = s.loop, el5 = wire(svg, "M" + cx[lp[0]] + "," + (CY - 30) + " L" + cx[lp[0]] + ",206 L" + cx[lp[1]] + ",206 L" + cx[lp[1]] + "," + (CY - 30), 0, 1.2);
    flow(el5, {every: 1100, speed: 300, r: 4, color: COLORS.azure});
  }
  var cubes = sv("g", {}, svg);
  s.hops.forEach(function (h, i) {
    var col = COLORS[h.kind], x = cx[i], y = CY;
    var g = sv("g", {class: "cube float", style: "animation-delay:" + (-i * .8) + "s;pointer-events:auto", tabindex: "0", role: "button", "aria-label": h.t}, cubes);
    var top = [[x, y - hgt / 2], [x + w / 2, y], [x, y + hgt / 2], [x - w / 2, y]];
    var left = [[x - w / 2, y], [x, y + hgt / 2], [x, y + hgt / 2 + d], [x - w / 2, y + d]];
    var right = [[x, y + hgt / 2], [x + w / 2, y], [x + w / 2, y + d], [x, y + hgt / 2 + d]];
    var P = function (a) { return a.map(function (p) { return p.join(","); }).join(" "); };
    sv("polygon", {points: P(left), fill: col, opacity: .55}, g);
    sv("polygon", {points: P(right), fill: col, opacity: .32}, g);
    sv("polygon", {class: "top", points: P(top), fill: col, opacity: h.optional ? .55 : .9, stroke: "#fff", "stroke-opacity": h.optional ? .9 : .5, "stroke-width": h.optional ? 2 : 1, "stroke-dasharray": h.optional ? "9 6" : null}, g);
    var inner = [[x, y - hgt / 2 + 14], [x + w / 2 - 28, y], [x, y + hgt / 2 - 14], [x - w / 2 + 28, y]];
    sv("polygon", {points: P(inner), fill: "none", stroke: "#fff", "stroke-opacity": .35}, g);
    var open = function () { openDrawer({kicker: (s.hopWord || "Hop") + " " + (i + 1) + " · " + (s.pathName || "request path"), title: h.t, body: h.detail, list: h.lev, src: s.sources}); };
    g.addEventListener("click", open);
    g.addEventListener("keydown", function (ev) { if (ev.key === "Enter") open(); });
    add(root, el("div", {class: "hoplab", style: px(x - 112, 372), "data-b": "0"}, el("h4", {text: h.t}), el("p", {text: h.d})));
    h.lev.forEach(function (t, j) {
      var bb = Math.floor(i / 2) + 1;
      add(root, el("div", {class: "lchip", style: px(x - 112, 446 + j * 57) + "--d:" + (j * .08 + (i % 2) * .25) + "s", "data-b": String(bb), text: t}));
    });
  });
  // step badges
  for (var bi = 0; bi < chain - 1; bi++) {
    var mx = (cx[bi] + cx[bi + 1]) / 2;
    sv("circle", {cx: mx, cy: CY, r: 13, fill: COLORS.tealhi}, svg); sv("text", {x: mx, y: CY + 4.5, "text-anchor": "middle", class: "stepb", text: String(bi + 1)}, svg);
  }
  if (s.loop) {
    var lx = (cx[s.loop[0]] + cx[s.loop[1]]) / 2;
    sv("circle", {cx: lx, cy: 206, r: 13, fill: COLORS.azure}, svg); sv("text", {x: lx, y: 210.5, "text-anchor": "middle", class: "stepb", text: String(chain)}, svg);
  }
  if (s.obs) add(root, el("div", {class: "band", style: "top:704px", "data-b": String(LASTB)}, el("span", {class: "h-sm", text: s.obsLabel || "OBSERVABILITY ACROSS EVERY HOP"}), el("span", {text: s.obs})));
  var lg = s.legend || [["Client", "client"], ["Azure resource", "azure"], ["Foundry service", "foundry"]];
  add(root, el("div", {class: "legend"},
    lg.map(function (l) { return el("span", {}, el("i", {style: "background:" + (COLORS[l[1]] || l[1])}), l[0]); }),
    el("span", {}, el("i", {style: "background:transparent;border:1.5px dashed #fff"}), "Optional"),
    el("span", {text: "Select a block for details"})));
  s.beats = LASTB;
};

R.table = function (s, root, svg) {
  var t = el("table", {class: "tbl big", style: px(70, 192, 1460), "data-b": "0"});
  var cg = el("colgroup"); s.widths.forEach(function (w) { add(cg, el("col", {style: "width:" + w + "px"})); }); add(t, cg);
  add(t, el("thead", {}, el("tr", {}, s.cols.map(function (c) { return el("th", {text: c}); }))));
  var tb = el("tbody"), jit = [];
  s.rows.forEach(function (r, ri) {
    var tr = el("tr", {style: "height:82px"});
    r.forEach(function (c) {
      if (typeof c === "object") {
        var td = el("td");
        if (c.text) { add(td, el("span", {style: "font-size:13px;color:var(--dim)", text: c.text})); }
        else {
          var js = sv("svg", {width: 170, height: 46, viewBox: "0 0 170 46"});
          sv("line", {x1: 0, y1: 23, x2: 170, y2: 23, stroke: "rgba(185,194,214,.2)", "stroke-dasharray": "3 4"}, js);
          var pl = sv("polyline", {fill: "none", stroke: ri === 2 ? COLORS.teal : (ri === 1 ? COLORS.hide : COLORS.steady), "stroke-width": 2}, js);
          jit.push({pl: pl, a: c.jitter, drop: c.drop, gaps: c.gaps, seed: ri * 7.3});
          add(td, js);
        }
        add(tr, td);
      } else add(tr, el("td", {text: c}));
    });
    tr.addEventListener("click", function () { tb.querySelectorAll("tr").forEach(function (x) { x.classList.toggle("sel", x === tr && !tr.classList.contains("sel")); }); });
    add(tb, tr);
  });
  add(t, tb); add(root, t);
  var ph = 0;
  function upd() {
    ph += 1;
    jit.forEach(function (j) {
      var pts = [];
      for (var x = 0; x <= 170; x += 5) {
        var k = x / 5 + ph;
        var n = Math.sin(k * 1.7 + j.seed) * .5 + Math.sin(k * .63 + j.seed * 2) * .35 + Math.sin(k * 3.1 + j.seed) * .15;
        var y = 23 - n * j.a * 20;
        if (j.drop && ((k + Math.floor(j.seed)) % 23) > 19) y = 23 - 16;
        if (j.gaps && ((k + 3) % 17) > 13) { pts.push(null); continue; }
        pts.push(x + "," + y.toFixed(1));
      }
      j.pl.setAttribute("points", pts.filter(Boolean).join(" "));
      if (j.gaps) j.pl.setAttribute("stroke-dasharray", "14 6");
    });
  }
  upd(); if (!RM) every(upd, 140);
  add(root, el("div", {class: "band", style: "top:716px", "data-b": "1"}, el("span", {class: "h-sm", text: s.band[0]}), el("span", {text: s.band[1]})));
  s.beats = 1;
};

R.tree = function (s, root, svg) {
  var Q = s.qs, n = Q.length, rows = n + 1, top = 196, avail = 580, pitch = Math.min(112, avail / rows), ch = pitch - 30;
  var qx = 96, qw = 494, rx = 660, rw = 470;
  var rowsEls = [], yesW = [], noW = [], walking = false, wIdx = 0;
  Q.forEach(function (q, i) {
    var y = top + i * pitch, b = String(i);
    var qe = box(qx, y, qw, ch, "q row", b);
    add(qe, el("span", {text: q.q}));
    clickable(qe, function () { openDrawer({kicker: s.title, title: q.q, body: q.detail, src: q.src}); }, q.q);
    add(root, qe);
    add(root, el("div", {class: "num", style: px(qx - 20, y + ch / 2 - 20), "data-b": b, text: String(i + 1)}));
    var yw = wire(svg, "M" + (qx + qw) + "," + (y + ch / 2) + " L" + (rx - 4) + "," + (y + ch / 2), i, .25, "");
    yw.setAttribute("marker-end", "url(#arr)"); yesW.push(yw);
    add(root, el("div", {class: "yn", style: px(qx + qw + 18, y + ch / 2 - 22) + "--d:.3s", "data-b": b, text: "Yes"}));
    var pv = /\*$/.test(q.t);
    var re = box(rx, y, rw, ch, "rec row", b, .35);
    add(re, el("b", {text: q.t}), el("span", {text: q.s}));
    clickable(re, function () { openDrawer({kicker: "Recommended option · question " + (i + 1), title: q.t.replace(/\*$/, ""), preview: pv, body: q.detail, src: q.src}); }, q.t);
    add(root, re);
    var nw = wire(svg, "M" + (qx + 54) + "," + (y + ch) + " L" + (qx + 54) + "," + (y + pitch - 4), i + 1, 0, "");
    nw.setAttribute("marker-end", "url(#arr)"); noW.push(nw);
    add(root, el("div", {class: "yn no", style: px(qx + 64, y + ch + 4), "data-b": String(i + 1), text: "No"}));
    rowsEls.push([qe, re]);
    flow(yw, {every: 1400, speed: 160, r: 3.5, when: function () { return yw.classList.contains("on") && (!walking || G.win === i); }});
  });
  var oy = top + n * pitch;
  var oe = box(qx, oy, qw, ch, "qo row", String(n)); add(oe, el("span", {text: "Otherwise"})); add(root, oe);
  var ow = wire(svg, "M" + (qx + qw) + "," + (oy + ch / 2) + " L" + (rx - 4) + "," + (oy + ch / 2), n, .25, "");
  ow.setAttribute("marker-end", "url(#arr)");
  var fe = box(rx, oy, rw, ch, "fb row", String(n), .35);
  add(fe, el("b", {text: s.other.t}), el("span", {text: s.other.s}));
  clickable(fe, function () { openDrawer({kicker: "Fallback option", title: s.other.t, body: s.other.detail, src: s.other.src}); }, s.other.t);
  add(root, fe);
  rowsEls.push([oe, fe]);
  flow(ow, {every: 1400, speed: 160, r: 3.5, color: COLORS.measure, when: function () { return ow.classList.contains("on") && (!walking || G.win === n); }});
  var asH = oy + ch - top;
  var as = box(1170, top, 360, asH, "card aside", String(n + 1));
  add(as, el("div", {class: "h-sm", text: s.aside.h}));
  s.aside.items.forEach(function (it) { add(as, el("div", {class: "it"}, el("b", {text: it[0]}), el("span", {text: it[1]}))); });
  add(root, as);
  add(root, el("div", {class: "legend"},
    el("span", {}, el("i", {style: "background:rgba(235,239,247,.16);border:1px solid rgba(185,194,214,.4)"}), "Question"),
    el("span", {}, el("i", {style: "background:rgba(0,179,159,.35);border:1.5px solid #00B39F"}), "Recommended option"),
    el("span", {}, el("i", {style: "border:1.5px dashed rgba(185,194,214,.6)"}), "Fallback option"),
    el("span", {text: "Select any box for details"})));
  if (s.next) add(root, el("button", {class: "nextlink", text: s.next.t + "  ›", onclick: function () { go(s.next.go); }}));
  // walk mode
  var wb = el("div", {class: "walkbar"}, el("button", {class: "tb", "aria-pressed": "false", html: "Walk the tree <kbd>W</kbd>"}));
  add(root, wb);
  var wbtn = wb.querySelector("button");
  var ctrl = el("div", {class: "walk", style: "display:none"},
    el("button", {class: "y", text: "Yes", onclick: function (ev) { ev.stopPropagation(); answer(true); }}),
    el("button", {class: "n", text: "No", onclick: function (ev) { ev.stopPropagation(); answer(false); }}));
  add(root, ctrl);
  var restart = el("button", {class: "tb", style: "display:none", text: "Restart", onclick: function () { startWalk(); }});
  add(wb, restart);
  function paint() {
    rowsEls.forEach(function (r, i) {
      var vis = walking ? (i <= wIdx) : true;
      r.forEach(function (e) { e.classList.remove("win", "dim", "pending"); });
      if (walking) {
        if (G.win !== null) { r.forEach(function (e) { if (i !== G.win) e.classList.add("dim"); }); if (i === G.win) r[1].classList.add("win"); }
        else if (i !== wIdx) r.forEach(function (e) { e.classList.add("dim"); });
        else { r[1].classList.add("dim"); if (G.win === null) r[1].classList.add("pending"); }
      }
    });
    yesW.concat([ow]).forEach(function (w, i) { w.classList.toggle("hot", walking && G.win === i); });
    noW.forEach(function (w, i) { w.classList.toggle("hot", walking && i < wIdx); });
    if (walking && G.win === null && wIdx < n) {
      var y = top + wIdx * pitch; ctrl.style.cssText = px(rx + rw / 2 - 72, y + ch / 2 - 17); ctrl.style.display = "flex";
    } else ctrl.style.display = "none";
  }
  function startWalk() { walking = true; wIdx = 0; G.win = null; beat = s.beats; applyBeat(true); wbtn.setAttribute("aria-pressed", "true"); restart.style.display = ""; paint(); }
  function stopWalk() { walking = false; G.win = null; wbtn.setAttribute("aria-pressed", "false"); restart.style.display = "none"; paint(); }
  function answer(yes) {
    if (yes) { G.win = wIdx; paint(); var q = Q[wIdx]; later(function () { openDrawer({kicker: "Result of the walk", title: q.t.replace(/\*$/, ""), preview: /\*$/.test(q.t), body: q.detail, src: q.src}); }, 500); }
    else { wIdx++; if (wIdx >= n) { G.win = n; paint(); later(function () { openDrawer({kicker: "Result of the walk", title: s.other.t, body: s.other.detail, src: s.other.src}); }, 500); } else paint(); }
  }
  wbtn.addEventListener("click", function () { walking ? stopWalk() : startWalk(); });
  G.walk = function () { walking ? stopWalk() : startWalk(); };
  G.win = null;
  G.focus = function (i) {
    later(function () {
      var r = rowsEls[Math.min(i, rowsEls.length - 1)];
      r.forEach(function (e) { e.classList.add("focus"); });
      later(function () { r.forEach(function (e) { e.classList.remove("focus"); }); }, 5200);
    }, 700);
  };
  s.beats = n + 1;
};

var DG = {
  direct: {n: [[40, 85, "App", "app"], [188, 85, "Model", "mt"]], e: [[0, 1, -26], [1, 0, -26]], seq: [[0], [1]]},
  single: {n: [[40, 85, "Agent", "ag"], [188, 38, "Model", "mt"], [188, 136, "Tool", "mt"]], e: [[0, 1, 0], [1, 0, 0], [0, 2, 0], [2, 0, 0]], seq: [[0], [1], [2], [3], [0], [1]]},
  seq: {n: [[34, 85, "A", "ag"], [114, 85, "B", "ag"], [194, 85, "C", "ag"]], e: [[0, 1, 0], [1, 2, 0]], seq: [[0], [1]]},
  conc: {n: [[34, 85, "Start", "app"], [180, 30, "A", "ag"], [180, 85, "B", "ag"], [180, 140, "C", "ag"]], e: [[0, 1, 0], [0, 2, 0], [0, 3, 0]], seq: [[0, 1, 2]]},
  hand: {n: [[40, 132, "A", "ag"], [114, 40, "B", "ag"], [188, 132, "C", "ag"]], e: [[0, 1, 0], [1, 2, 0]], seq: [[0], [1]]},
  group: {n: [[114, 34, "Manager", "ag"], [40, 138, "A", "ag"], [114, 138, "B", "ag"], [188, 138, "C", "ag"]], e: [[0, 1, 0], [1, 0, 0], [0, 2, 0], [2, 0, 0], [0, 3, 0], [3, 0, 0]], seq: [[0], [1], [2], [3], [4], [5]]}
};
R.spectrum = function (s, root, svg) {
  var nC = s.cols.length, w = 228, gap = nC > 1 ? Math.min(60, (1460 - nC * w) / (nC - 1)) : 0, x0 = 70 + (1460 - (nC * w + (nC - 1) * gap)) / 2;
  s.cols.forEach(function (c, i) {
    var x = x0 + i * (w + gap);
    var b = box(x, 190, w, 420, "card pcol", String(i));
    add(b, el("h3", {text: c.t}), el("div", {class: "lab", text: s.callsLabel || "CALLS IN SERIES"}), el("div", {class: "calls", text: c.calls}));
    var ds = sv("svg", {width: w, height: 180, viewBox: "0 0 " + w + " 180"}); add(b, ds);
    var D = typeof c.dg === "string" ? DG[c.dg] : c.dg, paths = [];
    D.e.forEach(function (e) {
      var a = D.n[e[0]], z = D.n[e[1]], bend = e[2] || 0;
      var dx = z[0] - a[0], dy = z[1] - a[1], L = Math.sqrt(dx * dx + dy * dy) || 1, ux = dx / L, uy = dy / L;
      var x1 = a[0] + ux * 17, y1 = a[1] + uy * 17, x2 = z[0] - ux * 17, y2 = z[1] - uy * 17;
      var off = bend || ((e[0] > e[1]) ? 10 : -10) * (D.e.some(function (o) { return o[0] === e[1] && o[1] === e[0]; }) ? 1 : 0);
      var mx = (x1 + x2) / 2 - uy * off, my = (y1 + y2) / 2 + ux * off;
      paths.push(sv("path", {d: "M" + x1 + "," + y1 + " Q" + mx + "," + my + " " + x2 + "," + y2, fill: "none", stroke: "rgba(185,194,214,.32)", "stroke-width": 1.6}, ds));
    });
    D.n.forEach(function (nn) {
      var col = nn[3] === "app" ? COLORS.client : nn[3] === "ag" ? COLORS.teal : COLORS.azure;
      sv("circle", {cx: nn[0], cy: nn[1], r: 16, fill: col, opacity: .9}, ds);
      var ly = nn[2].length > 1 ? (nn[1] < 60 ? nn[1] - 24 : nn[1] + 34) : nn[1] + 5;
      var t = sv("text", {x: nn[0], y: ly, "text-anchor": "middle", class: "svgt " + (nn[2].length > 1 ? "" : "b"), text: nn[2]}, ds);
      t.style.fontSize = nn[2].length > 1 ? "12px" : "13px";
    });
    var k = 0;
    every(function () {
      if (!b.classList.contains("on")) return;
      D.seq[k % D.seq.length].forEach(function (ei) { spawn(paths[ei], ds, COLORS.tealhi, 150, 4); });
      k++;
    }, 900);
    add(b, el("div", {class: "cap", text: c.cap}));
    clickable(b, function () { openDrawer({kicker: "Orchestration pattern", title: c.t, body: c.detail, src: s.sources}); }, c.t);
    add(root, b);
  });
  if (s.arrow) add(root, el("div", {class: "arrowband", style: "top:636px", "data-b": String(nC), text: s.arrow}));
  if (s.band) add(root, el("div", {class: "band", style: "top:700px;padding:12px 22px", "data-b": String(nC)}, el("span", {class: "h-sm", text: s.band[0]}), el("span", {text: s.band[1]})));
  add(root, el("div", {class: "legend", style: "top:792px"},
    el("span", {}, el("i", {style: "background:" + COLORS.client}), "Application"), el("span", {}, el("i", {style: "background:" + COLORS.teal}), "Agent"),
    el("span", {}, el("i", {style: "background:" + COLORS.azure}), "Model or tool"), el("span", {}, el("i", {style: "background:" + COLORS.tealhi}), "Call")));
  s.beats = nC;
};

R.trace = function (s, root, svg) {
  var bx = 360, bw = 680, y0 = 214, pitch = 62;
  var spanCol = {agent: COLORS.teal, model: COLORS.reduce, tool: COLORS.hide}, hasFt = s.ft !== undefined && s.ft !== null;
  var bars = [];
  s.spans.forEach(function (sp, i) {
    var y = y0 + i * pitch, indent = i === 0 ? 0 : 18;
    add(root, el("div", {class: "span-l", style: px(70 + indent, y + 2) + "--d:" + (i * .1) + "s", "data-b": "0"}, el("code", {text: sp[0]}), sp[1]));
    sv("rect", {x: bx, y: y + 6, width: bw, height: 34, rx: 5, fill: "rgba(185,194,214,.06)"}, svg);
    var r = sv("rect", {x: bx + sp[2] * bw, y: y + 6, width: Math.max(4, (sp[3] - sp[2]) * bw), height: 34, rx: 5, fill: spanCol[sp[4]] || COLORS[sp[4]] || COLORS.teal, class: "grow", style: "transform:scaleX(0)"}, svg);
    bars.push({r: r, a: sp[2], b: sp[3]});
  });
  var yb = y0 + s.spans.length * pitch;
  var fx = bx + (hasFt ? s.ft : 0) * bw;
  var fl = sv("line", {x1: fx, y1: y0 - 6, x2: fx, y2: yb, stroke: COLORS.steady, "stroke-width": 2, "stroke-dasharray": "5 5", opacity: 0}, svg);
  var ftl = sv("text", {x: fx + 8, y: yb + 2, class: "svgt", text: s.ftLabel || "first token reaches the client", opacity: 0}, svg); ftl.setAttribute("fill", COLORS.steady); ftl.style.fontWeight = "700"; ftl.style.fontSize = "14px";
  var ph = sv("line", {x1: bx, y1: y0 - 10, x2: bx, y2: yb, stroke: "#fff", "stroke-width": 1.5, opacity: .7}, svg);
  add(root, el("div", {style: "position:absolute;" + px(70, yb + 22, 980) + "font-size:14px;color:var(--muted)", "data-b": "0", text: s.caption}));
  var timers = [];
  function play() {
    timers.forEach(clearTimeout); timers = [];
    bars.forEach(function (b) { b.r.style.transition = "none"; b.r.style.transform = "scaleX(0)"; });
    fl.setAttribute("opacity", 0); ftl.setAttribute("opacity", 0);
    void svg.getBoundingClientRect();
    var T = RM ? 0 : 4200, start = performance.now();
    bars.forEach(function (b) {
      timers.push(setTimeout(function () { b.r.style.transition = "transform " + ((b.b - b.a) * T / 1000) + "s linear"; b.r.style.transform = "scaleX(1)"; }, b.a * T));
    });
    if (hasFt) timers.push(setTimeout(function () { fl.setAttribute("opacity", 1); ftl.setAttribute("opacity", 1); }, s.ft * T));
    function mv() { var k = Math.min(1, (performance.now() - start) / (T || 1)); ph.setAttribute("x1", bx + k * bw); ph.setAttribute("x2", bx + k * bw); if (k < 1 && G) requestAnimationFrame(mv); }
    requestAnimationFrame(mv);
  }
  G.cleanups.push(function () { timers.forEach(clearTimeout); });
  later(play, 300); every(play, 7000);
  var mon = box(1100, 196, 430, 420, "card mon", 1);
  add(mon, el("div", {class: "h-sm", style: "margin-bottom:8px", text: s.monitorLabel || "What to monitor"}));
  s.monitor.forEach(function (m) { add(mon, el("div", {class: "it"}, el("b", {text: m[0]}), el("span", {text: m[1]}))); });
  add(root, mon);
  add(root, el("div", {class: "band", style: "top:704px", "data-b": "2"}, el("span", {class: "h-sm", text: s.band[0]}), el("span", {text: s.band[1]})));
  add(root, el("div", {class: "legend"},
    el("span", {}, el("i", {style: "background:" + COLORS.teal}), "Agent span"), el("span", {}, el("i", {style: "background:" + COLORS.reduce}), "Model call span"),
    el("span", {}, el("i", {style: "background:" + COLORS.hide}), "Tool span"), el("span", {text: "Illustrative trace"})));
  s.beats = 2;
};

R.compare = function (s, root, svg) {
  var nF = s.feats.length, qw = 250, cx0 = 340, gap = 12, cw = (1530 - cx0 - (nF - 1) * gap) / nF, hy = 192, hh = 70, ry0 = hy + hh + 10, rh = 66, rg = 7;
  var cells = [], sel = null;
  s.feats.forEach(function (f, j) {
    var x = cx0 + j * (cw + gap);
    var h = box(x, hy, cw, hh, "card cmp-h", String(j));
    add(h, el("b", {text: f[0]}), chip(f[1]));
    clickable(h, function () { spot(sel === j ? null : j); }, f[0]);
    add(root, h);
  });
  s.rows.forEach(function (r, i) {
    var y = ry0 + i * (rh + rg);
    add(root, box(70, y, qw, rh, "cmp-q", "0", (i * .04).toFixed(2)));
    root.lastChild.textContent = r[0];
    cells[i] = [];
    for (var j = 0; j < nF; j++) {
      var c = box(cx0 + j * (cw + gap), y, cw, rh, "cmp-c", String(j), (i * .05).toFixed(2));
      c.textContent = r[j + 1]; cells[i].push(c); add(root, c);
    }
  });
  function spot(j) {
    sel = j;
    cells.forEach(function (row) { row.forEach(function (c, k) { c.classList.toggle("hl", j !== null && k === j); c.classList.toggle("lo", j !== null && k !== j); }); });
  }
  G.focus = function (j) { beat = s.beats; applyBeat(true); later(function () { spot(j); }, 500); };
  if (s.band) add(root, el("div", {class: "band", style: "top:" + (ry0 + s.rows.length * (rh + rg) + 8) + "px", "data-b": String(nF)}, el("span", {class: "h-sm", text: s.band[0]}), el("span", {text: s.band[1]})));
  add(root, el("div", {class: "legend", style: "top:806px"}, el("span", {text: "Select a feature heading to compare its column"})));
  s.beats = nF;
};

R.phases = function (s, root, svg) {
  var nP = s.phases.length, w = 300, step = nP > 1 ? (1460 - w) / (nP - 1) : 0;
  var hold = el("div", {style: px(0, 0, 1600, 900) + "pointer-events:none"});
  s.phases.forEach(function (p, i) {
    var x = 70 + i * step, col = COLORS[p[1]];
    var c = el("div", {class: "chev", style: px(x, 196, w) + "background:linear-gradient(90deg," + col + "55," + col + "22);--d:0s", "data-b": String(i)}, el("span", {class: "pn", text: String(i + 1)}), el("span", {text: p[0]}));
    if (i === 0) c.style.clipPath = "polygon(0 0,90% 0,100% 50%,90% 100%,0 100%)";
    add(root, c);
    var b = box(x + 6, 300, step - 18 + (i === nP - 1 ? w - step : 0), 260, "card pbul", String(i), .15);
    p[2].forEach(function (t) { add(b, el("div", {text: t})); });
    add(root, b);
  });
  var pr = box(70, 590, 1460, 196, "card prove", String(nP));
  add(pr, el("div", {class: "h-sm", text: s.proveLabel || "Prove first"}));
  var grid = el("div", {style: "display:grid;grid-template-columns:1fr 1fr;column-gap:40px"});
  s.prove.forEach(function (t, i) { add(grid, el("div", {class: "pv"}, el("i", {text: "✓"}), el("span", {text: t}))); });
  add(pr, grid); add(root, pr);
  var line = sv("path", {d: "M70,238 L1530,238", fill: "none", stroke: "none"}, svg);
  flow(line, {every: 2400, speed: 420, r: 5, color: "#fff", when: function () { return beat >= nP - 1; }});
  s.beats = nP;
};

R.status = function (s, root, svg) {
  var t = el("table", {class: "tbl", style: px(70, 192, 1460)});
  add(t, el("colgroup", {}, el("col", {style: "width:380px"}), el("col"), el("col", {style: "width:130px"})));
  var sc = s.cols || ["Capability", "Note or recent change", "Status"];
  add(t, el("thead", {}, el("tr", {}, el("th", {text: sc[0]}), el("th", {text: sc[1]}), el("th", {text: sc[2]}))));
  var tb = el("tbody");
  s.rows.forEach(function (r) {
    var tr = el("tr", {"data-p": r[2] ? "1" : "0"}, el("td", {text: r[0] + (r[2] ? "*" : "")}), el("td", {text: r[1]}), el("td", {}, r[2] ? el("span", {class: "badge", text: "PREVIEW"}) : ""));
    tr.style.height = "38px"; add(tb, tr);
  });
  add(t, tb); add(root, t);
  var fb = el("div", {class: "filters"});
  [["All", "all"], ["Preview only", "p"], ["Without preview label", "g"]].forEach(function (f, i) {
    add(fb, el("button", {class: "tb", "aria-pressed": i === 0 ? "true" : "false", text: f[0], onclick: function (ev) {
      fb.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", b === ev.currentTarget ? "true" : "false"); });
      tb.querySelectorAll("tr").forEach(function (tr) { var p = tr.getAttribute("data-p") === "1"; tr.style.display = (f[1] === "all" || (f[1] === "p" && p) || (f[1] === "g" && !p)) ? "" : "none"; });
    }}));
  });
  add(root, fb);
  s.beats = 0;
};

R.refs = function (s, root, svg) {
  var nG = s.groups.length, w = (1460 - (nG - 1) * 20) / nG;
  s.groups.forEach(function (g, i) {
    var b = box(70 + i * (w + 20), 190, w, 560, "card refcol", null);
    add(b, el("h3", {text: g[0]}));
    g[1].forEach(function (l) { add(b, el("a", {href: l.url, target: "_blank", rel: "noopener", title: l.url, text: l.label + " ↗"})); });
    add(root, b);
  });
  if (s.current) add(root, el("div", {class: "band", style: "top:770px;padding:10px 22px"}, el("span", {class: "h-sm", text: s.currentLabel || "STAYING CURRENT"}), links(s.current)));
  s.beats = 0;
};

/* ------------------------------------------------------------------ TOPIC RENDERERS (injected by build_story.py --extra-js) */
/*@@TOPIC_RENDERERS@@*/

/* ------------------------------------------------------------------ build and navigate */
function build(i) {
  var s = SC[i];
  var root = el("div", {class: "scene", "data-id": s.id, role: "region", "aria-label": s.title || META.title});
  var svg = sv("svg", {class: "wires", viewBox: "0 0 1600 900", "aria-hidden": "true"});
  sv("defs", {}, svg).innerHTML = '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="rgba(185,194,214,.7)"/></marker>';
  add(root, svg);
  G = {root: root, svg: svg, pt: null, flows: [], parts: [], timers: [], intervals: [], cleanups: [], onBeat: null, focus: null, walk: null, active: null};
  G.pt = sv("g", {}, svg);
  if (s.type !== "title") chrome(s, root);
  if (!R[s.type]) throw new Error("No renderer for scene type " + s.type + " (scene " + s.id + ")");
  R[s.type](s, root, svg);
  svg.appendChild(G.pt);
  return G;
}
function teardown(g) {
  if (!g) return;
  g.timers.forEach(clearTimeout); g.intervals.forEach(clearInterval); g.cleanups.forEach(function (f) { f(); });
  g.flows = []; g.parts = [];
}
function applyBeat(instant) {
  if (!G) return;
  G.root.querySelectorAll("[data-b]").forEach(function (e) { e.classList.toggle("on", +e.getAttribute("data-b") <= beat); });
  if (G.onBeat) G.onBeat(beat);
  updateBars();
}
function go(target, opt) {
  opt = opt || {};
  var i = typeof target === "number" ? target : IDX[target];
  if (i === undefined || i < 0 || i >= SC.length) return;
  closeDrawer();
  var oldG = G, oldEl = G && G.root, dir = i >= cur ? 1 : -1;
  if (oldEl) {
    if (opt.from && !RM) {
      var r = opt.from.getBoundingClientRect(), sr = stage.getBoundingClientRect(), k = sr.width / W;
      oldEl.style.transformOrigin = ((r.left + r.width / 2 - sr.left) / k) + "px " + ((r.top + r.height / 2 - sr.top) / k) + "px";
      oldEl.classList.add("dive");
    } else oldEl.classList.add("leave");
    teardown(oldG);
    setTimeout(function () { oldEl.remove(); }, RM ? 0 : 560);
  }
  if (SC[cur] && SC[cur].type === "map" && i !== cur) cameFrom = "map";
  else if (SC[i].type === "map") cameFrom = null;
  cur = i;
  var g = build(i);
  g.root.classList.add(opt.from && SC[i].type !== "map" ? "rise" : "enter");
  stage.appendChild(g.root);
  beat = opt.full ? (SC[i].beats || 0) : 0;
  if (opt.focus !== undefined && opt.focus !== null) beat = SC[i].beats || 0;
  applyBeat(true);
  requestAnimationFrame(function () { requestAnimationFrame(function () { g.root.classList.remove("enter", "rise"); }); });
  if (opt.focus !== undefined && opt.focus !== null && g.focus) g.focus(opt.focus);
  if (location.hash.slice(1) !== SC[i].id) history.replaceState(null, "", "#" + SC[i].id);
  setNotes(); updateRail(); updateCrumb();
  document.getElementById("walkBtn").classList.toggle("hidden", SC[i].type !== "tree");
}
function next() {
  var s = SC[cur];
  if (beat < (s.beats || 0)) { beat++; applyBeat(); return true; }
  if (cur < SC.length - 1) { go(cur + 1); return true; }
  return false;
}
function prev() {
  if (beat > 0) { beat--; applyBeat(); return; }
  if (cur > 0) go(cur - 1, {full: true});
}

/* ------------------------------------------------------------------ chrome: progress, rail, crumb */
var progress = document.getElementById("progress"), beatsEl = document.getElementById("beats"), counter = document.getElementById("counter");
SC.forEach(function (s, i) {
  add(progress, el("button", {class: s.type === "map" ? "hub" : "", title: s.short, "aria-label": s.short, onclick: function () { go(i); }}));
});
function updateBars() {
  progress.querySelectorAll("button").forEach(function (b, i) { b.classList.toggle("cur", i === cur); b.classList.toggle("done", i < cur); });
  beatsEl.innerHTML = "";
  for (var k = 0; k <= (SC[cur].beats || 0); k++) add(beatsEl, el("i", {class: k <= beat ? "on" : ""}));
  counter.textContent = (cur + 1) + " / " + SC.length;
}
function buildRail() {
  var body = railEl.querySelector(".body"); body.innerHTML = "";
  STORY.sections.forEach(function (sec) {
    add(body, el("h3", {text: (sec.num === "00" ? "" : sec.num + " · ") + sec.name}));
    SC.forEach(function (s, i) {
      if (s.section !== sec.id) return;
      var dots = el("span", {class: "dots"}, (s.tags || []).map(function (t) { return el("i", {style: "background:" + COLORS[t]}); }));
      add(body, el("button", {"data-i": i, onclick: function () { go(i); toggle(railEl, document.getElementById("railBtn"), false); }}, el("span", {text: s.short}), dots, el("small", {text: slideLabel(s, "")})));
    });
  });
}
function updateRail() { railEl.querySelectorAll("button[data-i]").forEach(function (b) { b.classList.toggle("cur", +b.getAttribute("data-i") === cur); }); }
function updateCrumb() {
  var c = document.getElementById("crumb"); c.innerHTML = "";
  var s = SC[cur], sec = STORY.sections.filter(function (x) { return x.id === s.section; })[0];
  if (s.type !== "map" && s.type !== "title") {
    if (HUB) add(c, el("button", {text: LBL("hub", "Main decision tree"), onclick: function () { go(HUB, {full: true}); }}), "  ›  ");
  }
  add(c, el("span", {text: (sec && sec.num !== "00" ? sec.num + " " + sec.name + "  ›  " : "")}), el("b", {text: s.short}));
}

/* ------------------------------------------------------------------ fit, background, events */
function fit() {
  var r = viewport.getBoundingClientRect(), k = Math.min(r.width / W, r.height / H);
  var x = (r.width - W * k) / 2, y = (r.height - H * k) / 2;
  stage.style.transform = "translate(" + x + "px," + y + "px) scale(" + k + ")";
}
window.addEventListener("resize", fit);

(function bg() {
  var cv = document.getElementById("bg"), ctx = cv.getContext("2d"), pts = [], DPR = Math.min(2, window.devicePixelRatio || 1);
  function size() { cv.width = innerWidth * DPR; cv.height = innerHeight * DPR; }
  size(); window.addEventListener("resize", size);
  for (var i = 0; i < 70; i++) pts.push({x: Math.random(), y: Math.random(), vx: (Math.random() - .5) * .00012, vy: (Math.random() - .5) * .00012});
  function draw() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    var Wd = cv.width, Hd = cv.height;
    pts.forEach(function (p) { if (!RM) { p.x += p.vx; p.y += p.vy; if (p.x < 0 || p.x > 1) p.vx *= -1; if (p.y < 0 || p.y > 1) p.vy *= -1; } });
    for (var a = 0; a < pts.length; a++) for (var b = a + 1; b < pts.length; b++) {
      var dx = (pts[a].x - pts[b].x) * Wd, dy = (pts[a].y - pts[b].y) * Hd, d = Math.sqrt(dx * dx + dy * dy), lim = 170 * DPR;
      if (d < lim) { ctx.strokeStyle = "rgba(0,179,159," + (0.09 * (1 - d / lim)).toFixed(3) + ")"; ctx.lineWidth = DPR; ctx.beginPath(); ctx.moveTo(pts[a].x * Wd, pts[a].y * Hd); ctx.lineTo(pts[b].x * Wd, pts[b].y * Hd); ctx.stroke(); }
    }
    pts.forEach(function (p) { ctx.fillStyle = "rgba(44,229,203,.35)"; ctx.beginPath(); ctx.arc(p.x * Wd, p.y * Hd, 1.6 * DPR, 0, 6.3); ctx.fill(); });
    if (!RM) requestAnimationFrame(draw);
  }
  draw();
})();

document.getElementById("nextBtn").addEventListener("click", function () { next(); });
document.getElementById("prevBtn").addEventListener("click", prev);
document.getElementById("railBtn").addEventListener("click", function (e) { toggle(railEl, e.currentTarget); });
document.getElementById("notesBtn").addEventListener("click", function (e) { toggle(notesEl, e.currentTarget); });
document.getElementById("mapBtn").addEventListener("click", function () { if (HUB) go(HUB, {full: true}); });
if (!HUB) document.getElementById("mapBtn").classList.add("hidden");
document.getElementById("walkBtn").addEventListener("click", function () { if (G && G.walk) G.walk(); });
document.getElementById("fsBtn").addEventListener("click", fullscreen);
document.getElementById("playBtn").addEventListener("click", function (e) { setAuto(!autoplay); });
var uiT, viewOnly = false;
/* Full screen: standard API, webkit-prefixed fallback (older Safari), and a toolbar-free view when the
   browser or the hosting page blocks the API (an embedded preview, a sandboxed frame or a browser policy). */
function fsEl() { return document.fullscreenElement || document.webkitFullscreenElement || null; }
function pres() {
  var on = !!fsEl() || viewOnly;
  document.body.classList.toggle("pres", on); fit();
  document.getElementById("fsBtn").setAttribute("aria-pressed", on ? "true" : "false");
  if (on) { poke(); }
}
function poke() { document.body.classList.add("ui"); clearTimeout(uiT); uiT = setTimeout(function () { document.body.classList.remove("ui"); }, 2600); }
function setViewOnly(on) { viewOnly = on; if (!on) { clearTimeout(toastT); document.getElementById("toast").classList.remove("on"); } pres(); }
function fsBlocked() {
  if (fsEl() || viewOnly) return;
  setViewOnly(true);
  toast("Full screen is blocked in this view, so the toolbars are hidden instead. F11 gives browser full screen; F or Esc restores the toolbars.", 6000);
}
document.addEventListener("fullscreenchange", pres);
document.addEventListener("webkitfullscreenchange", pres);
document.addEventListener("fullscreenerror", fsBlocked);
document.addEventListener("webkitfullscreenerror", fsBlocked);
document.addEventListener("mousemove", function () { if (document.body.classList.contains("pres")) poke(); });
function fullscreen() {
  if (fsEl()) { var x = document.exitFullscreen || document.webkitExitFullscreen; if (x) x.call(document); return; }
  if (viewOnly) { setViewOnly(false); return; }
  var d = document.documentElement, req = d.requestFullscreen || d.webkitRequestFullscreen;
  var enabled = document.fullscreenEnabled !== undefined ? document.fullscreenEnabled : document.webkitFullscreenEnabled;
  if (!req || enabled === false) { fsBlocked(); return; }
  try { var r = req.call(d); if (r && typeof r.then === "function") r.then(null, fsBlocked); }
  catch (e) { fsBlocked(); }
}
function setAuto(on) {
  var b = document.getElementById("playBtn");
  if (autoplay) { clearInterval(autoplay); autoplay = null; }
  if (on) { autoplay = setInterval(function () { if (!next()) setAuto(false); }, 4500); toast("Autoplay on"); }
  b.setAttribute("aria-pressed", on ? "true" : "false");
  b.querySelector("span").textContent = on ? "Pause" : "Play";
}
document.addEventListener("keydown", function (e) {
  if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  var k = e.key;
  if (k === "ArrowRight" || k === "PageDown" || (k === " " && !(e.target && e.target.closest && e.target.closest("button,[role=button]")))) { e.preventDefault(); next(); }
  else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); prev(); }
  else if (k === "Home") go(0);
  else if (k === "End") go(SC.length - 1, {full: true});
  else if (k === "Escape") { if (viewOnly) setViewOnly(false); closeDrawer(); toggle(railEl, document.getElementById("railBtn"), false); toggle(notesEl, document.getElementById("notesBtn"), false); }
  else if (k === "n" || k === "N") toggle(notesEl, document.getElementById("notesBtn"));
  else if (k === "c" || k === "C") toggle(railEl, document.getElementById("railBtn"));
  else if ((k === "m" || k === "M") && HUB) go(HUB, {full: true});
  else if (k === "f" || k === "F") fullscreen();
  else if (k === "p" || k === "P") setAuto(!autoplay);
  else if ((k === "w" || k === "W") && G && G.walk) G.walk();
});
window.addEventListener("hashchange", function () { var id = location.hash.slice(1); if (IDX[id] !== undefined && IDX[id] !== cur) go(id); });

window.__story = {count: SC.length, go: function (id, full) { go(id, {full: !!full}); }, state: function () { return {i: cur, id: SC[cur].id, beat: beat, beats: SC[cur].beats || 0}; }};
buildRail(); fit();
var start = IDX[location.hash.slice(1)];
go(start !== undefined ? start : 0);
requestAnimationFrame(tick);
})();
