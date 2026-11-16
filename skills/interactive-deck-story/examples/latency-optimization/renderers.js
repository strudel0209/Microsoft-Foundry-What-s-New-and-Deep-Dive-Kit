/* Topic renderers for the latency story: the anatomy of a model call (scene type "anatomy")
 * and the four model-call feature panels (scene type "features", animations in ANIM).
 * Injected into the engine closure by build_story.py --extra-js; every core helper is in scope. */
R.anatomy = function (s, root, svg) {
  var x0 = 150, xf = 450, AX = 300, n = 30, streaming = true;
  var g = sv("g", {}, svg);
  var ctl = el("div", {class: "ctl", style: px(820, 192)},
    el("span", {text: "Streaming"}),
    el("span", {class: "seg2"}, el("button", {class: "sel", text: "On", "data-v": "1"}), el("button", {text: "Off", "data-v": "0"})),
    el("span", {text: "Generated tokens"}),
    el("input", {type: "range", min: "8", max: "46", value: String(n), "aria-label": "Generated tokens, fewer to more"}),
    el("button", {class: "tb", text: "Replay"}));
  add(root, ctl);
  var rng = ctl.querySelector("input"), segBtns = ctl.querySelectorAll(".seg2 button");
  segBtns.forEach(function (b) { b.addEventListener("click", function () { streaming = b.getAttribute("data-v") === "1"; segBtns.forEach(function (o) { o.classList.toggle("sel", o === b); }); draw(true); }); });
  rng.addEventListener("input", function () { n = +rng.value; draw(false); });
  ctl.querySelector(".tb").addEventListener("click", function () { draw(true); });
  function T(x, y, t, cls, anchor) { return sv("text", {x: x, y: y, class: "svgt " + (cls || ""), "text-anchor": anchor || "middle", text: t}, g); }
  function bracket(xa, xb, y, label, up, col) {
    var t = up ? -8 : 8;
    sv("path", {d: "M" + xa + "," + (y - t) + " L" + xa + "," + y + " L" + xb + "," + y + " L" + xb + "," + (y - t), fill: "none", stroke: col, "stroke-width": 1.5}, g);
    var tt = T((xa + xb) / 2, up ? y - 10 : y + 22, label, "", "middle"); tt.setAttribute("fill", col); tt.style.fontSize = "14px"; tt.style.fontWeight = "600";
  }
  var timers = [];
  function draw(animate) {
    timers.forEach(clearTimeout); timers = []; g.innerHTML = "";
    var xl = xf + 10 + n * 22;
    sv("line", {x1: x0 - 20, y1: AX, x2: 1530, y2: AX, stroke: "rgba(185,194,214,.35)", "stroke-width": 1.5}, g);
    sv("rect", {x: x0 + 4, y: AX - 32, width: xf - x0 - 10, height: 26, rx: 4, fill: "rgba(124,143,224,.35)"}, g);
    T((x0 + xf) / 2, AX - 14, "Queueing and prompt processing", "", "middle");
    var toks = [];
    for (var i = 0; i < n; i++) {
      var r = sv("rect", {x: xf + 10 + i * 22, y: AX - 30, width: 15, height: 22, rx: 3, fill: COLORS.teal, opacity: animate && !RM ? 0 : 1}, g);
      toks.push(r);
    }
    [[x0, "Request received"], [xf, "First token"], [xl, "Last token"]].forEach(function (m) {
      sv("circle", {cx: m[0], cy: AX, r: 7, fill: "#fff"}, g); T(m[0], AX + 26, m[1], "b");
    });
    bracket(x0, xf - 4, AX - 52, "Time to first token (TTFT)", true, COLORS.hide);
    bracket(xf + 4, xl, AX - 52, "Generation: time between tokens (TBT) × generated tokens", true, COLORS.teal);
    bracket(x0, xl, AX + 50, "Time to last token (TTLT): the whole model call", false, COLORS.reduce);
    var sx = streaming ? xf : xl;
    var eye = sv("g", {opacity: animate && !RM ? 0 : 1, style: "transition:opacity .4s"}, g);
    sv("path", {d: "M" + sx + "," + (AX + 88) + " l-9,16 h18 z", fill: COLORS.steady}, eye);
    var et = sv("text", {x: sx, y: AX + 124, "text-anchor": sx > 1300 ? "end" : "middle", class: "svgt", text: streaming ? "User starts reading at the first token" : "User sees nothing until the last token"}, eye);
    et.setAttribute("fill", COLORS.steady); et.style.fontWeight = "700"; et.style.fontSize = "14px";
    if (animate && !RM) {
      toks.forEach(function (r, i) { timers.push(setTimeout(function () { r.setAttribute("opacity", 1); }, 700 + i * 70)); });
      timers.push(setTimeout(function () { eye.setAttribute("opacity", 1); }, streaming ? 760 : 760 + n * 70));
    }
  }
  G.cleanups.push(function () { timers.forEach(clearTimeout); });
  draw(true);
  var fm = el("div", {class: "formula", "data-b": "1"}, el("code", {text: s.formula}), el("span", {text: s.formulaNote}));
  add(root, fm);
  var t = el("table", {class: "tbl", style: px(70, 548, 1000), "data-b": "2"});
  add(t, el("thead", {}, el("tr", {}, el("th", {text: "Metric"}), el("th", {text: "Azure Monitor name"}), el("th", {text: "Use"}))));
  var tb = el("tbody"); s.metrics.forEach(function (m) { add(tb, el("tr", {}, el("td", {text: m[0]}), el("td", {}, el("code", {text: m[1]})), el("td", {text: m[2]}))); }); add(t, tb);
  add(root, t);
  var as = box(1110, 548, 420, 236, "card aside", 3);
  add(as, el("div", {class: "h-sm", text: "Reading the numbers"}));
  s.reading.forEach(function (r) { add(as, el("div", {class: "it"}, el("b", {text: r[0]}), el("span", {text: r[1]}))); });
  add(root, as);
  s.beats = 3;
};

