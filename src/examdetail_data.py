# -*- coding: utf-8 -*-
"""十套赛题的「完整操作流程 + 命令 + 截图位 + 总结」

按 ZZ052 的三个模块组织：
  模块一 = 环境搭建（装组件 + 验证可用性，截图即得分证据）
  模块二 = 数据采集与处理（清洗、标注、入库、统计）
  模块三 = 数据分析与可视化（出图、出表、出报表）

每套给出：
  steps  分步操作流程（照着做就能做完）
  cmds   可直接复制的命令块
  shots  必须截图的证据点
  summary 复盘：考什么 / 易错点 / 时间分配 / 交卷自查
"""

DETAIL = {

# ============================== 第 01 套 ==============================
1: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 完全分布式：先建数据目录再改配置", "d": "建 hadoopDatas 系列子目录（tempDatas、namenodeDatas、datanodeDatas、dfs/nn/edits、dfs/snn/name），改 core-site.xml / hdfs-site.xml / yarn-site.xml / mapred-site.xml / workers，scp 分发 slave1、slave2，三节点配 HADOOP_HOME 与 PATH"},
        {"p": "模块一", "t": "格式化并启动，jps 验活", "d": "主节点 hdfs namenode -format（**只做一次**）→ start-dfs.sh → start-yarn.sh → 三节点 jps 都要有对应进程"},
        {"p": "模块一", "t": "MySQL 5.7：rpm 顺序不能乱", "d": "解压到 /root/software，依次 rpm -ivh common → libs → libs-compat → client → server，初始化启动，root 改密，改 user 表 host 为 % 开远程"},
        {"p": "模块一", "t": "MySQL 验证", "d": "mysql -uroot -p -e \"SELECT VERSION();\" 与完整 CRUD 链路各截一张"},
        {"p": "模块二", "t": "HDFS 落地原始日志", "d": "hdfs dfs -mkdir -p /behavior/origin_log → put 上传本地日志 → 9870 Web UI 验证"},
        {"p": "模块二", "t": "Excel 清洗 time 列", "d": "behavior2023-01-01.csv 的 time 列分列成「日期 + 时间」两列，另存"},
        {"p": "模块二", "t": "建数仓：comm 库 + 两张外部表", "d": "建 dim_date、dim_area 外部表（HDFS 路径 /behavior/dim/，\\t 分隔），**先删后建**，load data 导入，查前 3 行与总行数"},
        {"p": "模块二", "t": "统计并导出结果", "d": "省份访问量、时间段浏览量、设备类型、上网模式 → 导出到 /root/eduhq/result/ads_*，**逗号分隔**"},
        {"p": "模块三", "t": "出七张图", "d": "中国地图（省份访问量）、带时间轴柱形图、浏览量折线图、节假日与工作日对比折线图、设备类型堆积柱形图、上网模式堆积柱形图、域名访问词云图"},
        {"p": "模块三", "t": "收尾：脚本与 HTML 归位 + 背景图", "d": "脚本统一放 /root/eduhq/python/，HTML 输出到 /root/eduhq/html/，并嵌入指定背景图"},
    ],
    "cmds": [
        {"t": "模块一 · Hadoop 目录与分发", "lang": "bash", "code":
"mkdir -p /root/hadoopDatas/tempDatas\n"
"mkdir -p /root/hadoopDatas/namenodeDatas\n"
"mkdir -p /root/hadoopDatas/datanodeDatas\n"
"mkdir -p /root/hadoopDatas/dfs/nn/edits\n"
"mkdir -p /root/hadoopDatas/dfs/snn/name\n\n"
"# 改完配置后分发（三节点都要）\n"
"scp -r /opt/bigdata/hadoop-3.1.3 slave1:/opt/bigdata/\n"
"scp -r /opt/bigdata/hadoop-3.1.3 slave2:/opt/bigdata/\n"
"scp /etc/profile slave1:/etc/profile && scp /etc/profile slave2:/etc/profile\n\n"
"hdfs namenode -format      # 只在首次执行\n"
"start-dfs.sh && start-yarn.sh\n"
"jps                         # 主节点应有 4 个进程"},
        {"t": "模块一 · MySQL 安装与验证", "lang": "bash", "code":
"cd /root/software\n"
"rpm -ivh mysql-community-common-5.7*.rpm\n"
"rpm -ivh mysql-community-libs-5.7*.rpm\n"
"rpm -ivh mysql-community-libs-compat-5.7*.rpm\n"
"rpm -ivh mysql-community-client-5.7*.rpm\n"
"rpm -ivh mysql-community-server-5.7*.rpm\n\n"
"systemctl start mysqld\n"
"grep 'temporary password' /var/log/mysqld.log    # 取初始密码\n"
"mysql -uroot -p -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';\"\n"
"mysql -uroot -p -e \"UPDATE mysql.user SET host='%' WHERE user='root'; FLUSH PRIVILEGES;\"\n\n"
"# 验证（截图点）\n"
"mysql -uroot -p -e \"SELECT VERSION();\"\n"
"mysql -uroot -p -e \"SHOW DATABASES;\""},
        {"t": "模块二 · Hive 外部表与统计", "lang": "sql", "code":
"CREATE DATABASE IF NOT EXISTS comm;\n"
"USE comm;\n\n"
"DROP TABLE IF EXISTS dim_area;\n"
"CREATE EXTERNAL TABLE dim_area (\n"
"  province_id INT, province_name STRING\n"
") ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t'\n"
"LOCATION '/behavior/dim/';\n\n"
"LOAD DATA INPATH '/behavior/dim/area.txt' INTO TABLE dim_area;\n\n"
"SELECT * FROM dim_area LIMIT 3;\n"
"SELECT COUNT(*) FROM dim_area;"},
        {"t": "模块二 · 结果导出（逗号分隔，带条数）", "lang": "sql", "code":
"INSERT OVERWRITE LOCAL DIRECTORY '/root/eduhq/result/ads_province'\n"
"ROW FORMAT DELIMITED FIELDS TERMINATED BY ','\n"
"SELECT province_name, COUNT(*) AS cnt\n"
"FROM comm.behavior_log GROUP BY province_name ORDER BY cnt DESC;\n\n"
"# 导出后核对条数，文件名按题目要求带上 N\n"
"wc -l /root/eduhq/result/ads_province/000000_0"},
        {"t": "模块三 · Pyecharts 七图骨架", "lang": "python", "code":
"from pyecharts.charts import Map, Bar, Line, Pie, WordCloud\n"
"from pyecharts import options as opts\n\n"
"import pandas as pd\n"
"df = pd.read_csv('/root/eduhq/result/ads_province.csv', names=['province','cnt'])\n\n"
"m = (Map()\n"
"     .add('访问量', [list(z) for z in zip(df.province, df.cnt)], 'china')\n"
"     .set_global_opts(title_opts=opts.TitleOpts(title='各省份访问量'),\n"
"                      visualmap_opts=opts.VisualMapOpts(max_=int(df.cnt.max()))))\n"
"m.render('/root/eduhq/html/province_map.html')\n\n"
"# 其余六图同理：Bar（带时间轴用 Timeline）、Line、Pie、WordCloud\n"
"# ⚠ 题目若要求「嵌入背景图」，render 之后还要往 HTML 里补背景样式"},
    ],
    "shots": [
        "三节点 jps 输出（缺一个进程都要回查日志）",
        "MySQL 版本 + SHOW DATABASES 两张",
        "NameNode 9870 页面里 /behavior/origin_log 目录结构",
        "Hive 建表 + SELECT COUNT(*) 结果",
        "/root/eduhq/result/ 下结果文件列表（**要能看清文件名带条数**）",
        "七张图各截一张（HTML 在浏览器打开后的样子）",
    ],
    "summary": {
        "focus": "最完整的一套：三节点 Hadoop + MySQL + Hive + Flume 全链路，最后七张 Pyecharts 图。题量最大，时间最紧。",
        "traps": [
            "外部表必须先删后建，重复跑会报 AlreadyExists",
            "结果文件要求**逗号分隔**，写成 \\t 直接扣分",
            "Pyecharts 出的是 HTML 用 render，不是 savefig",
            "背景图嵌入这一步最容易漏，题目明确要求就要做",
        ],
        "time": "模块一 50 分钟（组件多，按 先Hadoop→MySQL→Hive→Flume 顺序）｜模块二 60 分钟｜模块三 50 分钟｜留 20 分钟自查",
        "check": [
            "结果文件都在 /root/eduhq/result/ 下且文件名带条数",
            "分隔符是逗号",
            "七张 HTML 都能打开且有数据",
            "脚本都在 /root/eduhq/python/",
        ],
    },
},

