# -*- coding: utf-8 -*-
"""构建大数据学习网站的数据文件。

输入：
  ../大数据理论知识点归纳.md   理论知识点（12 章）
  ../bigdata-config-guide.md  配置详解（17 章）
  ../conf-annotated/*         24 个带中文注释的配置文件
  ../_tiku.txt                712 道题库原文
输出：
  web/data/knowledge.json / configs.json / quiz.json / env.json
"""
import io
import json
import os
import re
import collections
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import exam_data  # noqa: E402
import skills_data  # noqa: E402
import concepts_data  # noqa: E402
ROOT = os.path.dirname(BASE)
OUT = os.path.join(BASE, "web", "data")


# --------------------------- Markdown -> HTML ---------------------------
def inline(s):
    """行内标记：转义 HTML + 代码 + 粗体 + 斜体"""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # 行内代码先占位，避免被粗体规则误伤
    codes = []

    def _code(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    s = re.sub(r"`([^`]+)`", _code, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    for i, c in enumerate(codes):
        s = s.replace("\x00%d\x00" % i, "<code>%s</code>" % c)
    return s


def md2html(text):
    """极简 Markdown 渲染：标题 / 代码块 / 表格 / 引用 / 列表 / 分隔线 / 段落"""
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)

    def flush_list(buf):
        if not buf:
            return
        out.append("<ul>" + "".join("<li>%s</li>" % inline(x) for x in buf) + "</ul>")
        buf[:] = []

    while i < n:
        line = lines[i]

        # 代码块
        if line.strip().startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            body = "\n".join(buf).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append("<pre><code>%s</code></pre>" % body)
            continue

        # 分隔线
        if re.match(r"^\s*---+\s*$", line):
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lv = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lv, inline(m.group(2).strip()), lv))
            i += 1
            continue

        # 表格
        if line.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                raw = lines[i].strip()
                if re.match(r"^\s*\|[\s:\-|]+\|\s*$", raw):
                    i += 1
                    continue
                cells = [c.strip() for c in raw.strip("|").split("|")]
                rows.append(cells)
                i += 1
            if rows:
                head = "".join("<th>%s</th>" % inline(c) for c in rows[0])
                body = "".join(
                    "<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in rows[1:]
                )
                out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (head, body))
            continue

        # 引用（连续行合并为一个 blockquote）
        if line.strip().startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner = "\n".join(buf)
            # 引用里的软换行保留为 <br>
            paras = [p for p in inner.split("\n\n") if p.strip()]
            html = "".join("<p>%s</p>" % inline(p.strip()).replace("\n", "<br>") for p in paras)
            out.append("<blockquote>%s</blockquote>" % html)
            continue

        # 列表
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            buf = []
            while i < n:
                mm = re.match(r"^\s*[-*]\s+(.*)$", lines[i])
                if not mm:
                    break
                buf.append(mm.group(1).strip())
                i += 1
            flush_list(buf)
            continue

        # 有序列表
        m = re.match(r"^\s*\d+[.、)]\s+(.*)$", line)
        if m:
            buf = []
            while i < n:
                mm = re.match(r"^\s*\d+[.、)]\s+(.*)$", lines[i])
                if not mm:
                    break
                buf.append(mm.group(1).strip())
                i += 1
            out.append("<ol>" + "".join("<li>%s</li>" % inline(x) for x in buf) + "</ol>")
            continue

        # 空行
        if not line.strip():
            i += 1
            continue

        # 段落（连续非空行合并）
        buf = []
        while i < n and lines[i].strip() and not re.match(
            r"^\s*(#{1,6}\s|>|[-*]\s|\d+[.、)]\s|\||```|---+$)", lines[i]
        ):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
        else:
            i += 1

    return "\n".join(out)


