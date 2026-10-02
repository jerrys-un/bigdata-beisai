# -*- coding: utf-8 -*-
"""基础概念库：给零基础学生的「大白话解释 + 图解动画」

文字素材来源：GitHub 仓库 jerrys-un/BigDataGuide
（Docs/大数据简介.md、Hadoop/NN、2NN、DN工作机制.md、Hadoop/MapReduce.md、Hadoop/YARN.md 等）
动画为站点自建的 SVG 步骤动画（离线可用，不依赖任何视频文件）。
"""

CONCEPTS = [
    {
        "id": "c1", "name": "大数据概论", "icon": "🌍",
        "desc": "先搞清楚「大数据」到底指什么、有什么特点、用在哪儿",
        "cards": [
            {
                "t": "什么是大数据",
                "plain": "大到普通软件工具处理不了的数据集合，需要新的处理方式才能挖掘出价值。",
                "points": [
                    "关键不在「大」，而在「常规工具处理不了」——所以它是一个相对概念，不是单纯的容量门槛",
                    "考试常考判断题：「大数据是指存储量超过 100TB 的数据集」→ **错**，那是把特征当成了门槛",
                    "配套的是新处理模式：分布式存储 + 分布式计算",
                ],
                "src": "BigDataGuide · Docs/大数据简介.md",
            },
            {
                "t": "4V 特征（必背）",
                "plain": "Volume 大量、Velocity 高速、Variety 多样、Value 低价值密度。",
                "points": [
                    "**Volume 大量**：个人电脑硬盘 TB 量级，大企业数据量接近 EB 量级",
                    "**Velocity 高速**：这是大数据区别于传统数据挖掘**最显著的特征**——处理效率就是生命",
                    "**Variety 多样**：分结构化（数据库表）与非结构化（日志、音频、视频、图片、位置信息）",
                    "**Value 低价值密度**：价值密度与数据总量**成反比**，一天监控里可能只关心一分钟",
                ],
                "src": "BigDataGuide · Docs/大数据简介.md",
            },
            {
                "t": "数据单位换算",
                "plain": "bit → Byte → KB → MB → GB → TB → PB → EB → ZB → YB，1024 进一级。",
                "points": [
                    "最小单位是 **bit**（位），1 Byte = 8 bit",
                    "1 KB = 1024 B，1 MB = 1024 KB，1 GB = 1024 MB，1 TB = 1024 GB",
                    "再往上：1 PB = 1024 TB，1 EB = 1024 PB，1 ZB = 1024 EB",
                    "常见考点：HDFS 默认块大小 Hadoop 3.x 是 **128MB**（1.x 是 64MB）",
                ],
                "src": "BigDataGuide · Docs/大数据简介.md",
            },
            {
                "t": "大数据用在哪儿",
                "plain": "物流、零售、旅游、广告推荐、房产、保险、金融、人工智能。",
                "points": [
                    "零售经典案例：**纸尿裤 + 啤酒**（分析购买习惯做关联推荐）",
                    "广告推荐：买过一本书，再推荐若干本",
                    "金融：多维度刻画用户特征，推荐优质客户 + 防范欺诈",
                    "这部分常出「下列属于大数据应用场景的是」这类多选题",
                ],
                "src": "BigDataGuide · Docs/大数据简介.md",
            },
        ],
        "anims": [],
    },
    {
        "id": "c2", "name": "HDFS 存储原理", "icon": "🗂️",
        "desc": "块与副本、三个角色怎么配合、文件是怎么写进去的",
        "cards": [
            {
                "t": "三大角色各自干啥",
                "plain": "NameNode 记账、DataNode 存数据、SecondaryNameNode 只负责合并日志。",
                "points": [
                    "**NameNode（NN）**：管理元数据（文件名、目录结构、块位置映射），相当于「账房先生」",
                    "**DataNode（DN）**：真正存放数据块的节点，定时向 NN 报心跳和块信息",
                    "**SecondaryNameNode（2NN）**：**不是** NN 的备用节点！它只做一件事——定期合并 fsimage 与 edits",
                    "⚠️ 全题库最集中的陷阱：NN 挂了 2NN **不会**接替工作；真正的单点解决方案是 HA（双 NN + ZooKeeper 切换）",
                ],
                "src": "BigDataGuide · Hadoop/NN、2NN、DN工作机制.md",
            },
            {
                "t": "DataNode 的心跳与掉线判定",
                "plain": "每 3 秒心跳一次，超过 10 分 30 秒没心跳就判定节点不可用。",
                "points": [
                    "心跳默认 **3 秒**一次，心跳返回里带着 NN 下给 DN 的命令（复制块、删除块等）",
                    "DN 启动后向 NN 注册，**周期性（1 小时）上报所有块信息**",
                    "超时时长公式：timeout = 2 × heartbeat.recheck-interval + 10 × heartbeat.interval",
                    "默认 recheck-interval = 300000（**毫秒**），heartbeat.interval = 3（**秒**）→ 2×5分 + 10×3秒 = **10 分 30 秒**",
                    "⚠️ 单位陷阱：配置文件里前者是毫秒、后者是秒",
                ],
                "src": "BigDataGuide · Hadoop/NN、2NN、DN工作机制.md",
            },
            {
                "t": "数据完整性怎么保证",
                "plain": "写入时算校验和，读取时再算一次，对不上说明块坏了就去别的副本读。",
                "points": [
                    "DN 读取 block 时会计算 **checksum**，与创建时的值比对",
                    "不一致说明 block 已损坏 → 客户端改读其他 DN 上的副本",
                    "DN 在文件创建后会周期性验证 checksum",
                ],
                "src": "BigDataGuide · Hadoop/NN、2NN、DN工作机制.md",
            },
        ],
        "anims": ["hdfs-write", "checkpoint"],
    },
    {
        "id": "c3", "name": "MapReduce 计算", "icon": "🔁",
        "desc": "分而治之：先分片，再 Map、Shuffle、Reduce",
        "cards": [
            {
                "t": "一句话理解 MapReduce",
                "plain": "把大任务拆成小任务分给多台机器（Map），再把结果汇总起来（Reduce）。",
                "points": [
                    "核心理念：**移动计算比移动数据更划算**（计算向数据靠拢）——判断题常考，答案是**对**",
                    "输入先 **分片（Split）**，一个分片交给一个 Map 任务",
                    "Map 输出在内存缓冲区排序 → 溢写磁盘 → 合并（Combine）",
                    "Reduce 端**拉取（Shuffle）**属于自己分区的数据 → 归并排序 → 输出",
                ],
                "src": "BigDataGuide · Hadoop/MapReduce.md",
            },
            {
                "t": "Combiner 不是万能的",
                "plain": "它是「Map 端的本地小 Reduce」，能减少网络传输，但不能随便用。",
                "points": [
                    "作用：在 Map 端先聚合一次，**减少传给 Reduce 的数据量**",
                    "使用前提：聚合操作必须满足**交换律和结合律**（求和、求最大值可以）",
                    "⚠️ **求平均值不能用 Combiner**——这是高频考点",
                ],
                "src": "BigDataGuide · Hadoop/MapReduce.md",
            },
        ],
        "anims": ["mapreduce"],
    },
    {
        "id": "c4", "name": "YARN 资源调度", "icon": "📦",
        "desc": "集群的「管家」：谁干活、干多久、用多少资源",
        "cards": [
            {
                "t": "YARN 的四个角色",
                "plain": "ResourceManager 管总资源，NodeManager 管单机，ApplicationMaster 管单个作业，Container 是资源容器。",
                "points": [
                    "**ResourceManager（RM）**：整个集群资源的总调度（一个集群一个）",
                    "**NodeManager（NM）**：单台机器上的资源管理者，向 RM 汇报",
                    "**ApplicationMaster（AM）**：**每个作业一个**，负责向 RM 申请资源、监控任务",
                    "**Container**：资源的抽象封装（多少内存 + 几个核）",
                ],
                "src": "BigDataGuide · Hadoop/YARN.md",
            },
            {
                "t": "提交一个作业的链路",
                "plain": "客户端 → RM 申请 → 起 AM → AM 申请 Container → NM 启动任务 → 跑完注销。",
                "points": [
                    "先看下面的动画，再记这条链路，比背文字快得多",
                    "Web UI 地址：ResourceManager 默认 **8088**（本机就是这个端口）",
                ],
                "src": "BigDataGuide · Hadoop/YARN.md",
            },
        ],
        "anims": ["yarn"],
    },
    {
        "id": "c5", "name": "Kafka 消息系统", "icon": "📨",
        "desc": "Topic、分区、生产者与消费者组",
        "cards": [
            {
                "t": "三个核心概念",
                "plain": "Topic 是逻辑上的分类，Partition 是物理上的分段，消息在分区里是有序的。",
                "points": [
                    "**Topic**：逻辑概念，消息按 Topic 分类（不是物理存储单位）",
                    "**Partition**：物理概念，一个 Topic 分成多个分区，**每个分区是一个有序队列**",
                    "每个 Partition 对应一个 log 文件，再由多个 **segment** 组成",
                    "⚠️ 常考错项：「partition 是一个没有顺序的队列」→ **错**，分区内是有序的",
                ],
                "src": "题库归纳 · Kafka 模块",
            },
            {
                "t": "生产者、消费者与副本",
                "plain": "生产者往 leader 写，消费者按组消费，靠副本保证不丢。",
                "points": [
                    "生产者发送数据的对象是 **leader**（不是随便一个副本）",
                    "同一个消费者组里，一个分区只能被一个消费者消费（组内分摊）",
                    "节点故障时 Replica 上的分区数据**不会丢**",
                    "⚠️ Kafka 默认是「至少一次」，**不是**精确一次（Exactly Once）——判断题高频错点",
                ],
                "src": "题库归纳 · Kafka 模块",
            },
        ],
        "anims": ["kafka"],
    },
    {
        "id": "c6", "name": "生态名词速查", "icon": "🧭",
        "desc": "一张表认全全家桶，选择题看到名字就知道干什么",
        "cards": [
            {
                "t": "全家桶名词对照",
                "plain": "采集用 Flume/Sqoop，传运用 Kafka，存储用 HDFS/HBase，计算用 MapReduce/Spark/Flink，查询用 Hive，协调用 ZooKeeper。",
                "points": [
                    "**Sqoop**：Hadoop/Hive 与传统数据库（MySQL、Oracle）之间**传数据**的开源工具，双向",
                    "**Flume**：高可用、高可靠的**日志采集、聚合和传输**系统，支持定制发送方与接收方",
                    "**Kafka**：高吞吐的分布式**发布订阅消息系统**，O(1) 磁盘结构做持久化，普通硬件也能每秒百万级消息",
                    "**Spark**：最流行的开源大数据**内存计算**框架，可基于 HDFS 上的数据计算",
                    "**HBase**：分布式、面向**列**的开源数据库，适合非结构化数据存储（依赖 HDFS + ZooKeeper）",
                    "**Hive**：**数据仓库工具**，把结构化数据文件映射成表，用类 SQL 转成 MapReduce 任务执行",
                    "**ZooKeeper**：分布式**协调系统**（配置维护、命名服务、分布式同步、组服务），HBase/Kafka 都依赖它",
                    "**Mahout**：可扩展的**机器学习与数据挖掘库**（推荐挖掘、聚类、分类、频繁项集挖掘）",
                    "**Oozie**：Hadoop 作业的**工作流调度**管理系统（按时间/数据触发）",
                    "**Storm**：分布式**实时计算**（流处理）框架，与 Flink 属同类定位",
                ],
                "src": "BigDataGuide · Docs/大数据简介.md（生态体系章节）",
            },
        ],
        "anims": [],
    },
]

