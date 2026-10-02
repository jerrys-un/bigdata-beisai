/* ============================================================================
   Cloudflare Pages Functions —— 进站口令（服务端校验）

   为什么用这个而不是 Cloudflare Access：
     Access 要求域名为「本账号下的活跃 zone」，而 pages.dev 是 Cloudflare 自己的域名，
     不在你的账号里，所以 Access 里选不到 pages.dev。这个中间件直接在 Pages 上做校验，
     同样跑在服务器端，前端绕不过去。

   怎么用：
     口令从两级里取，优先 1：
     1) 环境变量 SITE_PASSWORD —— 想换口令就在面板加
        Cloudflare Pages 项目 → Settings → Environment variables（Variables and Secrets）
        添加变量 SITE_PASSWORD（建议 Secret 类型），保存后重新部署
     2) 没配环境变量时，自动回退到本文件里的内置口令（******，只存 SHA-256 摘要）
        → 也就是说，代码一部署上去口令就生效，不必先去面板配变量

   注意：
     · cookie 里存的是口令的 SHA-256 摘要，不是口令本身；有效期 30 天
     · 本文件对 GitHub Pages / 本地打开没有任何影响（那边不跑 Functions）
   ========================================================================== */

const COOKIE = "bdgate";
const MAX_AGE = 60 * 60 * 24 * 30;   // 30 天

// 内置兜端口令 = ****** 的 SHA-256（改口令：node -e 求新摘要后替换这行）
const FALLBACK_PW_HASH =
  "94150766b347706e3a6b46d70c59fb11593d6972f493ec5a57cb80b23f837dda";

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function page(err, to) {
  const safeTo = String(to || "/").replace(/"/g, "%22");
  return `<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>大数据备赛 · 请输入口令</title>
<style>
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px;
    font-family:"Microsoft YaHei","PingFang SC",-apple-system,"Segoe UI",Roboto,sans-serif;
    background:#f4f6fb;color:#3b4664;-webkit-font-smoothing:antialiased}
  .box{width:100%;max-width:400px;background:#fff;border:1px solid #e7eaf3;border-radius:16px;
    padding:34px 28px;text-align:center;box-shadow:0 1px 2px rgba(20,27,52,.05),0 10px 34px rgba(20,27,52,.08)}
  .logo{width:56px;height:56px;margin:0 auto 14px;border-radius:16px;display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;font-weight:800;font-size:20px;letter-spacing:.5px;
    box-shadow:0 6px 18px rgba(79,70,229,.32)}
  h1{font-size:17px;margin:0 0 8px;color:#141b34;line-height:1.45}
  p.sub{font-size:13px;color:#7b87a6;margin:0 0 20px;line-height:1.7}
  input{width:100%;padding:12px 14px;border:1px solid #e7eaf3;border-radius:11px;font-size:15px;
    outline:none;text-align:center;color:#141b34;background:#fff}
  input:focus{border-color:#4f46e5;box-shadow:0 0 0 3px rgba(79,70,229,.12)}
  button{width:100%;margin-top:12px;padding:12px;border:0;border-radius:11px;color:#fff;font-size:15px;font-weight:600;
    cursor:pointer;background:linear-gradient(135deg,#4f46e5,#7c3aed);box-shadow:0 4px 14px rgba(79,70,229,.3)}
  button:active{transform:translateY(1px)}
  .err{color:#e11d48;font-size:13px;margin:14px 0 0}
  .tip{font-size:12px;color:#9aa4bf;margin:18px 0 0;line-height:1.7}
</style></head>
<body>
  <form class="box" method="POST" action="/__gate">
    <input type="hidden" name="to" value="${safeTo}">
    <div class="logo">BD</div>
    <h1>大数据应用与服务 · 闯关学习站</h1>
    <p class="sub">本站需要口令才能进入，口令找老师要</p>
    <input type="password" name="pass" placeholder="请输入口令" autocomplete="current-password" autofocus>
    <button type="submit">进入学习站</button>
    ${err ? `<p class="err">✗ ${err}</p>` : ""}
    <p class="tip">口令只需要输一次，这台设备 30 天内不用再输</p>
  </form>
</body></html>`;
}

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const E = env || {};

  // 两级口令：环境变量优先，没有就用内置摘要
  const envPW = E.SITE_PASSWORD || "";
  const want = envPW ? await sha256(envPW) : FALLBACK_PW_HASH;
  const source = envPW ? "env:SITE_PASSWORD" : "builtin";

  // 自检端点：访问 /__gate/status 就能看出中间件跑没跑、口令配没配
  // （只暴露状态，不暴露口令本身）
  if (url.pathname === "/__gate/status") {
    const related = Object.keys(E).filter((k) => /pass|pwd|secret|site/i.test(k));
    return new Response(JSON.stringify({
      codeVersion: "2026-10-02.4",      // 每次改这个文件就 +1，用来判断部署有没有更新
      middleware: "running",
      passwordConfigured: true,
      passwordSource: source,
      builtinPassword: "******",
      relatedEnvKeys: related,
      verdict: envPW
        ? "✅ 已读环境变量 SITE_PASSWORD"
        : "✅ 正在用内置口令 ******（无需配变量，部署即生效）",
    }, null, 2), {
      headers: { "Content-Type": "application/json;charset=utf-8", "Cache-Control": "no-store" },
    });
  }

  const cookie = request.headers.get("Cookie") || "";
  const hit = new RegExp("(?:^|;\\s*)" + COOKIE + "=([^;]+)").exec(cookie);

  // 退出
  if (url.pathname === "/__gate/out") {
    return new Response(null, {
      status: 302,
      headers: { Location: "/", "Set-Cookie": COOKIE + "=; Path=/; Max-Age=0; Secure; HttpOnly; SameSite=Lax" },
    });
  }

  // 提交口令
  if (url.pathname === "/__gate" && request.method === "POST") {
    let pass = "", to = "/";
    try {
      const f = await request.formData();
      pass = String(f.get("pass") || "");
      to = String(f.get("to") || "/");
      if (!to.startsWith("/")) to = "/";
    } catch (e) { /* 表单解析失败按空口令处理 */ }
    if ((await sha256(pass)) === want) {
      return new Response(null, {
        status: 302,
        headers: { Location: to, "Set-Cookie": COOKIE + "=" + want + "; Path=/; Max-Age=" + MAX_AGE + "; Secure; HttpOnly; SameSite=Lax" },
      });
    }
    return new Response(page("口令不对，再试一次", to), {
      status: 401, headers: { "Content-Type": "text/html;charset=utf-8" },
    });
  }

  // 已通过
  if (hit && hit[1] === want) return next();

  // 未通过：返回登录页（内联样式，不依赖任何外部资源）
  return new Response(page("", url.pathname + url.search), {
    status: 401, headers: { "Content-Type": "text/html;charset=utf-8" },
  });
}