# --------------------------- 1. 理论知识点 ---------------------------
def build_knowledge():
    path = os.path.join(ROOT, "大数据理论知识点归纳.md")
    text = io.open(path, encoding="utf-8").read()
    lines = text.replace("\r\n", "\n").split("\n")

    # 按二级标题切块
    blocks = []
    cur = None
    for ln in lines:
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            cur = {"title": m.group(1).strip(), "lines": []}
            blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(ln)

    # 章节序号 -> 稳定英文 id（供路由 / 练习跳转使用）
    CNID = {
        "一": "intro", "二": "hadoop", "三": "hive", "四": "spark", "五": "flink",
        "六": "docker", "七": "kafka", "八": "sqoop", "九": "flume", "十": "zookeeper",
        "十一": "compare", "十二": "tips", "十三": "x13", "十四": "x14",
    }
    mods = []
    for b in blocks:
        title = b["title"]
        body = "\n".join(b["lines"]).strip()
        cnt = re.search(r"（\s*(\d+)\s*题\s*）", title)
        mseq = re.match(r"^([一二三四五六七八九十]+)、", title)
        mods.append(
            {
                "id": CNID.get(mseq.group(1), "m%d" % len(mods)) if mseq else "m%d" % len(mods),
                "title": title,
                "count": int(cnt.group(1)) if cnt else 0,
                "html": md2html(body),
            }
        )

    # 拆分：前 3 块（一、二…）里的「一、题库结构总览」作为 intro
    intro = [m for m in mods if m["title"].startswith("一、")]
    theory = [m for m in mods if not m["title"].startswith("一、")]
    # 学习模块只取带题量的 9 个 + 跨模块对比 / 备考
    learn = [m for m in theory if m["count"] > 0]
    extra = [m for m in theory if m["count"] == 0]

    data = {
        "intro": md2html("\n".join(x["html"] for x in intro))
        if intro
        else "",
        "modules": learn,
        "extra": extra,
    }
    io.open(os.path.join(OUT, "knowledge.json"), "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1)
    )
    print("knowledge.json: 模块 %d + 附加 %d" % (len(learn), len(extra)))
    return data