# ============================== 第 02 套 ==============================
2: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 完全分布式 + Hive 安装", "d": "按标准流程装 Hadoop，再装 Hive 3.1.2（放 MySQL 驱动、配 hive-site.xml、schematool 初始化元数据库）"},
        {"p": "模块一", "t": "MySQL 维护题（先做，最省时间）", "d": "改 root_sl_src 库 province 表 province_id=24 的名称为「内蒙古自治区」；按要求删除 city 表数据"},
        {"p": "模块二", "t": "12 张 CSV 导入 Hive", "d": "load 导入 equipment_dashboard 库；**自建** ods_province、ods_city 两张表（题目不会给建表语句）"},
        {"p": "模块二", "t": "上传原始日志到 HDFS", "d": "put sms_so_failure_logs_shell.txt 到 /source/logs/sms_so_failure_log"},
        {"p": "模块二", "t": "文本清洗（Python）", "d": "删工单表与设备表的首行标题、删前两列脏数据，另存为 *_shell.txt"},
        {"p": "模块二", "t": "MapReduce 数据标注", "d": "空字段统一打「未获取」，统一时间格式，**保证每行字段长度一致**，结果存 HDFS /source/mr/sms_so"},
        {"p": "模块二", "t": "建数仓表并统计", "d": "建 ods_sms_so_failure_log、ods_province_iso，统计设备数量与用户数量"},
        {"p": "模块三", "t": "三项分析", "d": "故障类型分布（正序前五）、交付状态（正序前五）、设备状态分布"},
        {"p": "模块三", "t": "出四张图", "d": "设备类型 TOP5 饼图、设备状态饼图、交付状态条形图、设备数量数字卡片"},
    ],
    "cmds": [
        {"t": "模块一 · Hive 初始化（截图取最后 10 行）", "lang": "bash", "code":
"cp mysql-connector-java-5.1.37.jar $HIVE_HOME/lib/\n"
"schematool -dbType mysql -initSchema\n\n"
"# 验证（本题型必截）\n"
"hive -e \"SELECT 1;\"\n"
"hive -e \"SHOW DATABASES;\"\n\n"
"# ⚠ schematool 输出很长，截图要取命令结束后的最后 10 行"},
        {"t": "模块一 · MySQL 维护题", "lang": "sql", "code":
"USE root_sl_src;\n"
"UPDATE province SET province_name = '内蒙古自治区' WHERE province_id = 24;\n"
"SELECT * FROM province WHERE province_id = 24;      -- 验证（截图）\n\n"
"DELETE FROM city WHERE city_id = 指定值;\n"
"SELECT COUNT(*) FROM city;                           -- 验证（截图）"},
        {"t": "模块二 · Python 文本清洗", "lang": "python", "code":
"import pandas as pd\n\n"
"# 工单表：删首行标题 + 删前两列\n"
"df = pd.read_csv('/root/sms_so_failure_logs.txt', header=None, dtype=str)\n"
"df = df.iloc[1:]            # 去掉首行标题\n"
"df = df.iloc[:, 2:]         # 去掉前两列脏数据\n"
"df.to_csv('/root/sms_so_failure_logs_shell.txt', index=False, header=False)\n"
"print('处理条数:', len(df))\n\n"
"# 设备表同样处理，另存 *_shell.txt"},
        {"t": "模块二 · MapReduce 标注要点", "lang": "java", "code":
"// map：按分隔符切分，逐字段判空\n"
"String[] fs = value.toString().split(\"\\\\|\", -1);   // -1 保留末尾空字段\n"
"StringBuilder sb = new StringBuilder();\n"
"for (String f : fs) {\n"
"    if (f == null || f.trim().isEmpty()) f = \"未获取\";   // 空字段统一打标\n"
"    sb.append(f).append(\"|\");\n"
"}\n"
"// ⚠ 关键：split 必须加 -1，否则末尾空字段被吞掉，字段长度就不一致了\n"
"// ⚠ 时间格式统一：SimpleDateFormat 解析后再 format 输出\n"
"context.write(NullWritable.get(), new Text(sb.toString()));"},
        {"t": "模块三 · 出四图", "lang": "python", "code":
"import pandas as pd, matplotlib.pyplot as plt\n"
"plt.rcParams['font.sans-serif'] = ['SimHei']      # 中文不乱码\n"
"plt.rcParams['axes.unicode_minus'] = False\n\n"
"df = pd.read_csv('/root/eduhq/result/fault_type.csv')\n"
"top5 = df.sort_values('cnt', ascending=True).tail(5)   # 正序前五 = 升序取尾\n\n"
"plt.figure(figsize=(10, 6))\n"
"plt.pie(top5['cnt'], labels=top5['type'], autopct='%1.1f%%')\n"
"plt.title('设备类型 TOP5')\n"
"plt.savefig('/root/eduhq/html/device_type_pie.png', dpi=150)\n"
"plt.show()"},
    ],
    "shots": [
        "schematool 初始化输出的**最后 10 行**",
        "hive -e \"SELECT 1;\" 返回 1",
        "MySQL province 表改后查询结果（含「内蒙古自治区」那一行）",
        "HDFS 上 /source/mr/sms_so 目录与文件",
        "MR 结果前 20 行（字段长度一致、空字段已打「未获取」）",
        "四张图各一张",
    ],
    "summary": {
        "focus": "数据标注 + 清洗的一套。核心难点是 MapReduce 标注：字段长度必须一致，空值统一打标、时间格式统一。",
        "traps": [
            "split 不加 -1 会吞掉末尾空字段 → 字段长度不一致直接判错",
            "ods_province / ods_city 题目不给建表语句，要自己按数据写",
            "「正序前五」是升序取尾 5 条，别写成倒序取前 5",
            "Hive 初始化截图只取最后 10 行，截全了反而看不清结论",
        ],
        "time": "模块一 45 分钟｜模块二 70 分钟（标注是重头）｜模块三 45 分钟｜留 20 分钟",
        "check": [
            "MR 输出每行字段数一致",
            "空字段都变成「未获取」",
            "两张自建表存在且能查到数据",
            "四张图中文不乱码",
        ],
    },
},