R.features = function (s, root, svg) {
  var P = s.panels, xs = [70, 440, 810, 1180];
  P.forEach(function (p, i) {
    var b = box(xs[i], 190, 350, 610, "card fpanel", i < 2 ? 0 : (i < 3 ? 1 : 2), (i % 2 * .1).toFixed(2));
    b.setAttribute("data-panel", i);
    add(b, el("h3", {text: p.t}), chip(p.tag));
    var asv = sv("svg", {width: 350, height: 250, viewBox: "0 0 350 250"}); add(b, asv);
    ANIM[p.anim](asv, b, p);
    add(b, el("ul", {}, p.b.map(function (t) { return el("li", {text: t}); })));
    clickable(b, function () { openDrawer({kicker: "Model-call feature", title: p.t, body: p.detail, list: p.b, tag: p.tag, src: p.src}); }, p.t);
    add(root, b);
  });
  G.focus = function (i) { later(function () { var p = root.querySelector('[data-panel="' + i + '"]'); if (!p) return; p.classList.add("focus"); later(function () { p.classList.remove("focus"); }, 5000); }, 600); };
  s.beats = 2;
};
var ANIM = {
  cache: function (svg) {
    function T(x, y, t, c) { var e = sv("text", {x: x, y: y, class: "svgt " + (c || ""), text: t}, svg); return e; }
    T(20, 22, "Request 1", "b"); T(20, 112, "Request 2 · same prefix", "b");
    var rows = [36, 126], prefix = [], dyn = [];
    rows.forEach(function (y, r) {
      sv("rect", {x: 20, y: y, width: 200, height: 34, rx: 5, fill: "rgba(167,139,250,.18)", stroke: "rgba(167,139,250,.5)"}, svg);
      prefix.push(sv("rect", {x: 20, y: y, width: 200, height: 34, rx: 5, fill: r ? COLORS.teal : COLORS.reduce, class: "grow", style: "transform:scaleX(0)"}, svg));
      sv("rect", {x: 226, y: y, width: 104, height: 34, rx: 5, fill: "rgba(56,189,248,.15)", stroke: "rgba(56,189,248,.45)"}, svg);
      dyn.push(sv("rect", {x: 226, y: y, width: 104, height: 34, rx: 5, fill: COLORS.hide, class: "grow", style: "transform:scaleX(0)"}, svg));
      var t1 = T(30, y + 22, "Stable prefix", "b"); t1.style.fontSize = "12.5px";
      var t2 = T(236, y + 22, "User turn", "b"); t2.style.fontSize = "12.5px";
    });
    var tag = T(20, 192, "", "t"); tag.style.fontSize = "13px"; tag.style.fontWeight = "700";
    var note = T(20, 214, "Instructions, tool definitions and schemas first;"); note.style.fontSize = "12px"; var note2 = T(20, 232, "identical, 1,024 tokens or more; dynamic content last"); note2.style.fontSize = "12px";
    function run() {
      prefix.concat(dyn).forEach(function (r) { r.style.transition = "none"; r.style.transform = "scaleX(0)"; });
      tag.textContent = "";
      void svg.getBoundingClientRect();
      later(function () { prefix[0].style.transition = "transform 1.6s linear"; prefix[0].style.transform = "scaleX(1)"; }, 100);
      later(function () { dyn[0].style.transition = "transform .8s linear"; dyn[0].style.transform = "scaleX(1)"; }, 1750);
      later(function () { prefix[1].style.transition = "transform .25s ease-out"; prefix[1].style.transform = "scaleX(1)"; tag.textContent = "Reused on repeat → cached_tokens in usage"; }, 2900);
      later(function () { dyn[1].style.transition = "transform .8s linear"; dyn[1].style.transform = "scaleX(1)"; }, 3200);
    }
    run(); every(run, 6200);
  },
  stream: function (svg) {
    function T(x, y, t, c) { return sv("text", {x: x, y: y, class: "svgt " + (c || ""), text: t}, svg); }
    function node(x, y, label, col) { sv("circle", {cx: x, cy: y, r: 15, fill: col}, svg); var t = T(x, y + 32, label); t.setAttribute("text-anchor", "middle"); t.style.fontSize = "12px"; }
    T(20, 24, "Default", "b"); T(20, 150, "Asynchronous", "b");
    var p1 = sv("path", {d: "M40,64 L160,64", stroke: "rgba(185,194,214,.3)", fill: "none"}, svg);
    var p2 = sv("path", {d: "M200,64 L310,64", stroke: "rgba(185,194,214,.3)", fill: "none"}, svg);
    sv("rect", {x: 155, y: 48, width: 50, height: 32, rx: 6, fill: "rgba(251,191,36,.25)", stroke: COLORS.steady}, svg);
    var bt = T(180, 100, "Filter buffer"); bt.setAttribute("text-anchor", "middle"); bt.style.fontSize = "12px";
    node(30, 64, "", COLORS.reduce); node(320, 64, "", COLORS.hide);
    var p3 = sv("path", {d: "M40,186 L310,186", stroke: "rgba(185,194,214,.3)", fill: "none"}, svg);
    var p4 = sv("path", {d: "M90,186 C120,222 230,222 260,200", stroke: "rgba(251,191,36,.6)", fill: "none", "stroke-dasharray": "4 4"}, svg);
    node(30, 186, "Model", COLORS.reduce); node(320, 186, "Client", COLORS.hide);
    var ft = T(20, 244, "Filters in parallel; flagged text removed afterwards"); ft.style.fontSize = "11.5px";
    var c1 = T(170, 124, "text in chunks, after filtering"); c1.setAttribute("text-anchor", "middle"); c1.style.fontSize = "11.5px";
    flow(p1, {layer: svg, every: 260, speed: 160, r: 3.5, color: COLORS.tealhi});
    flow(p2, {layer: svg, every: 1500, speed: 220, r: 3.5, color: COLORS.tealhi, burst: 5});
    flow(p3, {layer: svg, every: 260, speed: 160, r: 3.5, color: COLORS.tealhi});
    flow(p4, {layer: svg, every: 1800, speed: 120, r: 3, color: COLORS.steady});
  },
  caps: function (svg) {
    function T(x, y, t, c) { return sv("text", {x: x, y: y, class: "svgt " + (c || ""), text: t}, svg); }
    T(20, 26, "Uncapped", "b"); T(20, 116, "Capped, concise", "b");
    var rows = [[40, 30], [130, 13]], cells = [];
    rows.forEach(function (r, ri) {
      for (var i = 0; i < r[1]; i++) cells.push({e: sv("rect", {x: 20 + i * 10.4, y: r[0], width: 8, height: 30, rx: 2, fill: ri ? COLORS.teal : COLORS.reduce, opacity: .15}, svg), i: i});
      sv("line", {x1: 20 + r[1] * 10.4 + 2, y1: r[0] - 6, x2: 20 + r[1] * 10.4 + 2, y2: r[0] + 38, stroke: COLORS.steady, "stroke-width": 2}, svg);
      var lt = T(20 + r[1] * 10.4 - 2, r[0] + 54, "last token", "", "end"); lt.setAttribute("text-anchor", ri ? "start" : "end"); lt.style.fontSize = "12px"; lt.setAttribute("fill", COLORS.steady);
    });
    var tt = T(20, 214, "fewer tokens, earlier last token", "t"); tt.style.fontWeight = "700";
    function run() {
      cells.forEach(function (c) { c.e.setAttribute("opacity", .15); });
      cells.forEach(function (c) { later(function () { c.e.setAttribute("opacity", 1); }, 200 + c.i * 90); });
    }
    run(); every(run, 4200);
  },
  effort: function (svg, panel) {
    var levels = ["none", "minimal", "low", "medium", "high", "xhigh", "max"], lv = 0, auto = true;
    var bar = el("div", {class: "eff"}, levels.map(function (l, i) { return el("button", {text: l, "data-i": i, onclick: function (ev) { ev.stopPropagation(); auto = false; set(i); }}); }));
    add(panel, bar);
    function T(x, y, t, c) { return sv("text", {x: x, y: y, class: "svgt " + (c || ""), text: t}, svg); }
    T(20, 92, "Reasoning tokens", "b"); T(20, 158, "Visible answer", "b");
    sv("rect", {x: 20, y: 100, width: 310, height: 28, rx: 5, fill: "rgba(167,139,250,.12)"}, svg);
    var rb = sv("rect", {x: 20, y: 100, width: 310, height: 28, rx: 5, fill: COLORS.reduce, class: "grow", style: "transition:transform .6s cubic-bezier(.2,.7,.2,1);transform:scaleX(0)"}, svg);
    sv("rect", {x: 20, y: 166, width: 90, height: 28, rx: 5, fill: COLORS.teal}, svg);
    var lab = T(20, 222, "", "t"); lab.style.fontSize = "12.5px"; lab.style.fontWeight = "700";
    function set(i) {
      lv = i; bar.querySelectorAll("button").forEach(function (b, j) { b.classList.toggle("sel", j === i); });
      rb.style.transform = "scaleX(" + (i === 0 ? 0.015 : (0.1 + i * 0.15)) + ")";
      lab.textContent = i === 0 ? "none: answer starts almost at once" : "more reasoning tokens, longer call";
    }
    set(0); every(function () { if (auto) set((lv + 1) % levels.length); }, 1700);
    var cap = T(20, 244, "Illustrative; supported values vary by model"); cap.style.fontSize = "11.5px";
  }
};

