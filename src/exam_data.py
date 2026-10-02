# -*- coding: utf-8 -*-
"""赛项资料数据（来源：资料库「大数据」文件夹：赛项规程、ZZ052 十套赛题、备赛总览、实训范例）"""

# 八大考核任务模块（规程）
MODULES8 = [
    {"name": "大数据平台搭建", "icon": "🏗️", "desc": "Hadoop 完全分布式、组件安装与环境变量、集群启停与进程核对"},
    {"name": "数据采集", "icon": "📥", "desc": "Flume 日志采集、Scrapy/Requests 爬取、Sqoop 导入导出、HDFS 上传下载"},
    {"name": "数据库运行维护", "icon": "🗄️", "desc": "MySQL 安装部署、建库建表、增删改查、导入导出、容灾备份恢复（2026 版扩到 6 个子任务）"},
    {"name": "数据清洗", "icon": "🧹", "desc": "pandas 条件筛选与删除、缺失值处理、异常值处理、Excel 分列与去重"},
    {"name": "数据标注", "icon": "🏷️", "desc": "MapReduce 空值打标、字段长度归一、时间格式统一、行业/情感分类标注"},
    {"name": "数据分析与可视化", "icon": "📊", "desc": "Hive 数仓统计、ECharts / Pyecharts / Matplotlib / Seaborn / Excel 出图"},
    {"name": "业务分析和方案设计", "icon": "💡", "desc": "业务指标解读、趋势分析、机器学习预测（2026 版明确要求 scikit-learn）"},
    {"name": "职业素养", "icon": "🎯", "desc": "单独占 5%：操作规范、文件命名与目录结构、提交物完整"},
]

# 2025 / 2026 两届规程差异
RULE_DIFF = {
    "head": ["维度", "JSZ2025052（2025）", "中职组 JSZ2026018-5（2026）"],
    "rows": [
        ["学生组权重", "理论 10% + 操作 70% + 展示 20%", "同左，不变"],
        ["教师组权重", "同学生组（含展示讲解 20%）", "理论 10% + 操作 90%，取消展示讲解"],
        ["操作技能时长", "2 小时 45 分钟", "3 小时"],
        ["展示讲解时长", "15 分钟", "20 分钟"],
        ["平台搭建子任务", "Hadoop 完全分布式 + Flume + Flink on Yarn", "Hadoop 完全分布式 + Hive + Flink on Yarn"],
        ["数据库运行维护", "4 个子任务", "6 个子任务（新增安装部署、数据导入导出）"],
        ["可视化工具", "Echarts、matplotlib、pyecharts", "新增 Power BI（学生组任务三）"],
        ["业务分析", "运用机器学习模型预测", "明确要求 scikit-learn，并评估算法效果"],
    ],
}

# 展示讲解评分维度
SHOW_SCORE = [
    ["技能水平", 60], ["职业素养", 10], ["应用价值", 10], ["团队合作", 10], ["创新创意", 10],
]

# 资料四层
SOURCES4 = [
    ["规则层", "2025 赛项规程、2026 项目规程、ZZ202452", "定考纲、定分值、定评分与申诉规则"],
    ["题型层", "ZZ052 赛题 01~10 套、2025 中职样题、样题及答案、理论题库", "定题面形式与提交规范"],
    ["实现层", "Hadoop 集群搭建与管理、zookeeper、数据爬取、大数据应用、预测分析", "可运行范例，对应各任务模块"],
    ["延伸层", "HCIP-Big Data Developer V2、大数据技能展示", "认证能力与展示讲解"],
]

# 备赛策略（规程 vs 赛题落差）
STRATEGY = [
    {"t": "规程是上限，ZZ052 是下限", "d": "规程拆 8 个模块，ZZ052 只压成 3 个，颗粒度更粗。用规程定广度（补齐机器学习与 BI 工具），用 ZZ052 练速度与熟练度。"},
    {"t": "机器学习几乎不出现在 ZZ052", "d": "预测只在 2025 中职样题（设备故障预测）与「预测分析」范例中出现，但 2026 规程明确要求 scikit-learn——这块必须自己补。"},
    {"t": "Power BI 只在纸面上", "d": "2026 新增的 Power BI 在 ZZ052 中完全未出现，实际以 Excel + ECharts + Python 替代。"},
    {"t": "两个时间变化要提前适应", "d": "教师组取消展示讲解；学生组操作时长增加 15 分钟（2h45m → 3h）。"},
]