# ============================== 第 03 套 ==============================
3: {
    "steps": [
        {"p": "模块一", "t": "ZooKeeper 集群", "d": "apache-zookeeper-3.5.7-bin.tar.gz 解压改名，配 zoo.cfg（dataDir + 三个 server 节点），各节点 data 目录写 myid"},
        {"p": "模块一", "t": "Kafka 集群", "d": "kafka_2.11-2.4.1 解压改名，改 server.properties（broker.id 各节点不同、zookeeper.connect、advertised.listeners）"},
        {"p": "模块一", "t": "启 ZK → 启 Kafka → 验证", "d": "zkServer.sh start 三节点 → kafka-server-start.sh -daemon → **建 topic + 生产 + 消费**验证"},
        {"p": "模块一", "t": "Hive 元数据初始化", "d": "schematool 执行，**截图取命令结束最后 10 行**"},
        {"p": "模块二", "t": "pandas 读 hotel.csv", "d": "读 25 字段酒店详情并 print 打印（打印结果要截图）"},
        {"p": "模块二", "t": "pandas 四项清洗", "d": "删商圈为空的行；删缺失值 > 3 的列；评分空置 0；评分空置总平均（**保留一位小数**）"},
        {"p": "模块二", "t": "Excel 数据清洗", "d": "按题目要求完成 Excel 侧清洗"},
        {"p": "模块三", "t": "Python 分析三项", "d": "各商圈酒店总数（倒序前五）、各商圈平均房间数（正序前五）、五星级酒店平均评分"},
        {"p": "模块三", "t": "Python 出两图", "d": "各商圈酒店总数柱状图、各星级酒店平均评分折线图"},
        {"p": "模块三", "t": "Excel 透视表与透视图", "d": "一级/二级分类为行、楼层为列、合计（万元）为统计量，**降序**；透视图用柱状图，去掉纵轴与网格线"},
    ],
    "cmds": [
        {"t": "模块一 · ZooKeeper 配置", "lang": "bash", "code":
"tar -zxvf apache-zookeeper-3.5.7-bin.tar.gz -C /opt/bigdata/\n"
"mv /opt/bigdata/apache-zookeeper-3.5.7-bin /opt/bigdata/zookeeper-3.5.7\n\n"
"# zoo.cfg 关键三项\n"
"dataDir=/opt/bigdata/zookeeper-3.5.7/zkData\n"
"server.1=master:2888:3888\n"
"server.2=slave1:2888:3888\n"
"server.3=slave2:2888:3888\n\n"
"# 每个节点写自己的 myid（master 写 1，slave1 写 2 …）\n"
"echo 1 > /opt/bigdata/zookeeper-3.5.7/zkData/myid\n\n"
"zkServer.sh start && zkServer.sh status   # Mode: leader / follower"},
        {"t": "模块一 · Kafka 配置与验证（必截）", "lang": "bash", "code":
"# server.properties 关键三项（各节点 broker.id 不同）\n"
"broker.id=1\n"
"zookeeper.connect=master:2181,slave1:2181,slave2:2181\n"
"advertised.listeners=PLAINTEXT://master:9092\n\n"
"kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties\n\n"
"# 验证三连（截图点）\n"
"kafka-topics.sh --zookeeper master:2181 --create --topic vtest --partitions 1 --replication-factor 1\n"
"kafka-topics.sh --zookeeper master:2181 --describe --topic vtest    # Leader 不能是 -1\n"
"kafka-console-producer.sh --broker-list master:9092 --topic vtest   # 发一条 hello\n"
"kafka-console-consumer.sh --bootstrap-server master:9092 --topic vtest --from-beginning\n"
"# ⚠ 2.4.1 的 topics.sh 必须用 --zookeeper，用 --bootstrap-server 只打印 usage"},
        {"t": "模块二 · pandas 四项清洗", "lang": "python", "code":
"import pandas as pd\n"
"df = pd.read_csv('/root/hotel.csv')\n"
"print(df.head())                       # 读 + 打印（截图点）\n\n"
"df = df.dropna(subset=['商圈'])         # 1 删商圈为空的行\n"
"df = df.dropna(axis=1, thresh=len(df)-3)  # 2 删缺失值 > 3 的列\n"
"df['评分'] = df['评分'].fillna(0)        # 3 评分空置 0\n"
"mean_score = round(df['评分'].mean(), 1) # 4 总平均，保留一位小数\n"
"df['评分'] = df['评分'].replace(0, mean_score)\n\n"
"print('处理条数:', len(df))"},
        {"t": "模块三 · 分析与出图", "lang": "python", "code":
"# 各商圈酒店总数（倒序前五）\n"
"g1 = df.groupby('商圈').size().sort_values(ascending=False).head(5)\n"
"# 各商圈平均房间数（正序前五）\n"
"g2 = df.groupby('商圈')['房间数'].mean().sort_values(ascending=True).head(5)\n"
"# 五星级酒店平均评分\n"
"g3 = df[df['星级'] == '五星级']['评分'].mean()\n\n"
"import matplotlib.pyplot as plt\n"
"plt.rcParams['font.sans-serif'] = ['SimHei']; plt.rcParams['axes.unicode_minus'] = False\n"
"g1.plot(kind='bar'); plt.title('各商圈酒店总数 TOP5')\n"
"plt.savefig('/root/eduhq/html/hotel_area_bar.png', dpi=150); plt.show()"},
    ],
    "shots": [
        "zkServer.sh status 三节点（一个 leader 两个 follower）",
        "Kafka describe 结果（Leader 非 -1）",
        "Kafka 消费者收到消息（**这是链路打通的铁证**）",
        "schematool 输出最后 10 行",
        "pandas 读取 hotel.csv 的 print 结果",
        "两张 Python 图 + Excel 透视表与透视图",
    ],
    "summary": {
        "focus": "ZK + Kafka 集群配置的一套，配合 pandas 酒店数据清洗与 Excel 透视。组件配置分最重，Python 侧相对常规。",
        "traps": [
            "各节点 broker.id 必须不同，相同会互相踢",
            "各节点 myid 必须与 zoo.cfg 的 server.N 对应",
            "Kafka topics.sh 用错参数只打印 usage 不报错，容易误判",
            "「正序前五」与「倒序前五」别搞反",
            "评分总平均要保留一位小数",
        ],
        "time": "模块一 60 分钟（ZK+Kafka+Hive）｜模块二 50 分钟｜模块三 50 分钟｜留 20 分钟",
        "check": [
            "ZK 三节点状态正常",
            "Kafka 生产消费真的收到消息",
            "四项清洗都做了且顺序对",
            "Excel 透视表是降序、透视图去掉了纵轴与网格线",
        ],
    },
},