# --------------------------- 2. 配置文件 ---------------------------
CONF_DEF = [
    ("hadoop", "Hadoop 3.1.3", [
        ("core-site.xml", "/opt/hadoop/etc/hadoop/core-site.xml", "xml", "全局默认文件系统与临时目录，管「全局」"),
        ("hdfs-site.xml", "/opt/hadoop/etc/hadoop/hdfs-site.xml", "xml", "副本数、NameNode/DataNode 数据目录，管「存储」"),
        ("yarn-site.xml", "/opt/hadoop/etc/hadoop/yarn-site.xml", "xml", "ResourceManager/NodeManager 通信与 Web 端口，管「资源」"),
        ("mapred-site.xml", "/opt/hadoop/etc/hadoop/mapred-site.xml", "xml", "指明计算框架跑在 yarn 上，管「计算」"),
        ("hadoop-env.sh", "/opt/hadoop/etc/hadoop/hadoop-env.sh", "bash", "JAVA_HOME 与各角色 JVM 堆大小"),
        ("workers", "/opt/hadoop/etc/hadoop/workers", "text", "从节点清单，伪分布式只有本机"),
    ]),
    ("zookeeper", "ZooKeeper 3.5.7", [
        ("zoo.cfg", "/opt/zookeeper/conf/zoo.cfg", "ini", "tickTime / dataDir / clientPort 三大件"),
        ("java.env", "/opt/zookeeper/conf/java.env", "bash", "ZK 的 JVM 堆与 GC 日志"),
    ]),
    ("mysql", "MySQL 5.7.44", [
        ("zz-charset.cnf", "/etc/my.cnf.d/zz-charset.cnf", "ini", "统一 utf8mb4，避免 Hive 元数据中文乱码"),
    ]),
    ("hive", "Hive 3.1.2", [
        ("hive-site.xml", "/opt/hive/conf/hive-site.xml", "xml", "元数据库指向 MySQL 的连接串与账号"),
        ("hive-env.sh", "/opt/hive/conf/hive-env.sh", "bash", "HADOOP_HOME / HIVE_CONF_DIR 等环境"),
    ]),
    ("kafka", "Kafka 2.4.1", [
        ("kafka-server.properties", "/opt/kafka/config/server.properties", "ini", "broker.id、日志目录、ZK 连接、监听地址"),
    ]),
    ("spark", "Spark 3.1.1", [
        ("spark-defaults.conf", "/opt/spark/conf/spark-defaults.conf", "text", "driver/executor 内存与核数，4G 机器必须压小"),
        ("spark-env.sh", "/opt/spark/conf/spark-env.sh", "bash", "JAVA_HOME / SPARK_MASTER / 历史服务"),
    ]),
    ("flink", "Flink 1.14.0", [
        ("flink-conf.yaml", "/opt/flink/conf/flink-conf.yaml", "yaml", "slot 数、内存模型、Web UI 端口"),
    ]),
    ("hbase", "HBase 2.2.3", [
        ("hbase-site.xml", "/opt/hbase/conf/hbase-site.xml", "xml", "分布式开关、根路径、外部 ZooKeeper 地址"),
        ("hbase-env.sh", "/opt/hbase/conf/hbase-env.sh", "bash", "禁用自带 ZK、堆大小、Hadoop 3 classpath"),
    ]),
    ("redis", "Redis 6.2.6", [
        ("redis.conf", "/opt/redis/redis.conf", "ini", "绑定地址、持久化、内存上限"),
        ("redis.service", "/etc/systemd/system/redis.service", "ini", "systemd 单元：前台运行 + 开机自启"),
    ]),
    ("system", "系统与容器", [
        ("bigdata.sh", "/etc/profile.d/bigdata.sh", "bash", "一键注入所有组件的环境变量"),
        ("daemon-json-说明.txt", "/etc/docker/daemon.json（注释版）", "text", "Docker 引擎：数据盘、镜像加速、日志轮转"),
        ("aria2-compose.yml", "/data/aria2/docker-compose.yml", "yaml", "aria2 + AriaNg 下载服务"),
        ("metube-compose.yml", "/data/metube/docker-compose.yml", "yaml", "MeTube 视频下载网页界面"),
        ("beszel-compose.yml", "/data/beszel/docker-compose.yml", "yaml", "Beszel 轻量监控（hub + agent）"),
    ]),
]


def build_configs():
    src = os.path.join(ROOT, "conf-annotated")
    groups = []
    total = 0
    for gid, gname, files in CONF_DEF:
        items = []
        for fname, path, lang, desc in files:
            fp = os.path.join(src, fname)
            if not os.path.exists(fp):
                print("!! 缺失配置文件:", fname)
                continue
            content = io.open(fp, encoding="utf-8", errors="replace").read()
            items.append(
                {
                    "name": fname,
                    "path": path,
                    "lang": lang,
                    "desc": desc,
                    "lines": content.count("\n") + 1,
                    "content": content,
                }
            )
            total += 1
        groups.append({"id": gid, "name": gname, "files": items})
    io.open(os.path.join(OUT, "configs.json"), "w", encoding="utf-8").write(
        json.dumps({"groups": groups}, ensure_ascii=False, indent=1)
    )
    print("configs.json: %d 组 / %d 个文件" % (len(groups), total))


