# -*- coding: utf-8 -*-
"""把 VM 上真跑一遍第 01 套的记录（demo_steps.json + 真实出图）打包成 demo.js

数据来源：
  demo_steps.json —— 在 CentOS 7.9 上真实执行每一步抓到的 stdout（run_demo.py 产出）
  web/demo/*.png   —— Matplotlib 真实生成的图
  web/demo/*.html  —— Pyecharts 真实生成的交互图
"""

DEMO_META = {
    "title": "真题示范 · 第 01 套（用户行为日志 / 数仓）",
    "sub": "下面每一步都是在这台 CentOS 7.9 机器上真实敲出来、真实跑出来的 —— 命令、输出、结果图都是真的，不是示意图。",
    "env": "CentOS 7.9 · Hadoop 3.1.3（伪分布式）· Hive 3.1.2 · MySQL 5.7.44 · Python 3.7.9",
    "how": [
        "先看命令，再看输出 —— 输出的每一行都要能对上号，看不懂就回速查手册查这条命令",
        "每块右下角有「退出码」和「耗时」：退出码 0 才叫跑通了，非 0 就是报错，要会看报错",
        "带 📷 的步骤是「必须截图」的点，你自己做的时候也要在这些位置截图",
        "结果图是真的 PNG，点开可以看大图；交互图是真的 Pyecharts HTML（可缩放、悬浮看数值）",
        "最后一步做了 Spark 与 MapReduce 的结果对照 —— 两个引擎算出一样的数，才说明前面没错",
        "照着这个顺序做一遍，第 01 套的流程就算走通了",
    ],
    "shots": [
        "jps —— NameNode / DataNode / ResourceManager / NodeManager 都在（缺一个都要回去查日志）",
        "HDFS 上传后的 ls 结果（要能看到文件名和大小，269.1 K 对得上本地文件）",
        "redis-cli ping 返回 PONG",
        "hive -e \"SELECT 1;\" 返回 1",
        "Hive 查询结果（COUNT(*) = 5000，以及前 3 行原始数据）",
        "/root/eduhq/result/ 下的结果文件与条数（3 / 24 / 12 条都要对得上）",
        "三份统计结果的真实内容（省份 12 条、设备 3 条、时段 24 条）",
        "MapReduce 跑完的词频结果",
        "Spark 跑完的词频结果，以及与 MR 的 diff 对照（一致 ✓）",
        "三张出图 PNG + 两张交互 HTML",
    ],
}

IMG_DESC = {
    "province_bar.png": "各省份访问量（Matplotlib 柱状图，含数值标注）",
    "device_pie.png": "设备类型占比（Matplotlib 饼图，带百分比）",
    "hour_line.png": "各时段浏览量（Matplotlib 折线图）",
    "province_bar.html": "各省份访问量（Pyecharts 交互柱状图，可缩放）",
    "device_pie.html": "设备类型占比（Pyecharts 交互环形图）",
}