# ============================== 第 04 套 ==============================
4: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 完全分布式", "d": "标准流程：解压 → 改五个配置 → 分发 → 格式化 → 启动 → jps"},
        {"p": "模块一", "t": "Flume 1.9.0 安装验证", "d": "解压、配环境变量、**flume-ng version 验证**，传输 Hadoop 日志并查看 HDFS /tmp/flume 下的落地文件"},
        {"p": "模块一", "t": "Flink 1.14.0 on Yarn", "d": "per-job 模式跑 WordCount.jar：flink run -m yarn-cluster ... WordCount.jar"},
        {"p": "模块二", "t": "pandas 读 shopping.csv", "d": "读商品 ID、名称、价格、浏览量、销量、库存并打印"},
        {"p": "模块二", "t": "pandas 四项清洗", "d": "删库存 <10 或 >10000；删含「刷单」「捡漏」的行；删含「女装」的行；手机价格区间取平均"},
        {"p": "模块二", "t": "MapReduce 统计买家印象", "d": "按 user_impression 统计印象数并**降序**，格式 (印象, 次数)，存 HDFS 后读前 10 条"},
        {"p": "模块三", "t": "商品名分割分析", "d": "商品名按空格分割：首元素是品牌、其余是特征；统计品牌前十、特征前六、品牌销量前五"},
        {"p": "模块三", "t": "Matplotlib 出两图", "d": "不同价格区间手机销量柱状图、不同地区手机品牌占比饼图"},
    ],
    "cmds": [
        {"t": "模块一 · Flume 验证", "lang": "bash", "code":
"tar -zxvf apache-flume-1.9.0-bin.tar.gz -C /opt/bigdata/\n"
"flume-ng version                     # 必须能打印版本（截图点）\n\n"
"# 起 agent 传 Hadoop 日志到 HDFS\n"
"flume-ng agent -n a1 -c conf -f /root/flume-hdfs.conf \\\n"
"  -Dflume.root.logger=INFO,console\n\n"
"# 验证落地\n"
"hdfs dfs -ls -R /tmp/flume\n"
"hdfs dfs -cat /tmp/flume/* | head -5\n"
"# ⚠ -n 后面的 agent 名必须和 conf 文件里写的一致"},
        {"t": "模块一 · Flink on Yarn per-job", "lang": "bash", "code":
"flink run -m yarn-cluster \\\n"
"  -yjm 1024 -ytm 1024 \\\n"
"  $FLINK_HOME/examples/batch/WordCount.jar \\\n"
"  --input hdfs:///tmp/flume/events --output hdfs:///tmp/flink_out\n\n"
"# 验证\n"
"hdfs dfs -cat /tmp/flink_out/* | head -10\n"
"# ⚠ Flink 集群约 1.8G 内存，4G 机器上别和 HBase 同时开\n"
"# ⚠ 默认 Web 端口 8081 会与 MeTube 冲突，本机已改 8083"},
        {"t": "模块二 · pandas 四项清洗", "lang": "python", "code":
"import pandas as pd\n"
"df = pd.read_csv('/root/shopping.csv')\n"
"print(df.head())\n\n"
"df = df[(df['库存'] >= 10) & (df['库存'] <= 10000)]              # 1\n"
"df = df[~df['名称'].str.contains('刷单|捡漏', na=False)]           # 2\n"
"df = df[~df['名称'].str.contains('女装', na=False)]                # 3\n"
"df.loc[df['名称'].str.contains('手机', na=False), '价格'] = \\\n"
"    df.loc[df['名称'].str.contains('手机', na=False), '价格'].mean()  # 4\n\n"
"df.to_csv('/root/clean_shopping.csv', index=False)\n"
"print('处理条数:', len(df))"},
        {"t": "模块二 · MR 统计印象数（降序）", "lang": "java", "code":
"// Mapper：把每个 impression 拆出来写 1\n"
"String[] imps = value.toString().split(\",\");\n"
"for (String s : imps) {\n"
"    if (s != null && !s.trim().isEmpty())\n"
"        context.write(new Text(s.trim()), new IntWritable(1));\n"
"}\n\n"
"// 降序技巧：写两个 Job，或用 TreeMap 在 Reduce 端排序后输出\n"
"// 最简单：Reducer 里先收进 TreeMap，cleanup 时倒序写出\n"
"private TreeMap<Integer, String> tm = new TreeMap<>();\n"
"public void reduce(Text key, Iterable<IntWritable> vals, Context ctx) {\n"
"    int sum = 0; for (IntWritable v : vals) sum += v.get();\n"
"    tm.put(sum, key.toString());\n"
"}\n"
"protected void cleanup(Context ctx) {\n"
"    tm.descendingMap().forEach((c, k) -> { /* write (k, c) */ });\n"
"}"},
        {"t": "模块三 · 品牌/特征拆分与出图", "lang": "python", "code":
"parts = df['名称'].str.split(' ', expand=True)\n"
"df['品牌'] = parts[0]                                  # 首元素 = 品牌\n"
"df['特征'] = parts.iloc[:, 1:].apply(\n"
"    lambda r: ' '.join([x for x in r if x]), axis=1)   # 其余 = 特征\n\n"
"brand_top10 = df.groupby('品牌').size().sort_values(ascending=False).head(10)\n"
"feat_top6   = df['特征'].value_counts().head(6)\n"
"brand_sales = df.groupby('品牌')['销量'].sum().sort_values(ascending=False).head(5)\n\n"
"import matplotlib.pyplot as plt\n"
"plt.rcParams['font.sans-serif'] = ['SimHei']\n"
"brand_sales.plot(kind='bar')\n"
"plt.savefig('/root/eduhq/html/brand_sales.png', dpi=150)"},
    ],
    "shots": [
        "flume-ng version 输出",
        "HDFS /tmp/flume 下落地文件列表 + cat 内容",
        "Flink 作业提交成功 + 结果输出前 10 行",
        "pandas 读取与清洗后条数",
        "MR 印象统计结果前 10 条（**降序**）",
        "两张 Matplotlib 图",
    ],
    "summary": {
        "focus": "Flume + Flink 组件配置的一套，配合 pandas 条件清洗与 MR 排序统计。「降序输出」是这套的技术难点。",
        "traps": [
            "MR 默认只按 key 升序，要降序得自己排序（TreeMap 倒序或两 Job 法）",
            "Flume 的 -n 参数要与 conf 里的 agent 名完全一致",
            "Flink 内存吃 1.8G，先确认 Kafka/HBase 关了再跑",
            "pandas 条件筛选每个条件都要加括号，且 & 不是 and",
        ],
        "time": "模块一 60 分钟（Hadoop+Flume+Flink）｜模块二 55 分钟｜模块三 45 分钟｜留 20 分钟",
        "check": [
            "MR 输出确实是降序",
            "四项清洗顺序和阈值都对",
            "Flink 结果文件在 HDFS 上",
            "两张图中文正常",
        ],
    },
},

# ============================== 第 05 套 ==============================
5: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 完全分布式（唯一组件）", "d": "这套组件最少，Hadoop 装完即可，把时间留给后面三块分析"},
        {"p": "模块二", "t": "缺失值统计", "d": "读 distribution.csv，统计每列缺失值个数输出到 result_1.csv（字段 Column、Null_count）"},
        {"p": "模块二", "t": "HDFS 操作四连", "d": "根目录建 student → 上传 /root/clean-month.csv → 查看后 5 条 → 用**人性化显示**看占用空间"},
        {"p": "模块三", "t": "Echarts 补全饼图", "d": "统计 chengdu.js 中 11 种天气类型出现次数，转成 Echarts 数据格式并画饼图"},
        {"p": "模块三", "t": "Excel 处理与折线图", "d": "E_weather.csv 建成数据表并修整字段类型，过滤重复日期、按日期升序，画 4 城市 2011—2020 四季度平均低温折线图"},
        {"p": "模块三", "t": "Seaborn 面积图", "d": "clean-month.csv 画平均高温与低温面积图（主题 darkgrid、字体 SimSun、缩放 2；高温 #CC3…）"},
    ],
    "cmds": [
        {"t": "模块二 · 缺失值统计与导出", "lang": "python", "code":
"import pandas as pd\n"
"df = pd.read_csv('/root/distribution.csv')\n\n"
"null_cnt = df.isnull().sum()\n"
"out = pd.DataFrame({'Column': null_cnt.index, 'Null_count': null_cnt.values})\n"
"out.to_csv('/root/result_1.csv', index=False)\n"
"print(out)\n"
"# ⚠ 字段名必须是 Column / Null_count，大小写不对就扣分"},
        {"t": "模块二 · HDFS 四连（含人性化显示）", "lang": "bash", "code":
"hdfs dfs -mkdir /student\n"
"hdfs dfs -put /root/clean-month.csv /student/\n"
"hdfs dfs -cat /student/clean-month.csv | tail -5      # 查看后 5 条\n"
"hdfs dfs -du -h /student                              # **人性化显示** = -h\n"
"# ⚠ 题目要求「人性化显示」，就是 -h，别写成 -du -s"},
        {"t": "模块三 · Echarts 饼图补全", "lang": "js", "code":
"// 1) 先统计 11 种天气出现次数\n"
"// 2) 转成 Echarts 需要的 [{name:'晴', value:123}, ...]\n"
"var weatherData = weatherList.map(function (t) {\n"
"    return { name: t, value: countMap[t] };\n"
"});\n\n"
"// 3) 补全 option\n"
"option = {\n"
"    title:  { text: '天气类型分布', left: 'center' },\n"
"    tooltip:{ trigger: 'item' },\n"
"    legend: { orient: 'vertical', left: 'left' },\n"
"    series: [{\n"
"        name: '天气类型',\n"
"        type: 'pie',          // ⚠ 饼图是 pie\n"
"        radius: '50%',\n"
"        data: weatherData,\n"
"        emphasis: { itemStyle: { shadowBlur: 10 } }\n"
"    }]\n"
"};\n"
"myChart.setOption(option);"},
        {"t": "模块三 · Seaborn 面积图（参数要对齐题目要求）", "lang": "python", "code":
"import seaborn as sns, matplotlib.pyplot as plt\n"
"import pandas as pd\n\n"
"df = pd.read_csv('/root/clean-month.csv')\n\n"
"sns.set_theme(style='darkgrid', font='SimSun', font_scale=2)   # 主题/字体/缩放\n"
"plt.figure(figsize=(14, 8))\n"
"plt.fill_between(df['month'], df['high'], color='#CC3399', alpha=.5, label='平均高温')\n"
"plt.fill_between(df['month'], df['low'],  color='#3399CC', alpha=.5, label='平均低温')\n"
"plt.legend(); plt.xlabel('月份'); plt.ylabel('温度(℃)')\n"
"plt.savefig('/root/eduhq/html/weather_area.png', dpi=150)\n"
"plt.show()\n"
"# ⚠ 题目给了主题、字体、缩放、色值，必须逐条对齐，少一个就扣一分"},
    ],
    "shots": [
        "jps 四个进程",
        "result_1.csv 内容（Column / Null_count 两列）",
        "HDFS du -h 的人性化输出",
        "Echarts 饼图在浏览器中的效果",
        "Excel 折线图（4 城市四季度）",
        "Seaborn 面积图（主题字体缩放都对）",
    ],
    "summary": {
        "focus": "组件最少的一套（只有 Hadoop），但**分析题最碎**：Python 统计 + HDFS 操作 + Echarts 补全 + Excel + Seaborn，五块都要做。",
        "traps": [
            "result_1.csv 的字段名必须写成 Column / Null_count",
            "「人性化显示」= dfs -du -h，写错参数看不出容量单位",
            "Echarts 补全题要看清是饼图还是柱状图（yAxis 类目轴 vs 数值轴）",
            "Seaborn 的主题 / 字体 / 缩放 / 色值都是评分点，逐条核对",
        ],
        "time": "模块一 30 分钟｜模块二 40 分钟｜模块三 90 分钟（三块分析）｜留 20 分钟",
        "check": [
            "result_1.csv 字段与内容正确",
            "HDFS 后 5 条与 du -h 都截了",
            "Echarts 饼图数据 11 种天气齐全",
            "Seaborn 图与题目给的样式参数一致",
        ],
    },
},

