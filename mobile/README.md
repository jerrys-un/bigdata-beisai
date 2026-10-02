# 安卓客户端（Capacitor）

大数据应用与服务 · 闯关学习站的安卓 App。网页内容全部打进 APK，**完全离线运行**，不联网也能用。

## 📦 产物说明

构建会出两个包：

| 产物 | 体积 | 用途 |
|---|---|---|
| **release** | 约原来一半 | ✅ **发给学生用这个**（R8 混淆 + 资源压缩） |
| debug | 较大 | 自己排查问题时用（不混淆，可反查堆栈） |

本地目录：`dist/bigdata-beisai-<版本>.apk`（release）

## 🔧 本地构建链路

```bash
python build.py           # 生成 data/*.js 数据
python sanitize.py        # 脱敏 → public/
python build_mobile.py    # 同步到 mobile/www/ 并瘦身
cd mobile && npm install && npx cap sync android
cd android && ./gradlew assembleRelease
```

本机没有 JDK，编译交给 GitHub Actions：

```bash
python push_github.py "说明"   # 推代码（mobile/ 有改动会自动触发构建）
python get_apk.py              # 等构建完并下载到 dist/
python get_apk.py --status     # 只看状态
```

## 🔏 正式签名（重要）

不配签名时构建会**自动退回 debug 签名** —— 包能装，但每次重装签名不一致会冲突，
且无法上架应用市场。正式分发前请在 GitHub 仓库配两个 Secret：

| Secret 名 | 内容 | 怎么生成 |
|---|---|---|
| `BIGDATA_KEYSTORE_BASE64` | keystore 文件的 base64 | `base64 -w0 bigdata.keystore` |
| `BIGDATA_KEYSTORE_PASS` | keystore 密码 | 生成时自己定 |

一次性生成 keystore（**在你自己电脑上做，别在仓库里**）：

```bash
keytool -genkeypair -v -keystore bigdata.keystore \
        -alias bigdata -keyalg RSA -keysize 2048 -validity 10000
```

配好后 `mobile/android/app/build.gradle` 会自动识别并使用正式签名。

> ⚠️ keystore 一旦丢失，**已发布的 App 永远无法覆盖升级**，只能改包名重发。
> 建议同时离线备份一份。

## 📂 体积优化记录

原始 debug APK 5.3MB（解压后 11.5MB，其中 dex 8.3MB）。做了这些：

| 措施 | 省下 |
|---|---|
| R8 混淆 + 资源压缩（release 才生效） | dex 8.3MB → 约 2MB |
| 删掉 `data/*.json`（页面只读 `.js`，全项目零处 `fetch`） | 748 KB |
| 禁掉 App 内的 Service Worker | 避免缓存住旧版本 |
| 锁定竖屏 + 品牌色补全 | — |

**不要删 `data/*.js`** —— 那是页面真正加载的数据。`.json` 只是给 GitHub Pages
和 `file://` 直开时做 fetch 兜底，App 里走不到。
