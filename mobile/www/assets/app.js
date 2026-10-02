/* 大数据闯关学习站 —— 纯前端，无外部依赖，离线可用 */
(function () {
  "use strict";

  var BD = window.BD || {};
  var D = {
    env: BD.env || null,
    exam: BD.exam || { levels: [], modules8: [] },
    kn: BD.knowledge || { modules: [], extra: [], intro: "" },
    cfg: BD.configs || { groups: [] },
    quiz: BD.quiz || { items: [], total: 0 },
    skills: BD.skills || { cats: [] },
    cp: BD.concepts || { groups: [], anims: [] },
    demo: BD.demo || { meta: {}, steps: [], imgs: [], pages: [] }
  };

  var view = document.getElementById("view");
  var sidebar = document.getElementById("sidebar");
  var nav = document.getElementById("nav");
  var PASS = 0.8;          // 通关线：正确率 80%
  var CONF_PASS = 10;      // 配置关：看过 10 个文件算通关

  /* ---------------- 工具 ---------------- */
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function el(id) { return document.getElementById(id); }
  function countConf() { var n = 0; D.cfg.groups.forEach(function (g) { n += g.files.length; }); return n; }
  function countCards() { var n = 0; D.skills.cats.forEach(function (c) { n += c.cards.length; }); return n; }
  function shortTitle(t) { return t.replace(/^[一二三四五六七八九十]+、/, ""); }

  /* ---------------- 进度（localStorage，按使用者隔离） ---------------- */
  // KEY 只存「全局设置」：当前使用者名；每个人的进度存在 bdstudy_v2::<名字> 下
  var KEY = "bdstudy_v2";
  var USER = "";
  function gset() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function gsave(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }
  function curKey() { return USER ? KEY + "::" + USER : KEY; }
  function prog() {
    try { return JSON.parse(localStorage.getItem(curKey())) || {}; } catch (e) { return {}; }
  }
  function save(p) { try { localStorage.setItem(curKey(), JSON.stringify(p)); } catch (e) {} }
  function setUser(name) {
    USER = String(name || "").trim();
    var g = gset();
    g.user = USER;
    g.users = g.users || [];
    if (USER && g.users.indexOf(USER) < 0) g.users.push(USER);
    gsave(g);
    updMe();
  }
  function allUsers() { return (gset().users || []).slice(); }
  function updMe() {
    var m = el("me");
    if (m) m.textContent = USER ? "👤 " + USER : "👤 未选择";
  }
  function userStat(u) {
    try {
      var d = JSON.parse(localStorage.getItem(KEY + "::" + u)) || {};
      return {
        read: (d.read || []).length,
        conf: (d.conf || []).length,
        cards: Object.keys(d.cSeen || {}).length,
        hist: (d.hist || []).length,
        shot: Object.keys(d.shot || {}).length,
        task: Object.keys(d.task || {}).length,
        best: d.best || {},
      };
    } catch (e) { return { read: 0, conf: 0, cards: 0, hist: 0, shot: 0, task: 0, best: {} }; }
  }
  function markRead(id) { var p = prog(); p.read = p.read || []; if (p.read.indexOf(id) < 0) { p.read.push(id); save(p); } }
  function markConf(name) { var p = prog(); p.conf = p.conf || []; if (p.conf.indexOf(name) < 0) { p.conf.push(name); save(p); } }
  function setBest(mod, s, n) {
    var p = prog(); p.best = p.best || {};
    var old = p.best[mod];
    if (!old || s / n > old.s / old.n) p.best[mod] = { s: s, n: n };
    save(p);
  }
  function taskKey(no, i) { return no + "-" + i; }
  function toggleTask(k) { var p = prog(); p.task = p.task || {}; p.task[k] = !p.task[k]; save(p); }
  function setLevelDone(no, v) { var p = prog(); p.lvl = p.lvl || {}; p.lvl[no] = v; save(p); }

  /* ---------------- 代码高亮 ---------------- */
  var SQL_KW = ("SELECT|FROM|WHERE|GROUP|BY|ORDER|HAVING|LIMIT|OFFSET|INSERT|INTO|VALUES|UPDATE|SET|DELETE|" +
    "CREATE|EXTERNAL|TABLE|DATABASE|SCHEMA|VIEW|DROP|ALTER|PARTITIONED|PARTITION|ROW|FORMAT|DELIMITED|" +
    "FIELDS|TERMINATED|LINES|STORED|TEXTFILE|LOCATION|LOAD|DATA|INPATH|OVERWRITE|LOCAL|USE|SHOW|TABLES|" +
    "GRANT|REVOKE|PRIVILEGES|FLUSH|IDENTIFIED|WITH|OPTION|USER|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|ON|UNION|ALL|" +
    "DISTINCT|COUNT|SUM|AVG|MAX|MIN|ROUND|CASE|WHEN|THEN|ELSE|END|NULL|NOT|DEFAULT|AUTO_INCREMENT|PRIMARY|KEY|" +
    "COMMENT|ENGINE|CHARSET|COLLATE|IF|EXISTS|AND|OR|IN|LIKE|BETWEEN|DESC|ASC|AS|INT|VARCHAR|DECIMAL|DOUBLE|" +
    "DATETIME|DATE|TEXT|BIGINT|FLOAT|CHAR|BOOLEAN").split("|");
  var JAVA_KW = ("public|private|protected|class|interface|extends|implements|static|final|void|new|return|" +
    "import|package|if|else|for|while|do|switch|case|break|continue|try|catch|finally|throw|throws|this|super|" +
    "null|true|false|int|long|double|float|boolean|char|String|var").split("|");
  var JS_KW = ("function|var|let|const|return|if|else|for|while|new|class|this|import|export|from|default|" +
    "true|false|null|undefined|typeof|async|await|document").split("|");

  var COM_PAT = {
    xml: /<!--[\s\S]*?-->/g,
    bash: /#[^\n]*/g,
    ini: /#[^\n]*/g,
    yaml: /#[^\n]*/g,
    text: /#[^\n]*/g,
    java: /\/\/[^\n]*|\/\*[\s\S]*?\*\//g,
    js: /\/\/[^\n]*|\/\*[\s\S]*?\*\//g,
    sql: /--[^\n]*|\/\*[\s\S]*?\*\//g,
    properties: /#[^\n]*/g
  };
  function kwRe(words) { return new RegExp("\\b(" + words.join("|") + ")\\b", "g"); }

  function paint(s, lang) {
    var t = esc(s), ph = [];
    function keep(html) { ph.push(html); return new Array(ph.length + 1).join("\u0001"); }
    function wrap(re, cls, pick) {
      t = t.replace(re, function (m) { return keep('<span class="' + cls + '">' + (pick ? pick(m) : m) + "</span>"); });
    }
    wrap(/(&quot;|")[^"\n]{0,300}?\1/g, "c-str");

    if (lang === "xml") {
      wrap(/&lt;\/?[a-zA-Z][\w.:-]*/g, "c-tag");
      wrap(/[\w.:-]+(?==)/g, "c-attr");
    } else if (lang === "sql") {
      wrap(/'[^'\n]{0,300}?'/g, "c-str");
      wrap(kwRe(SQL_KW), "c-kw");
      wrap(/\b\d+(?:\.\d+)?\b/g, "c-num");
    } else if (lang === "java") {
      wrap(kwRe(JAVA_KW), "c-kw");
      wrap(/\b\d+(?:\.\d+)?[fLdD]?\b/g, "c-num");
    } else if (lang === "js") {
      wrap(kwRe(JS_KW), "c-kw");
      wrap(/\b\d+(?:\.\d+)?\b/g, "c-num");
    } else if (lang === "bash") {
      wrap(/\$\{?[A-Za-z_][A-Za-z0-9_]*\}?/g, "c-var");
      wrap(/\b(export|if|then|else|elif|fi|for|in|do|done|echo|source|case|esac|function|return|local|while|set|cd|mkdir|chown|chmod|cat|sed|grep|java|nohup|scp|ssh|tar|mysql|mysqldump|sqoop|flink|hadoop|hdfs|spark-submit)\b/g, "c-kw");
      wrap(/^([ \t-]*)([A-Za-z_][\w.-]*)(?==)/gm, "c-key", function (m) { return m.replace(/^[ \t-]+/, ""); });
    } else {
      wrap(/^([ \t-]*)([A-Za-z_][\w.-]*)(?=[ \t]*[:=])/gm, "c-key", function (m) { return m.replace(/^[ \t-]+/, ""); });
      wrap(/\b\d+(?:\.\d+)?(?:[KMGT]B|ms|m|s)?\b/g, "c-num");
    }
    return t.replace(/\u0001+/g, function (m) { return ph[m.length - 1]; });
  }
  function highlight(code, lang) {
    var pat = COM_PAT[lang] || COM_PAT.text, out = "", last = 0, m;
    pat.lastIndex = 0;
    while ((m = pat.exec(code)) !== null) {
      out += paint(code.slice(last, m.index), lang) + '<span class="c-com">' + esc(m[0]) + "</span>";
      last = m.index + m[0].length;
    }
    return out + paint(code.slice(last), lang);
  }

  /* ---------------- 关卡体系 ---------------- */
  var MODICON = {
    hadoop: "🐘", hive: "🐝", spark: "⚡", flink: "🌊", docker: "🐳",
    kafka: "📨", sqoop: "🔄", flume: "🚰", zookeeper: "🦁"
  };
  function buildStages() {
    var p = prog(), st = [];

    st.push({
      no: 1, name: "认识赛场", tip: "先搞懂考什么、怎么评分",
      levels: [{
        id: "race", icon: "📜", title: "赛项规程与考核框架",
        desc: "八大任务模块 · 2025/2026 两届差异 · 展示讲解评分",
        href: "#/race", kind: "read", key: "race"
      }]
    });

    var cp = D.cp.groups.map(function (g) {
      return {
        id: "concept:" + g.id, icon: g.icon, title: g.name,
        desc: g.desc, href: "#/concept/" + g.id, kind: "concept", key: g.id
      };
    });
    st.push({ no: 2, name: "基础概念", tip: "零基础先看这个：大白话 + 图解动画，看懂再背", levels: cp });

    var th = D.kn.modules.map(function (m) {
      var b = (p.best || {})[m.id];
      return {
        id: "theory:" + m.id, icon: MODICON[m.id] || "📘", title: shortTitle(m.title),
        desc: "题库 " + m.count + " 题 · 正确率 ≥ 80% 通关",
        href: "#/knowledge/" + m.id, kind: "theory", key: m.id, best: b
      };
    });
    st.push({ no: 3, name: "理论闯关", tip: "九个模块逐块啃，练到 80% 再往下走", levels: th });

    st.push({
      no: 4, name: "配置实操", tip: "对照本机真实配置，看懂每一项为什么这么写；装完必须验证",
      levels: [
        {
          id: "config", icon: "⚙️", title: "24 个配置文件精读",
          desc: "Hadoop / Hive / Kafka / Spark / Flink / HBase / Redis …",
          href: "#/config", kind: "conf", key: "config"
        },
        {
          id: "verify", icon: "✅", title: "装完怎么验（14 个组件）",
          desc: "每个组件的验证命令 + 期望结果 + 截图点，验证截图 = 得分证据",
          href: "#/verify", kind: "read", key: "verify"
        }
      ]
    });

    var sk = D.skills.cats.map(function (c) {
      return {
        id: "skill:" + c.id, icon: c.icon, title: c.name,
        desc: c.desc, href: "#/skill/" + c.id, kind: "skill", key: c.id
      };
    });
    st.push({ no: 5, name: "技能实操", tip: "MySQL / pandas / 标注 / MR / Hive / Spark / 可视化 / 预测，逐项练代码", levels: sk });

    var ex = [];
    if (D.demo.steps && D.demo.steps.length) {
      ex.push({
        id: "demo", icon: "🎬", title: "真题示范 · 第 01 套（真跑一遍）",
        desc: "真实命令 + 真实输出 + 真实结果图，照着做一遍就通了",
        href: "#/demo", kind: "read", key: "demo"
      });
    }
    ex = ex.concat(D.exam.levels.map(function (l) {
      return {
        id: "exam:" + l.no, icon: "🎯", title: "第 " + pad(l.no) + " 套 · " + l.scene,
        desc: l.comps.join(" / ") + " · " + l.charts,
        href: "#/exam/" + l.no, kind: "exam", key: l.no
      };
    }));
    st.push({ no: 6, name: "赛题实战", tip: "十套真题当关卡打，练手速与熟练度", levels: ex });

    st.push({
      no: 7, name: "速查与范例", tip: "考前扫一遍，救回好几分",
      levels: [
        { id: "tool", icon: "🧰", title: "命令速查 + 避坑清单", desc: "常用命令 / 本机踩过的坑", href: "#/tool", kind: "read", key: "tool" },
        { id: "demo", icon: "🧪", title: "实训范例三件套", desc: "数据爬取 / 预测分析 / 大数据应用", href: "#/tool?p=demo", kind: "read", key: "demo" }
      ]
    });
    return st;
  }
  function pad(n) { return n < 10 ? "0" + n : "" + n; }

  function lstate(lv) {
    var p = prog();
    if (lv.kind === "read") {
      var done = (p.read || []).indexOf(lv.key) >= 0;
      return { done: done, ratio: done ? 1 : 0, label: done ? "已学习" : "未开始" };
    }
    if (lv.kind === "theory") {
      var b = (p.best || {})[lv.key];
      if (!b) return { done: false, ratio: 0, label: "未练习" };
      var r = b.s / b.n;
      return { done: r >= PASS, ratio: r, label: "最佳 " + b.s + "/" + b.n + "（" + Math.round(r * 100) + "%）" };
    }
    if (lv.kind === "conf") {
      var c = (p.conf || []).length, total = countConf() || 24;
      var r2 = Math.min(1, c / total);
      return { done: c >= CONF_PASS, ratio: r2, label: "已读 " + c + "/" + total + " 个文件" };
    }
    if (lv.kind === "concept") {
      var g = findGroup(lv.key);
      var tot2 = g ? g.cards.length : 0, sn = 0;
      for (var k2 = 0; k2 < tot2; k2++) { if ((p.cSeen || {})[cptKey(lv.key, k2)]) sn++; }
      var r5 = tot2 ? sn / tot2 : 0;
      return { done: tot2 > 0 && sn === tot2, ratio: r5, label: tot2 ? ("已看 " + sn + "/" + tot2) : "" };
    }
    if (lv.kind === "skill") {
      var cat = findCat(lv.key);
      var tot = cat ? cat.cards.length : 0, seenN = 0;
      for (var s = 0; s < tot; s++) { if ((p.cardSeen || {})[cardKey(lv.key, s)]) seenN++; }
      var r4 = tot ? seenN / tot : 0;
      return { done: tot > 0 && seenN === tot, ratio: r4, label: tot ? ("看过 " + seenN + "/" + tot + " 张卡") : "" };
    }
    if (lv.kind === "exam") {
      var lvinfo = findLevel(lv.key);
      var tot = lvinfo ? lvinfo.tasks.length : 0, doneN = 0;
      for (var i = 0; i < tot; i++) { if ((p.task || {})[taskKey(lv.key, i)]) doneN++; }
      var forced = (p.lvl || {})[lv.key];
      var r3 = tot ? doneN / tot : (forced ? 1 : 0);
      return { done: forced || (tot > 0 && doneN === tot), ratio: r3, label: tot ? ("子任务 " + doneN + "/" + tot) : "" };
    }
    return { done: false, ratio: 0, label: "" };
  }
  function cptKey(gid, i) { return "cp-" + gid + "-" + i; }
  function markCpt(k) { var p = prog(); p.cSeen = p.cSeen || {}; if (!p.cSeen[k]) { p.cSeen[k] = 1; save(p); } }
  function findGroup(id) {
    for (var i = 0; i < D.cp.groups.length; i++) if (D.cp.groups[i].id === id) return D.cp.groups[i];
    return null;
  }
  function findAnim(key) {
    for (var i = 0; i < D.cp.anims.length; i++) if (D.cp.anims[i].key === key) return D.cp.anims[i];
    return null;
  }
  function cardKey(cat, i) { return cat + "-" + i; }
  function markCard(k) { var p = prog(); p.cardSeen = p.cardSeen || []; if (p.cardSeen.indexOf(k) < 0) { p.cardSeen.push(k); save(p); } }
  function findCat(id) {
    for (var i = 0; i < D.skills.cats.length; i++) if (D.skills.cats[i].id === id) return D.skills.cats[i];
    return null;
  }
  function findLevel(no) {
    for (var i = 0; i < D.exam.levels.length; i++) if (D.exam.levels[i].no === parseInt(no, 10)) return D.exam.levels[i];
    return null;
  }

  function overview() {
    var st = buildStages(), done = 0, tot = 0;
    st.forEach(function (s) { s.levels.forEach(function (l) { tot++; if (lstate(l).done) done++; }); });
    return { done: done, total: tot, pct: tot ? Math.round(done / tot * 100) : 0 };
  }
  function ringSvg(pct, size) {
    size = size || 104;
    var c = size / 2, r = c - 9, cir = 2 * Math.PI * r;
    return '<svg width="' + size + '" height="' + size + '">' +
      '<circle cx="' + c + '" cy="' + c + '" r="' + r + '" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="9"/>' +
      '<circle cx="' + c + '" cy="' + c + '" r="' + r + '" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-dasharray="' + cir + '" stroke-dashoffset="' + (cir * (1 - pct / 100)) + '"/></svg>';
  }
  function cheer(pct) {
    if (pct === 0) return "从第一关开始，一步步来 💪";
    if (pct < 25) return "开了个好头，继续保持 🔥";
    if (pct < 55) return "进度过半前，先把理论啃完 📚";
    if (pct < 80) return "不错，开始刷真题练手速 ⏱️";
    if (pct < 100) return "冲刺阶段，查漏补缺 🎯";
    return "全部通关，赛场上见！🏆";
  }

  /* ---------------- 路由 ---------------- */
  function parseHash() {
    var h = location.hash.replace(/^#\/?/, ""), q = "", i = h.indexOf("?");
    if (i >= 0) { q = h.slice(i + 1); h = h.slice(0, i); }
    var parts = h.split("/");
    return { route: parts[0] || "home", arg: parts[1] ? decodeURIComponent(parts[1]) : "", query: q };
  }
  function go(h) { location.hash = h; }
  function setNav(r) {
    var as = nav.querySelectorAll("a"), map = { quiz: "knowledge" };
    for (var i = 0; i < as.length; i++) {
      as[i].className = as[i].getAttribute("data-r") === (map[r] || r) ? "on" : "";
    }
  }
  /* ---------------- 进站口令门 ----------------
     GitHub Pages 是纯静态托管，做不了服务端校验（nginx Basic Auth 那套用不上）。
     这里的做法是：进站先输口令，口令只存 SHA-256 摘要，输对了才渲染内容。
     它能挡住随手点开链接的人，但挡不住懂技术的人 —— 要真正拦得住，见页面里的说明。 */
  function gateCfg() { return (window.BD && window.BD.gate) || { on: false }; }
  function gatePassed() {
    var g = gateCfg();
    try { return !g.on || localStorage.getItem("bdstudy_gate") === g.hash; } catch (e) { return false; }
  }
  var SHA_K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  function sha256(str) {
    var H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var m = unescape(encodeURIComponent(str)), bytes = [], i, j;
    for (i = 0; i < m.length; i++) bytes.push(m.charCodeAt(i));
    bytes.push(0x80);
    while (bytes.length % 64 !== 56) bytes.push(0);
    var bits = m.length * 8;
    bytes.push(0, 0, 0, 0, (bits >>> 24) & 255, (bits >>> 16) & 255, (bits >>> 8) & 255, bits & 255);
    var w = new Array(64);
    for (var b = 0; b < bytes.length; b += 64) {
      for (j = 0; j < 16; j++) {
        w[j] = (bytes[b + j * 4] << 24) | (bytes[b + j * 4 + 1] << 16) | (bytes[b + j * 4 + 2] << 8) | bytes[b + j * 4 + 3];
      }
      for (j = 16; j < 64; j++) {
        var x = w[j - 15], y = w[j - 2];
        var s0 = ((x >>> 7) | (x << 25)) ^ ((x >>> 18) | (x << 14)) ^ (x >>> 3);
        var s1 = ((y >>> 17) | (y << 15)) ^ ((y >>> 19) | (y << 13)) ^ (y >>> 10);
        w[j] = (w[j - 16] + s0 + w[j - 7] + s1) | 0;
      }
      var a = H[0], bb = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (j = 0; j < 64; j++) {
        var S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
        var ch = (e & f) ^ ((~e) & g);
        var t1 = (h + S1 + ch + SHA_K[j] + w[j]) | 0;
        var S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
        var maj = (a & bb) ^ (a & c) ^ (bb & c);
        var t2 = (S0 + maj) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = bb; bb = a; a = (t1 + t2) | 0;
      }
      H[0] = (H[0] + a) | 0; H[1] = (H[1] + bb) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
      H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }
    var out = "";
    for (i = 0; i < 8; i++) {
      for (j = 7; j >= 0; j--) out += ((H[i] >>> (j * 4)) & 15).toString(16);
    }
    return out;
  }
  function renderGate(err) {
    var g = gateCfg();
    sidebar.innerHTML = "";
    view.innerHTML =
      '<div class="gate"><div class="gate-box">' +
      '<div class="gate-logo">🔒</div>' +
      "<h1>大数据应用与服务 · 闯关学习站</h1>" +
      '<p class="gate-sub">本站点需要口令才能进入' + (g.hint ? "（" + esc(g.hint) + "）" : "") + "</p>" +
      '<input id="gateIn" class="cs-inp" type="password" placeholder="请输入口令" autocomplete="off">' +
      '<button class="btn" id="gateGo">进入</button>' +
      (err ? '<p class="gate-err">✗ ' + esc(err) + "</p>" : "") +
      '<p class="gate-tip">口令只在你这台浏览器里记一次（localStorage），换浏览器要重新输。</p>' +
      "</div></div>";
    var go = function () {
      var v = el("gateIn").value.trim();
      if (!v) return;
      if (sha256(v) === g.hash) {
        try { localStorage.setItem("bdstudy_gate", g.hash); } catch (e) {}
        render();
      } else {
        renderGate("口令不对，再试一次");
      }
    };
    el("gateGo").onclick = go;
    el("gateIn").onkeydown = function (e2) { if (e2.key === "Enter" || e2.keyCode === 13) go(); };
    el("gateIn").focus();
  }

  function render() {
    if (!gatePassed()) { renderGate(""); return; }
    var r = parseHash();
    setNav(r.route);
    window.scrollTo(0, 0);
    if (!D.env) { view.innerHTML = '<div class="empty">数据未加载：请确认 data/*.js 与 index.html 在同一目录。</div>'; return; }
    switch (r.route) {
      case "race": renderRace(); break;
      case "knowledge": renderKnowledge(r.arg); break;
      case "config": renderConfig(r.arg); break;
      case "concept": renderConcept(r.arg, r.query); break;
      case "verify": renderVerify(r.arg); break;
      case "skill": renderSkill(r.arg); break;
      case "exam": renderExam(r.arg, r.query); break;
      case "tool": renderTool(r.query); break;
      case "demo": renderDemo(); break;
      case "me": renderMe(); break;
      case "quiz": renderQuiz(r.query); break;
      case "search": renderSearch(r.query); break;
      default: renderHome();
    }
    remember();
  }
  function remember() {
    var h = location.hash;
    if (!h || /#\/(home|search)/.test(h)) return;
    var t = view.querySelector("h1.page");
    if (!t) return;
    var p = prog(); p.last = { h: h, t: t.textContent.trim() }; save(p);
  }

  /* ---------------- 首页：学习地图 ---------------- */
  function renderHome() {
    var ov = overview(), p = prog();
    var hist = p.hist || [];

    // 侧栏
    var links = buildStages().map(function (s) {
      return '<div class="side-group"><div class="g-name">' + s.no + "、" + s.name + "</div>" +
        s.levels.map(function (l) {
          return '<a href="' + l.href + '">' + l.title + '<span class="badge">' + (lstate(l).done ? "✓" : "") + "</span></a>";
        }).join("") + "</div>";
    }).join("");
    sidebar.innerHTML = '<div class="side-title">全部关卡</div>' + links;

    // 今日一题
    var dq = D.quiz.items[Math.floor(Math.random() * D.quiz.items.length)];

    var stages = buildStages().map(function (s) {
      var cards = s.levels.map(function (l) {
        var stt = lstate(l);
        return '<a class="lv' + (stt.done ? " done" : "") + '" href="' + l.href + '">' +
          '<div class="licon">' + l.icon + "</div>" +
          '<div class="lbody"><div class="ltitle">' + l.title +
          (stt.done ? ' <span class="star">⭐</span>' : "") +
          (stt.label ? ' <span class="pill b">' + stt.label + "</span>" : "") + "</div>" +
          '<div class="ldesc">' + esc(l.desc) + "</div>" +
          '<div class="lbar"><i style="width:' + Math.round(stt.ratio * 100) + '%"></i></div></div>' +
          '<div class="lgoto">' + (stt.done ? "再看 →" : "进入 →") + "</div></a>";
      }).join("");
      return '<div class="stage"><div class="stage-head"><div class="sno">' + s.no + "</div>" +
        "<h2>" + s.name + '</h2><div class="stip">' + s.tip + "</div></div>" + cards + "</div>";
    }).join("");

    var resume = p.last ? '<a class="resume" href="' + p.last.h + '"><b>继续上次学习</b>　' +
      esc(p.last.t) + '<span>→</span></a>' : "";

    view.innerHTML =
      '<div class="hero">' +
      "<h1>大数据应用与服务 · 闯关学习站</h1>" +
      "<p>规程 → 理论 → 配置 → 技能 → 真题 → 速查，六阶段 " + ov.total + " 关。每关都有明确通关线，练完就能上场。</p>" +
      '<div class="nums">' +
      "<div><b>" + D.quiz.total + "</b><span>题库题目</span></div>" +
      "<div><b>" + countCards() + "</b><span>实操代码卡</span></div>" +
      "<div><b>" + countConf() + "</b><span>真实配置文件</span></div>" +
      "<div><b>" + D.exam.levels.length + "</b><span>真题关卡</span></div>" +
      "<div><b>" + ov.done + " / " + ov.total + "</b><span>已通关</span></div>" +
      "</div>" +
      '<div class="ring">' + ringSvg(ov.pct) + '<div class="txt"><b>' + ov.pct + '%</b><span>总进度</span></div></div>' +
      "</div>" +

      resume +
      (USER ? "" : '<a class="me-banner" href="#/me">👤 还没选使用者 —— 多人共用这台电脑的话，点这里填个名字，进度就各存各的（不影响使用，随时可跳过）</a>') +
      '<div class="daily"><div class="dh">🎲 今日一题' +
      '<span class="pill b" style="margin-left:auto">' + dq.module + " · " + dq.type + " · " + dq.difficulty + "</span></div>" +
      '<div class="q">' + esc(dq.stem) + "</div>" +
      '<div class="opts" id="dqOpts"></div><div class="res" id="dqRes"></div></div>' +

      stages +

      '<div class="card"><h2><span class="no">i</span>你的战绩</h2>' +
      '<div class="grid4">' +
      statBox(ov.pct + "%", "总进度 · " + cheer(ov.pct)) +
      statBox((p.cardSeen || []).length, "已掌握实操卡 / " + countCards()) +
      statBox((p.conf || []).length, "已读配置文件 / " + countConf()) +
      statBox(hist.length ? Math.round(hist[0].s / hist[0].n * 100) + "%" : "—", "最近正确率 · 自测 " + hist.length + " 次") +
      "</div></div>";

    // 今日一题交互
    var box = el("dqOpts"), res = el("dqRes");
    var optsHtml = "";
    if (dq.type === "判断") {
      optsHtml = '<button data-k="Y">✔ 正确</button><button data-k="N">✘ 错误</button>';
    } else {
      optsHtml = dq.options.map(function (o) { return '<button data-k="' + o.key + '">' + o.key + ". " + esc(o.text) + "</button>"; }).join("");
    }
    box.innerHTML = optsHtml + '<button id="dqNext" style="margin-left:auto">换一题 ↻</button>';
    var btns = box.querySelectorAll("button[data-k]");
    for (var i = 0; i < btns.length; i++) {
      btns[i].onclick = function () {
        var k = this.getAttribute("data-k");
        var right = dq.type === "判断" ? (dq.answer === k) : (k === dq.answer);
        res.className = "res " + (right ? "ok" : "no");
        res.innerHTML = (right ? "✅ 答对了！" : "❌ 答错了，正确答案：" + (dq.type === "判断" ? (dq.answer === "Y" ? "正确" : "错误") : dq.answer)) +
          '　<a href="#/knowledge/' + dq.module.toLowerCase() + '">看知识点 →</a>';
      };
    }
    el("dqNext").onclick = function () { render(); };
  }
  function statBox(n, t) {
    return '<div class="mini"><div class="mt" style="font-size:24px;font-weight:800;color:var(--brand)">' + n + "</div>" +
      '<div class="md">' + t + "</div></div>";
  }

  /* ---------------- 认识赛场 ---------------- */
  function renderRace() {
    markRead("race");
    var e = D.exam;
    sidebar.innerHTML = '<div class="side-title">本页</div><div class="side-group">' +
      "<a>八大任务模块</a><a>两届规程差异</a><a>展示讲解评分</a><a>资料四层</a><a>备赛策略</a>" +
      '<a href="#/exam">去刷真题 →</a></div>';

    var m8 = e.modules8.map(function (m) {
      return '<div class="mini"><div class="mi">' + m.icon + '</div><div class="mt">' + m.name + "</div>" +
        '<div class="md">' + m.desc + "</div></div>";
    }).join("");

    var rd = '<table><thead><tr><th>' + e.ruleDiff.head[0] + "</th><th>" + e.ruleDiff.head[1] +
      "</th><th>" + e.ruleDiff.head[2] + "</th></tr></thead><tbody>" +
      e.ruleDiff.rows.map(function (r) { return "<tr><td><b>" + r[0] + "</b></td><td>" + r[1] + "</td><td>" + r[2] + "</td></tr>"; }).join("") +
      "</tbody></table>";

    var ss = e.showScore.map(function (r) {
      return "<tr><td>" + r[0] + '</td><td><b style="color:var(--brand)">' + r[1] + " 分</b></td></tr>";
    }).join("");

    var s4 = e.sources4.map(function (r) { return "<tr><td><b>" + r[0] + "</b></td><td>" + r[1] + "</td><td>" + r[2] + "</td></tr>"; }).join("");

    var stg = e.strategy.map(function (s) {
      return '<div class="mini"><div class="mt">' + s.t + '</div><div class="md">' + s.d + "</div></div>";
    }).join("");

    var adv = e.advice.map(function (a) {
      return '<div class="lv" style="cursor:default"><div class="licon">' + a.n + '</div><div class="lbody">' +
        '<div class="ltitle">' + a.t + '</div><div class="ldesc" style="white-space:normal">' + a.d + "</div></div></div>";
    }).join("");

    view.innerHTML =
      '<h1 class="page">认识赛场：考什么、怎么评分</h1>' +
      '<p class="sub">先建立整体认知，再动手训练。这一页全部来自资料库里的赛项规程与备赛总览。</p>' +

      '<div class="card"><h2><span class="no">1</span>八大考核任务模块</h2>' +
      '<div class="grid4">' + m8 + "</div>" +
      '<p style="font-size:13.5px;color:var(--ink3);margin:14px 0 0">操作技能按模块拆子任务，单项分值常见 5 / 10 / 15 / 20 分；' +
      "数据库运行维护与数据分析与可视化是分值最集中的区域，职业素养单独占 5%。</p></div>" +

      '<div class="card"><h2><span class="no">2</span>2025 / 2026 两届规程差异</h2>' + rd +
      '<div class="warn-item" style="margin-top:14px"><b>要提前适应两点：</b>教师组取消展示讲解；学生组操作时长增加 15 分钟（2h45m → 3h）。</div></div>' +

      '<div class="grid2">' +
      '<div class="card"><h2><span class="no">3</span>展示讲解评分维度</h2><table><tbody>' + ss + "</tbody></table></div>" +
      '<div class="card"><h2><span class="no">4</span>资料四层拼图</h2><table><tbody>' + s4 + "</tbody></table></div>" +
      "</div>" +

      '<div class="card"><h2><span class="no">5</span>备赛策略：规程与真题的落差</h2><div class="grid2">' + stg + "</div></div>" +

      '<div class="card"><h2><span class="no">6</span>四步使用建议</h2>' + adv + "</div>";
  }

  /* ---------------- 理论闯关 ---------------- */
  function renderKnowledge(arg) {
    var mods = D.kn.modules.concat(D.kn.extra), cur = null;
    for (var i = 0; i < mods.length; i++) if (mods[i].id === arg) cur = mods[i];
    if (!cur) cur = mods[0];
    markRead(cur.id);

    var p = prog(), b = (p.best || {})[cur.id];
    var links = D.kn.modules.map(function (m) {
      var bb = (p.best || {})[m.id];
      var okk = bb && bb.s / bb.n >= PASS;
      return '<a href="#/knowledge/' + m.id + '"' + (m.id === cur.id ? ' class="on"' : "") + ">" +
        shortTitle(m.title) + '<span class="badge">' + (okk ? "⭐" : m.count) + "</span></a>";
    }).join("");
    var links2 = D.kn.extra.map(function (m) {
      return '<a href="#/knowledge/' + m.id + '"' + (m.id === cur.id ? ' class="on"' : "") + ">" + shortTitle(m.title) + "</a>";
    }).join("");
    sidebar.innerHTML = '<div class="side-title">理论关卡（按题量）</div><div class="side-group">' + links + "</div>" +
      '<div class="side-title">综合</div><div class="side-group">' + links2 + "</div>";

    var tmp = document.createElement("div");
    tmp.innerHTML = cur.html;
    var h3s = tmp.querySelectorAll("h3"), toc = "";
    if (h3s.length > 1) {
      var items = [];
      for (var j = 0; j < h3s.length; j++) {
        h3s[j].id = "sec" + j;
        items.push('<a href="javascript:;" data-sec="sec' + j + '">' + h3s[j].textContent + "</a>");
      }
      toc = '<div class="side-title">本页目录</div><div class="side-group">' + items.join("") + "</div>";
    }

    var isMod = cur.count > 0;
    var bar = isMod ? '<div class="card" style="padding:16px 20px">' +
      '<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">' +
      "<div><b style=\"font-size:16px\">通关线：正确率 ≥ 80%</b>" +
      '<div style="font-size:13px;color:var(--ink3)">' + (b ? "你的最佳：" + b.s + "/" + b.n + "（" + Math.round(b.s / b.n * 100) + "%）" : "还没练过，先来一组") + "</div></div>" +
      '<div style="flex:1;min-width:180px"><div class="lbar" style="max-width:none"><i style="width:' + (b ? Math.round(b.s / b.n * 100) : 0) + '%"></i></div></div>' +
      (b && b.s / b.n >= PASS ? '<span class="pass">已通关 ⭐</span>' : "") +
      '<a class="btn" href="#/quiz?m=' + cur.id + '" style="margin-left:auto">开始练习 →</a>' +
      "</div></div>" : "";

    view.innerHTML =
      '<h1 class="page">' + cur.title.replace(/^[一二三四五六七八九十]+、/, "") + "</h1>" +
      '<p class="sub">' + (cur.count ? "对应题库 " + cur.count + " 题" : "综合提升") + "</p>" +
      bar +
      '<div class="card doc">' + tmp.innerHTML + "</div>";

    sidebar.innerHTML += toc;
    var tl = sidebar.querySelectorAll("[data-sec]");
    for (var k = 0; k < tl.length; k++) {
      tl[k].onclick = function () { var t = el(this.getAttribute("data-sec")); if (t) t.scrollIntoView({ behavior: "smooth", block: "start" }); };
    }
  }

  /* ---------------- 装完怎么验（验证可用性清单） ---------------- */
  var VF = (D.env && D.env.verify) || { intro: {}, rules: [], items: [] };
  function findVerify(id) {
    for (var i = 0; i < VF.items.length; i++) if (VF.items[i].id === id) return VF.items[i];
    return null;
  }
  // 文件名 / 分类名 → 验证项 id（用于自动挂载【备注】）
  var VMAP = [
    [/jdk|java/i, "jdk"],
    [/core-site|hdfs-site|yarn-site|mapred-site|workers|hadoop/i, "hadoop"],
    [/zoo.cfg|zookeeper|zk/i, "zk"],
    [/my.cnf|mysql/i, "mysql"],
    [/hive/i, "hive"],
    [/kafka|server.properties|producer|consumer/i, "kafka"],
    [/spark/i, "spark"],
    [/flink/i, "flink"],
    [/hbase/i, "hbase"],
    [/flume/i, "flume"],
    [/sqoop/i, "sqoop"],
    [/redis/i, "redis"],
    [/python|pandas|matplotlib|seaborn|pyecharts|sklearn/i, "python"],
    [/docker|compose|nginx/i, "docker"],
  ];
  function verifyOf(text) {
    for (var i = 0; i < VMAP.length; i++) { if (VMAP[i][0].test(text)) return findVerify(VMAP[i][1]); }
    return null;
  }
  function verifySteps(v, limit) {
    var arr = limit ? v.steps.slice(0, limit) : v.steps;
    return arr.map(function (s) {
      return '<div class="vstep"><div class="vc">' + esc(s.cmd) + "</div>" +
        '<div class="ve">期望：<b>' + esc(s.expect) + "</b></div>" +
        '<div class="vs">📷 ' + esc(s.shot) + "</div></div>";
    }).join("");
  }
  function verifyNote(v) {
    if (!v) return "";
    var more = v.steps.length > 2 ? '<a class="btn ghost sm" href="#/verify">看完整 ' + v.steps.length + " 步 →</a>" : "";
    return '<div class="vnote">' +
      '<div class="vhead"><b>【备注】' + v.icon + " " + esc(v.name) + ' 装完必须验证可用性</b>' +
      '<span class="pill m">验证截图 = 得分证据</span>' + more + "</div>" +
      '<div class="vpre">' + esc(v.pre) + "</div>" +
      verifySteps(v, 3) +
      (v.pit ? '<div class="vpit">⚠️ ' + esc(v.pit) + "</div>" : "") +
      "</div>";
  }

  function renderVerify(arg) {
    var links = VF.items.map(function (v) {
      return '<a href="#/verify/' + v.id + '"' + (v.id === arg ? ' class="on"' : "") + ">" +
        v.icon + " " + v.name + '<span class="badge">' + v.steps.length + " 步</span></a>";
    }).join("");
    sidebar.innerHTML = '<div class="side-title">验证清单（' + VF.items.length + "）</div>" +
      '<div class="side-group">' + links + "</div>" +
      '<div class="side-title">相关</div><div class="side-group">' +
      '<a href="#/config">配置文件精读</a><a href="#/skill">技能实操</a><a href="#/tool">命令速查</a></div>';

    var intro = VF.intro || {};
    var head =
      '<h1 class="page">✅ 装完怎么验 · 验证可用性清单</h1>' +
      '<p class="sub">' + esc(intro.why || "") + "</p>" +
      '<div class="card" style="padding:14px 20px">' +
      '<div class="vpre" style="margin:0 0 8px">顺序：' + esc(intro.order || "") + "</div>" +
      '<div style="font-size:14px;color:var(--ink2)">硬规矩：<b>' + esc(intro.rule || "") + "</b></div></div>" +
      '<div class="card"><h2><span class="no">📷</span>截图规范（不合规会被扣分）</h2>' +
      VF.rules.map(function (r) {
        return '<div class="cmd"><div class="c" style="font-family:inherit">' + esc(r.t) + '</div><div class="d">' + esc(r.d) + "</div></div>";
      }).join("") + "</div>";

    if (!arg) {
      var cards = VF.items.map(function (v) {
        return '<div class="card vcard"><h2><span class="no">' + v.icon + "</span>" + esc(v.name) +
          '<span class="pill b" style="margin-left:8px;font-weight:400">' + v.steps.length + " 步</span>" +
          '<a class="btn ghost sm" href="#/verify/' + v.id + '" style="margin-left:auto">展开 →</a></h2>' +
          '<div class="vpre">' + esc(v.pre) + "</div>" + verifySteps(v, 2) + "</div>";
      }).join("");
      view.innerHTML = head + cards;
      return;
    }
    var v = findVerify(arg);
    if (!v) { view.innerHTML = head; return; }
    view.innerHTML = head +
      '<h1 class="page">' + v.icon + " " + esc(v.name) + " · 完整验证步骤</h1>" +
      '<div class="card vcard"><h2><span class="no">▶</span>验证步骤（' + v.steps.length + " 步）</h2>" +
      '<div class="vpre">' + esc(v.pre) + "</div>" + verifySteps(v, 0) +
      (v.pit ? '<div class="vpit">⚠️ ' + esc(v.pit) + "</div>" : "") + "</div>";
  }

  function shotKey(no, i) { return "s-" + no + "-" + i; }
  function toggleShot(k) { var p = prog(); p.shot = p.shot || {}; p.shot[k] = !p.shot[k]; save(p); }

  function examFlow(lv) {
    var p = prog(), out = "";
    /* 完整操作流程 */
    if (lv.steps && lv.steps.length) {
      var byPhase = {}, order = [];
      lv.steps.forEach(function (s) {
        if (!byPhase[s.p]) { byPhase[s.p] = []; order.push(s.p); }
        byPhase[s.p].push(s);
      });
      out += '<div class="card"><h2><span class="no">🗺️</span>完整操作流程（照着做就能做完）</h2>' +
        order.map(function (ph) {
          return '<div class="phase"><b>' + ph + "（" + byPhase[ph].length + " 步）</b>" +
            '<ol class="flow">' + byPhase[ph].map(function (s) {
              return '<li><div class="ft">' + esc(s.t) + '</div><div class="fd">' + esc(s.d) + "</div></li>";
            }).join("") + "</ol></div>";
        }).join("") + "</div>";
    }
    /* 关键命令 */
    if (lv.cmds && lv.cmds.length) {
      out += '<div class="card"><h2><span class="no">$</span>关键命令（可直接复制）</h2>' +
        lv.cmds.map(function (c, i) {
          return '<div class="cmdt"><b>' + esc(c.t) + "</b></div>" + codeBlock(c.code, c.lang || "bash", "ex" + lv.no + i);
        }).join("") + "</div>";
    }
    /* 截图证据清单 */
    if (lv.shots && lv.shots.length) {
      var n = 0;
      var items = lv.shots.map(function (s, i) {
        var on = (p.shot || {})[shotKey(lv.no, i)];
        if (on) n++;
        return '<div class="shot' + (on ? " on" : "") + '" data-s="' + shotKey(lv.no, i) + '">' +
          '<div class="box">' + (on ? "✓" : "") + '</div><div class="tt">📷 ' + esc(s) + "</div></div>";
      }).join("");
      out += '<div class="card"><h2><span class="no">📷</span>截图证据清单（打勾记录，' + n + " / " + lv.shots.length + "）</h2>" +
        '<p class="sub" style="margin:0 0 10px">赛场按结果给分：<b>验证过程的截图就是得分证据</b>。做完一步截一张，别攒到最后。</p>' +
        items + "</div>";
    }
    /* 本套总结 */
    if (lv.summary) {
      var sm = lv.summary;
      out += '<div class="card"><h2><span class="no">📌</span>本套总结</h2>' +
        '<div class="sm-focus">' + esc(sm.focus) + "</div>" +
        '<div class="sm-sec"><b>⏱ 时间怎么分</b><div>' + esc(sm.time) + "</div></div>" +
        '<div class="sm-sec"><b>⚠️ 易错点</b><ul class="cp-pts">' +
        sm.traps.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul></div>" +
        '<div class="sm-sec"><b>✅ 交卷前自查</b><ul class="cp-pts">' +
        sm.check.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul></div></div>";
    }
    return out;
  }

  /* ---------------- 配置实操 ---------------- */
  function renderConfig(arg) {
    var all = [];
    D.cfg.groups.forEach(function (g) { g.files.forEach(function (f) { all.push({ g: g, f: f }); }); });
    var cur = null;
    for (var i = 0; i < all.length; i++) if (all[i].f.name === arg) cur = all[i];
    if (!cur) cur = all[0];
    markConf(cur.f.name);

    var p = prog(), seen = (p.conf || []).length, total = countConf();
    var links = D.cfg.groups.map(function (g) {
      var fs = g.files.map(function (f) {
        return '<a href="#/config/' + encodeURIComponent(f.name) + '"' + (f.name === cur.f.name ? ' class="on"' : "") + ">" +
          f.name + '<span class="badge">' + ((p.conf || []).indexOf(f.name) >= 0 ? "✓" : "") + "</span></a>";
      }).join("");
      return '<div class="side-group"><div class="g-name">' + g.name + "</div>" + fs + "</div>";
    }).join("");
    sidebar.innerHTML = '<div class="side-title">已读 ' + seen + " / " + total + "</div>" + links +
      '<div class="side-title">重要</div><div class="side-group">' +
      '<a href="#/verify">✅ 装完怎么验（必看）</a></div>';

    var note = verifyNote(verifyOf(cur.f.name + " " + cur.g.name));

    view.innerHTML =
      '<h1 class="page">配置实操 · ' + cur.f.name + "</h1>" +
      '<p class="sub">' + cur.g.name + "　·　共 " + total + " 个文件，左侧切换　·　注释写明「是什么 / 本机值 / 为什么」</p>" +
      note +
      '<div class="card">' +
      '<div class="code-head">' +
      '<span class="fname">' + cur.f.name + '</span><span class="fpath">' + cur.f.path + "</span>" +
      '<button class="copybtn" id="copyBtn">复制全文</button>' +
      '<div class="fdesc">' + cur.f.desc + "　·　" + cur.f.lines + " 行</div></div>" +
      '<pre class="code"><code>' + highlight(cur.f.content, cur.f.lang) + "</code></pre>" +
      '<p style="font-size:13px;color:var(--ink3);margin:13px 0 0">灰色斜体是注释，其余是生效配置。' +
      "<b>改配置只改值、别删注释</b>；改完要重启服务才生效。</p></div>";

    var cb = el("copyBtn");
    if (cb) cb.onclick = function () {
      var ta = document.createElement("textarea");
      ta.value = cur.f.content; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); cb.textContent = "已复制 ✓"; } catch (e) { cb.textContent = "复制失败"; }
      document.body.removeChild(ta);
      setTimeout(function () { cb.textContent = "复制全文"; }, 1600);
    };
  }

  /* ---------------- 技能实操 ---------------- */
  var LANGNAME = { python: "Python", sql: "SQL", bash: "Shell", java: "Java", js: "JavaScript", xml: "XML", properties: "配置", text: "要点" };

  function codeBlock(code, lang, idx) {
    var id = "cb" + idx;
    return '<div class="codeblk">' +
      '<div class="cbhead"><span class="cblang">' + (LANGNAME[lang] || lang) + "</span>" +
      '<button class="copybtn2" data-copy="' + id + '">复制</button>' +
      '<button class="foldbtn" data-fold="' + id + '">收起</button></div>' +
      '<pre class="code" id="' + id + '"><code>' + highlight(code, lang) + "</code></pre></div>";
  }
  function bindCodeBlocks() {
    var bs = document.querySelectorAll("[data-copy]");
    for (var i = 0; i < bs.length; i++) {
      bs[i].onclick = function () {
        var pre = el(this.getAttribute("data-copy"));
        var ta = document.createElement("textarea");
        ta.value = pre.textContent;
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); this.textContent = "已复制 ✓"; } catch (e) { this.textContent = "失败"; }
        document.body.removeChild(ta);
        var b = this;
        setTimeout(function () { b.textContent = "复制"; }, 1500);
      };
    }
    var fs = document.querySelectorAll("[data-fold]");
    for (var j = 0; j < fs.length; j++) {
      fs[j].onclick = function () {
        var pre = el(this.getAttribute("data-fold"));
        var hidden = pre.style.display === "none";
        pre.style.display = hidden ? "" : "none";
        this.textContent = hidden ? "收起" : "展开";
      };
    }
  }

  /* ---------------- 基础概念（大白话 + 图解动画） ---------------- */
  function mdInline(s) {
    return esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  }

  function animSvg(a) {
    var NW = 118, NH = 46, PAD = 30, i, j, maxX = 0, maxY = 0;
    for (i = 0; i < a.nodes.length; i++) { maxX = Math.max(maxX, a.nodes[i].x); maxY = Math.max(maxY, a.nodes[i].y); }
    var W = maxX + NW + PAD, H = maxY + NH + PAD, cx = {}, cy = {};
    for (i = 0; i < a.nodes.length; i++) { cx[a.nodes[i].id] = a.nodes[i].x + NW / 2; cy[a.nodes[i].id] = a.nodes[i].y + NH / 2; }

    var s = '<svg class="anim-svg" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="xMidYMid meet">';
    s += '<defs><marker id="ar-' + a.key + '" markerWidth="9" markerHeight="8" refX="8" refY="3" orient="auto">' +
      '<path d="M0,0 L0,6 L9,3 z" fill="#8a97c4"/></marker></defs>';
    for (i = 0; i < a.edges.length; i++) {
      var e = a.edges[i], x1 = cx[e.f], y1 = cy[e.f], x2 = cx[e.t], y2 = cy[e.t];
      var dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx * dx + dy * dy) || 1, ux = dx / len, uy = dy / len;
      var sx = x1 + ux * (NW / 2 + 5), sy = y1 + uy * (NH / 2 + 5);
      var ex2 = x2 - ux * (NW / 2 + 10), ey2 = y2 - uy * (NH / 2 + 10);
      s += '<path class="anim-edge" data-e="' + i + '" marker-end="url(#ar-' + a.key + ')" d="M' +
        sx.toFixed(1) + "," + sy.toFixed(1) + " L" + ex2.toFixed(1) + "," + ey2.toFixed(1) + '"/>';
      s += '<text class="anim-elabel" data-el="' + i + '" x="' + ((sx + ex2) / 2).toFixed(1) +
        '" y="' + ((sy + ey2) / 2 - 7).toFixed(1) + '" text-anchor="middle">' + esc(e.l) + "</text>";
    }
    for (i = 0; i < a.nodes.length; i++) {
      var n = a.nodes[i], lines = String(n.t).split("\n");
      s += '<g class="anim-node" data-n="' + n.id + '"><rect x="' + n.x + '" y="' + n.y +
        '" width="' + NW + '" height="' + NH + '" rx="10"/>';
      for (j = 0; j < lines.length; j++) {
        s += '<text class="anim-ntext" x="' + (n.x + NW / 2) + '" y="' +
          (n.y + (lines.length > 1 ? 20 + j * 16 : NH / 2 + 5)) + '" text-anchor="middle">' + esc(lines[j]) + "</text>";
      }
      s += "</g>";
    }
    return s + "</svg>";
  }

  function animBlock(a) {
    var dots = a.steps.map(function (_, i) { return "<i" + (i === 0 ? ' class="on"' : "") + "></i>"; }).join("");
    return '<div class="anim" data-anim="' + a.key + '">' +
      '<div class="anim-head"><b>' + esc(a.title) + '</b><span class="pill b">图解动画 · ' + a.steps.length + " 步</span>" +
      '<span class="anim-btns">' +
      '<button class="btn ghost sm" data-ap="prev">← 上一步</button>' +
      '<button class="btn sm" data-ap="play">▶ 自动播放</button>' +
      '<button class="btn ghost sm" data-ap="next">下一步 →</button>' +
      "</span></div>" +
      '<div class="anim-stage">' + animSvg(a) + "</div>" +
      '<div class="anim-ctl"><div class="anim-dots">' + dots + '</div><div class="anim-step">第 <b>1</b> / ' + a.steps.length + " 步</div></div>" +
      '<div class="anim-say">' + esc(a.steps[0].say) + "</div>" +
      '<div class="anim-sum">💡 ' + esc(a.summary) + "</div>" +
      "</div>";
  }

  function initAnim(box) {
    var a = findAnim(box.getAttribute("data-anim"));
    if (!a) return;
    var cur = 0, timer = null, svg = box.querySelector("svg");
    function pick(sel) { return svg.querySelectorAll(sel); }
    function paint() {
      var st = a.steps[cur], i;
      var es = pick("[data-e]");
      for (i = 0; i < es.length; i++) {
        var on = st.e.indexOf(parseInt(es[i].getAttribute("data-e"), 10)) >= 0;
        es[i].setAttribute("class", "anim-edge" + (on ? " on" : ""));
      }
      var ls = pick("[data-el]");
      for (i = 0; i < ls.length; i++) {
        ls[i].setAttribute("class", "anim-elabel" + (st.e.indexOf(parseInt(ls[i].getAttribute("data-el"), 10)) >= 0 ? " on" : ""));
      }
      var ns = pick("[data-n]");
      for (i = 0; i < ns.length; i++) {
        ns[i].setAttribute("class", "anim-node" + (st.n.indexOf(ns[i].getAttribute("data-n")) >= 0 ? " on" : ""));
      }
      var dots = box.querySelectorAll(".anim-dots i");
      for (i = 0; i < dots.length; i++) dots[i].setAttribute("class", i <= cur ? "on" : "");
      var sp = box.querySelector(".anim-step b"); if (sp) sp.textContent = String(cur + 1);
      var say = box.querySelector(".anim-say"); if (say) say.textContent = st.say;
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
      var pb = box.querySelector('[data-ap="play"]'); if (pb) pb.textContent = "▶ 自动播放";
    }
    function set(i) { cur = (i + a.steps.length) % a.steps.length; paint(); }
    var bs = box.querySelectorAll("[data-ap]");
    for (var b = 0; b < bs.length; b++) {
      bs[b].onclick = function () {
        var w = this.getAttribute("data-ap");
        if (w === "next") { stop(); set(cur + 1); }
        else if (w === "prev") { stop(); set(cur - 1); }
        else {
          if (timer) { stop(); return; }
          this.textContent = "⏸ 暂停";
          timer = setInterval(function () { set(cur + 1); }, 2400);
          set(cur === a.steps.length - 1 ? 0 : cur + 1);
        }
      };
    }
    var ds = box.querySelectorAll(".anim-dots i");
    for (var d = 0; d < ds.length; d++) {
      ds[d].onclick = (function (k) { return function () { stop(); set(k); }; })(d);
    }
    paint();
  }

  function renderConcept(arg, query) {
    var gs = D.cp.groups, cur = null, i;
    for (i = 0; i < gs.length; i++) if (gs[i].id === arg) cur = gs[i];
    if (arg && !cur) { view.innerHTML = '<div class="empty">没有这一关</div>'; return; }
    var p = prog();

    function glink(list) {
      return list.map(function (g) {
        var stt = lstate({ kind: "concept", key: g.id });
        return '<a href="#/concept/' + g.id + '"' + (cur && g.id === cur.id ? ' class="on"' : "") + ">" +
          g.icon + " " + g.name + '<span class="badge">' + (stt.done ? "✓" : g.cards.length + " 卡") + "</span></a>";
      }).join("");
    }
    var core = gs.slice(0, 6), base = gs.slice(6);
    sidebar.innerHTML =
      '<div class="side-title">大数据本体（6）</div><div class="side-group">' + glink(core) + "</div>" +
      (base.length ? '<div class="side-title">零基础四大件（' + base.length + "）</div><div class=\"side-group\">" + glink(base) + "</div>" : "") +
      '<div class="side-title">下一步</div><div class="side-group">' +
      '<a href="#/verify">✅ 装完怎么验</a><a href="#/knowledge">去理论闯关</a><a href="#/config">看真实配置</a><a href="#/race">赛项规程</a></div>';

    if (!cur) {
      function tile(g) {
        var stt = lstate({ kind: "concept", key: g.id });
        var hasA = g.anims && g.anims.length ? '<span class="pill m">🎬 ' + g.anims.length + " 个动画</span>" : "";
        return '<a class="cp-tile" href="#/concept/' + g.id + '">' +
          '<div class="cp-ico">' + g.icon + "</div>" +
          "<div><b>" + esc(g.name) + "</b><p>" + esc(g.desc) + "</p>" +
          '<div class="cp-meta">' + g.cards.length + " 张卡 " + hasA +
          '<span class="pill ' + (stt.done ? "ok" : "mutex") + '">' + (stt.done ? "已通关" : stt.label || "未开始") + "</span></div>" +
          "</div></a>";
      }
      var coreG = gs.slice(0, 6), baseG = gs.slice(6);
      var tiles =
        '<div class="sec-h">一、大数据本体：先搞懂这些词在说什么</div><div class="cp-grid">' + coreG.map(tile).join("") + "</div>" +
        (baseG.length ? '<div class="sec-h">二、零基础四大件：没接触过就从这几关开始</div><div class="cp-grid">' + baseG.map(tile).join("") + "</div>" : "");
      var tot = 0, seen = 0;
      gs.forEach(function (g) { tot += g.cards.length; });
      for (var k in (p.cSeen || {})) if (p.cSeen[k]) seen++;
      view.innerHTML =
        '<h1 class="page">🌱 基础概念 · 先看懂，再去背</h1>' +
        '<p class="sub">零基础同学从这儿开始：每张卡都是「大白话一句 + 考点几句」，带 🎬 的还有分步骤图解动画。共 ' +
        gs.length + " 关 / " + tot + " 张卡 / " + D.cp.anims.length + " 个动画。</p>" +
        '<div class="card" style="padding:14px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap">' +
        "<div><b>总进度</b>　<span class=\"pill b\">" + seen + " / " + tot + "</span></div>" +
        '<div style="flex:1;min-width:180px"><div class="lbar" style="max-width:none"><i style="width:' +
        Math.round(tot ? seen / tot * 100 : 0) + '%"></i></div></div></div>' +
        tiles +   // tiles 自带分区标题 + cp-grid，这里不能再套一层 cp-grid（会挤成一列）
        '<div class="card"><h2><span class="no">💡</span>怎么学这一关</h2>' +
        '<ul class="cp-pts"><li>先读 <b>大白话</b> 那一句，用自己的话复述一遍</li>' +
        "<li>再考点睛那几条，尤其是带 ⚠️ 的陷阱判断题</li>" +
        "<li>带动画的，点「自动播放」看一遍流程，再手动一步步点，边点边说步骤</li>" +
        "<li>看完点「我看懂了」，全关看完才算通关</li></ul></div>";
      return;
    }

    var stt = lstate({ kind: "concept", key: cur.id }), seenN = 0;
    var cards = cur.cards.map(function (c, idx) {
      var ok = (p.cSeen || {})[cptKey(cur.id, idx)];
      if (ok) seenN++;
      var pts = c.points.map(function (d) { return "<li>" + mdInline(d) + "</li>"; }).join("");
      return '<div class="card cp-card' + (ok ? " seen" : "") + '">' +
        '<h2><span class="no">' + (idx + 1) + "</span>" + esc(c.t) +
        '<span class="pill b" style="margin-left:8px;font-weight:400">来源：' + esc(c.src) + "</span>" +
        '<button class="btn ghost sm" data-cpt="' + cptKey(cur.id, idx) + '" style="margin-left:auto">' +
        (ok ? "已看懂 ✓" : "我看懂了") + "</button></h2>" +
        '<div class="cp-plain"><span class="tag">大白话</span>' + mdInline(c.plain) + "</div>" +
        '<ul class="cp-pts">' + pts + "</ul></div>";
    }).join("");

    var anims = (cur.anims || []).map(function (k) {
      var a = findAnim(k);
      return a ? animBlock(a) : "";
    }).join("");

    var gi = gs.indexOf(cur);
    var prev = gi > 0 ? '<a class="btn ghost" href="#/concept/' + gs[gi - 1].id + '">← ' + gs[gi - 1].name + "</a>" : "";
    var next = gi < gs.length - 1 ? '<a class="btn" href="#/concept/' + gs[gi + 1].id + '">' + gs[gi + 1].name + " →</a>"
      : '<a class="btn" href="#/knowledge">去理论闯关 →</a>';

    view.innerHTML =
      '<h1 class="page">' + cur.icon + " " + esc(cur.name) + "</h1>" +
      '<p class="sub">' + esc(cur.desc) + "　·　共 " + cur.cards.length + " 张概念卡" +
      ((cur.anims || []).length ? "，" + cur.anims.length + " 个图解动画" : "") + "</p>" +
      '<div class="card" style="padding:14px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap">' +
      "<div><b>阅读进度</b>　<span class=\"pill b\">" + seenN + " / " + cur.cards.length + "</span></div>" +
      '<div style="flex:1;min-width:180px"><div class="lbar" style="max-width:none"><i style="width:' +
      Math.round(stt.ratio * 100) + '%"></i></div></div>' +
      (stt.done ? '<span class="pass">已通关 ⭐</span>' : "") + "</div>" +
      anims + cards +
      '<div style="display:flex;gap:10px;flex-wrap:wrap">' + prev + next + "</div>";

    var cbs = view.querySelectorAll("[data-cpt]");
    for (i = 0; i < cbs.length; i++) {
      cbs[i].onclick = function () { markCpt(this.getAttribute("data-cpt")); render(); };
    }
    var ab = view.querySelectorAll(".anim");
    for (i = 0; i < ab.length; i++) initAnim(ab[i]);
  }

  function renderSkill(arg) {
    var cats = D.skills.cats, cur = null;
    for (var i = 0; i < cats.length; i++) if (cats[i].id === arg) cur = cats[i];
    if (!cur) cur = cats[0];
    var p = prog();

    var links = cats.map(function (c) {
      var stt = lstate({ kind: "skill", key: c.id });
      return '<a href="#/skill/' + c.id + '"' + (c.id === cur.id ? ' class="on"' : "") + ">" +
        c.icon + " " + c.name + '<span class="badge">' + (stt.done ? "✓" : c.cards.length) + "</span></a>";
    }).join("");
    sidebar.innerHTML = '<div class="side-title">十类实操技能</div><div class="side-group">' + links + "</div>" +
      '<div class="side-title">相关</div><div class="side-group">' +
      '<a href="#/verify">✅ 装完怎么验（必看）</a>' +
      '<a href="#/config">配置文件精读</a><a href="#/exam">十套真题</a><a href="#/tool">命令速查</a></div>';

    var seenN = 0;
    var cards = cur.cards.map(function (c, i) {
      var seen = (p.cardSeen || {})[cardKey(cur.id, i)];
      if (seen) seenN++;
      var pts = c.d.map(function (d) { return "<li>" + esc(d) + "</li>"; }).join("");
      return '<div class="card sk-card' + (seen ? " seen" : "") + '">' +
        '<h2><span class="no">' + (i + 1) + "</span>" + esc(c.t) +
        '<span class="pill b" style="margin-left:8px;font-weight:400">来源：' + esc(c.src) + "</span>" +
        '<button class="btn ghost sm" data-seen="' + cardKey(cur.id, i) + '" style="margin-left:auto">' + (seen ? "已掌握 ✓" : "标记掌握") + "</button></h2>" +
        '<ul class="sk-pts">' + pts + "</ul>" +
        codeBlock(c.code, c.lang, cur.id + i) +
        "</div>";
    }).join("");

    var stt = lstate({ kind: "skill", key: cur.id });
    var SVID = { linux: "hadoop", mysql: "mysql", pandas: "python", label: "hadoop", collect: "flume", mr: "hadoop", hive: "hive", spark: "spark", vis: "python", ml: "python" };
    var note = verifyNote(findVerify(SVID[cur.id]));

    view.innerHTML =
      '<h1 class="page">' + cur.icon + " " + cur.name + "</h1>" +
      '<p class="sub">' + esc(cur.desc) + '　·　共 ' + cur.cards.length + " 张卡，看完即通关</p>" +
      note +
      '<div class="card" style="padding:14px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap">' +
      "<div><b>掌握进度</b>　<span class=\"pill b\">" + seenN + " / " + cur.cards.length + "</span></div>" +
      '<div style="flex:1;min-width:180px"><div class="lbar" style="max-width:none"><i style="width:' + Math.round(stt.ratio * 100) + '%"></i></div></div>' +
      (stt.done ? '<span class="pass">已通关 ⭐</span>' : "") +
      "</div>" + cards;

    bindCodeBlocks();
    var sb = view.querySelectorAll("[data-seen]");
    for (var j = 0; j < sb.length; j++) {
      sb[j].onclick = function () {
        var k = this.getAttribute("data-seen");
        markCard(k);
        render();
      };
    }
  }

  /* ---------------- 赛题实战 ---------------- */
  function renderExam(arg, query) {
    var p = prog();
    var links = D.exam.levels.map(function (l) {
      var stt = lstate({ kind: "exam", key: l.no });
      return '<a href="#/exam/' + l.no + '"' + (String(l.no) === String(arg) ? ' class="on"' : "") + ">" +
        "第 " + pad(l.no) + " 套 · " + l.scene + '<span class="badge">' + (stt.done ? "✓" : stt.label) + "</span></a>";
    }).join("");
    sidebar.innerHTML = '<div class="side-title">十套真题关卡</div><div class="side-group">' + links + "</div>" +
      '<div class="side-title">相关</div><div class="side-group">' +
      '<a href="#/tool?p=demo">实训范例</a><a href="#/race">赛项规程</a></div>';

    if (!arg) {
      var rows = D.exam.levels.map(function (l) {
        var stt = lstate({ kind: "exam", key: l.no });
        return "<tr><td><b>第 " + pad(l.no) + ' 套</b></td><td>' + l.scene + "</td><td>" +
          l.comps.map(function (c) { return '<span class="pill b" style="margin-right:4px">' + c + "</span>"; }).join("") +
          "</td><td>" + l.charts + "</td><td>" + l.tasks.length + " 项</td><td>" +
          (stt.done ? '<span class="pass">已通关</span>' : '<span class="pill ' + (stt.ratio > 0 ? "m" : "mutex") + '">' + stt.label + "</span>") +
          '</td><td><a href="#/exam/' + l.no + '">进入 →</a></td></tr>';
      }).join("");

      var tr = D.exam.training.map(function (t) {
        return '<div class="cmd"><div class="c" style="font-family:inherit">' + t.skill + '</div><div class="d">出现在 ' + t.sets + "</div></div>";
      }).join("");

      view.innerHTML =
        '<h1 class="page">赛题实战 · ZZ052 十套真题</h1>' +
        '<p class="sub">每套 = 一个关卡：模块一装环境 / 模块二取数与处理 / 模块三分析与出图。点进去按子任务清单逐项打勾。</p>' +
        '<div class="card"><h2><span class="no">▤</span>十套速查表</h2>' +
        '<table><thead><tr><th>套次</th><th>数据场景</th><th>模块一核心组件</th><th>模块三出图路线</th><th>子任务</th><th>进度</th><th></th></tr></thead><tbody>' +
        rows + "</tbody></table></div>" +
        '<div class="card"><h2><span class="no">↻</span>跨套共性：按技能专项练</h2>' + tr + "</div>";
      return;
    }

    var lv = findLevel(arg);
    if (!lv) { view.innerHTML = '<div class="empty">没有这一套</div>'; return; }
    var stt = lstate({ kind: "exam", key: lv.no });
    var doneN = 0;
    for (var i = 0; i < lv.tasks.length; i++) if ((p.task || {})[taskKey(lv.no, i)]) doneN++;

    var tasks = lv.tasks.map(function (t, i) {
      var on = (p.task || {})[taskKey(lv.no, i)];
      if (on) doneN = doneN;
      return '<div class="task' + (on ? " on" : "") + '" data-t="' + taskKey(lv.no, i) + '">' +
        '<div class="box">' + (on ? "✓" : "") + '</div><div class="tt">' + esc(t) + "</div></div>";
    }).join("");

    var prev = lv.no > 1 ? '<a class="btn ghost" href="#/exam/' + (lv.no - 1) + '">← 第 ' + pad(lv.no - 1) + " 套</a>" : "";
    var next = lv.no < 10 ? '<a class="btn" href="#/exam/' + (lv.no + 1) + '">第 ' + pad(lv.no + 1) + " 套 →</a>" : '<a class="btn" href="#/exam">回列表</a>';

    view.innerHTML =
      '<h1 class="page">第 ' + pad(lv.no) + " 套 · " + lv.scene + "</h1>" +
      '<p class="sub">模块一组件：' + lv.comps.join(" / ") + "　·　模块三出图：" + lv.charts + "</p>" +
      '<div class="card" style="padding:16px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap">' +
      "<div><b>子任务进度</b>　<span class=\"pill b\">" + doneN + " / " + lv.tasks.length + "</span></div>" +
      '<div style="flex:1;min-width:180px"><div class="lbar" style="max-width:none"><i style="width:' + Math.round(doneN / lv.tasks.length * 100) + '%"></i></div></div>' +
      (stt.done ? '<span class="pass">已通关 ⭐</span>' : "") +
      '<button class="btn ghost" id="btnDone">' + (stt.done ? "取消通关标记" : "标记本套已练完") + "</button>" +
      "</div>" +
      '<div class="card"><h2><span class="no">✓</span>子任务清单（点击打勾，自动保存）</h2>' + tasks + "</div>" +
      examFlow(lv) +
      '<div style="display:flex;gap:10px;flex-wrap:wrap">' + prev + next + "</div>";

    bindCodeBlocks();
    var ss = view.querySelectorAll(".shot");
    for (var m = 0; m < ss.length; m++) {
      ss[m].onclick = function () {
        var k = this.getAttribute("data-s");
        toggleShot(k);
        this.classList.toggle("on");
        var bx = this.querySelector(".box");
        bx.textContent = this.classList.contains("on") ? "✓" : "";
      };
    }
    var ts = view.querySelectorAll(".task");
    for (var j = 0; j < ts.length; j++) {
      ts[j].onclick = function () {
        var k = this.getAttribute("data-t");
        toggleTask(k);
        this.classList.toggle("on");
        var bx = this.querySelector(".box");
        bx.textContent = this.classList.contains("on") ? "✓" : "";
        render();
      };
    }
    el("btnDone").onclick = function () { setLevelDone(lv.no, !(p.lvl || {})[lv.no]); render(); };
  }

  /* ---------------- 速查手册 ---------------- */
  function renderTool(query) {
    markRead("tool");
    var anchor = query && /p=demo/.test(query) ? "demo" : "";
    sidebar.innerHTML = '<div class="side-title">本页</div><div class="side-group">' +
      '<a href="#/tool">常用命令速查</a><a href="#/tool?p=demo">实训范例三件套</a><a href="#/tool">避坑清单</a></div>' +
      '<div class="side-title">配套</div><div class="side-group">' +
      '<a href="#/verify">✅ 装完怎么验（必看）</a><a href="#/concept">零基础四大件</a></div>';

    var secs = [], seenSec = {};
    D.env.commands.forEach(function (g) {
      if (!seenSec[g.sec]) { seenSec[g.sec] = 1; secs.push(g.sec); }
    });
    var total = 0;
    D.env.commands.forEach(function (g) { total += g.cmds.length; });

    var tabs = secs.map(function (s, i) {
      return '<button class="tabb' + (i === 0 ? " on" : "") + '" data-tab="' + i + '">' + esc(s) + "</button>";
    }).join("");
    var panes = secs.map(function (s, i) {
      var gs = D.env.commands.filter(function (g) { return g.sec === s; });
      return '<div class="pane" data-pane="' + i + '"' + (i === 0 ? "" : ' style="display:none"') + ">" +
        gs.map(function (g) {
          return '<div class="card"><h2><span class="no">$</span>' + esc(g.group) +
            '<span class="pill b" style="margin-left:8px;font-weight:400">' + g.cmds.length + " 条</span></h2>" +
            g.cmds.map(function (c) {
              var hi = /^★/.test(c[0]), warn = /^⚠/.test(c[0]);
              return '<div class="cmd' + (hi ? " hi" : "") + (warn ? " warn" : "") + '">' +
                '<div class="c">' + esc(c[0]) + '</div><div class="d">' + esc(c[1]) + "</div></div>";
            }).join("") + "</div>";
        }).join("") + "</div>";
    }).join("");

    var cmds =
      '<div class="card"><h2><span class="no">$</span>常用命令速查（' + D.env.commands.length + " 组 / " + total + " 条）</h2>" +
      '<input id="csFilter" class="cs-inp" placeholder="过滤命令，例如：mkdir / groupby / redis / 联合主键 …">' +
      '<div class="tabs">' + tabs + "</div>" + panes +
      '<p class="sub" style="margin:10px 0 0">★ = 必须记熟　⚠ = 高危或易错。面向零基础：先看 Linux 与赛场通用两栏。</p></div>';

    var demos = D.exam.demos.map(function (d) {
      return '<div class="card"><h2><span class="no">' + d.icon + "</span>" + d.name +
        '<span class="pill b" style="margin-left:8px;font-weight:400">' + d.tools + "</span></h2>" +
        "<ol>" + d.steps.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ol>" +
        '<pre class="code" style="margin-top:12px;max-height:none"><code>' + highlight(d.code, "bash") + "</code></pre></div>";
    }).join("");

    var tips = D.kn.extra.filter(function (m) { return m.id === "tips"; })[0];
    var cmp = D.kn.extra.filter(function (m) { return m.id === "compare"; })[0];
    markRead("demo");

    view.innerHTML =
      '<h1 class="page">速查手册</h1>' +
      '<p class="sub">命令 + 范例 + 避坑，考前扫一遍</p>' +
      (anchor === "demo" ? "" : "") +
      demos +
      cmds +
      '<div class="card" id="pit"><h2><span class="no">!</span>本机环境五条硬规矩</h2>' +
      D.env.warn.map(function (w, i) { return '<div class="warn-item"><b>' + (i + 1) + ".</b> " + w + "</div>"; }).join("") + "</div>" +
      (cmp ? '<div class="card"><h2><span class="no">⇄</span>跨模块易混点对比</h2><div class="doc">' + cmp.html + "</div></div>" : "") +
      (tips ? '<div class="card"><h2><span class="no">★</span>备考建议</h2><div class="doc">' + tips.html + "</div></div>" : "");

    var tbs = view.querySelectorAll("[data-tab]");
    for (var ti = 0; ti < tbs.length; ti++) {
      tbs[ti].onclick = function () {
        var k = this.getAttribute("data-tab"), a;
        var bs = view.querySelectorAll("[data-tab]");
        for (a = 0; a < bs.length; a++) bs[a].setAttribute("class", "tabb" + (bs[a] === this ? " on" : ""));
        var ps = view.querySelectorAll("[data-pane]");
        for (a = 0; a < ps.length; a++) ps[a].style.display = ps[a].getAttribute("data-pane") === k ? "" : "none";
        filterCs();
      };
    }
    var fi = el("csFilter");
    if (fi) fi.oninput = filterCs;
    function filterCs() {
      var inp = el("csFilter"), kw = inp ? (inp.value || "").trim().toLowerCase() : "";
      var vis = view.querySelectorAll("[data-pane]");
      for (var a = 0; a < vis.length; a++) {
        if (vis[a].style.display === "none") continue;
        var rows = vis[a].querySelectorAll(".cmd");
        for (var b = 0; b < rows.length; b++) {
          var txt = rows[b].textContent.toLowerCase();
          rows[b].style.display = (!kw || txt.indexOf(kw) >= 0) ? "" : "none";
        }
        var cards = vis[a].querySelectorAll(".card");
        for (var c = 0; c < cards.length; c++) {
          var any = false, rs = cards[c].querySelectorAll(".cmd");
          for (var d = 0; d < rs.length; d++) if (rs[d].style.display !== "none") any = true;
          cards[c].style.display = any ? "" : "none";
        }
      }
    }

    if (anchor === "demo") {
      var t = view.querySelector(".card");
      if (t) t.scrollIntoView({ block: "start" });
    }
  }

  /* ---------------- 在线练习 ---------------- */
  var Q = { list: [], answers: {}, submitted: false, showAns: false };
  function renderQuiz(query) {
    var preset = "";
    if (query) { var mm = /m=([^&]+)/.exec(query); if (mm) preset = decodeURIComponent(mm[1]); }
    var mods = ["all"].concat(D.kn.modules.map(function (m) { return m.id; }));
    var modOpts = mods.map(function (m) {
      var label = m === "all" ? "全部模块" : m;
      var n = m === "all" ? D.quiz.total : D.quiz.items.filter(function (q) { return q.module.toLowerCase() === m; }).length;
      return '<option value="' + m + '"' + (m === preset ? " selected" : "") + ">" + label + "（" + n + "题）</option>";
    }).join("");

    sidebar.innerHTML = '<div class="side-title">题库</div><div class="side-group">' +
      "<a>共 " + D.quiz.total + " 题</a>" +
      "<a>单选 " + cnt("单选") + " · 多选 " + cnt("多选") + " · 判断 " + cnt("判断") + "</a>" +
      "<a>易 " + cntD("易") + " · 中 " + cntD("中") + " · 难 " + cntD("难") + "</a></div>" +
      '<div class="side-title">按模块开练</div><div class="side-group">' +
      D.kn.modules.map(function (m) { return '<a href="#/quiz?m=' + m.id + '">' + shortTitle(m.title) + '<span class="badge">' + m.count + "</span></a>"; }).join("") +
      "</div>";

    view.innerHTML =
      '<h1 class="page">在线练习</h1>' +
      '<p class="sub">题目来自赛项理论题库 · 交卷后自动判分，单模块正确率 ≥ 80% 即通关</p>' +
      '<div class="card"><div class="filters">' +
      "<label>模块<select id=\"fMod\">" + modOpts + "</select></label>" +
      '<label>题型<select id="fType"><option value="all">全部</option><option value="单选">单选</option><option value="多选">多选</option><option value="判断">判断</option></select></label>' +
      '<label>难度<select id="fDiff"><option value="all">全部</option><option value="易">易</option><option value="中">中</option><option value="难">难</option></select></label>' +
      '<label>题量<select id="fNum"><option value="10">10 题</option><option value="20" selected>20 题</option><option value="50">50 题</option><option value="999">全部</option></select></label>' +
      '<label style="flex-direction:row;align-items:center;gap:6px"><input type="checkbox" id="fShuffle" checked> 随机打乱</label>' +
      '<button class="btn" id="btnStart">开始练习</button></div>' +
      '<div id="paper"></div></div>';

    el("btnStart").onclick = startQuiz;
    if (preset) startQuiz();
  }
  function cnt(t) { return D.quiz.items.filter(function (q) { return q.type === t; }).length; }
  function cntD(d) { return D.quiz.items.filter(function (q) { return q.difficulty === d; }).length; }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function startQuiz() {
    var m = el("fMod").value, t = el("fType").value, d = el("fDiff").value;
    var n = parseInt(el("fNum").value, 10), sh = el("fShuffle").checked;
    var pool = D.quiz.items.filter(function (q) {
      if (m !== "all" && q.module.toLowerCase() !== m) return false;
      if (t !== "all" && q.type !== t) return false;
      if (d !== "all" && q.difficulty !== d) return false;
      return true;
    });
    if (!pool.length) { el("paper").innerHTML = '<div class="empty">这个组合没有题目，换个筛选试试。</div>'; return; }
    if (sh) pool = shuffle(pool.slice());
    Q.list = pool.slice(0, Math.min(n, pool.length));
    Q.answers = {}; Q.submitted = false; Q.showAns = false;
    drawPaper();
  }
  function findQ(id) { for (var i = 0; i < Q.list.length; i++) if (Q.list[i].id === id) return Q.list[i]; return { id: id, type: "单选", answer: "" }; }
  function isRight(q) { return (Q.answers[q.id] || []).join("") === q.answer; }
  function qhtml(q, i) {
    var opts = "";
    if (q.type === "判断") {
      opts = ["Y", "N"].map(function (k) {
        var on = (Q.answers[q.id] || []).indexOf(k) >= 0;
        return '<div class="opt' + (on ? " sel" : "") + '" data-q="' + q.id + '" data-k="' + k + '">' +
          '<span class="k">' + (k === "Y" ? "√" : "×") + "</span><span>" + (k === "Y" ? "正确" : "错误") + "</span></div>";
      }).join("");
    } else {
      opts = q.options.map(function (o) {
        var on = (Q.answers[q.id] || []).indexOf(o.key) >= 0;
        return '<div class="opt' + (on ? " sel" : "") + '" data-q="' + q.id + '" data-k="' + o.key + '">' +
          '<span class="k">' + o.key + "</span><span>" + esc(o.text) + "</span></div>";
      }).join("");
    }
    var cls = Q.submitted ? (isRight(q) ? " right" : " wrong") : (Q.showAns ? " right" : "");
    var ansline = "";
    if (Q.submitted || Q.showAns) {
      var mine = (Q.answers[q.id] || []).join("") || "未作答";
      var right = q.type === "判断" ? (q.answer === "Y" ? "正确" : "错误") : q.answer;
      ansline = '<div class="ansline">你的答案：<span class="' + (isRight(q) ? "ok" : "no") + '">' + esc(mine) + "</span>" +
        '　正确答案：<span class="ok">' + esc(right) + "</span>" +
        (isRight(q) ? "" : '　<a href="#/knowledge/' + q.module.toLowerCase() + '">看知识点 →</a>') + "</div>";
    }
    return '<div class="qcard' + cls + '" id="q' + q.id + '">' +
      '<div class="qmeta"><span>第 ' + (i + 1) + " 题</span><span class=\"pill m\">" + q.module + "</span>" +
      '<span class="pill ' + ({ "易": "e", "中": "m", "难": "h" }[q.difficulty] || "m") + '">' + q.difficulty + "</span>" +
      "<span>" + q.type + "</span><span>#" + q.id + "</span></div>" +
      '<div class="qstem">' + esc(q.stem) + "</div>" + opts + ansline + "</div>";
  }
  function drawPaper() {
    var box = el("paper");
    box.innerHTML =
      '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:14px">' +
      '<b>共 ' + Q.list.length + " 题</b>" +
      '<label style="font-size:13px;color:var(--ink3);display:flex;gap:6px;align-items:center"><input type="checkbox" id="fShowAns"> 背题模式（直接看答案）</label>' +
      '<button class="btn" id="btnSubmit" style="margin-left:auto">交卷判分</button>' +
      '<button class="btn ghost" id="btnReset">重新抽题</button></div>' +
      '<div id="qlist">' + Q.list.map(function (q, i) { return qhtml(q, i); }).join("") + "</div>";
    el("btnSubmit").onclick = submitQuiz;
    el("btnReset").onclick = startQuiz;
    el("fShowAns").onchange = function () { Q.showAns = el("fShowAns").checked; drawPaper(); };
    bindOpts();
  }
  function bindOpts() {
    var os = document.querySelectorAll(".opt");
    for (var i = 0; i < os.length; i++) {
      os[i].onclick = function () {
        if (Q.submitted) return;
        var qid = parseInt(this.getAttribute("data-q"), 10), k = this.getAttribute("data-k"), q = findQ(qid);
        var cur = Q.answers[qid] || [];
        if (q.type === "多选") {
          var p = cur.indexOf(k);
          if (p >= 0) cur.splice(p, 1); else cur.push(k);
          cur.sort();
        } else cur = (cur.length === 1 && cur[0] === k) ? [] : [k];
        Q.answers[qid] = cur;
        var card = el("q" + qid), opts = card.querySelectorAll(".opt");
        for (var j = 0; j < opts.length; j++) opts[j].className = "opt" + (cur.indexOf(opts[j].getAttribute("data-k")) >= 0 ? " sel" : "");
        if (Q.showAns) card.className = "qcard" + (isRight(q) ? " right" : " wrong");
      };
    }
  }
  function submitQuiz() {
    Q.submitted = true;
    var right = 0, un = 0, modCount = {};
    Q.list.forEach(function (q) {
      if (!(Q.answers[q.id] || []).length) un++;
      if (isRight(q)) right++;
      var m = q.module.toLowerCase();
      modCount[m] = (modCount[m] || 0) + 1;
    });
    // 单模块练习才记通关成绩
    var only = Object.keys(modCount).length === 1 ? Object.keys(modCount)[0] : null;
    if (only) setBest(only, right, Q.list.length);
    var p = prog(); p.hist = p.hist || [];
    p.hist.unshift({ t: Date.now(), s: right, n: Q.list.length, m: only });
    p.hist = p.hist.slice(0, 20); save(p);

    var pct = Math.round(right / Q.list.length * 100);
    var pass = only && right / Q.list.length >= PASS;
    el("paper").innerHTML =
      '<div class="scorebox">' +
      '<div><div class="big">' + pct + '%</div><div class="lb">正确率</div></div>' +
      "<div><div class=\"big\">" + right + " / " + Q.list.length + '</div><div class="lb">答对</div></div>' +
      "<div><div class=\"big\">" + un + '</div><div class="lb">未作答</div></div>' +
      (pass ? '<span class="pass">🎉 本模块通关！</span>' : (only ? '<span class="pill mutex">还差一点，80% 通关</span>' : "")) +
      '<div style="margin-left:auto;display:flex;gap:10px">' +
      '<button class="btn ghost" id="btnOnlyWrong">只看错题</button>' +
      '<button class="btn" id="btnAgain">再来一组</button></div></div>' +
      '<div id="qlist">' + Q.list.map(function (q, i) { return qhtml(q, i); }).join("") + "</div>";
    el("btnAgain").onclick = startQuiz;
    el("btnOnlyWrong").onclick = function () {
      var cs = document.querySelectorAll("#qlist .qcard");
      for (var i = 0; i < cs.length; i++) if (cs[i].className.indexOf("right") >= 0) cs[i].style.display = "none";
    };
    window.scrollTo(0, 0);
  }

  /* ---------------- 搜索 ---------------- */
  function renderSearch(q) {
    var kw = (q || "").replace(/^kw=/, "").trim();
    if (el("searchInput")) el("searchInput").value = kw;
    sidebar.innerHTML = '<div class="side-title">范围</div><div class="side-group">' +
      "<a>题目 " + D.quiz.total + " 条</a><a>知识点 " + D.kn.modules.length + " 个模块</a>" +
      "<a>配置 " + countConf() + " 个文件</a><a>真题 " + D.exam.levels.length + " 套</a></div>";
    if (!kw) { view.innerHTML = '<h1 class="page">搜索</h1><div class="empty">输入关键词，例如：副本数、NameNode、checkpoint、词云、透视表</div>'; return; }

    var qhits = D.quiz.items.filter(function (x) { return x.stem.indexOf(kw) >= 0; }).slice(0, 40);
    var mhits = D.kn.modules.concat(D.kn.extra).filter(function (m) { return strip(m.html).indexOf(kw) >= 0; });
    var chits = [];
    D.cfg.groups.forEach(function (g) { g.files.forEach(function (f) { if (f.content.indexOf(kw) >= 0) chits.push({ g: g, f: f }); }); });
    chits = chits.slice(0, 20);
    var ehits = D.exam.levels.filter(function (l) {
      return JSON.stringify(l).indexOf(kw) >= 0;
    });

    var h = '<h1 class="page">搜索「' + esc(kw) + "」</h1>" +
      '<p class="sub">题目 ' + qhits.length + " 条　·　知识点 " + mhits.length + " 个　·　配置 " + chits.length + " 个　·　真题 " + ehits.length + " 套</p>";
    if (ehits.length) h += '<div class="card"><h2><span class="no">🎯</span>真题关卡</h2>' + ehits.map(function (l) {
      return '<div class="res"><div class="t"><a href="#/exam/' + l.no + '">第 ' + pad(l.no) + " 套 · " + l.scene + "</a></div>" +
        '<div class="m">' + l.comps.join(" / ") + " · " + l.charts + "</div></div>";
    }).join("") + "</div>";
    if (mhits.length) h += '<div class="card"><h2><span class="no">📘</span>知识点模块</h2>' + mhits.map(function (m) {
      return '<div class="res"><div class="t"><a href="#/knowledge/' + m.id + '">' + esc(m.title) + "</a></div>" +
        '<div class="m">' + esc(snippet(strip(m.html), kw)) + "</div></div>";
    }).join("") + "</div>";
    if (chits.length) h += '<div class="card"><h2><span class="no">⚙️</span>配置文件</h2>' + chits.map(function (c) {
      return '<div class="res"><div class="t"><a href="#/config/' + encodeURIComponent(c.f.name) + '">' + c.f.name + "</a>　" +
        '<span class="m">' + c.f.path + "</span></div><div class=\"m\">" + esc(snippet(c.f.content, kw)) + "</div></div>";
    }).join("") + "</div>";
    if (qhits.length) h += '<div class="card"><h2><span class="no">📝</span>题库题目</h2>' + qhits.map(function (x) {
      return '<div class="res"><div class="t">' + mark(x.stem, kw) + "</div>" +
        '<div class="m"><span class="pill m">' + x.module + "</span> " + x.type + " · " + x.difficulty +
        ' · 答案 <b>' + (x.type === "判断" ? (x.answer === "Y" ? "正确" : "错误") : x.answer) + "</b></div></div>";
    }).join("") + "</div>";
    if (!qhits.length && !mhits.length && !chits.length && !ehits.length) {
      h += '<div class="empty">没有命中。换个词试试，例如「HDFS」「副本」「算子」「词云」。</div>';
    }
    view.innerHTML = h;
  }
  function strip(html) { var d = document.createElement("div"); d.innerHTML = html; return (d.textContent || "").replace(/\s+/g, " "); }
  function mark(t, kw) { return esc(t).split(kw).join("<mark>" + esc(kw) + "</mark>"); }
  function snippet(t, kw) {
    var i = t.indexOf(kw);
    if (i < 0) return t.slice(0, 130);
    return (i > 60 ? "…" : "") + t.slice(Math.max(0, i - 60), i + 160).replace(/\s+/g, " ") + "…";
  }

  /* ---------------- 真题示范（真实执行记录 + 真实出图） ---------------- */
  function termBlock(s, idx, no) {
    var id = "tb" + idx;
    return '<div class="term">' +
      '<div class="tbar"><i></i><i></i><i></i><span>' + esc(s.p) + " · " + esc(s.t) + "</span>" +
      '<button class="copybtn2" data-copy="' + id + '">复制命令</button></div>' +
      '<div class="tbody"><div class="tcmd"><span class="tp">[root@master ~]</span># ' +
      esc(s.cmd) + "</div>" +
      (s.out ? '<pre class="tout" id="' + id + '">' + esc(s.out) + "</pre>" : '<pre class="tout">（无输出）</pre>') +
      '<div class="tfoot">' + (s.rc === 0 ? '<span class="ok">✓ 退出码 0</span>' : '<span class="no">✗ 退出码 ' + s.rc + "</span>") +
      "　耗时 " + (s.ms / 1000).toFixed(1) + "s</div>" +
      (s.shot ? '<div class="shotfold">' +
        '<div class="shoth">📷 第 ' + no + ' 步的真实截图（点图看大图）</div>' +
        '<a href="demo/' + s.shot + '" target="_blank"><img class="shotimg" src="demo/' + s.shot +
        '" alt="第 ' + no + ' 步真实截图" loading="lazy"></a></div>' : "") +
      "</div></div>";
  }

  function renderDemo() {
    var dm = D.demo, meta = dm.meta || {}, steps = dm.steps || [];
    sidebar.innerHTML = '<div class="side-title">本页</div><div class="side-group">' +
      '<a href="#/demo">完整流程</a><a href="#/demo">结果图</a><a href="#/demo">截图位</a></div>' +
      '<div class="side-title">相关</div><div class="side-group">' +
      '<a href="#/exam/1">第 01 套题面</a><a href="#/verify">装完怎么验</a><a href="#/skill">技能实操</a></div>';

    var byPhase = {}, order = [];
    steps.forEach(function (s) {
      if (!byPhase[s.p]) { byPhase[s.p] = []; order.push(s.p); }
      byPhase[s.p].push(s);
    });

    var gno = 0;
    var flow = order.map(function (ph) {
      return '<div class="sec-h">' + esc(ph) + "（" + byPhase[ph].length + " 步）</div>" +
        byPhase[ph].map(function (s) { gno += 1; return termBlock(s, ph + gno, gno); }).join("");
    }).join("");

    var imgs = (dm.imgs || []).map(function (g) {
      return '<figure class="shotfig"><a href="demo/' + g.f + '" target="_blank">' +
        '<img src="demo/' + g.f + '" alt="' + esc(g.t) + '" loading="lazy"></a>' +
        "<figcaption>📷 " + esc(g.t) + "</figcaption></figure>";
    }).join("");

    var pages = (dm.pages || []).map(function (g) {
      return '<div class="card"><h2><span class="no">📈</span>' + esc(g.t) + "</h2>" +
        '<iframe class="chartframe" src="demo/' + g.f + '" loading="lazy"></iframe>' +
        '<p class="sub" style="margin:8px 0 0">这是 Pyecharts 真实生成的交互图（可缩放、悬浮看数值）。' +
        '<a href="demo/' + g.f + '" target="_blank">新窗口打开 →</a></p></div>';
    }).join("");

    var shotList = (meta.shots || []).map(function (s) {
      return "<li>" + esc(s) + "</li>";
    }).join("");

    view.innerHTML =
      '<h1 class="page">🎬 ' + esc(meta.title || "真题示范") + "</h1>" +
      '<p class="sub">' + esc(meta.sub || "") + "</p>" +
      '<div class="card" style="padding:14px 20px"><div class="vpre" style="margin:0">' +
      "执行环境：" + esc(meta.env || "") + "</div>" +
      (meta.cost ? '<p class="sub" style="margin:8px 0 0">⏱ ' + esc(meta.cost) + "</p>" : "") +
      (meta.note ? '<div class="vnote" style="margin:10px 0 0"><div class="vhead">⚠ 先说清楚数据来源</div>' +
        esc(meta.note) + "</div>" : "") + "</div>" +
      '<div class="card"><h2><span class="no">💡</span>怎么用它</h2><ul class="cp-pts">' +
      (meta.how || []).map(function (h) { return "<li>" + esc(h) + "</li>"; }).join("") + "</ul></div>" +
      (steps.length ? '<div class="card" style="padding:16px 20px"><h2 style="margin-bottom:10px">' +
        '<span class="no">$</span>完整操作流程（' + steps.length + " 步，真实执行）</h2>" + flow + "</div>" : "") +
      (imgs ? '<div class="card"><h2><span class="no">🖼️</span>真实结果图</h2>' +
        '<div class="shotgrid">' + imgs + "</div>" +
        '<p class="sub" style="margin:10px 0 0">图上的中文、数值、条数都是这次真跑出来的结果，点图看大图。</p></div>' : "") +
      pages +
      (shotList ? '<div class="card"><h2><span class="no">📷</span>你做的时候要在这些位置截图</h2>' +
        '<ul class="cp-pts">' + shotList + "</ul></div>" : "") +
      '<div style="display:flex;gap:10px;flex-wrap:wrap">' +
      '<a class="btn" href="#/exam/1">看第 01 套题面 →</a>' +
      '<a class="btn ghost" href="#/verify">装完怎么验</a></div>';

    bindCodeBlocks();
  }

  /* ---------------- 使用者（多人共用一台机器时进度互不影响） ---------------- */
  function renderMe() {
    var us = allUsers();
    sidebar.innerHTML = '<div class="side-title">说明</div><div class="side-group">' +
      "<a>进度按使用者名分开保存</a><a>换浏览器/清缓存会丢失</a><a>建议：姓名 + 班级</a></div>";
    var rows = us.map(function (u) {
      var s = userStat(u);
      var passed = 0;
      for (var k in s.best) if (s.best[k].s / s.best[k].n >= PASS) passed++;
      return "<tr" + (u === USER ? ' class="onu"' : "") + "><td><b>" + esc(u) + "</b>" +
        (u === USER ? ' <span class="pill e">当前</span>' : "") + "</td><td>" + s.read +
        "</td><td>" + s.conf + "</td><td>" + s.cards + "</td><td>" + s.task + "</td><td>" + s.shot +
        "</td><td>" + s.hist + " 次 / 通关 " + passed + " 模块</td><td>" +
        '<button class="btn ghost sm" data-use="' + esc(u) + '">切换</button> ' +
        '<button class="btn ghost sm" data-del="' + esc(u) + '">删除</button></td></tr>';
    }).join("");
    view.innerHTML =
      '<h1 class="page">👤 使用者</h1>' +
      '<p class="sub">多人共用这台电脑 / 这个浏览器时，各填一次名字，进度就各存各的，互不影响。</p>' +
      '<div class="card"><h2><span class="no">✏️</span>我是谁</h2>' +
      '<div style="display:flex;gap:9px;flex-wrap:wrap;align-items:center">' +
      '<input id="meName" class="cs-inp" style="flex:1;min-width:200px;margin:0" placeholder="输入姓名，例如：张三（计网2401）" value="' + esc(USER) + '">' +
      '<button class="btn" id="meSave">保存并切换</button>' +
      (USER ? '<button class="btn ghost" id="meQuit">退出（用匿名进度）</button>' : "") +
      "</div>" +
      '<p class="sub" style="margin:10px 0 0">如果整台机器只你一个人用，不填也行 —— 进度会存在「匿名」下面。</p></div>' +
      '<div class="card"><h2><span class="no">👥</span>本机已有使用者（' + us.length + "）</h2>" +
      (us.length ? '<table><thead><tr><th>姓名</th><th>已读页</th><th>配置</th><th>实操卡</th><th>子任务</th><th>截图</th><th>练习</th><th></th></tr></thead><tbody>' + rows + "</tbody></table>"
        : '<div class="empty">还没有人填过名字。</div>') + "</div>" +
      '<div class="card"><h2><span class="no">🔒</span>关于账号密码</h2>' +
      '<ul class="cp-pts">' +
      "<li><b>这个站点是纯静态的</b>（没有后端服务器），所以网页本身做不了真正的密码校验——任何写在网页里的口令都能被看到。</li>" +
      "<li>真正拦得住的做法是在 <b>Web 服务器层</b>加账号密码（nginx Basic Auth）：进站前浏览器弹框要求输入用户名与口令，输错进不来。局域网自建部署时用这个方法（口令在服务端校验，看不到也绕不过）。</li>" +
      "<li>公网版（GitHub Pages）是纯静态托管，没有服务器，只能用<b>进站口令门</b>：输对口令才渲染内容，口令只存摘要不明文。它能挡住随手点开链接的人，但挡不住懂技术的人 —— 内容本质上仍是对外公开的。</li>" +
      "<li>要真正在公网上严格管控，把站点搬到 <b>Cloudflare Pages</b>（可连私有仓库），再用 <b>Zero Trust → Access</b> 配一条访问策略（邮箱验证码 / 指定邮箱 / IP 段），这是免费且真正拦得住的方案。</li>" +
      "<li>这里的「使用者」只做一件事：<b>把学习进度按人分开存</b>，适合机房多人共用一台电脑的场景。</li>" +
      "</ul></div>";

    var b = el("meSave");
    if (b) b.onclick = function () {
      var n = el("meName").value.trim();
      if (!n) { alert("请输入姓名"); return; }
      setUser(n); render();
    };
    var q = el("meQuit");
    if (q) q.onclick = function () { setUser(""); render(); };
    var ub = view.querySelectorAll("[data-use]");
    for (var i = 0; i < ub.length; i++) {
      ub[i].onclick = function () { setUser(this.getAttribute("data-use")); render(); };
    }
    var db = view.querySelectorAll("[data-del]");
    for (var j = 0; j < db.length; j++) {
      db[j].onclick = function () {
        var u = this.getAttribute("data-del");
        if (!confirm("删除「" + u + "」的全部学习进度？此操作不可恢复。")) return;
        try { localStorage.removeItem(KEY + "::" + u); } catch (e) {}
        var g = gset();
        g.users = (g.users || []).filter(function (x) { return x !== u; });
        if (g.user === u) { g.user = ""; USER = ""; }
        gsave(g); updMe(); render();
      };
    }
  }

  /* ---------------- 事件 ---------------- */
  var tt = el("toTop");
  if (tt) {
    tt.onclick = function () { window.scrollTo({ top: 0, behavior: "smooth" }); };
    window.addEventListener("scroll", function () {
      tt.style.display = window.pageYOffset > 400 ? "flex" : "none";
    });
  }
  el("searchForm").onsubmit = function (e) {
    e.preventDefault();
    var kw = el("searchInput").value.trim();
    if (kw) go("#/search?kw=" + encodeURIComponent(kw));
  };
  window.addEventListener("hashchange", render);
  USER = (gset().user || "").trim();
  updMe();
  render();
})();