# ============================== 第 06 套 ==============================
6: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 完全分布式", "d": "标准流程，三节点"},
        {"p": "模块一", "t": "Kafka 集群（含分发）", "d": "配环境变量文件并连同解压包一起拷到 slave1/slave2，启动后 **jps 查三节点进程**"},
        {"p": "模块一", "t": "Spark standalone", "d": "解压改名，配 spark-env.sh（SPARK_MASTER_HOST）与 slaves，start-all.sh 启动，8080 页面看 Worker"},
        {"p": "模块二", "t": "缺失字段计数最大值", "d": "按 distribution.csv 统计单条数据缺失字段计数的最大值，按指定格式输出到控制台"},
        {"p": "模块二", "t": "HDFS 五连操作", "d": "列目录 → 建 bigdata 目录 → 上传 /opt/eurasia_mainland.csv → 下载到 /root → 查看内容"},
        {"p": "模块二", "t": "MR 清洗异常值", "d": "清除年份/国家/区域为空的数据，存 HDFS /clean_data 并看大小"},
        {"p": "模块二", "t": "MR 统计灾害损失", "d": "每个国家不同年份中气候灾害受损经济最高的国家，输出前 10"},
        {"p": "模块三", "t": "Echarts 双柱状图", "d": "成都 2021 年每月平均最高/最低气温柱状图"},
        {"p": "模块三", "t": "Excel 带数据标记折线图", "d": "北京 2018—2021 年 12 个月空气质量最佳与最差，标题「空气质量波动」加粗居中、图例置底、涨跌柱线改浅色"},
        {"p": "模块三", "t": "Seaborn 柱状图", "d": "2011—2021 各城市最高温前 10（whitegrid、SimSun、缩放 3、hls 调色板、标签带 ℃、纵轴…）"},
    ],
    "cmds": [
        {"t": "模块一 · Kafka 分发与三节点验证", "lang": "bash", "code":
"tar -zxvf kafka_2.11-2.4.1.tgz -C /opt/bigdata/\n"
"mv /opt/bigdata/kafka_2.11-2.4.1 /opt/bigdata/kafka-2.4.1\n\n"
"# 环境变量文件 + 解压包一起拷\n"
"scp -r /opt/bigdata/kafka-2.4.1 slave1:/opt/bigdata/\n"
"scp -r /opt/bigdata/kafka-2.4.1 slave2:/opt/bigdata/\n"
"scp /etc/profile.d/bigdata.sh slave1:/etc/profile.d/\n"
"scp /etc/profile.d/bigdata.sh slave2:/etc/profile.d/\n\n"
"# 各节点改 broker.id 与 advertised.listeners 后启动\n"
"kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties\n\n"
"# 验证：三节点都要看\n"
"jps                                   # master / slave1 / slave2 各截一张\n"
"kafka-topics.sh --zookeeper master:2181 --list"},
        {"t": "模块一 · Spark standalone 与验证", "lang": "bash", "code":
"# spark-env.sh\n"
"export SPARK_MASTER_HOST=master\n"
"export JAVA_HOME=/opt/bigdata/jdk1.8.0_412\n"
"# slaves 文件里写 worker 主机名\n\n"
"$SPARK_HOME/sbin/start-all.sh\n"
"jps | grep -E 'Master|Worker'\n\n"
"# 验证（截图点）\n"
"spark-submit --class org.apache.spark.examples.SparkPi \\\n"
"  --master spark://master:7077 $SPARK_HOME/examples/jars/spark-examples_2.12-3.1.1.jar 10\n"
"# 输出 Pi is roughly 3.14xxxx\n"
"# 浏览器 http://master:8080 看 Worker 是否注册"},
        {"t": "模块二 · MR 清洗空值", "lang": "java", "code":
"public void map(LongWritable k, Text v, Context ctx) {\n"
"    String[] fs = v.toString().split(\",\", -1);\n"
"    // 年份 / 国家 / 区域 三个字段任一为空就丢弃\n"
"    if (fs.length < 3) return;\n"
"    if (fs[0].trim().isEmpty() || fs[1].trim().isEmpty() || fs[2].trim().isEmpty()) return;\n"
"    ctx.write(NullWritable.get(), v);\n"
"}\n"
"// ⚠ split 加 -1 保留末尾空字段，否则空值行会被误判为字段数不足\n"
"// ⚠ FileInputFormat 会静默过滤 _ / . 开头的文件，输入别用这类文件名"},
        {"t": "模块二 · MR 求每国家每年最高损失（前 10）", "lang": "java", "code":
"// Mapper：key = 国家 + 年份，value = 损失金额\n"
"String key = country + \"\\t\" + year;\n"
"ctx.write(new Text(key), new DoubleWritable(loss));\n\n"
"// Reducer：同 key 取最大值\n"
"double max = 0;\n"
"for (DoubleWritable v : vals) max = Math.max(max, v.get());\n"
"ctx.write(key, new DoubleWritable(max));\n\n"
"// 取前 10：cleanup 里用 TreeMap 倒序，或再跑一个排序 Job\n"
"// ⚠ 金额用 DoubleWritable，别用 IntWritable 截断小数"},
        {"t": "模块三 · Seaborn 参数逐条对齐", "lang": "python", "code":
"import seaborn as sns, matplotlib.pyplot as plt\n\n"
"sns.set_theme(style='whitegrid', font='SimSun', font_scale=3)   # 主题/字体/缩放\n"
"palette = sns.color_palette('hls', 10)                          # hls 调色板\n\n"
"ax = sns.barplot(x='city', y='high', data=top10, palette=palette)\n"
"for i, v in enumerate(top10['high']):\n"
"    ax.text(i, v, f'{v}℃', ha='center')                         # 标签带 ℃\n"
"plt.ylim(0, max(top10['high']) * 1.15)                          # 纵轴范围\n"
"plt.savefig('/root/eduhq/html/city_high.png', dpi=150)\n"
"plt.show()"},
    ],
    "shots": [
        "三节点 jps（Kafka 进程都在）",
        "Spark Pi 计算结果 + 8080 页面 Worker 列表",
        "HDFS 五连操作的过程（列目录/建目录/上传/下载/查看）",
        "MR 清洗后 /clean_data 目录大小",
        "MR 灾害统计前 10 条输出",
        "Echarts 双柱图 + Excel 折线图 + Seaborn 柱状图各一张",
    ],
    "summary": {
        "focus": "组件最多的一套（Hadoop + Kafka + Spark），加上两个 MR 编程题。时间最容易不够，Spark 能跑通 Pi 就赶紧往下走。",
        "traps": [
            "Kafka 分发后**各节点 broker.id 必须改**，忘了会互相踢",
            "Spark 的 examples jar 名含 Scala 版本 2.12，用 tab 补全",
            "MR 清洗时 split 不加 -1 会误判空值行",
            "金额用 DoubleWritable，IntWritable 会截断",
            "Seaborn 主题/字体/缩放/调色板/℃标签全是评分点",
        ],
        "time": "模块一 70 分钟（三个组件）｜模块二 70 分钟（两个 MR）｜模块三 50 分钟｜留 10 分钟",
        "check": [
            "三节点 Kafka 进程齐全",
            "Spark 作业能跑通",
            "两个 MR 输出都在 HDFS 上",
            "三张图的样式参数逐条核对过",
        ],
    },
},

