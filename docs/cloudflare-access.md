# 用 Cloudflare 给学习站加访问控制（免费，服务端鉴权）

> 现状：GitHub Pages 上的口令门是**前端挡住**的——懂技术的人打开源码就能绕过。
> 本文的做法把校验放到 Cloudflare 的服务器上，**没通过验证的人连页面都下载不到**。

## 先说结论：两条路，推荐第一条

| 方案 | 需要什么 | 学生体验 | 推荐度 |
|---|---|---|---|
| **A. Pages Functions 自建口令**（仓库已内置） | 只需在 Pages 里加**一个环境变量** | 输一次口令，30 天不用再输 | ⭐ 推荐 |
| B. Cloudflare Access | **必须有自定义域名** | 邮箱收验证码 | 有域名时可选 |

> ⚠️ **重要**：Cloudflare Access **不能保护 `pages.dev` 域名**。官方文档要求
> 「Domains must belong to an active zone in your Cloudflare account」，而 `pages.dev`
> 是 Cloudflare 自己的域名，不在你的账号里 —— 所以在 Access 的域名下拉里根本选不到它
> （只会看到你自己账号下的域名）。想在 Access 里用，就得先买一个域名绑到 Pages 上。

---

## 第一步：把站点部署到 Cloudflare

1. 打开 <https://dash.cloudflare.com>，注册并登录
2. 左侧菜单 → **Workers 和 Pages** → **创建**
   - 仓库里已有 `wrangler.jsonc`（Worker）或 `functions/`（Pages），**选 Pages 或 Worker 都行**，
     两套服务端口令代码都提交了，逻辑一致。按你实际建的项目类型选。
3. 授权 GitHub，选中仓库 **`jerrys-un/bigdata-beisai`** → 开始设置
4. **构建设置**这样填：

   | 字段 | 填什么 |
   |---|---|
   | 框架预设 Framework preset | `None` |
   | 构建命令 Build command | `printf %s 'window.BD=window.BD||{};window.BD.gate={"on": false};' > data/gate.js` |
   | 部署命令 Deploy command | `npx wrangler deploy`（Worker）/ 留空（Pages） |
   | 构建输出目录 Build output directory | `/` |

   > 构建命令那行是在**关掉站点自带的前端口令门**（那个是给 GitHub Pages 静态版用的）。
   > 不关的话学生会连输两次密码。
   >
   > **为什么用 `printf` 覆盖写而不是 `sed -i 's/"on": true/.../'`**：
   > `sed` 只在原文是 `on: true` 时有效。如果 `data/gate.js` 已经是 `on: false`，
   > `sed` 什么都不改（日志照样显示"成功"），非常容易误判。`printf` 无条件覆盖，幂等。

5. **保存并部署**，等 1 分钟

---

## 第二步：开启口令（约 2 分钟）

**口令默认已经生效了。** 仓库里内置了一条兜端口令 `******`
（只存 SHA-256 摘要，不存明文），所以第 5 步点完「保存并部署」之后，
站点就已经会要求输口令了 —— **不必先去面板配任何变量**。

1. 打开站点 `https://bigdata-beisai.pages.dev`（或你的 `*.workers.dev` 地址）
2. 弹出口令页，输 **`******`** → 进站
3. 之后 30 天内这台设备不用再输；退出用 `/__gate/out`

### 换成你自己的口令（可选，推荐）

1. 进入 Pages 项目 → **设置 Settings** → **变量和机密 Variables and Secrets**
2. 添加一个变量：
   - 名称：`SITE_PASSWORD`（**一字不差**）
   - 值：你要的口令
   - 类型选 **Secret / 加密**
3. 保存 → 回 **部署 Deployments** 页，对最新一次部署点 **重试 Retry deployment**
   （变量改动**不会**自动触发重新部署，这一步最容易漏）

配了变量就以变量为准，内置的那条自动作废。

### 自检

浏览器访问 `你的站点地址/__gate/status`，看两个字段：

- `codeVersion`：应为 `2026-10-02.4`。数字更小 → 服务器还在跑旧代码
- `passwordSource`：`builtin` = 用的内置口令，`env:SITE_PASSWORD` = 用的环境变量

### 它是怎么拦住的

仓库里的 `functions/_middleware.js`（Pages）或 `worker.js`（Worker）会拦截**每一个请求**：

- 没带有效 cookie 的，直接返回登录页（连 HTML 都不给）
- 提交口令时，**在服务器端比对**，对了才下发一个 cookie
- cookie 里存的是**口令的 SHA-256 摘要**，不是口令本身
- 想换口令：加/改环境变量 `SITE_PASSWORD` 后**必须重新部署**（cookie 自动失效）
- 想彻底取消验证：删掉 `functions/` 目录推上去，或把 `FALLBACK_PW_HASH` 改成 `null`

### 排查口令不生效

| 现象 | 原因 | 怎么办 |
|---|---|---|
| 直接进站，没口令页 | 代码没重新部署 | Deployments → Retry deployment |
| `codeVersion` 是旧数字 | 同上，服务器跑旧代码 | 同上 |
| 变量配了但没用上 | 变量改动不触发重新部署 | 手动 Retry deployment 一次 |
| `passwordSource` 是 `env:` 但口令还是旧的 | 加到了别的项目/别的环境 | 确认加在**这个**项目的**生产**环境 |

---

## 方案 B：用 Access + 自定义域名（邮箱验证码）

如果你以后买了一个域名并绑到 Pages 项目上（Pages → 自定义域 Custom domains），就可以用 Access：

1. Cloudflare 控制台 → **Zero Trust** → 首次进入先设一个 team name
2. **Access** → **应用程序 Applications** → **添加应用程序** → **自托管 Self-hosted**
3. 应用域名：
   - **子域**只填一段名字，例如 `bigdata`（⚠️ 别填成 `bigdata.example.com`，那会报错）
   - **域**下拉里选你的域名，例如 `example.com`
   - 合起来就是 `bigdata.example.com`
4. 会话持续时间建议选 **30 天**（选短了学生每次都要重收验证码）
5. **策略**：动作 = 允许 Allow，选择器 = 所有人 Everyone
   （意思是：谁都能进，但必须先收一次邮箱验证码）
   - 想更严：选择器换成 `Emails ending in` → 填学校邮箱域名，就只有本校学生能进
6. 保存后，用无痕窗口验证会出现 Cloudflare 登录页

---

## 常见问题

**免费吗？**
Pages 免费（每月 500 次构建、无限带宽）；Functions 免费额度 10 万次请求/天；Access 免费版 50 个用户。一个班都用不完。

**方案 A 的口令在源码里吗？**
不在。口令存在 Cloudflare 的环境变量里（加密），仓库里只有一段「比对口令」的代码。

**两种方案能同时用吗？**
可以，但没必要——会让学生先过 Access 再输口令，两道关卡。

**学生收不到验证码？**（方案 B）
先看垃圾邮件；QQ 邮箱偶尔延迟。发件人是 "Cloudflare Access"。

**以后更新站点内容怎么办？**
推代码到 GitHub，Cloudflare Pages 会自动重新部署，口令设置保持不变。

**想彻底关掉验证？**
方案 A：删掉 `SITE_PASSWORD` 变量并重新部署。方案 B：删掉 Access 里那条应用。