# --------------------------- 3. 题库 ---------------------------
def build_quiz():
    path = os.path.join(ROOT, "_tiku.txt")
    txt = io.open(path, encoding="utf-8").read()
    txt = txt.replace("江苏省职业学校技能大赛", "").replace("大数据应用与服务\n", "", 1)

    pat = re.compile(
        r"\[(\d+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]*)\]\s*\n(.*?)(?=\n\[\d+\]\[|\Z)",
        re.S,
    )
    items = pat.findall(txt)
    quiz = []
    for num, typ, _race, diff, kp, ans, body in items:
        body = body.strip()
        # 去掉题干前缀序号
        body = re.sub(r"^\s*\d+\s*[.、]\s*", "", body)
        lines = [l.rstrip() for l in body.split("\n")]
        stem = lines[0].strip()
        # 判断题题干常以空括号开头，去掉
        stem = re.sub(r"^[（(]\s*[)）]\s*", "", stem)
        options = []
        for l in lines[1:]:
            m = re.match(r"^\s*([A-D])[\.、:：]\s*(.*)$", l)
            if m:
                options.append({"key": m.group(1), "text": m.group(2).strip()})
            elif options and l.strip():
                options[-1]["text"] += " " + l.strip()
        if not stem:
            continue
        short = {"单项选择题": "单选", "判断题": "判断", "多选选择题": "多选"}.get(typ, typ)
        quiz.append(
            {
                "id": int(num),
                "type": short,
                "module": kp.strip(),
                "difficulty": diff.strip(),
                "answer": ans.strip(),
                "stem": stem,
                "options": options,
            }
        )
    quiz.sort(key=lambda x: x["id"])
    io.open(os.path.join(OUT, "quiz.json"), "w", encoding="utf-8").write(
        json.dumps({"total": len(quiz), "items": quiz}, ensure_ascii=False, indent=1)
    )
    print(
        "quiz.json: %d 题" % len(quiz),
        "| 题型", dict(collections.Counter(q["type"] for q in quiz)),
        "| 答案样例", dict(list(collections.Counter(q["answer"] for q in quiz).items())[:8]),
    )