# ============================== 第 07 套 ==============================
7: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 完全分布式", "d": "标准流程"},
        {"p": "模块一", "t": "Flume 1.9.0（传日志到 HDFS /tmp/flume）", "d": "解压配环境变量，写 conf，起 agent 验证落地"},
        {"p": "模块一", "t": "Flink on Yarn（per-job 跑 WordCount）", "d": "flink run -m yarn-cluster ... WordCount.jar"},
        {"p": "模块二", "t": "MySQL 建库三表", "d": "建 test 库，stu 表（学号主键）、course 表（课程号主键）、score 表（学号+课程号联合主键）"},
        {"p": "模块二", "t": "SQL 六连查", "d": "电子学院学生、选修 KCJG01 与 KCDZ02 的学生、姓名末尾带「华」、班级筛选、学分=2、成绩 75~80"},
        {"p": "模块二", "t": "HDFS result 目录往返", "d": "/root 建 result → 上传至根目录 → 查看 → 再下载回 /root"},
        {"p": "模块二", "t": "MR 两题", "d": "清 sku_info.csv 字段长度 <11 的记录（输出 HDFS 并打印前 20）；按 gender 统计 user 数"},
        {"p": "模块三", "t": "Excel 两图", "d": "岗位数量前十城市柱状图、各学历岗位占比饼图（ANALYSE.xlsx）"},
        {"p": "模块三", "t": "Web 项目补全（jobSite）", "d": "补 js/chat.js 的 getHotskill()（热门技术柱状图，**yAxis 类目轴**）与 getSalary()"},
        {"p": "模块三", "t": "Python 分析与四图", "d": "分析不同职业客户购买银行产品意向并画条形图；age / duration / campaign 三特征的直方图与概率密度图"},
    ],
    "cmds": [
        {"t": "模块二 · MySQL 三表（注意联合主键）", "lang": "sql", "code":
"CREATE DATABASE IF NOT EXISTS test DEFAULT CHARSET utf8mb4;\n"
"USE test;\n\n"
"CREATE TABLE stu (\n"
"  sno VARCHAR(20) PRIMARY KEY,\n"
"  sname VARCHAR(50) NOT NULL,\n"
"  dept VARCHAR(50),\n"
"  class VARCHAR(50)\n"
") DEFAULT CHARSET=utf8mb4;\n\n"
"CREATE TABLE course (\n"
"  cno VARCHAR(20) PRIMARY KEY,\n"
"  cname VARCHAR(50),\n"
"  credit INT\n"
") DEFAULT CHARSET=utf8mb4;\n\n"
"CREATE TABLE score (\n"
"  sno VARCHAR(20),\n"
"  cno VARCHAR(20),\n"
"  grade DECIMAL(5,2),\n"
"  PRIMARY KEY (sno, cno)          -- ⚠ 联合主键这么写，不能给两列各写一个 PRIMARY KEY\n"
") DEFAULT CHARSET=utf8mb4;"},
        {"t": "模块二 · SQL 六连查", "lang": "sql", "code":
"-- 1 电子学院学生\n"
"SELECT * FROM stu WHERE dept = '电子学院';\n\n"
"-- 2 同时选修 KCJG01 与 KCDZ02 的学生\n"
"SELECT s.* FROM stu s JOIN score sc ON s.sno = sc.sno\n"
"WHERE sc.cno IN ('KCJG01','KCDZ02')\n"
"GROUP BY s.sno HAVING COUNT(DISTINCT sc.cno) = 2;\n\n"
"-- 3 姓名末尾带「华」\n"
"SELECT * FROM stu WHERE sname LIKE '%华';\n\n"
"-- 4 班级筛选\n"
"SELECT * FROM stu WHERE class = '指定班级';\n\n"
"-- 5 学分 = 2 的课程\n"
"SELECT * FROM course WHERE credit = 2;\n\n"
"-- 6 成绩 75~80\n"
"SELECT * FROM score WHERE grade BETWEEN 75 AND 80;\n"
"-- ⚠ BETWEEN 是闭区间，包含 75 和 80"},
        {"t": "模块二 · MR 过滤短记录", "lang": "java", "code":
"public void map(LongWritable k, Text v, Context ctx) {\n"
"    String[] fs = v.toString().split(\",\", -1);\n"
"    if (fs.length >= 11) ctx.write(NullWritable.get(), v);   // 只留 >= 11 的\n"
"}\n"
"// 验证：hdfs dfs -cat /输出路径/part-* | head -20\n"
"// ⚠ 题目说「字段长度 < 11 的清除」，保留的是 >= 11；别把方向搞反"},
        {"t": "模块三 · Web 补全（yAxis 类目轴）", "lang": "js", "code":
"function getHotskill() {\n"
"    // 热门技术柱状图：横向柱状图 = xAxis 数值轴 + yAxis 类目轴\n"
"    var option = {\n"
"        title: { text: '热门技术 TOP10' },\n"
"        tooltip: { trigger: 'axis' },\n"
"        xAxis: { type: 'value' },\n"
"        yAxis: { type: 'category', data: skillNames },   // ⚠ 类目轴在 y\n"
"        series: [{ type: 'bar', data: skillCounts }]\n"
"    };\n"
"    chart.setOption(option);\n"
"}\n"
"// ⚠ 题目明确说 yAxis 是类目轴，写成 xAxis 类目就整题错"},
        {"t": "模块三 · 直方图与概率密度图", "lang": "python", "code":
"import pandas as pd, matplotlib.pyplot as plt\n"
"df = pd.read_csv('/root/bank.csv')\n\n"
"fig, axes = plt.subplots(3, 2, figsize=(14, 12))\n"
"for i, col in enumerate(['age', 'duration', 'campaign']):\n"
"    axes[i][0].hist(df[col], bins=30, color='#4f46e5', alpha=.7)\n"
"    axes[i][0].set_title(f'{col} 直方图')\n"
"    df[col].plot.density(ax=axes[i][1])          # 概率密度图\n"
"    axes[i][1].set_title(f'{col} 概率密度')\n"
"plt.tight_layout()\n"
"plt.savefig('/root/eduhq/html/bank_dist.png', dpi=150)\n"
"plt.show()"},
    ],
    "shots": [
        "jps + Flume 版本 + Flink 提交成功",
        "MySQL 三表结构（DESC 三张）",
        "六条 SQL 查询结果",
        "MR 短记录过滤后前 20 行",
        "Excel 两张图（ANALYSE.xlsx）",
        "Web 页面两个图表渲染效果",
        "Python 六宫格分布图",
    ],
    "summary": {
        "focus": "题量最大、类型最杂的一套：三个组件 + MySQL 建表查询 + 两个 MR + Excel + Web 补全 + Python 四图。**必须严格控时**。",
        "traps": [
            "score 表是联合主键 PRIMARY KEY (sno, cno)，写法特殊",
            "「同时选修两门」要用 HAVING COUNT(DISTINCT cno) = 2，不能简单 IN",
            "Echarts 补全题 yAxis 是类目轴，别写反",
            "MR 过滤方向：清除 < 11，保留 >= 11",
            "BETWEEN 75 AND 80 是闭区间",
        ],
        "time": "模块一 55 分钟｜模块二 65 分钟｜模块三 65 分钟｜留 5 分钟（这套接近做不完，优先保证组件与 SQL）",
        "check": [
            "三张表结构与主键都对",
            "六条查询都有结果截图",
            "Web 两个图表能渲染",
            "Python 六宫格图存在",
        ],
    },
},