# 资料使用建议（四步走）
ADVICE = [
    {"n": 1, "t": "先读两份规程", "d": "把八大任务模块与分值分布抄成一张对照表，贴在实训室墙上。"},
    {"n": 2, "t": "90 分钟限时热身", "d": "用第 09 套（纯组件安装）和第 05 套（HDFS + 轻量清洗）暴露环境搭建速度瓶颈。"},
    {"n": 3, "t": "按模块专项突破", "d": "模块一练版本与配置文件套路；模块二练 pandas 四类高频操作；模块三把三类出图模板各写一遍。"},
    {"n": 4, "t": "全流程模拟", "d": "用 2025 中职样题做模拟，重点补第 7 题（预测分析）——赛题覆盖最薄、规程要求最明确。"},
]

# ZZ052 十套赛题：每套 = 一个实战关卡
LEVELS = [
    {
        "no": 1, "scene": "用户行为日志 / 数仓", "comps": ["Hadoop", "MySQL", "Hive", "Flume"],
        "charts": "Pyecharts（七图）",
        "tasks": [
            "Hadoop 完全分布式：建 hadoopDatas 系列子目录（tempDatas、namenodeDatas、datanodeDatas、dfs/nn/edits、dfs/snn/name），scp 分发 slave1/slave2，三节点配 HADOOP_HOME 与 PATH，主节点格式化后启动 HDFS、YARN、历史服务",
            "MySQL 5.7.25：解压到 /root/software，rpm -ivh 依次装 common / libs / libs-compat / client / server，初始化启动，root 改密 123456，改 user 表 host 为 % 允许远程登录",
            "HDFS Shell：级联创建 /behavior/origin_log，上传本地日志，用 9870 Web UI 验证",
            "Excel 清洗：behavior2023-01-01.csv 的 time 列分列成日期 + 时间两列",
            "数仓：comm 库建 dim_date、dim_area 外部表（HDFS 路径 /behavior/dim/，\\t 分隔），先删后建，load data 导入，查前 3 行与总行数",
            "统计导出：省份访问量、时间段浏览量、设备类型、上网模式 → 导出 /root/eduhq/result/ads_*，逗号分隔",
            "出图七张：中国地图（省份访问量）、带时间轴柱形图、浏览量折线图、节假日与工作日对比折线图、设备类型堆积柱形图、上网模式堆积柱形图、域名访问词云图",
            "脚本统一放 /root/eduhq/python/，HTML 输出到 /root/eduhq/html/，并嵌入指定背景图",
        ],
    },
    {
        "no": 2, "scene": "设备故障工单整理", "comps": ["Hadoop", "Hive"],
        "charts": "离线数仓 + 看板图",
        "tasks": [
            "Hadoop 完全分布式安装配置；Hive 安装配置",
            "MySQL 维护：改 root_sl_src 库 province 表 province_id=24 的名为「内蒙古自治区」；删 city 表 city_id=142",
            "load 导入 12 张 CSV 到 Hive 库 equipment_dashboard；自建 ods_province、ods_city 表结构",
            "put 上传 sms_so_failure_logs_shell.txt 到 /source/logs/sms_so_failure_logs/，province_iso_shell.txt 到 /source/logs/province_iso/",
            "文本清洗：删工单表与设备表首行标题、删前两列脏数据，另存 *_shell.txt",
            "数据标注（MapReduce）：空字段统一打「未获取」，统一时间格式，保证每行字段长度一致，存 HDFS /source/mr/sms_so_failure_logs/",
            "数仓：建 ods_sms_so_failure_log、ods_province_iso，统计设备数量与用户数量",
            "分析：故障类型分布（正序前五）、交付状态（正序前五）、设备状态分布",
            "出图：设备类型 TOP5 饼图、设备状态饼图、交付状态条形图、设备数量数字卡片",
        ],
    },
    {
        "no": 3, "scene": "酒店数据 + 项目预算", "comps": ["ZooKeeper", "Kafka", "Hive"],
        "charts": "Python + Excel 透视表",
        "tasks": [
            "ZooKeeper 集群安装配置；Kafka 安装配置（apache-zookeeper-3.5.7-bin.tar.gz、kafka_2.12-2.4.1.tgz 解压至 /opt/module）",
            "Hive 元数据初始化：schematool 执行，截图取命令结束最后 10 行",
            "pandas 读取 hotel.csv（25 字段酒店详情）并打印",
            "pandas 清洗 4 项：删商圈为空的行；删缺失值 > 3 的列；评分空置 0；评分空置总平均（保留一位小数）",
            "Excel 数据清洗",
            "Python 分析：各商圈酒店总数（倒序前五）、各商圈平均房间数（正序前五）、五星级酒店平均评分",
            "Python 出图：各商圈酒店总数柱状图、各星级酒店平均评分折线图",
            "Excel 透视表：一级/二级分类为行、楼层为列、合计（万元）为统计量，降序；透视图用柱状图，去掉纵轴与网格线",
        ],
    },
    {
        "no": 4, "scene": "购物平台数据", "comps": ["Hadoop", "Flume", "Flink"],
        "charts": "Matplotlib",
        "tasks": [
            "Hadoop 完全分布式安装配置",
            "Flume 1.9.0：解压、配环境变量、flume-ng version 验证、传输 Hadoop 日志并查看 HDFS /tmp/flume（至少 5 条）",
            "Flink 1.14.0 on Yarn：per-job 模式跑 WordCount.jar（flink run -m yarn-cluster -p 2 -yjm 2G -ytm 2G）",
            "pandas 读取 shopping.csv（商品 ID、名称、价格、浏览量、销量、库存）并打印",
            "pandas 清洗 4 项：删库存 <10 或 >10000；删含「刷单」「捡漏」；删含「女装」；手机价格区间取平均",
            "MapReduce：按 user_impression 统计买家印象数并降序，格式 (印象, 次数)，存 HDFS 并读前 10 条",
            "分析：商品名分割（首元素品牌、其余特征），统计品牌前十、特征前六、品牌销量前五",
            "Matplotlib 出图：不同价格区间手机销量柱状图、不同地区手机品牌占比饼图",
        ],
    },
    {
        "no": 5, "scene": "天气数据（轻量清洗）", "comps": ["Hadoop"],
        "charts": "Echarts + Excel + Seaborn",
        "tasks": [
            "Hadoop 完全分布式安装配置",
            "读 distribution.csv，统计每列缺失值个数输出到 result_1.csv（字段 Column、Null_count）",
            "HDFS：根目录建 student，上传 /root/clean-month.csv，查看后 5 条，用「人性化显示」看占用空间",
            "Echarts：统计 chengdu.js 中 11 种天气类型出现次数，转 Echarts 数据格式并画饼图",
            "Excel：E_weather.csv 建成数据表并修整字段类型，过滤重复日期、按日期升序，画 4 城市 2011—2020 四季度平均低温簇状柱形图（图例置底、数据标签两位小数、低于 0℃ 显红）",
            "Seaborn：clean-month.csv 画平均高温与低温面积图（主题 darkgrid、字体 SimSun、缩放 2；高温 #CC3300 α0.4、低温 #339999 α0.7；边缘线宽 2 加圆点标记）",
        ],
    },
    {
        "no": 6, "scene": "灾害数据 + Spark", "comps": ["Hadoop", "Kafka", "Spark"],
        "charts": "Echarts + Excel + Seaborn",
        "tasks": [
            "Hadoop 完全分布式安装配置",
            "Kafka 集群：配环境变量文件并连同解压包拷到 slave1/slave2，启动后 jps 查三节点进程",
            "Spark standalone 安装配置",
            "按 distribution.csv 统计单条数据缺失字段计数最大值，按指定格式输出到控制台",
            "HDFS：列目录、建 bigdata 目录、上传 /opt/eurasia_mainland.csv、下载到 /root、查看内容",
            "MapReduce 处理异常值：清除年份/国家/区域为空的数据，存 HDFS /clean_data 并看大小",
            "MapReduce 统计：每个国家不同年份中气候灾害受损经济最高的国家，输出前 10",
            "Echarts：成都 2021 年每月平均最高/最低气温柱状图",
            "Excel：北京 2018—2021 年 12 个月空气质量最佳与最差带数据标记折线图（标题「空气质量波动」加粗居中、图例置底、涨跌柱线改浅绿）",
            "Seaborn：2011—2021 各城市最高温前 10 柱状图（whitegrid、SimSun、缩放 3、hls 调色板、标签带 ℃、纵轴 0~55）",
        ],
    },
    {
        "no": 7, "scene": "招聘 / 电商 / 银行", "comps": ["Hadoop", "Flume", "Flink"],
        "charts": "Excel + Web 项目 + Python",
        "tasks": [
            "Hadoop 完全分布式安装配置",
            "Flume 1.9.0 安装配置（传日志到 HDFS /tmp/flume）",
            "Flink on Yarn 安装配置（per-job 跑 WordCount）",
            "MySQL 建 test 库与 stu、course、score 三表（学号主键 / 课程号主键 / 学号+课程号联合主键）",
            "SQL 查询：电子学院学生、选修 KCJG01 与 KCDZ02 的学生、姓名末尾带「华」、班级筛选、学分=2、成绩 75~80",
            "HDFS：/root 建 result 上传至根目录、查看、再下载回 /root",
            "MapReduce：清 sku_info.csv 字段长度 <11 的记录（输出 HDFS 并打印前 20）；按 gender 统计 user_info.csv 男女数量",
            "Excel：岗位数量前十城市柱状图、各学历岗位占比饼图（ANALYSE.xlsx）",
            "Web 项目 jobSite：补 js/chat.js 的 getHotskill()（热门技术柱状图，yAxis 类目轴）与 getSalaryData()（学历饼图，legend 垂直居右、半径 ['20%','55%']、圆角 4）",
            "Python：分析不同职业客户购买银行产品意向并画条形图；age / duration / campaign 三特征直方图与概率密度图",
        ],
    },
    {
        "no": 8, "scene": "电商用户 / 景区旅游", "comps": ["Hadoop", "ZooKeeper"],
        "charts": "Excel + Web 项目",
        "tasks": [
            "Hadoop 集群：master 启 hdfs、slave2 启 yarn，jps 查 master/slave1/slave2 三节点",
            "ZooKeeper 3.5.7 集群：master 解压改名，改 /root/.bash_profile 配环境变量，拷配置与包到 slave1/slave2，myid 分别改 2、3，三节点启动并查状态",
            "pandas 读取 data.csv（电商用户行为，14 字段）并打印",
            "清洗 3 项：NAN 替换为 0；正则把 page 文字信息转数字 1；删 age ≥ 100 异常数据",
            "缺失值处理：source 列新用户填 direct、老用户填 seo；device 列 mac/window/linux 填 desktop、iOS/android 填 mobile、other 与 NAN 填众数",
            "MySQL 建 test 库及三表，完成建表、添加记录、查询",
            "Excel：各景点评论人数前十柱状图（降序）、各地出游人数百分比圆环图",
            "Web 项目 traveSite：补 js/index.js 的 getGradeData()（好评度环形图）与 getHotScenery()（热门景点柱状图，yAxis 类目轴 + series）",
        ],
    },
    {
        "no": 9, "scene": "电力无人机巡检", "comps": ["JDK", "Hadoop", "Hive", "Flume", "Sqoop"],
        "charts": "词云 + 柱状图 + Excel",
        "tasks": [
            "node01 配 JDK 环境变量，java -version 与 javac 验证",
            "Hadoop 完全分布式：解压到 /root/software 分发 node02/node03，三节点均为 datanode，初始化 NameNode 后启动并查进程",
            "Hive 3.1.2：复制安装包与 mysql-connector-java-5.1.37.jar 到 node03，配环境变量，以 MySQL 作元数据库并初始化",
            "Flume 1.11.0 安装配置；Sqoop 1.4.7 安装配置",
            "数据采集；对文本做行业分类标注",
            "进入分区查看日志文件并下载至 /root/eduhq",
            "统计各个电压等级对应的线路名称",
            "分析：按 power.txt 计算各型号无人机巡检杆塔总数占比，结果写 HDFS /root/power_opt2/",
            "出图：无人机与巡检员工作量词云图、月度无人机巡检柱状图、月度巡检人员柱状图",
            "业务分析：当月巡检人员实际完成巡检数量 → /root/power_opt3/；Excel 对电力信息表 label 区域做透视",
        ],
    },
    {
        "no": 10, "scene": "酒店数据 / 评论情感", "comps": ["Hadoop", "Hive", "Flume"],
        "charts": "Python + Excel",
        "tasks": [
            "Hadoop 集群：启动 hdfs 与 yarn，jps 查 Master/slave1 进程",
            "Hive 3.1.2：解压安装包与 MySQL 驱动，配环境变量，用 schematool 初始化元数据（截图取最后 10 行）",
            "Flume 1.9.0 安装配置（传 Hadoop 日志到 HDFS /tmp/flume）",
            "Scrapy 爬取酒店详情列表：Chrome 看源码分析结构，建项目、构建请求、定义字段，爬取 25 个字段存入 hotel.csv",
            "HDFS：/root 建 result 上传至根目录、查看、再下载回 /root",
            "pandas 清洗 hotel.csv 4 项（同第 03 套）",
            "SQL 建评论表（id、name、commentator、score、comment_time、content）",
            "Python 分析：各商圈酒店总数倒序前五、平均评分排名倒序前五、平均房间数正序前五",
            "Python 出图：各商圈酒店总数柱状图、各星级平均评分折线图",
            "情感分析：基于 standard.csv 按月统计正向/中性/负向评价数量并画折线图，附发展趋势分析",
            "Excel 报表：正/负/中性趋势柱状图（按数量倒序）、整体评价趋势数量饼图",
        ],
    },
]

