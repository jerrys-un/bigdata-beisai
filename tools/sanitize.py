# -*- coding: utf-8 -*-
"""把 web/ 复制成 public/，并做公开脱敏：
   - 内网 IP / 主机名 → 教学示例地址
   - 真实口令 → ******
   - 公开版打开「进站口令门」（GitHub Pages 是静态托管，只能这样挡一层）

用法：
   python sanitize.py                     默认开启口令门，口令 bdstudy2026
   python sanitize.py --gate 我要的口令    自定义进站口令
   python sanitize.py --no-gate           不设口令（完全公开）
"""
import hashlib
import json
import os
import re
import shutil
import sys
import io

SRC = "web"
DST = "public"

RULES = [
    (r"10\.30\.11\.44", "192.168.1.100"),
    (r"10\.30\.11\.45", "192.168.1.101"),
    (r"10\.30\.11\.46", "192.168.1.102"),
    (r"centos7-vm", "master"),   # 不能加 \b：JSON 里前面是转义的 \n，n 属单词字符会破坏边界
    (r"Honghe@\d+", "******"),
    (r"Edu@\d+", "******"),
    (r"Hive@\d+", "******"),
    (r"Redis@\d+", "******"),
    (r"bdstudy2026", "******"),
    (r"闯关学习站 · ?10\.30\.11\.44", "闯关学习站 · 离线可用"),
]

SAFE_EXT = (".js", ".json", ".html", ".css", ".md", ".txt", ".yml", ".xml", ".sh", ".conf")


def clean(text):
    for pat, rep in RULES:
        text = re.sub(pat, rep, text)
    return text


def gate_js(pw, on):
    """进站口令门：只写 SHA-256 摘要，明文口令不会出现在仓库里"""
    h = hashlib.sha256(pw.encode("utf-8")).hexdigest()
    cfg = {"on": bool(on), "hash": h, "hint": "口令找老师要"}
    return "window.BD=window.BD||{};window.BD.gate=" + json.dumps(cfg, ensure_ascii=False) + ";"


def main():
    # 只同步站点三件套；public/ 下的 README.md、src/、tools/ 是手工维护的，不能删
    for sub in ("index.html", "assets", "data", "demo"):
        s = os.path.join(SRC, sub)
        d = os.path.join(DST, sub)
        if os.path.isfile(s):
            shutil.copy2(s, d)
        else:
            if os.path.isdir(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
    n = 0
    for root, dirs, files in os.walk(DST):
        for f in files:
            if not f.endswith(SAFE_EXT):
                continue
            p = os.path.join(root, f)
            t = io.open(p, encoding="utf-8").read()
            t2 = clean(t)
            if t2 != t:
                io.open(p, "w", encoding="utf-8").write(t2)
                n += 1
    print("已生成 %s/，脱敏 %d 个文件" % (DST, n))

    # 复查
    bad = []
    for root, dirs, files in os.walk(DST):
        for f in files:
            if not f.endswith(SAFE_EXT):
                continue
            t = io.open(os.path.join(root, f), encoding="utf-8").read()
            for pat in (r"10\.30\.11\.", r"centos7-vm", r"Honghe@", r"Edu@\d", r"Hive@\d", r"Redis@\d", r"bdstudy2026"):
                if re.search(pat, t):
                    bad.append((os.path.join(root, f), pat))
    print("复查：", "干净 ✓" if not bad else "仍有残留 %s" % bad[:5])

    # 进站口令门：脱敏之后写，避免被上面的规则误替换
    argv = sys.argv[1:]
    on = "--no-gate" not in argv
    pw = "bdstudy2026"
    if "--gate" in argv:
        i = argv.index("--gate")
        if i + 1 < len(argv):
            pw = argv[i + 1]
        if not pw or pw.startswith("--"):
            pw = "bdstudy2026"
    fp = os.path.join(DST, "data", "gate.js")
    if not os.path.isdir(os.path.dirname(fp)):
        os.makedirs(os.path.dirname(fp))
    io.open(fp, "w", encoding="utf-8").write(gate_js(pw, on))
    print("进站口令门：", ("已开启（口令摘要 %s…）" % hashlib.sha256(pw.encode("utf-8")).hexdigest()[:12]) if on else "已关闭")


if __name__ == "__main__":
    main()