# ---------------- 图解动画（SVG 步骤动画） ----------------
# nodes: id / t(标签) / x / y / k(类型: box|store|db)
# edges: f(起点) / t(终点) / l(连线上文字) / d(方向: r 右 | d 下 | l 左)
# steps: e(要点亮的连线下标数组) / n(要点亮的节点 id 数组) / say(解说)
ANIMS = [
    {
        "key": "hdfs-write", "title": "HDFS 写文件流程",
        "summary": "客户端先问 NameNode 能写哪儿，拿到地址后直接写 DataNode，副本由 DN 之间Pipeline 串联复制。",
        "nodes": [
            {"id": "c", "t": "客户端", "x": 40, "y": 110},
            {"id": "nn", "t": "NameNode\n（记账）", "x": 220, "y": 40},
            {"id": "d1", "t": "DataNode1", "x": 400, "y": 40},
            {"id": "d2", "t": "DataNode2", "x": 400, "y": 120},
            {"id": "d3", "t": "DataNode3", "x": 400, "y": 200},
        ],
        "edges": [
            {"f": "c", "t": "nn", "l": "① 请求上传 /user/a.txt"},
            {"f": "nn", "t": "c", "l": "② 返回可写的 3 个 DN 地址"},
            {"f": "c", "t": "d1", "l": "③ 建立管道，传数据块"},
            {"f": "d1", "t": "d2", "l": "④ 副本复制"},
            {"f": "d2", "t": "d3", "l": "⑤ 副本复制"},
            {"f": "d3", "t": "c", "l": "⑥ 逐级 ack 返回成功"},
        ],
        "steps": [
            {"e": [0], "n": ["c", "nn"], "say": "客户端向 NameNode 请求上传文件，NN 检查目录是否已存在、权限是否允许。"},
            {"e": [1], "n": ["nn"], "say": "NameNode 返回可写的 DataNode 列表（按机架感知与负载挑 3 个）。"},
            {"e": [2], "n": ["d1"], "say": "客户端与第一个 DN 建立传输管道，按块（默认 128MB）逐个发送数据包。"},
            {"e": [3, 4], "n": ["d2", "d3"], "say": "DN 之间形成 Pipeline 串联复制，副本数由 dfs.replication 决定（默认 3）。"},
            {"e": [5], "n": ["c"], "say": "三个副本都写完后，ack 逐级回传给客户端，客户端再通知 NameNode 写入完成。"},
        ],
    },
    {
        "key": "checkpoint", "title": "NameNode 与 2NN 的 Checkpoint",
        "summary": "2NN 定期把 NN 的 edits 日志和 fsimage 镜像拿过来合并，生成新的 fsimage 送回去——它只做合并，不做备份。",
        "nodes": [
            {"id": "nn", "t": "NameNode\nfsimage + edits", "x": 60, "y": 60, "k": "store"},
            {"id": "n2", "t": "SecondaryNameNode\n（只做合并）", "x": 60, "y": 200, "k": "store"},
            {"id": "ed", "t": "edits.inprogress\n（滚动新日志）", "x": 420, "y": 40},
            {"id": "fs", "t": "fsimage.chkpoint\n（合并结果）", "x": 420, "y": 150},
        ],
        "edges": [
            {"f": "n2", "t": "nn", "l": "① 询问是否需要 checkpoint"},
            {"f": "nn", "t": "ed", "l": "② 滚动 edits，生成新的 inprogress"},
            {"f": "nn", "t": "n2", "l": "③ 拷贝 edits + fsimage 到 2NN"},
            {"f": "n2", "t": "fs", "l": "④ 加载到内存合并，生成 fsimage.chkpoint"},
            {"f": "fs", "t": "nn", "l": "⑤ 拷回 NN，重命名为 fsimage"},
        ],
        "steps": [
            {"e": [0], "n": ["n2", "nn"], "say": "2NN 主动询问 NN 是否需要 checkpoint（触发条件：定时时间到 或 edits 写满，满足其一即可）。"},
            {"e": [1], "n": ["ed"], "say": "NN 滚动正在写的 edits，生成空的 edits.inprogress，之后新操作都写进这个文件。"},
            {"e": [2], "n": ["n2"], "say": "把滚动前的 edits 和 fsimage 拷贝到 2NN 本地。"},
            {"e": [3], "n": ["fs"], "say": "2NN 在内存里照着 edits 一步步执行，与 fsimage 合并，生成 fsimage.chkpoint。"},
            {"e": [4], "n": ["nn"], "say": "拷回 NN 并重命名成 fsimage 替换旧的。下次 NN 启动只需加载未合并的 edits + 最新 fsimage，启动更快。"},
            {"e": [], "n": [], "say": "⚠️ 记住：2NN 不会接替挂掉的 NameNode，它不是备份节点，只是「合并工」。真正的高可用靠 HA（双 NN + ZK 切换）。"},
        ],
    },
    {
        "key": "mapreduce", "title": "MapReduce 执行流程",
        "summary": "输入分片 → Map → 缓冲区排序溢写 → Shuffle 拉取 → 归并排序 → Reduce → 输出。",
        "nodes": [
            {"id": "i", "t": "输入文件\n（分片 Split）", "x": 40, "y": 130},
            {"id": "m", "t": "Map 任务\n（并行处理）", "x": 210, "y": 40},
            {"id": "b", "t": "内存缓冲区\n排序 + 溢写", "x": 210, "y": 200},
            {"id": "s", "t": "Shuffle\n（拉取 + 归并）", "x": 400, "y": 200},
            {"id": "r", "t": "Reduce 任务\n（汇总）", "x": 400, "y": 40},
            {"id": "o", "t": "输出结果\npart-r-00000", "x": 570, "y": 130},
        ],
        "edges": [
            {"f": "i", "t": "m", "l": "① 一个分片一个 Map"},
            {"f": "m", "t": "b", "l": "② 写入环形缓冲区"},
            {"f": "b", "t": "s", "l": "③ 分区排序后落盘"},
            {"f": "s", "t": "r", "l": "④ Reduce 拉取自己分区的数据"},
            {"f": "r", "t": "o", "l": "⑤ 结果写到 HDFS"},
        ],
        "steps": [
            {"e": [0], "n": ["i", "m"], "say": "输入文件按 Split 切分（默认一个块一个分片），每个分片启动一个 Map 任务，并行处理。"},
            {"e": [1], "n": ["b"], "say": "Map 输出先进入环形内存缓冲区，区内做分区 + 排序；满了就溢写到磁盘，产生多个溢写文件。"},
            {"e": [2], "n": ["s"], "say": "溢写文件合并成最终 Map 输出文件（可选 Combiner 在此先聚合一次，减少网络传输）。"},
            {"e": [3], "n": ["r"], "say": "Reduce 按分区从各个 Map 节点拉取属于自己的数据，再归并排序——这个阶段叫 Shuffle，最耗时。"},
            {"e": [4], "n": ["o"], "say": "Reduce 处理完写回 HDFS，输出文件名形如 part-r-00000。"},
        ],
    },
    {
        "key": "yarn", "title": "YARN 提交作业流程",
        "summary": "客户端 → ResourceManager → 启动 ApplicationMaster → 申请 Container → NodeManager 跑任务。",
        "nodes": [
            {"id": "c", "t": "Client\n（提交作业）", "x": 40, "y": 40},
            {"id": "rm", "t": "ResourceManager\n（总调度）", "x": 250, "y": 40},
            {"id": "am", "t": "ApplicationMaster\n（每个作业一个）", "x": 250, "y": 190},
            {"id": "nm", "t": "NodeManager\n（单节点资源）", "x": 460, "y": 190},
            {"id": "ct", "t": "Container\n（跑 Map/Reduce）", "x": 460, "y": 40},
        ],
        "edges": [
            {"f": "c", "t": "rm", "l": "① 提交 application"},
            {"f": "rm", "t": "am", "l": "② 分配第一个 Container 启动 AM"},
            {"f": "am", "t": "rm", "l": "③ AM 向 RM 申请资源"},
            {"f": "rm", "t": "nm", "l": "④ RM 分配 Container 给 NM"},
            {"f": "nm", "t": "ct", "l": "⑤ NM 启动任务"},
        ],
        "steps": [
            {"e": [0], "n": ["c", "rm"], "say": "客户端提交作业（jar + 配置 + 切片信息）给 ResourceManager，拿到 application id。"},
            {"e": [1], "n": ["am"], "say": "RM 在某台机器上分配第一个 Container，在里面启动 ApplicationMaster——每个作业独有一个 AM。"},
            {"e": [2], "n": ["am"], "say": "AM 向 RM 注册，并按需要申请运行 Map/Reduce 任务用的资源。"},
            {"e": [3], "n": ["nm"], "say": "RM 以 Container 形式把资源分配给具体的 NodeManager。"},
            {"e": [4], "n": ["ct"], "say": "NM 启动 Container 跑任务，AM 全程监控；跑完 AM 向 RM 注销，释放资源。"},
        ],
    },
    {
        "key": "kafka", "title": "Kafka 生产与消费",
        "summary": "生产者往 Topic 的 leader 分区写，消费者组分摊分区消费，各自记自己的 offset。",
        "nodes": [
            {"id": "p", "t": "Producer\n（生产者）", "x": 40, "y": 120},
            {"id": "t", "t": "Topic\n（逻辑分类）", "x": 230, "y": 120, "k": "store"},
            {"id": "p0", "t": "Partition 0\nleader", "x": 420, "y": 40},
            {"id": "p1", "t": "Partition 1\nleader", "x": 420, "y": 120},
            {"id": "p2", "t": "Partition 2\nleader", "x": 420, "y": 200},
            {"id": "cg", "t": "Consumer Group\n（消费者组）", "x": 610, "y": 120},
        ],
        "edges": [
            {"f": "p", "t": "t", "l": "① 指定 Topic 发送"},
            {"f": "t", "t": "p0", "l": "② 按分区策略落到某个分区"},
            {"f": "t", "t": "p1", "l": ""},
            {"f": "t", "t": "p2", "l": ""},
            {"f": "p0", "t": "cg", "l": "③ 组内消费者各自拉取"},
            {"f": "p1", "t": "cg", "l": ""},
            {"f": "p2", "t": "cg", "l": ""},
        ],
        "steps": [
            {"e": [0], "n": ["p", "t"], "say": "生产者面向 Topic 发送，实际写入的对象是该分区的 leader 副本。"},
            {"e": [1, 2, 3], "n": ["p0", "p1", "p2"], "say": "Topic 是逻辑概念，数据实际分散在多个 Partition（物理），分区内消息有序、offset 递增。"},
            {"e": [4, 5, 6], "n": ["cg"], "say": "同一个消费者组内，一个分区只能被一个消费者消费（组内分摊并行）；不同组互不影响，各自维护 offset。"},
            {"e": [], "n": [], "say": "⚠️ Kafka 默认是「至少一次」投递，不是精确一次（Exactly Once）——判断题常设陷阱。"},
        ],
    },
]