# 模块化训练建议（跨套共性）
TRAINING = [
    {"skill": "pandas 条件筛选与删除", "sets": "第 03、04、08、10 套"},
    {"skill": "HDFS 目录创建 / 上传 / 下载 / 查看", "sets": "第 01、05、06、07、10 套"},
    {"skill": "文本清洗与删除标题行", "sets": "第 02、05 套"},
    {"skill": "MapReduce 空值处理与条件统计", "sets": "第 02、04、06、07 套"},
    {"skill": "MySQL 建库建表 + 增删改查", "sets": "第 07、08 套"},
    {"skill": "ECharts 补全题：取 DOM → echarts.init → 补 legend/yAxis/series → setOption", "sets": "第 05、06 套"},
    {"skill": "Pyecharts 脚本：Bar / Pie / Line / Map / WordCloud + set_global_opts + render", "sets": "第 01 套"},
    {"skill": "Matplotlib / Seaborn：主题与字体、颜色与透明度、数据标签与单位、坐标轴范围", "sets": "第 04、05、06 套"},
    {"skill": "Excel：透视表字段、带数据标记折线图、涨跌柱线、圆环图与簇状柱形图", "sets": "第 03、05、06、09 套"},
]

# 实训范例（资料库 03-实训与教学素材）
DEMOS = [
    {
        "name": "数据爬取", "icon": "🕷️", "tools": "Scrapy / Requests + BeautifulSoup / Selenium",
        "steps": [
            "选路线：复杂项目用 Scrapy（异步 + 中间件 + Pipeline），简单静态页用 Requests + BeautifulSoup",
            "定位数据：Chrome DevTools 看 HTML 结构，确定 XPath 或 CSS 选择器",
            "动态页面：Ajax 接口分析或 Selenium 渲染（driver.page_source）",
            "Scrapy 流程：startproject → genspider → 写 parse → Pipeline 清洗 → FEED_FORMAT 存 CSV → crawl 运行",
            "反爬绕过：fake_useragent 随机 UA、代理池、time.sleep 限速",
        ],
        "code": "scrapy startproject movie_crawler\ncd movie_crawler\nscrapy genspider douban_movie movie.douban.com\nscrapy crawl douban_movie",
    },
    {
        "name": "预测分析", "icon": "🔮", "tools": "scikit-learn（2026 规程明确要求）",
        "steps": [
            "准备特征与标签：pd.read_csv 后切 X / y",
            "划分数据集：train_test_split(test_size=0.2, random_state=42)",
            "预处理：get_dummies 编码类别列 + StandardScaler 标准化（注意补齐 train/test 列差）",
            "训练：GradientBoostingRegressor().fit(X_train, y_train)",
            "评估：model.score(X_test, y_test) 输出 R²，按规程要求做算法效果评估",
        ],
        "code": "from sklearn.ensemble import GradientBoostingRegressor\nmodel = GradientBoostingRegressor()\nmodel.fit(X_train, y_train)\nprint('R2 Score:', model.score(X_test, y_test))",
    },
    {
        "name": "大数据应用（完整实操链）", "icon": "🧩", "tools": "JDK → Hadoop 完全分布式 → MySQL → pandas",
        "steps": [
            "基础环境：host 配置、JDK 解压到 /opt/module、/etc/profile 配 JAVA_HOME、建 hadoop 用户、关防火墙、三节点 SSH 免密",
            "Hadoop 完全分布式：解压重命名、改所属者、配 6 个配置文件（hadoop-env.sh / core-site.xml / hdfs-site.xml / mapred-site.xml / yarn-site.xml / workers）、scp 分发、格式化、启动 HDFS+YARN+历史服务、jps 核对",
            "MySQL 运维：rpm 装 5 个包、初始化启动、改 root 密码、授权远程（host=%）、建库 education、建 course 与 learning_record 表、建 eduadmin 用户并授权",
            "数据处理：pandas 读 learning_data.csv 打印前 10 行；清洗五项（删空/0 时长、删异常成绩、时间标准化、进度封顶 100%、去重）",
            "数据标注：按学习时长与互动次数做投入度分类标注",
        ],
        "code": "# 清洗要点（五步）\ndf = df[df['duration'].notna() & (df['duration'] > 0)]\ndf = df[(df['score'] >= 0) & (df['score'] <= 100)]\ndf['last_time'] = pd.to_datetime(df['last_time'], errors='coerce')\ndf.loc[df['progress'] > 100, 'progress'] = 100\ndf = df.drop_duplicates()",
    },
]
