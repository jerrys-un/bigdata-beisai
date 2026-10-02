/* ============================================================================
   游戏化引擎：积分 · 等级 · 徽章 · 连续学习天数 · 音效 · 反馈动画
   —— 纯前端、零依赖、离线可用；数据跟着「使用者」走，存在 localStorage
   —— 音效用 Web Audio 现场合成，不引入任何音频文件
   ========================================================================== */
(function () {
  var LKEY = "bdstudy_v2";        // 与 app.js 同一套键
  var CFG = "bdstudy_game";       // 全局设置（音效开关）

  /* ---------- 等级 ---------- */
  var RANKS = [
    { lv: 1, xp: 0, name: "初来乍到" },
    { lv: 2, xp: 80, name: "摸到门道" },
    { lv: 3, xp: 200, name: "上手了" },
    { lv: 4, xp: 380, name: "熟练工" },
    { lv: 5, xp: 620, name: "老手" },
    { lv: 6, xp: 950, name: "高手" },
    { lv: 7, xp: 1400, name: "大神" },
    { lv: 8, xp: 2000, name: "宗师" },
    { lv: 9, xp: 2800, name: "备赛王者" },
  ];

  /* ---------- 徽章 ---------- */
  var BADGES = [
    { id: "first", icon: "🌱", name: "迈出第一步", desc: "第一次开始学习", test: function (d) { return d.xp > 0; } },
    { id: "pass1", icon: "🎯", name: "拿下第一关", desc: "某个模块练习正确率达到 80%", test: function (d) { return countPass(d) >= 1; } },
    { id: "perfect", icon: "💯", name: "满分答卷", desc: "一次练习全部答对", test: function (d) { return !!d.perfect; } },
    { id: "read30", icon: "📖", name: "读过三十页", desc: "读过 30 个页面", test: function (d) { return d.read >= 30; } },
    { id: "cpt20", icon: "🧠", name: "概念通了", desc: "看懂 20 张概念卡", test: function (d) { return d.cpt >= 20; } },
    { id: "card10", icon: "🛠️", name: "动手十次", desc: "掌握 10 张实操卡", test: function (d) { return d.card >= 10; } },
    { id: "task20", icon: "✅", name: "任务打卡", desc: "赛题子任务打勾 20 个", test: function (d) { return d.task >= 20; } },
    { id: "shot10", icon: "📷", name: "证据齐全", desc: "截图证据打勾 10 个", test: function (d) { return d.shot >= 10; } },
    { id: "streak3", icon: "🔥", name: "坚持三天", desc: "连续 3 天学习", test: function (d) { return d.streak >= 3; } },
    { id: "streak7", icon: "🏔️", name: "一周不断", desc: "连续 7 天学习", test: function (d) { return d.streak >= 7; } },
    { id: "pass5", icon: "🏅", name: "通关五模块", desc: "5 个模块练习达到 80%", test: function (d) { return countPass(d) >= 5; } },
    { id: "lv5", icon: "⭐", name: "五级老手", desc: "等级达到 5 级", test: function (d) { return levelOf(d.xp).lv >= 5; } },
  ];

  var XP_RULE = { read: 2, cpt: 5, card: 8, task: 5, shot: 4, quiz: 3, pass: 25, daily: 3 };

  /* ---------- 读写 ---------- */
  function gset() { try { return JSON.parse(localStorage.getItem(CFG)) || {}; } catch (e) { return {}; } }
  function gsave(o) { try { localStorage.setItem(CFG, JSON.stringify(o)); } catch (e) {} }
  function userName() { try { return (JSON.parse(localStorage.getItem(LKEY)) || {}).user || ""; } catch (e) { return ""; } }
  function curKey() { var u = userName(); return u ? LKEY + "::" + u : LKEY; }
  function prog() { try { return JSON.parse(localStorage.getItem(curKey())) || {}; } catch (e) { return {}; } }
  function save(p) { try { localStorage.setItem(curKey(), JSON.stringify(p)); } catch (e) {} }

  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }
  function daysBetween(a, b) {
    return Math.round((new Date(b + "T00:00:00") - new Date(a + "T00:00:00")) / 86400000);
  }

  function countPass(d) {
    var n = 0, k, b;
    for (k in (d.best || {})) { b = d.best[k]; if (b && b.n && b.s / b.n >= 0.8) n++; }
    return n;
  }
  function collect(p) {
    var t = 0, k;
    for (k in (p.task || {})) if (p.task[k]) t++;
    var s = 0;
    for (k in (p.shot || {})) if (p.shot[k]) s++;
    var g = p.game || {};
    return {
      xp: g.xp || 0, streak: g.streak || 0, days: g.days || [], badges: g.badges || [],
      read: (p.read || []).length, cpt: Object.keys(p.cSeen || {}).length,
      card: (p.cardSeen || []).length, task: t, shot: s,
      hist: (p.hist || []).length, best: p.best || {}, perfect: g.perfect,
    };
  }
  function levelOf(xp) {
    var cur = RANKS[0], next = null, i;
    for (i = 0; i < RANKS.length; i++) {
      if (xp >= RANKS[i].xp) cur = RANKS[i];
      else { next = RANKS[i]; break; }
    }
    var base = cur.xp, cap = next ? next.xp : cur.xp + 1000;
    return { lv: cur.lv, name: cur.name, xp: xp, base: base, next: cap,
             pct: Math.max(0, Math.min(100, Math.round((xp - base) / (cap - base) * 100))) };
  }
  function todayXp() {
    var g = prog().game || {};
    return (g.todayDate === today()) ? (g.todayXp || 0) : 0;
  }

  /* ---------- 音效（Web Audio 合成） ---------- */
  var ac = null;
  function actx() {
    if (!ac) { var A = window.AudioContext || window.webkitAudioContext; if (A) ac = new A(); }
    if (ac && ac.state === "suspended") ac.resume();
    return ac;
  }
  function note(freq, at, dur, type, vol) {
    var c = actx(); if (!c) return;
    var o = c.createOscillator(), gn = c.createGain();
    o.type = type || "sine"; o.frequency.value = freq;
    var t0 = c.currentTime + at;
    gn.gain.setValueAtTime(0.0001, t0);
    gn.gain.exponentialRampToValueAtTime(vol || 0.16, t0 + 0.012);
    gn.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(gn); gn.connect(c.destination); o.start(t0); o.stop(t0 + dur + 0.03);
  }
  function sfx(name) {
    if (gs().sound === false) return;
    try {
      if (name === "ok") { note(880, 0, 0.09, "sine", 0.12); note(1320, 0.07, 0.12, "sine", 0.1); }
      else if (name === "no") { note(220, 0, 0.16, "triangle", 0.12); note(165, 0.1, 0.2, "triangle", 0.1); }
      else if (name === "xp") { note(1046, 0, 0.06, "sine", 0.07); }
      else if (name === "badge") { [784, 988, 1175, 1568].forEach(function (f, i) { note(f, i * 0.07, 0.22, "sine", 0.11); }); }
      else if (name === "level") { [523, 659, 784, 1046, 1318].forEach(function (f, i) { note(f, i * 0.085, 0.3, "triangle", 0.12); }); }
      else if (name === "pass") { [659, 784, 1046].forEach(function (f, i) { note(f, i * 0.09, 0.26, "sine", 0.13); }); }
    } catch (e) {}
  }
  function gs() { return gset(); }
  function setSound(on) { var c = gset(); c.sound = !!on; gsave(c); }

  /* ---------- 反馈动画 ---------- */
  function layer() {
    var d = document.getElementById("fxLayer");
    if (!d) {
      d = document.createElement("div");
      d.id = "fxLayer";
      document.body.appendChild(d);
    }
    return d;
  }
  function floatXp(txt, x, y) {
    var s = document.createElement("div");
    s.className = "fx-xp";
    s.textContent = txt;
    s.style.left = (x || window.innerWidth / 2) + "px";
    s.style.top = (y || 120) + "px";
    layer().appendChild(s);
    setTimeout(function () { if (s.parentNode) s.parentNode.removeChild(s); }, 1100);
  }
  function toast(icon, title, sub, kind) {
    var d = document.createElement("div");
    d.className = "fx-toast" + (kind ? " " + kind : "");
    d.innerHTML = '<span class="ti">' + icon + '</span><div><b>' + title + "</b>" +
      (sub ? "<i>" + sub + "</i>" : "") + "</div>";
    layer().appendChild(d);
    setTimeout(function () { d.classList.add("out"); }, 2600);
    setTimeout(function () { if (d.parentNode) d.parentNode.removeChild(d); }, 3200);
  }
  function confetti(n) {
    var wrap = layer(), i, s;
    var chars = ["🎉", "✨", "⭐", "🎊", "💫"];
    for (i = 0; i < (n || 18); i++) {
      s = document.createElement("div");
      s.className = "fx-conf";
      s.textContent = chars[i % chars.length];
      s.style.left = (10 + Math.random() * 80) + "%";
      s.style.animationDelay = (Math.random() * 0.35) + "s";
      s.style.fontSize = (14 + Math.random() * 18) + "px";
      wrap.appendChild(s);
      (function (el) { setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 2400); })(s);
    }
  }

  /* ---------- 学习日 / 连续天数 ---------- */
  function touchDay(p) {
    var g = p.game || (p.game = {});
    var t = today();
    g.days = g.days || [];
    if (g.days.indexOf(t) < 0) {
      var last = g.days[g.days.length - 1];
      if (last && daysBetween(last, t) === 1) g.streak = (g.streak || 1) + 1;
      else if (last && daysBetween(last, t) === 0) { /* 同一天 */ }
      else g.streak = 1;
      g.days.push(t);
      if (g.days.length > 120) g.days = g.days.slice(-120);   // 只留最近 120 天
      if ((g.streak || 0) > (g.bestStreak || 0)) g.bestStreak = g.streak;
    }
    if (g.todayDate !== t) { g.todayDate = t; g.todayXp = 0; }
    return p;
  }

  /* ---------- 加分 & 检查徽章/升级 ---------- */
  function award(type, key, extra) {
    var p = prog();
    p.got = p.got || {};
    var gk = type + ":" + key;
    if (key != null && p.got[gk]) return null;      // 同一件事不重复给分
    var xp = XP_RULE[type] || 0;
    var pct = null;

    if (type === "quiz") {
      // 每次交卷都算，但只按实际答对数给分
      xp = (extra && extra.s ? extra.s * XP_RULE.quiz : 0);
      if (extra && extra.n && extra.s / extra.n >= 0.8) xp += XP_RULE.pass;
    }
    if (xp <= 0 && type !== "quiz") return null;
    if (key != null) p.got[gk] = 1;

    p = touchDay(p);
    var g = p.game;
    g.xp = (g.xp || 0) + xp;
    g.todayXp = (g.todayXp || 0) + xp;
    if (type === "quiz" && extra && extra.s === extra.n && extra.n > 0) g.perfect = 1;
    save(p);

    var before = levelOf(g.xp - xp).lv, after = levelOf(g.xp).lv;
    var won = checkBadges(p);
    save(p);

    if (xp > 0) { sfx(type === "quiz" && extra && extra.s === 0 ? "no" : "xp"); floatXp("+" + xp + " XP"); }
    if (type === "quiz" && extra) {
      if (extra.s / extra.n >= 0.8) sfx("pass");
      else if (extra.s === 0) sfx("no");
    }
    if (after > before) {
      var r = levelOf(g.xp);
      sfx("level");
      confetti(22);
      toast("🎖️", "升到 " + after + " 级 · " + r.name, "继续加油！", "level");
    }
    won.forEach(function (b) {
      sfx("badge");
      toast(b.icon, "获得徽章 · " + b.name, b.desc, "badge");
    });
    if (won.length) confetti(16);
    return { xp: xp, levelUp: after > before, badges: won };
  }

  function checkBadges(p) {
    var d = collect(p);
    var g = p.game || (p.game = {});
    g.badges = g.badges || [];
    var won = [];
    BADGES.forEach(function (b) {
      if (g.badges.indexOf(b.id) >= 0) return;
      var ok = false;
      try { ok = b.test(d); } catch (e) {}
      if (ok) { g.badges.push(b.id); won.push(b); }
    });
    return won;
  }

  /* ---------- 供页面展示的数据 ---------- */
  function summary() {
    var p = prog();
    var g = p.game || {};
    var d = collect(p);
    var lv = levelOf(g.xp || 0);
    var t = today();
    // 最近 21 天的打卡格子
    var grid = [], i, day, has;
    for (i = 20; i >= 0; i--) {
      var dt = new Date(); dt.setDate(dt.getDate() - i);
      day = dt.getFullYear() + "-" + ("0" + (dt.getMonth() + 1)).slice(-2) + "-" + ("0" + dt.getDate()).slice(-2);
      has = (g.days || []).indexOf(day) >= 0;
      grid.push({ d: day, on: has, t: day.slice(5), isToday: day === t });
    }
    return {
      level: lv, xp: g.xp || 0, todayXp: todayXp(),
      streak: (g.streak || 0), bestStreak: g.bestStreak || 0,
      badges: BADGES.map(function (b) {
        return { id: b.id, icon: b.icon, name: b.name, desc: b.desc, got: (g.badges || []).indexOf(b.id) >= 0 };
      }),
      gotCount: (g.badges || []).length, totalBadges: BADGES.length,
      grid: grid, stats: d,
    };
  }

  window.Game = {
    award: award,
    touchDay: function () { var p = touchDay(prog()); save(p); },
    summary: summary,
    levelOf: levelOf,
    sound: function () { return gs().sound !== false; },
    setSound: setSound,
    sfx: sfx,
    confetti: confetti,
    toast: toast,
    floatXp: floatXp,
    BADGES: BADGES,
    RANKS: RANKS,
  };
})();
