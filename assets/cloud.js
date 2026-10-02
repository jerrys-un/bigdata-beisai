/* ============================================================================
   云端账号与进度同步（WorkBuddy 云服务）
   —— 学生端：邮箱登录后，进度自动上报到 study_progress（按 uid 隔离）
   —— 老师端：#/admin 根据角色拉全班数据（students / attempts / overview）
   设计原则：云端是「附加能力」。SDK 没加载 / 断网 / 非发布域名 —— 一律静默降级，
   本地 localStorage 进度照常工作，绝不因为云端失败而卡住学习。
   ========================================================================== */
(function () {
  var ENDPOINT = "https://bigdata-beisai.app.workbuddy.host";
  var PUB_KEY = "wbpk_z9g0p8yEhMXiWhfmgk07VO_23Cpv3jth0rB76fKlaPHXEpQmoPW87KM";
  var CDN = "https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js";

  // 云端只放行发布域名（服务端强校验 Origin）。非发布域名下不加载、不初始化。
  var HOST_OK = /\.workbuddy\.host$/i.test(location.hostname);

  var cloud = null;
  var st = { on: false, err: "", ok: 0, tries: 0 };
  var profile = null;       // 当前登录用户的 profiles 行 { role, display_name, email }
  var session = null;       // cloud.auth 的会话（含 user）

  function connect() {
    try {
      if (!window.WorkBuddyCloud || !window.WorkBuddyCloud.createWorkBuddyCloud) return false;
      cloud = window.WorkBuddyCloud.createWorkBuddyCloud({ endpoint: ENDPOINT, publishableKey: PUB_KEY });
      st.on = true;
      st.err = "";
      return true;
    } catch (e) {
      st.err = "云服务初始化失败";
      return false;
    }
  }

  // SDK 走 CDN，异步注入，不阻塞页面；失败就当没有云端
  function loadSdk() {
    if (!HOST_OK) return;
    if (connect()) return;
    var s = document.createElement("script");
    s.src = CDN;
    s.async = true;
    s.onload = function () { connect(); };
    s.onerror = function () { st.err = "云服务组件没加载成功（可能是离线或网络受限）"; };
    document.head.appendChild(s);
  }
  loadSdk();

  function ok(r) { return !r || !r.error; }
  function msg(r) { return r && r.error && r.error.message ? r.error.message : "网络不通"; }

  /* ================= 认证 ================= */

  function ensure() {
    if (!HOST_OK) return { ok: false, why: "本机版不支持登录" };
    if (!cloud && !connect()) return { ok: false, why: st.err || "云服务组件未加载" };
    return { ok: true };
  }

  function getSession() {
    var g = ensure();
    if (!g.ok) return Promise.resolve({ data: null, error: { message: g.why } });
    return cloud.auth.getSession();
  }

  function signInPassword(email, password) {
    var g = ensure();
    if (!g.ok) return Promise.resolve({ error: { message: g.why } });
    return cloud.auth.signInWithPassword({ email: email, password: password });
  }

  function sendOtp(email) {
    var g = ensure();
    if (!g.ok) return Promise.resolve({ error: { message: g.why } });
    return cloud.auth.sendOtp({ email: email });
  }

  // 已注册用户用验证码登录；新用户需带密码注册
  function verifyOtp(email, verificationId, isExistingUser, token, password) {
    var g = ensure();
    if (!g.ok) return Promise.resolve({ error: { message: g.why } });
    return cloud.auth.verifyOtp({
      email: email,
      verificationId: verificationId,
      isExistingUser: isExistingUser,
      token: token,
      password: isExistingUser ? undefined : password,
    });
  }

  function signOut() {
    if (cloud) return cloud.auth.signOut();
    return Promise.resolve({ error: null });
  }

  function onChange(cb) {
    if (cloud && cloud.auth.onAuthStateChange) return cloud.auth.onAuthStateChange(cb);
    return function () {};
  }

  /* ================= 个人资料（profiles） ================= */

  // 登录后取自己的资料；首次登录自动建一条 student 资料
  function getProfile() {
    var g = ensure();
    if (!g.ok) return Promise.resolve({ data: null, error: { message: g.why } });
    if (!cloud) return Promise.resolve({ data: null, error: { message: "未登录" } });
    return cloud.database.from("profiles").select("*").maybeSingle().then(function (r) {
      if (r.error) return r;
      if (r.data) { profile = r.data; return r; }
      // 首次：建一条默认 student 资料（email 从会话取，display_name 留空待填）
      var em = "";
      return cloud.auth.getUser().then(function (u) {
        em = (u && u.data && u.data.user && u.data.user.email) || "";
        return cloud.database.from("profiles").insert({ email: em, role: "student", display_name: "" }).select().single().then(function (ins) {
          if (ins.error) return ins;
          profile = ins.data;
          return { data: profile, error: null };
        });
      });
    });
  }

  function saveProfile(patch) {
    var g = ensure();
    if (!g.ok || !cloud || !profile) return Promise.resolve({ error: { message: "未登录" } });
    // 客户端永远不能改 role / owner_id；RLS 也会拦
    var safe = { display_name: patch.display_name };
    return cloud.database.from("profiles").update(safe).eq("owner_id", profile.owner_id).select().single();
  }

  function currentProfile() { return profile; }
  function currentRole() { return profile ? profile.role : "student"; }

  /* ================= 学生进度上报 ================= */

  function stats(p) {
    function n(o) { var c = 0, k; for (k in (o || {})) if (o[k]) c++; return c; }
    var best = p.best || {}, mod, pass = 0, hi = 0, total = 0, cnt = 0;
    for (mod in best) {
      var b = best[mod];
      if (!b || !b.n) continue;
      var r = b.s / b.n;
      if (r >= 0.8) pass++;
      if (r > hi) hi = r;
      total += r; cnt++;
    }
    return {
      read_n: (p.read || []).length,
      cards_n: Object.keys(p.cSeen || {}).length,
      task_n: n(p.task),
      shot_n: n(p.shot),
      hist_n: (p.hist || []).length,
      pass_n: pass,
      quiz_best: Math.round(hi * 100),
      quiz_avg: cnt ? Math.round(total / cnt * 100) : 0,
    };
  }

  var timer = null;
  function reportStudy(payload, totalPct) {
    var g = ensure();
    if (!g.ok || !cloud || !profile) return Promise.resolve({ ok: false, why: "未登录" });
    var s = stats(payload || {});
    var row = {
      payload: payload || {},
      total_pct: totalPct || 0,
      read_n: s.read_n, cards_n: s.cards_n, task_n: s.task_n, shot_n: s.shot_n,
      hist_n: s.hist_n, pass_n: s.pass_n, quiz_best: s.quiz_best, quiz_avg: s.quiz_avg,
    };
    return cloud.database.from("study_progress")
      .upsert(row, { onConflict: "owner_id" })
      .then(function (r) {
        if (r.error) { st.err = msg(r); return { ok: false, why: st.err }; }
        st.ok++;
        st.err = "";
        return { ok: true };
      })
      .catch(function (e) { st.err = (e && e.message) || "网络不通"; return { ok: false, why: st.err }; });
  }

  function queueStudy(payload, totalPct) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () { reportStudy(payload, totalPct); }, 6000);
  }

  function logAttempt(kind, refId, score, total, detail) {
    var g = ensure();
    if (!g.ok || !cloud) return Promise.resolve({ ok: false });
    return cloud.database.from("attempt_log").insert({
      kind: kind, ref_id: refId, score: score, total: total, detail: detail || {},
    }).then(function (r) {
      return { ok: !r.error };
    });
  }

  /* ================= 老师端（SECURITY DEFINER 函数，内部 is_teacher 把关） ================= */

  function rpc(fn, args) {
    var g = ensure();
    if (!g.ok || !cloud) return Promise.resolve({ data: null, error: { message: g.why || "未登录" } });
    return cloud.database.rpc(fn, args).then(function (r) {
      return { data: r && r.data, error: r && r.error };
    }).catch(function (e) {
      return { data: null, error: { message: (e && e.message) || "网络不通" } };
    });
  }

  function teacherOverview() { return rpc("admin_overview", {}); }
  function teacherStudents(search, limit, offset) {
    return rpc("admin_list_students", { p_search: search || "", p_limit: limit || 50, p_offset: offset || 0 });
  }
  function teacherAttempts(search, limit, offset) {
    return rpc("admin_list_attempts", { p_search: search || "", p_limit: limit || 50, p_offset: offset || 0 });
  }
  function teacherSetRole(ownerId, role) {
    return rpc("admin_set_role", { p_owner_id: ownerId, p_role: role });
  }

  window.CloudSync = {
    ready: function () { return !!cloud; },
    status: function () { return st; },
    profile: currentProfile,
    role: currentRole,
    // auth
    getSession: getSession,
    signInPassword: signInPassword,
    sendOtp: sendOtp,
    verifyOtp: verifyOtp,
    signOut: signOut,
    onChange: onChange,
    getProfile: getProfile,
    saveProfile: saveProfile,
    // student
    reportStudy: reportStudy,
    queueStudy: queueStudy,
    logAttempt: logAttempt,
    stats: stats,
    // teacher
    teacherOverview: teacherOverview,
    teacherStudents: teacherStudents,
    teacherAttempts: teacherAttempts,
    teacherSetRole: teacherSetRole,
  };
})();
