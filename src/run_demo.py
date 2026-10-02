# -*- coding: utf-8 -*-
"""在 VM 上真跑一遍「第 01 套」完整流程，把每一步的真实命令与真实输出抓成 JSON。
产物：/root/eduhq/ 下的结果文件 + 真实出图（PNG / HTML），以及 /root/eduhq/demo_steps.json
用法：python3 run_demo.py   （在 VM 上执行）
"""
import io
import json
import os
import random
import subprocess
import time

OUT = "/root/eduhq"
DATA = OUT + "/data"
RES = OUT + "/result"
HTML = OUT + "/html"
JSON_OUT = OUT + "/demo_steps.json"

STEPS = []


def env_prefix():
    return "source /etc/profile.d/bigdata.sh >/dev/null 2>&1; "


def run(cmd, title, phase, timeout=300, tail=None):
    """执行并记录真实输出"""
    full = "bash -c '" + env_prefix() + cmd.replace("'", "'\"'\"'") + "'"
    t0 = time.time()
    try:
        p = subprocess.run(["bash", "-c", env_prefix() + cmd],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        out = p.stdout.decode("utf-8", "replace")
        rc = p.returncode
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"").decode("utf-8", "replace")) + "\n…[执行超时，已截断]"
        rc = -1
    out = out.replace("\r\n", "\n").rstrip()
    if tail and len(out.split("\n")) > tail:
        lines = out.split("\n")
        out = "\n".join(lines[:tail]) + "\n…（共 %d 行，此处截取前 %d 行）" % (len(lines), tail)
    STEPS.append({
        "p": phase, "t": title, "cmd": cmd,
        "out": out[:6000], "rc": rc, "ms": int((time.time() - t0) * 1000),
    })
    print("[%s] rc=%s %s" % (phase, rc, title))
    return rc