# ============================== 第 08 套 ==============================
8: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 集群（跨节点分工）", "d": "**master 启 hdfs、slave2 启 yarn**，jps 查 master/slave1/slave2 三节点进程"},
        {"p": "模块一", "t": "ZooKeeper 3.5.7 集群", "d": "master 解压改名，改 /root/.bash_profile 配环境变量，拷配置与包到 slave，各节点写 myid，启动后查 Mode"},
        {"p": "模块二", "t": "pandas 读 data.csv", "d": "读电商用户行为 14 字段并打印"},
        {"p": "模块二", "t": "清洗三项", "d": "NAN 替换为 0；正则把 page 文字信息转数字 1；删 age ≥ 100 异常数据"},
        {"p": "模块二", "t": "缺失值定向填充", "d": "source 列：新用户填 direct、老用户填 seo；device 列：mac/window/linux 填 desktop"},
        {"p": "模块二", "t": "MySQL 建库三表与 CRUD", "d": "建 test 库及三表，完成建表、添加记录、查询"},
        {"p": "模块三", "t": "Excel 两图", "d": "各景点评论人数前十柱状图（**降序**）、各地出游人数百分比圆环图"},
        {"p": "模块三", "t": "Web 项目补全（traveSite）", "d": "补 js/index.js 的 getGradeData()（好评度**环形图**）与 getHotScenery()"},
    ],
    "cmds": [
        {"t": "模块一 · 跨节点启服务（注意分工）", "lang": "bash", "code":
"# ⚠ 本题特殊：hdfs 在 master 启，yarn 在 slave2 启\n"
"start-dfs.sh                  # master 上执行\n"
"ssh slave2 'source /etc/profile && start-yarn.sh'\n\n"
"# 三节点都要验\n"
"jps                       # master: NameNode / DataNode\n"
"ssh slave1 'jps'          # slave1: DataNode\n"
"ssh slave2 'jps'          # slave2: DataNode / ResourceManager / NodeManager\n\n"
"# ZK 环境变量写 .bash_profile 而不是 /etc/profile（题目指定）\n"
"echo 'export ZK_HOME=/opt/bigdata/zookeeper-3.5.7' >> /root/.bash_profile\n"
"echo 'export PATH=$PATH:$ZK_HOME/bin' >> /root/.bash_profile\n"
"source /root/.bash_profile"},
        {"t": "模块二 · pandas 清洗与定向填充", "lang": "python", "code":
"import pandas as pd, re\n"
"df = pd.read_csv('/root/data.csv')\n"
"print(df.head(), df.shape)\n\n"
"df = df.fillna(0)                                     # 1 NAN → 0\n"
"df['page'] = df['page'].apply(\n"
"    lambda x: 1 if re.search(r'\\d', str(x)) else x)   # 2 page 文字转数字 1\n"
"df = df[df['age'] < 100]                              # 3 删 age >= 100\n\n"
"# 定向填充：source 列\n"
"df.loc[(df['source'].isna()) & (df['user_type']=='new'), 'source'] = 'direct'\n"
"df.loc[(df['source'].isna()) & (df['user_type']=='old'), 'source'] = 'seo'\n"
"# 定向填充：device 列\n"
"df.loc[df['device'].isin(['mac','window','linux']), 'device'] = 'desktop'\n"
"print('处理条数:', len(df))"},
        {"t": "模块三 · Web 环形图补全", "lang": "js", "code":
"function getGradeData() {\n"
"    // 好评度环形图 = 饼图 + radius 写成 ['40%','70%']\n"
"    var option = {\n"
"        tooltip: { trigger: 'item' },\n"
"        legend: { bottom: 0 },\n"
"        series: [{\n"
"            type: 'pie',\n"
"            radius: ['40%', '70%'],      // ⚠ 内外半径 = 环形\n"
"            itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },\n"
"            label: { formatter: '{b}: {d}%' },\n"
"            data: [\n"
"                { name: '好评', value: good },\n"
"                { name: '中评', value: mid },\n"
"                { name: '差评', value: bad }\n"
"            ]\n"
"        }]\n"
"    };\n"
"    chart.setOption(option);\n"
"}"},
    ],
    "shots": [
        "master / slave1 / slave2 三节点 jps",
        "ZK 三节点 status（leader / follower）",
        "pandas 读取与清洗后条数",
        "MySQL 三张表 + 查询结果",
        "Excel 柱状图（降序）与圆环图",
        "Web 页面环形图渲染效果",
    ],
    "summary": {
        "focus": "跨节点分工启动（hdfs 在 master、yarn 在 slave2）是这套的特色，读题要看清在哪台机器上执行。pandas 定向填充是另一个重点。",
        "traps": [
            "**启动命令的执行机器别搞错**：hdfs 在 master、yarn 在 slave2",
            "ZK 环境变量题目指定写 /root/.bash_profile，不是 /etc/profile",
            "「删 age ≥ 100」保留的是 < 100，方向别反",
            "环形图 = pie + radius 数组，只写一个值是普通饼图",
            "Excel 柱状图要求降序",
        ],
        "time": "模块一 60 分钟（Hadoop + ZK 集群）｜模块二 60 分钟｜模块三 55 分钟｜留 15 分钟",
        "check": [
            "三节点进程与题目要求的位置一致",
            "ZK 三节点 Mode 正常",
            "三项清洗 + 定向填充都完成",
            "Web 环形图是空心环不是实心饼",
        ],
    },
},

# ============================== 第 09 套 ==============================
9: {
    "steps": [
        {"p": "模块一", "t": "JDK 环境变量（node01）", "d": "配 JAVA_HOME 与 PATH，**java -version 与 javac 都要验证**"},
        {"p": "模块一", "t": "Hadoop 完全分布式（三节点全 datanode）", "d": "解压到 /root/software 分发 node02/node03，三节点均为 datanode，初始化 NameNode 后启动"},
        {"p": "模块一", "t": "Hive 3.1.2 装在 node03", "d": "复制安装包与 mysql-connector-java-5.1.37.jar 到 node03，配环境变量，以 MySQL 作元数据库初始化"},
        {"p": "模块一", "t": "Flume 1.11.0 + Sqoop 1.4.7", "d": "两个采集工具都装，都要验证版本与连通性"},
        {"p": "模块二", "t": "数据采集与行业分类标注", "d": "采集文本数据，对文本做行业分类标注"},
        {"p": "模块二", "t": "分区查看日志并下载", "d": "进入分区查看日志文件并下载至 /root/eduhq"},
        {"p": "模块二", "t": "统计电压等级对应线路", "d": "统计各个电压等级对应的线路名称"},
        {"p": "模块三", "t": "无人机巡检占比分析", "d": "按 power.txt 计算各型号无人机巡检杆塔总数占比，结果写 HDFS /root/power_opt2/"},
        {"p": "模块三", "t": "出三张图", "d": "无人机与巡检员工作量词云图、月度无人机巡检柱状图、月度巡检人员柱状图"},
        {"p": "模块三", "t": "业务分析 + Excel 透视", "d": "当月巡检人员实际完成巡检数量 → /root/power_opt3/；Excel 对电力信息表 label 区域做透视"},
    ],
    "cmds": [
        {"t": "模块一 · JDK 与 Hive 远端安装（node03）", "lang": "bash", "code":
"# node01 配 JDK\n"
"export JAVA_HOME=/root/software/jdk1.8.0_412\n"
"export PATH=$PATH:$JAVA_HOME/bin\n"
"java -version && javac -version        # 两个都要验（截图点）\n\n"
"# Hive 装到 node03\n"
"scp -r /root/software/apache-hive-3.1.2-bin node03:/root/software/\n"
"scp mysql-connector-java-5.1.37.jar node03:/root/software/apache-hive-3.1.2-bin/lib/\n\n"
"# node03 上初始化元数据库\n"
"schematool -dbType mysql -initSchema\n"
"hive -e \"SELECT 1;\"                    # 验证（截图点）"},
        {"t": "模块一 · Sqoop 验证", "lang": "bash", "code":
"sqoop version\n\n"
"# 连通性验证（截图点）\n"
"sqoop list-databases --connect jdbc:mysql://node03:3306/ \\\n"
"  --username root --password ******\n\n"
"# 导入示例\n"
"sqoop import --connect jdbc:mysql://node03:3306/power \\\n"
"  --username root --password ****** \\\n"
"  --table line_info --target-dir /root/power_opt1 -m 1\n"
"# ⚠ --target-dir 已存在会报错，先 hdfs dfs -rm -r 删掉"},
        {"t": "模块三 · 占比计算与词云", "lang": "python", "code":
"import pandas as pd\n"
"from pyecharts.charts import WordCloud, Bar\n"
"from pyecharts import options as opts\n\n"
"df = pd.read_csv('/root/power.txt', sep='\\t')\n"
"g = df.groupby('drone_model')['tower_cnt'].sum()\n"
"ratio = (g / g.sum() * 100).round(2)\n"
"ratio.to_csv('/root/power_opt2/ratio.csv')     # 结果写指定目录\n\n"
"wc = (WordCloud()\n"
"      .add('', [list(z) for z in zip(ratio.index, ratio.values)],\n"
"           word_size_range=[20, 100])\n"
"      .set_global_opts(title_opts=opts.TitleOpts(title='无人机工作量词云')))\n"
"wc.render('/root/eduhq/html/drone_wc.html')"},
    ],
    "shots": [
        "java -version 与 javac -version（两个都要）",
        "三节点 jps（都是 datanode）",
        "node03 上 schematool 初始化 + hive -e \"SELECT 1;\"",
        "Flume 版本 + Sqoop list-databases 结果",
        "HDFS /root/power_opt2/ 与 power_opt3/ 目录内容",
        "三张图（词云 + 两个柱状图）+ Excel 透视表",
    ],
    "summary": {
        "focus": "组件最多的一套（JDK + Hadoop + Hive + Flume + Sqoop，共 5 个），且 Hive 装在 node03 而非主节点。**组件安装要快，别恋战**。",
        "traps": [
            "Hive 装在 node03，命令要在对应机器上敲",
            "mysql-connector 必须放进 Hive 的 lib 目录",
            "Sqoop 的 --target-dir 已存在会报错，先删",
            "三节点都是 datanode，workers 文件要写全",
            "javac 也要验证，只验 java 会漏分",
        ],
        "time": "模块一 80 分钟（5 个组件）｜模块二 50 分钟｜模块三 50 分钟｜留 10 分钟",
        "check": [
            "JDK 两个命令都验了",
            "Hive 在 node03 能查",
            "Sqoop 能连 MySQL",
            "power_opt2 / power_opt3 目录都有结果",
        ],
    },
},