# --------------------------- 4. 环境概览 ---------------------------
ENV = {
    "title": "大数据应用与服务 · 备赛学习站",
    "subtitle": "鸿合录播设备改造环境（Win7 + VMware + CentOS 7.9 单节点）",
    "host": "10.30.11.44",
    "machine": {
        "cpu": "Intel i7-4790（分配给 VM 2 vCPU）",
        "mem": "宿主机 8GB；VM 上限 4GB（务必留够给 Win7）",
        "disk0": "系统盘 33GB（/ 根分区）",
        "disk1": "数据盘 595GB（/data，独立物理盘）",
        "os": "CentOS 7.9 Minimal（glibc 2.17）",
        "vm": "VMware Workstation 15.5，单台 VM",
    },
    "components": [
        {"name": "Hadoop", "ver": "3.1.3", "role": "HDFS + YARN + MapReduce", "port": "9000 / 9870 / 8088", "status": "on"},
        {"name": "ZooKeeper", "ver": "3.5.7", "role": "分布式协调（Kafka / HBase 依赖）", "port": "2181", "status": "on"},
        {"name": "MySQL", "ver": "5.7.44", "role": "Hive 元数据库", "port": "3306", "status": "on"},
        {"name": "Hive", "ver": "3.1.2", "role": "数据仓库（SQL → MR/Spark）", "port": "10000 / 10002", "status": "按需"},
        {"name": "Kafka", "ver": "2.4.1", "role": "消息队列", "port": "9092", "status": "on"},
        {"name": "Spark", "ver": "3.1.1", "role": "内存计算", "port": "4040（运行时）", "status": "按需"},
        {"name": "Flink", "ver": "1.14.0", "role": "流计算", "port": "8081（与 MeTube 冲突，需改）", "status": "按需"},
        {"name": "HBase", "ver": "2.2.3", "role": "列式数据库", "port": "16000 / 16010", "status": "按需"},
        {"name": "Flume", "ver": "1.9.0", "role": "日志采集", "port": "—", "status": "按需"},
        {"name": "Redis", "ver": "6.2.6", "role": "缓存", "port": "6379", "status": "on"},
        {"name": "Python", "ver": "3.7.9", "role": "脚本与数据分析", "port": "—", "status": "on"},
        {"name": "Docker", "ver": "26.1.4", "role": "容器运行时", "port": "—", "status": "on"},
    ],
    "services": [
        {"name": "Samba", "port": "139 / 445", "url": "\\\\10.30.11.44\\share", "note": "Windows 直接访问 /data/share"},
        {"name": "OpenList", "port": "5244", "url": "http://10.30.11.44:5244", "note": "网页版文件管理"},
        {"name": "本学习站", "port": "8888", "url": "http://10.30.11.44:8888", "note": "理论 + 配置 + 练习"},
        {"name": "HDFS NameNode", "port": "9870", "url": "http://10.30.11.44:9870", "note": "看集群与文件树"},
        {"name": "YARN ResourceManager", "port": "8088", "url": "http://10.30.11.44:8088", "note": "看作业运行情况"},
        {"name": "AriaNg 下载", "port": "6880", "url": "http://10.30.11.44:6880", "note": "aria2 网页界面"},
        {"name": "MeTube", "port": "8081", "url": "http://10.30.11.44:8081", "note": "视频下载"},
        {"name": "Beszel 监控", "port": "8090", "url": "http://10.30.11.44:8090", "note": "CPU/内存/磁盘实时曲线"},
    ],
    "mem": {
        "total": "4 GB",
        "rows": [
            {"item": "CentOS 系统 + SSH + Docker 引擎", "size": "约 0.7 GB", "level": "base"},
            {"item": "NameNode + DataNode + SecondaryNameNode", "size": "约 1.0 GB", "level": "base"},
            {"item": "ResourceManager + NodeManager", "size": "约 0.6 GB", "level": "base"},
            {"item": "ZooKeeper", "size": "约 0.15 GB", "level": "base"},
            {"item": "Kafka", "size": "约 0.5 GB", "level": "on"},
            {"item": "MySQL 5.7", "size": "约 0.35 GB", "level": "on"},
            {"item": "Redis", "size": "约 0.05 GB", "level": "on"},
            {"item": "容器（Beszel / MeTube / aria2 / Hermes）", "size": "约 0.25 GB", "level": "on"},
            {"item": "HBase（与 Kafka 二选一）", "size": "约 1.4 GB", "level": "mutex"},
            {"item": "Flink 集群", "size": "约 1.8 GB", "level": "mutex"},
        ],
        "note": "实测常驻后剩余可用约 0.8 GB。HBase 与 Kafka 不能同时常驻；跑 Flink 前先停 Kafka + HBase。用 <code>bigdata-ctl</code> 一键启停。",
    },
    "warn": [
        "glibc 2.17 是硬门槛：任何需要 glibc ≥ 2.28 的软件在这台机器上跑不起来（Node.js 22+ 直接出局）。",
        "VM 内存上限 4GB，不要调到 5GB 以上——宿主机 Win7 自己要吃 1.5~2GB。",
        "aliyunpan 的 upload 不会跳过同名文件，而是生成 xxx(1) 副本；要同步请用 sync --policy increment，别用 -ow。",
        "VMware 里有快照时，数据盘的「独立」复选框是灰的，必须先关机删快照。",
        "systemctl is-active smbd 会返回 unknown——Samba 的单元名是 smb，不是 smbd。",
    ],
    "commands": [
        {"group": "Hadoop", "cmds": [
            ("start-dfs.sh && start-yarn.sh", "启动 HDFS 与 YARN"),
            ("hdfs dfs -ls /", "查看 HDFS 根目录"),
            ("hdfs dfsadmin -safemode get", "查安全模式（建不了目录先查它）"),
            ("hdfs dfsadmin -report", "看集群容量与 DataNode"),
            ("yarn application -list", "查看运行中的作业"),
        ]},
        {"group": "Hive", "cmds": [
            ("schematool -dbType mysql -initSchema", "初始化元数据库（只做一次）"),
            ("hive", "进入 Hive CLI"),
            ("SHOW DATABASES;", "查看库"),
        ]},
        {"group": "Kafka", "cmds": [
            ("kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties", "后台启动 broker"),
            ("kafka-topics.sh --create --bootstrap-server localhost:9092 --topic t1 --partitions 1 --replication-factor 1", "建主题（2.4.1 用 --bootstrap-server）"),
            ("kafka-console-producer.sh --broker-list localhost:9092 --topic t1", "命令行生产"),
            ("kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic t1 --from-beginning", "命令行消费"),
        ]},
        {"group": "ZooKeeper", "cmds": [
            ("zkServer.sh start", "启动 ZK"),
            ("zkCli.sh -server localhost:2181", "连客户端"),
            ("ls /", "查看根节点"),
        ]},
        {"group": "HBase", "cmds": [
            ("start-hbase.sh", "启动 HBase"),
            ("hbase shell -n < /tmp/cmd.txt", "批量执行命令（表名带引号）"),
            ("create 't2','cf'", "建表"),
        ]},
        {"group": "Redis", "cmds": [
            ("redis-cli ping", "探活（返回 PONG）"),
            ("redis-cli info memory", "看内存占用"),
        ]},
        {"group": "本机运维", "cmds": [
            ("bigdata-ctl status", "一键查看全部组件状态"),
            ("bigdata-ctl start all / stop all", "一键启停"),
            ("docker ps", "查看容器"),
            ("free -h", "看内存（备赛第一动作）"),
        ]},
    ],
}