def sh(cmd, timeout=300):
    p = subprocess.run(["bash", "-c", env_prefix() + cmd],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def main():
    for d in (OUT, DATA, RES, HTML):
        os.makedirs(d, exist_ok=True)

    # ---------- 造一份模拟的用户行为日志 ----------
    provinces = ["广东省", "江苏省", "浙江省", "山东省", "河南省", "四川省", "湖北省",
                 "湖南省", "河北省", "福建省", "北京市", "上海市"]
    devices = ["手机", "平板", "电脑"]
    netmodes = ["WIFI", "4G", "5G", "有线"]
    domains = ["www.taobao.com", "www.jd.com", "www.baidu.com", "www.bilibili.com",
               "www.zhihu.com", "www.qq.com", "www.163.com", "www.douyin.com"]
    random.seed(20260101)
    rows = []
    for i in range(5000):
        h = random.randint(0, 23)
        rows.append(",".join([
            random.choice(provinces),
            "2023-01-01 %02d:%02d:%02d" % (h, random.randint(0, 59), random.randint(0, 59)),
            random.choice(devices),
            random.choice(netmodes),
            random.choice(domains),
        ]))
    csv_path = DATA + "/behavior2023-01-01.csv"
    io.open(csv_path, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print("已生成模拟数据 %d 行 → %s" % (len(rows), csv_path))

    # ---------- 模块一：环境验活 ----------
    run("jps", "组件进程体检", "模块一")
    run("hdfs dfsadmin -report | head -14", "HDFS 集群容量报告", "模块一")

    pw = ""
    if os.path.exists("/root/.mysql_root_password"):
        pw = io.open("/root/.mysql_root_password", encoding="utf-8").read().strip().split("\n")[-1]
    run('mysql -uroot -p"%s" -e "SELECT VERSION(); SHOW DATABASES;"' % pw,
        "MySQL 版本与库列表", "模块一", tail=20)

    rp = ""
    if os.path.exists("/root/.redis_password"):
        rp = io.open("/root/.redis_password", encoding="utf-8").read().strip().split("\n")[-1]
    run('redis-cli -a "%s" ping; redis-cli -a "%s" info server | head -3' % (rp, rp),
        "Redis 探活（期望 PONG）", "模块一", tail=8)

    run("python3 -c \"import pandas, numpy, matplotlib; print('pandas', pandas.__version__); print('numpy', numpy.__version__); print('matplotlib', matplotlib.__version__)\"",
        "Python 三件套验证", "模块一", tail=8)

    # ---------- 模块二：数据落地 ----------
    run("hdfs dfs -mkdir -p /behavior/origin_log && hdfs dfs -put -f %s /behavior/origin_log/ && hdfs dfs -ls -h /behavior/origin_log/" % csv_path,
        "HDFS 建目录并上传原始日志", "模块二")
    run("hdfs dfs -cat /behavior/origin_log/behavior2023-01-01.csv | head -5",
        "查看 HDFS 上的原始日志前 5 行", "模块二", tail=8)

    # ---------- 模块二：Hive 数仓 ----------
    # 起 metastore（内存受限，限制堆大小）
    _, ms_state = sh("pgrep -f HiveMetaStore >/dev/null && echo up || echo down")
    if "down" in ms_state:
        print("metastore 未运行，启动中 …")
        subprocess.run(["bash", "-c", env_prefix() +
                        "HADOOP_HEAPSIZE=256 nohup hive --service metastore > /var/log/hive-metastore.log 2>&1 < /dev/null &"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(20)
    else:
        print("metastore 已在运行")

    run('hive -e "SELECT 1;" 2>/dev/null | tail -3', "Hive 可用性验证（SELECT 1）", "模块二", tail=6)

    hive_sql = """
CREATE DATABASE IF NOT EXISTS comm;
USE comm;
DROP TABLE IF EXISTS behavior_log;
CREATE EXTERNAL TABLE behavior_log (
  province STRING, log_time STRING, device STRING, netmode STRING, domain STRING
) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '/behavior/origin_log/';
SELECT COUNT(*) FROM behavior_log;
SELECT * FROM behavior_log LIMIT 3;
"""
    io.open("/root/eduhq/step_hive.sql", "w", encoding="utf-8").write(hive_sql)
    run("hive -f /root/eduhq/step_hive.sql 2>/dev/null | grep -vE '^(WARNING|SLF4J|Hive Session|OK$|Time taken)'",
        "Hive 建库建外部表并统计", "模块二", timeout=300, tail=25)

    exp_sql = """
USE comm;
INSERT OVERWRITE LOCAL DIRECTORY '/root/eduhq/result/ads_province'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT province, COUNT(*) AS cnt FROM behavior_log GROUP BY province ORDER BY cnt DESC;
INSERT OVERWRITE LOCAL DIRECTORY '/root/eduhq/result/ads_device'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT device, COUNT(*) AS cnt FROM behavior_log GROUP BY device ORDER BY cnt DESC;
INSERT OVERWRITE LOCAL DIRECTORY '/root/eduhq/result/ads_hour'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT hour(log_time) AS hh, COUNT(*) AS cnt FROM behavior_log GROUP BY hour(log_time) ORDER BY hh;
"""
    io.open("/root/eduhq/step_export.sql", "w", encoding="utf-8").write(exp_sql)
    run("hive -f /root/eduhq/step_export.sql 2>/dev/null | tail -4",
        "三份统计结果导出到 /root/eduhq/result/", "模块二", timeout=420, tail=8)

    run("ls -lh /root/eduhq/result/ && echo '--- 条数 ---' && wc -l /root/eduhq/result/*/000000_0",
        "核对结果文件与条数", "模块二", tail=20)

    # ---------- 模块二：MapReduce wordcount ----------
    run("hdfs dfs -cat /behavior/origin_log/behavior2023-01-01.csv | awk -F',' '{print $5}' > /root/eduhq/data/domain.txt && "
        "hdfs dfs -mkdir -p /behavior/wc_in && hdfs dfs -put -f /root/eduhq/data/domain.txt /behavior/wc_in/ && "
        "hdfs dfs -rm -r -f /behavior/wc_out",
        "抽取域名列为 MR 准备输入", "模块二", tail=6)
    run("hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.3.jar wordcount /behavior/wc_in /behavior/wc_out 2>&1 | tail -6",
        "MapReduce 跑 wordcount（域名词频）", "模块二", timeout=420, tail=8)
    run("hdfs dfs -cat /behavior/wc_out/part-r-00000", "查看 MR 词频结果", "模块二", tail=12)

    # ---------- 模块三：出图 ----------
    py = r'''
import pandas as pd, matplotlib.pyplot as plt, io, os
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

prov = pd.read_csv('/root/eduhq/result/ads_province/000000_0', header=None, names=['province','cnt'])
dev  = pd.read_csv('/root/eduhq/result/ads_device/000000_0', header=None, names=['device','cnt'])
hour = pd.read_csv('/root/eduhq/result/ads_hour/000000_0', header=None, names=['hh','cnt'])
print('省份', len(prov), '设备', len(dev), '时段', len(hour))

fig, ax = plt.subplots(figsize=(11,5))
d = prov.sort_values('cnt', ascending=False)
ax.bar(d['province'], d['cnt'], color='#4f46e5')
ax.set_title('各省份访问量'); ax.set_ylabel('访问量'); plt.xticks(rotation=35, ha='right')
for i,v in enumerate(d['cnt']): ax.text(i, v, str(v), ha='center', va='bottom', fontsize=9)
plt.tight_layout(); plt.savefig('/root/eduhq/html/province_bar.png', dpi=110); plt.close()

fig, ax = plt.subplots(figsize=(7,6))
ax.pie(dev['cnt'], labels=dev['device'], autopct='%1.1f%%', colors=['#4f46e5','#06b6d4','#f59e0b'])
ax.set_title('设备类型占比')
plt.tight_layout(); plt.savefig('/root/eduhq/html/device_pie.png', dpi=110); plt.close()

fig, ax = plt.subplots(figsize=(11,5))
ax.plot(hour['hh'], hour['cnt'], marker='o', color='#06b6d4', linewidth=2)
ax.set_title('各时段浏览量'); ax.set_xlabel('小时'); ax.set_ylabel('浏览量'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig('/root/eduhq/html/hour_line.png', dpi=110); plt.close()
print('三张 PNG 已生成')
'''
    io.open("/root/eduhq/step_plot.py", "w", encoding="utf-8").write(py)
    run("python3 /root/eduhq/step_plot.py", "Matplotlib 出三张结果图", "模块三", timeout=300, tail=10)

    pye = r'''
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
import pandas as pd
prov = pd.read_csv('/root/eduhq/result/ads_province/000000_0', header=None, names=['province','cnt'])
d = prov.sort_values('cnt', ascending=False)
bar = (Bar().add_xaxis(list(d['province'])).add_yaxis('访问量', list(d['cnt']))
       .set_global_opts(title_opts=opts.TitleOpts(title='各省份访问量（Pyecharts 交互图）'),
                        datazoom_opts=opts.DataZoomOpts()))
bar.render('/root/eduhq/html/province_bar.html')
dev = pd.read_csv('/root/eduhq/result/ads_device/000000_0', header=None, names=['device','cnt'])
pie = (Pie().add('', [list(z) for z in zip(dev['device'], dev['cnt'])], radius=['35%','65%'])
       .set_global_opts(title_opts=opts.TitleOpts(title='设备类型占比')))
pie.render('/root/eduhq/html/device_pie.html')
print('两个交互 HTML 已生成')
'''
    io.open("/root/eduhq/step_pye.py", "w", encoding="utf-8").write(pye)
    run("python3 /root/eduhq/step_pye.py 2>&1 | tail -4", "Pyecharts 出两张交互图", "模块三", timeout=300, tail=6)

    run("ls -lh /root/eduhq/html/", "核对出图产物", "模块三", tail=12)

    io.open(JSON_OUT, "w", encoding="utf-8").write(
        json.dumps({"steps": STEPS}, ensure_ascii=False, indent=1))
    print("已写出", JSON_OUT, len(STEPS), "步")


if __name__ == "__main__":
    main()