# ============================== 第 10 套 ==============================
10: {
    "steps": [
        {"p": "模块一", "t": "Hadoop 集群启停", "d": "启动 hdfs 与 yarn，jps 查 Master/slave1 进程"},
        {"p": "模块一", "t": "Hive 3.1.2 初始化", "d": "解压安装包与 MySQL 驱动，配环境变量，用 schematool 初始化元数据（**截图取最后 10 行**）"},
        {"p": "模块一", "t": "Flume 1.9.0（传 Hadoop 日志到 /tmp/flume）", "d": "写 conf 起 agent，验证 HDFS 落地"},
        {"p": "模块二", "t": "Scrapy 爬酒店详情", "d": "Chrome 看源码分析结构 → 建项目 → 构建请求 → 定义字段 → 爬取 25 个字段存入 hotel.csv"},
        {"p": "模块二", "t": "HDFS result 往返", "d": "/root 建 result → 上传至根目录 → 查看 → 下载回 /root"},
        {"p": "模块二", "t": "pandas 四项清洗", "d": "同第 03 套：删商圈为空、删缺失 >3 的列、评分空置 0、评分空置总平均（保留一位小数）"},
        {"p": "模块二", "t": "SQL 建评论表", "d": "建评论表（id、name、commentator、score、comment_time、content）"},
        {"p": "模块三", "t": "Python 分析三项", "d": "各商圈酒店总数倒序前五、平均评分排名倒序前五、平均房间数正序前五"},
        {"p": "模块三", "t": "Python 出两图", "d": "各商圈酒店总数柱状图、各星级平均评分折线图"},
        {"p": "模块三", "t": "情感分析 + 趋势", "d": "基于 standard.csv 按月统计正向/中性/负向评价数量并画折线图，附发展趋势分析文字"},
        {"p": "模块三", "t": "Excel 报表两图", "d": "正/负/中性趋势柱状图（按数量倒序）、整体评价趋势数量饼图"},
    ],
    "cmds": [
        {"t": "模块二 · Scrapy 爬取 25 字段", "lang": "bash", "code":
"scrapy startproject hotel_spider\n"
"cd hotel_spider\n"
"scrapy genspider hotel www.example.com\n\n"
"# items.py 里定义 25 个字段\n"
"# name / address / star / score / price / rooms / ... 共 25 个\n\n"
"# 反爬：随机 UA\n"
"# settings.py 加 USER_AGENT 或装 fake_useragent\n\n"
"scrapy crawl hotel -o hotel.csv\n"
"# ⚠ 题目要求 25 个字段，字段数不够直接扣分\n"
"# ⚠ 输出用 -o hotel.csv，编码加 FEED_EXPORT_ENCODING = 'utf-8'"},
        {"t": "模块二 · 评论表与情感统计", "lang": "sql", "code":
"CREATE TABLE comment_all (\n"
"  id INT PRIMARY KEY AUTO_INCREMENT,\n"
"  name VARCHAR(100),\n"
"  commentator VARCHAR(50),\n"
"  score DECIMAL(3,1),\n"
"  comment_time DATETIME,\n"
"  content TEXT\n"
") DEFAULT CHARSET=utf8mb4;         -- ⚠ 评论含中文，必须 utf8mb4\n\n"
"-- 按月统计情感倾向\n"
"SELECT DATE_FORMAT(comment_time, '%Y-%m') AS ym,\n"
"       SUM(CASE WHEN sentiment='正向' THEN 1 ELSE 0 END) AS pos,\n"
"       SUM(CASE WHEN sentiment='中性' THEN 1 ELSE 0 END) AS neu,\n"
"       SUM(CASE WHEN sentiment='负向' THEN 1 ELSE 0 END) AS neg\n"
"FROM comment_all GROUP BY ym ORDER BY ym;"},
        {"t": "模块三 · 情感趋势折线图", "lang": "python", "code":
"import pandas as pd, matplotlib.pyplot as plt\n"
"df = pd.read_csv('/root/standard.csv')\n"
"df['ym'] = pd.to_datetime(df['comment_time']).dt.strftime('%Y-%m')\n\n"
"pivot = df.pivot_table(index='ym', columns='sentiment',\n"
"                       values='id', aggfunc='count').fillna(0)\n\n"
"plt.rcParams['font.sans-serif'] = ['SimHei']\n"
"plt.rcParams['axes.unicode_minus'] = False\n"
"pivot.plot(kind='line', figsize=(14, 6), marker='o')\n"
"plt.title('评价情感月度趋势')\n"
"plt.savefig('/root/eduhq/html/sentiment_trend.png', dpi=150)\n"
"plt.show()\n\n"
"# 附发展趋势分析：把上升 / 下降 / 拐点写进结论\n"
"print(pivot.tail(6))"},
    ],
    "shots": [
        "jps（Master 与 slave1）",
        "schematool 输出最后 10 行",
        "Flume 落地文件",
        "hotel.csv 的 25 个字段表头",
        "评论表结构与按月统计结果",
        "三张 Python 图 + Excel 两张报表图",
    ],
    "summary": {
        "focus": "唯一带**爬虫**的一套（Scrapy 25 字段），加上情感分析与 Excel 报表。Scrapy 是最大变量，卡住要果断改用 requests 兜底。",
        "traps": [
            "25 个字段一个不能少，items.py 要写全",
            "CSV 导出编码要设 FEED_EXPORT_ENCODING = utf-8",
            "评论表必须 utf8mb4，否则中文变问号",
            "情感按月统计要用 DATE_FORMAT 分组",
            "Excel 柱状图要求按数量倒序",
        ],
        "time": "模块一 55 分钟｜模块二 65 分钟（爬虫占大头）｜模块三 60 分钟｜留 10 分钟",
        "check": [
            "hotel.csv 字段数是 25",
            "评论表能查到中文评论",
            "三张 Python 图 + 两张 Excel 图都在",
            "趋势结论文字写进答案",
        ],
    },
},
}