def build_env():
    io.open(os.path.join(OUT, "env.json"), "w", encoding="utf-8").write(
        json.dumps(ENV, ensure_ascii=False, indent=1)
    )
    print("env.json 已生成")


def build_exam():
    data = {
        "modules8": exam_data.MODULES8,
        "ruleDiff": exam_data.RULE_DIFF,
        "showScore": exam_data.SHOW_SCORE,
        "sources4": exam_data.SOURCES4,
        "strategy": exam_data.STRATEGY,
        "advice": exam_data.ADVICE,
        "levels": exam_data.LEVELS,
        "training": exam_data.TRAINING,
        "demos": exam_data.DEMOS,
    }
    io.open(os.path.join(OUT, "exam.json"), "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1)
    )
    print("exam.json: 关卡 %d / 八大模块 %d / 实训范例 %d" % (len(data["levels"]), len(data["modules8"]), len(data["demos"])))


def build_skills():
    data = {"cats": skills_data.SKILLS}
    n = sum(len(c["cards"]) for c in skills_data.SKILLS)
    io.open(os.path.join(OUT, "skills.json"), "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1)
    )
    print("skills.json: %d 类 / %d 张实操卡" % (len(data["cats"]), n))


def build_concepts():
    data = {"groups": concepts_data.CONCEPTS, "anims": concepts_data.ANIMS}
    n = sum(len(g["cards"]) for g in concepts_data.CONCEPTS)
    io.open(os.path.join(OUT, "concepts.json"), "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1)
    )
    print("concepts.json: %d 个概念关 / %d 张概念卡 / %d 个动画" % (len(data["groups"]), n, len(data["anims"])))


def dump_js(name, obj):
    """同时输出 .js，便于 file:// 直接打开（fetch 在 file:// 下会被 CORS 拦）"""
    fp = os.path.join(OUT, name + ".js")
    io.open(fp, "w", encoding="utf-8").write(
        "window.BD=window.BD||{};window.BD.%s=" % name + json.dumps(obj, ensure_ascii=False) + ";"
    )


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    k = build_knowledge()
    build_configs()
    build_quiz()
    build_env()
    build_exam()
    build_skills()
    build_concepts()
    for nm in ("knowledge", "configs", "quiz", "env", "exam", "skills", "concepts"):
        obj = json.load(io.open(os.path.join(OUT, nm + ".json"), encoding="utf-8"))
        dump_js(nm, obj)
    print("全部数据已输出到", OUT)
