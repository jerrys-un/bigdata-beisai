# -*- coding: utf-8 -*-
"""零基础四大件：Linux / Python / Java / MySQL

面向**高职一年级、还没接触过这些内容的备赛学生**。
写法统一：先给一句大白话，再给「最常用、赛场上真会敲」的几个点，
最后给一道「看到这个输出说明什么」的判断，帮学生建立手感。
"""

BASICS = [
    {
        "id": "b1", "name": "Linux 基础", "icon": "🐧",
        "desc": "比赛全程在 Linux 里敲命令，先把目录、权限、管道这三件事搞明白",
        "cards": [
            {
                "t": "为什么说「一切皆文件」",
                "plain": "Linux 里目录、硬盘、键盘、网卡，统统当成文件来处理，所以操作方式高度统一。",
                "points": [
                    "没有 C 盘 D 盘的概念：只有一个根目录 `/`，所有东西都挂在它下面",
                    "`/root` 是管理员的家，`/home/用户名` 是普通用户的家，`~` 就代表「当前用户的家」",
                    "赛题里让你把结果放 `/root/eduhq/result/`，那就是从根开始的绝对路径",
                    "⚠️ 最容易错的地方：把绝对路径 `/root/xxx` 写成相对路径 `root/xxx`（少个斜杠，文件就建在你当前目录下了）",
                ],
                "src": "零基础补充 · 赛场环境为 CentOS 7.9",
            },
            {
                "t": "必须记熟的目录操作",
                "plain": "pwd 看在哪、cd 去哪儿、ls 看有什么、mkdir 建目录、rm 删东西。",
                "points": [
                    "`pwd` —— 打印当前所在目录（迷路时第一件事）",
                    "`cd /root/eduhq` —— 切到绝对路径；`cd ..` 回上一级；`cd ~` 回家；`cd -` 回上一次的目录",
                    "`ls -l` 看详情，`ls -lh` 大小带单位（K/M/G），`ls -a` 连隐藏文件一起看",
                    "`mkdir -p /behavior/origin_log` —— **-p 是救命参数**，父目录不存在时一并创建，级联建目录全靠它",
                    "`rm -rf 目录` 强制删目录；⚠️ **`rm -rf /` 是删库跑路，永远不要敲**",
                ],
                "src": "零基础补充 · 每年都有人在 mkdir 上丢分",
            },
            {
                "t": "文件查看：cat / more / tail / head",
                "plain": "小文件用 cat 一次看完，大文件用 more 翻页或 tail 看末尾，查日志基本只用 tail -f。",
                "points": [
                    "`cat a.txt` 全文输出；`cat -n a.txt` 带行号",
                    "`head -20 a.txt` 看开头 20 行；`tail -20 a.txt` 看末尾 20 行",
                    "`tail -f 日志文件` —— **实时跟踪**，服务起不来时盯着日志看报错就靠它，Ctrl+C 退出",
                    "查关键词：`grep 'ERROR' 日志文件`；带行号 `grep -n`；反向排除 `grep -v`",
                    "⚠️ 常考：`cat` 适合小文件，几个 G 的日志用 `cat` 会直接把屏幕刷爆",
                ],
                "src": "零基础补充 · 排错必备",
            },
            {
                "t": "重定向与管道（必考）",
                "plain": "`>` 把结果存成文件，`>>` 追加，`|` 把前一个命令的输出交给后一个命令继续处理。",
                "points": [
                    "`hdfs dfs -ls / > /root/result.txt` —— 结果写进文件（**覆盖**原有内容）",
                    "`>>` 是追加，不清空原文件；比赛里连续导出多份结果要注意别互相覆盖",
                    "`|` 管道：`cat a.txt | grep 'error' | wc -l` —— 数一下有多少行含 error",
                    "`wc -l` 统计行数、`sort` 排序、`uniq -c` 去重计数、`awk '{print $1}'` 取第 1 列",
                    "典型考法：统计文件行数 / 统计某关键词出现次数 —— 就是这几个命令的组合",
                ],
                "src": "零基础补充 · 结果导出与统计",
            },
            {
                "t": "权限与属主：chmod / chown",
                "plain": "Linux 每个文件都有「谁可读、谁可写、谁可执行」三套开关，装软件、启服务卡住时八成是权限问题。",
                "points": [
                    "`ls -l` 第一列形如 `-rwxr-xr-x`：第 1 位是类型（- 文件 / d 目录），后面 9 位分三组 = 属主 / 属组 / 其他人",
                    "r=4 读、w=2 写、x=1 执行；`chmod 755 文件` = 属主 rwx、其他人 rx",
                    "`chmod +x start.sh` 给脚本加执行权限 —— **写完 shell 脚本跑不起来，99% 是忘了这句**",
                    "`chown -R hadoop:hadoop /opt/bigdata` 递归改属主；-R 表示连子目录一起",
                    "以 root 跑 Hadoop 3.x 还必须在 `hadoop-env.sh` 里显式写 6 个 `*_USER=root`",
                ],
                "src": "本机踩坑 · root 运行 Hadoop 的权限坑",
            },
            {
                "t": "进程与端口：装完先确认「活着」",
                "plain": "服务起没起来，用 jps 看 Java 进程、用 ss 看端口有没有在监听。",
                "points": [
                    "`jps` —— Hadoop 全家桶的体检表：NameNode / DataNode / ResourceManager / NodeManager 都在不在，一眼看清",
                    "`ss -lntp | grep 9870` 看端口是否被占用；没有 ss 就用 `netstat -lntp`",
                    "`ps -ef | grep java` 找进程；`kill -9 进程号` 强杀",
                    "`systemctl status 服务名` 看服务状态；⚠️ 返回 `unknown` 说明**压根没这个服务单元**，不代表服务挂了",
                    "卡死了：`top` 看谁占 CPU/内存，按 `q` 退出",
                ],
                "src": "本机踩坑 · 加组件前先 ss -lntp 查端口冲突",
            },
            {
                "t": "压缩包与环境变量",
                "plain": "比赛发的软件基本都是 .tar.gz，解压 → 改个名 → 配环境变量 → source 生效，四步走。",
                "points": [
                    "解压：`tar -zxvf hadoop-3.1.3.tar.gz -C /opt/`（-z 是 gzip，-x 解压，-v 显示过程，-f 指定文件）",
                    "压缩：`tar -zcvf 包名.tar.gz 目录`",
                    "环境变量写在 `/etc/profile`（全局）或 `~/.bashrc`（当前用户），改完必须 `source /etc/profile` 才生效",
                    "验证：`echo $HADOOP_HOME` 能打印出路径才算配好；`which hadoop` 能找到命令",
                    "⚠️ 新开的终端窗口不会自动继承，要么 source 一遍，要么重开会话",
                ],
                "src": "本机踩坑 · 环境变量不生效的高频原因",
            },
        ],
        "anims": [],
    },
    {
        "id": "b2", "name": "Python 基础", "icon": "🐍",
        "desc": "模块二的数据清洗、模块三的出图，全程 Python，语法不用背但要能读懂改得动",
        "cards": [
            {
                "t": "Python 是怎么跑起来的",
                "plain": "Python 是解释型语言，写好的 .py 文件交给解释器一行一行执行，不需要编译。",
                "points": [
                    "跑脚本：`python3 clean.py` 或 `python clean.py`（本机 3.7.9，命令是 `python3`）",
                    "交互式：`python3` 回车进 `>>>`，适合临时试一句代码，`exit()` 退出",
                    "⚠️ Python 靠**缩进**划分代码块，同一层必须对齐（4 个空格），缩进错了直接 IndentationError",
                    "中文乱码：文件头写 `# -*- coding: utf-8 -*-`，读文件时 `encoding='utf-8'`",
                ],
                "src": "零基础补充 · 赛题脚本统一放 /root/eduhq/python/",
            },
            {
                "t": "变量与数据类型",
                "plain": "变量就是给数据起个名字；类型决定你能对它做什么操作。",
                "points": [
                    "数字 `int / float`、字符串 `str`、布尔 `bool`（True / False 首字母大写）",
                    "字符串拼接用 `+`，格式化推荐 f-string：`f'共 {n} 条'`",
                    "类型转换：`int('123')`、`str(123)`、`float('1.5')` —— **读进来的数据默认是字符串，要算就得先转**",
                    "⚠️ 常错：`'3' + 4` 会报错，因为字符串不能和数字相加",
                ],
                "src": "零基础补充",
            },
            {
                "t": "列表与字典（最常用两个容器）",
                "plain": "列表是有顺序的一排东西，字典是「键 → 值」的对照表。",
                "points": [
                    "列表 `a = [1, 2, 3]`：按下标取 `a[0]`（**从 0 开始**）、切片 `a[1:3]`、追加 `a.append(4)`、长度 `len(a)`",
                    "字典 `d = {'name': 'Tom', 'age': 18}`：取值 `d['name']`、遍历 `for k, v in d.items()`",
                    "列表推导式（高频写法）：`[x * 2 for x in a if x > 1]` —— 一行完成筛选 + 变换",
                    "⚠️ `a[3]` 越界会 IndexError；字典取不存在的键会 KeyError，用 `d.get('k', 默认值)` 更安全",
                ],
                "src": "零基础补充",
            },
            {
                "t": "条件与循环",
                "plain": "让程序做判断、做重复的事，清洗脚本的主要骨架就是这两样。",
                "points": [
                    "`if 条件: ... elif 条件: ... else: ...` —— 注意冒号不能少",
                    "`for x in 列表:` 逐个取；`for i in range(10):` 跑 0~9",
                    "`while 条件:` 条件成立就一直跑（记得改条件，否则死循环）",
                    "配合 `break`（跳出循环）与 `continue`（跳过本次）",
                    "读文件标准写法：`with open('a.txt', encoding='utf-8') as f: lines = f.readlines()` —— with 会自动关闭文件",
                ],
                "src": "零基础补充",
            },
            {
                "t": "函数：把一段代码包起来反复用",
                "plain": "函数就是给一段代码起名字，需要时喊一声就执行，避免复制粘贴。",
                "points": [
                    "`def 函数名(参数):` 定义，`return` 返回结果",
                    "参数可以有默认值：`def read_csv(path, sep=','):`",
                    "`if __name__ == '__main__':` 下面写「直接运行这个文件时才执行」的代码",
                    "⚠️ 函数内部改全局变量要 `global`，新手很容易在这里踩坑",
                ],
                "src": "零基础补充 · 赛题要求脚本可独立运行",
            },
            {
                "t": "pandas：比赛真正的干活工具",
                "plain": "pandas 把表格变成 DataFrame 对象，筛选、去重、分组统计都只要一行。",
                "points": [
                    "读：`df = pd.read_csv('a.csv', encoding='utf-8')`；写：`df.to_csv('r.csv', index=False)`",
                    "看数据：`df.head()` 前 5 行、`df.info()` 列类型与空值、`df.shape` 行列数、`df.describe()` 统计摘要",
                    "筛选：`df[df['age'] > 18]`；多条件用 `&`（且）`|`（或），**每个条件都要加括号**",
                    "清洗四件套：`dropna()` 去空行、`drop_duplicates()` 去重、`fillna(0)` 填空、`astype(int)` 改类型",
                    "分组：`df.groupby('province')['cnt'].sum()` —— 出图前的数据聚合基本都靠它",
                    "⚠️ 赛题要求：**结果文件名要带处理条数 N**，所以 `len(df)` 别忘了",
                ],
                "src": "ZZ052 · 模块二数据处理高频操作",
            },
            {
                "t": "出图：三条路线要分清",
                "plain": "Matplotlib / Seaborn 出静态图存成 png，Pyecharts 出可交互 html，Excel 出表内图表。",
                "points": [
                    "Matplotlib：`plt.figure()` → `plt.plot/bar` → 标题标签 → `plt.savefig('x.png')` → `plt.show()`",
                    "**中文乱码是必踩的坑**：`plt.rcParams['font.sans-serif'] = ['SimHei']` + `plt.rcParams['axes.unicode_minus'] = False`",
                    "Seaborn：`sns.set_theme()` 定风格，`sns.barplot(x=, y=, data=df)` 一行出图",
                    "Pyecharts：`Bar().add_xaxis().add_yaxis().set_global_opts().render('x.html')` —— 注意是 render 不是 savefig",
                    "⚠️ 题目说「嵌入背景图」时，Pyecharts 要在 HTML 里加背景样式，别忘了这一步",
                ],
                "src": "ZZ052 第 01/04/05/06 套 · 模块三",
            },
        ],
        "anims": [],
    },
    {
        "id": "b3", "name": "Java 基础", "icon": "☕",
        "desc": "Hadoop / Hive / Spark 全是 Java 写的；写 MapReduce 要能看懂 Java 骨架",
        "cards": [
            {
                "t": "JDK / JRE / JVM 是什么关系",
                "plain": "JVM 是运行 Java 的虚拟机，JRE = JVM + 运行类库，JDK = JRE + 开发工具（编译用的 javac 在 JDK 里）。",
                "points": [
                    "装环境装的是 **JDK**（本机 1.8.0_412），因为要写代码、要编译",
                    "`java -version` 能打印版本就算装好；`javac -version` 能打印说明编译器在",
                    "Java 跨平台靠 JVM：同一份 `.class` 字节码，Windows / Linux 上的 JVM 都能跑",
                    "⚠️ 环境变量 `JAVA_HOME` 要指向 JDK 根目录，不是 bin 目录；Hadoop 找不到 JAVA_HOME 会直接起不来",
                ],
                "src": "本机环境 · JDK 1.8.0_412",
            },
            {
                "t": "一次编译，到处运行",
                "plain": "源码 .java 先用 javac 编译成字节码 .class，再由 JVM 解释执行。",
                "points": [
                    "`javac WordCount.java` 生成 `WordCount.class`；`java WordCount` 运行（**不要加 .class 后缀**）",
                    "类名必须和文件名一致：`WordCount.java` 里就得写 `public class WordCount`",
                    "`main` 方法是程序入口，签名固定：`public static void main(String[] args)`",
                    "打包成 jar 交给集群：`jar -cvf wc.jar *.class`，然后 `hadoop jar wc.jar WordCount 输入 输出`",
                    "⚠️ 常见报错 `ClassNotFoundException`：打包时没带依赖，或主类名写错",
                ],
                "src": "零基础补充 · MapReduce 提交流程",
            },
            {
                "t": "基本语法：类型、循环、字符串",
                "plain": "Java 是强类型语言，变量必须先声明类型才能用，这点和 Python 完全不同。",
                "points": [
                    "`int / long / double / boolean / char` 是基本类型，`String` 是类（首字母大写）",
                    "`String` 不可变：拼接会产生新对象，大量拼接要用 `StringBuilder`",
                    "循环与 Python 类似：`for (int i = 0; i < n; i++)`、`for (String s : 列表)` 增强 for",
                    "字符串比较**必须用 `equals`**：`s.equals(\"abc\")`，用 `==` 比的是地址不是内容（新手第一大坑）",
                    "数组长度 `arr.length`；字符串长度 `s.length()`（**后面有括号**）",
                ],
                "src": "零基础补充",
            },
            {
                "t": "面向对象：类、对象、继承",
                "plain": "类是图纸，对象是按图纸造出来的东西；继承让子类直接拥有父类的能力。",
                "points": [
                    "`class 类名 { 属性; 方法; }`；`new 类名()` 造对象",
                    "`private` 私有、`public` 公开；`static` 属于类本身，不用 new 就能调",
                    "`extends` 继承、`implements` 实现接口、`@Override` 标明重写父类方法",
                    "⚠️ MapReduce 里 `Mapper<LongWritable, Text, Text, IntWritable>` 这种尖括号就是**泛型**，规定输入输出的类型",
                ],
                "src": "零基础补充 · 为读 MR 代码打底",
            },
            {
                "t": "MapReduce 代码骨架怎么读",
                "plain": "不管题目怎么变，MR 程序就三块：Mapper、Reducer、Driver（main）。",
                "points": [
                    "**Mapper**：`map(KEYIN, VALUEIN, Context)` —— 一行变多组 `key, value`，`context.write()` 写出",
                    "**Reducer**：`reduce(KEYIN, Iterable<VALUEIN>, Context)` —— 同一个 key 的 value 都凑齐了再处理",
                    "**Driver**：配 Job（设 Jar 类、Mapper 类、Reducer 类、输出类型、输入输出路径）→ `job.waitForCompletion(true)`",
                    "Hadoop 的类型是包装过的：`Text` 对应 String，`IntWritable` 对应 int，**不能用 Java 原生类型**",
                    "⚠️ 输出目录必须不存在，否则报 `Output directory already exists` —— 跑之前先删",
                ],
                "src": "ZZ052 第 02/04/06/07 套 · 模块二",
            },
            {
                "t": "Maven：依赖不用自己找 jar",
                "plain": "Maven 靠 pom.xml 声明要用的库，自动从仓库下载，写完一条命令打包。",
                "points": [
                    "`pom.xml` 里 `<dependency>` 声明依赖；坐标三要素 groupId / artifactId / version",
                    "`mvn clean package` 清理 + 编译 + 打包，产物在 `target/` 目录",
                    "`mvn compile` 只编译；`mvn test` 跑测试",
                    "⚠️ 断网环境下 Maven 拉不到依赖 —— 比赛环境一般提前备好本地仓库，别临时换版本",
                ],
                "src": "零基础补充",
            },
        ],
        "anims": [],
    },
    {
        "id": "b4", "name": "MySQL 基础", "icon": "🗄️",
        "desc": "Hive 的元数据存在 MySQL 里，模块二也常直接考建库建表与增删改查",
        "cards": [
            {
                "t": "数据库 / 表 / 行 / 列",
                "plain": "数据库是一堆表的集合，表由列（字段）定义结构、由行（记录）存放数据。",
                "points": [
                    "一个 MySQL 里可以有多个库：`CREATE DATABASE education;`",
                    "进库：`USE education;` —— **建表前忘了 USE，表就建到别的库里了**",
                    "`SHOW DATABASES;` 看有哪些库；`SHOW TABLES;` 看有哪些表；`DESC 表名;` 看表结构",
                    "⚠️ Hive 不是数据库，是「用 SQL 语法查 HDFS 上文件」的工具，它自己的元数据存在 MySQL 里",
                ],
                "src": "零基础补充 · Hive 元数据库为 MySQL 5.7",
            },
            {
                "t": "建表三件事：字段、类型、约束",
                "plain": "每个字段要定类型和长度，主键保证不重复，字符集决定能不能存中文。",
                "points": [
                    "`CREATE TABLE 表名 (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50) NOT NULL, age INT);`",
                    "`PRIMARY KEY` 主键、`AUTO_INCREMENT` 自增、`NOT NULL` 不允许空、`DEFAULT` 默认值",
                    "常用类型：`INT`、`BIGINT`、`VARCHAR(n)`、`DECIMAL(10,2)` 金额、`DATETIME`、`TEXT`",
                    "**中文必加**：建库建表时指定 `DEFAULT CHARSET=utf8mb4`，否则中文变成问号",
                    "⚠️ `utf8` 与 `utf8mb4` 不一样，emoji 等四字节字符只有 utf8mb4 能存",
                ],
                "src": "本机踩坑 · 字符集不统一是乱码根源",
            },
            {
                "t": "增删改查：CRUD",
                "plain": "增 INSERT、删 DELETE、改 UPDATE、查 SELECT，四句话覆盖 90% 的操作。",
                "points": [
                    "增：`INSERT INTO 表名 (列1, 列2) VALUES (值1, 值2);`",
                    "查：`SELECT 列 FROM 表 WHERE 条件;`；`SELECT *` 是所有列",
                    "改：`UPDATE 表 SET 列=新值 WHERE 条件;` —— ⚠️ **不加 WHERE 会把整表都改了**",
                    "删：`DELETE FROM 表 WHERE 条件;`；⚠️ 同理，不加 WHERE 就是清空表",
                    "导入文件：`LOAD DATA LOCAL INFILE '/root/a.csv' INTO TABLE 表名 FIELDS TERMINATED BY ',';`",
                ],
                "src": "ZZ052 第 07/08 套 · 模块二",
            },
            {
                "t": "查询进阶：排序、分组、连表",
                "plain": "WHERE 筛行、GROUP BY 分组统计、ORDER BY 排序、LIMIT 限条数，顺序不能乱。",
                "points": [
                    "固定顺序：`SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT`",
                    "聚合函数：`COUNT()`、`SUM()`、`AVG()`、`MAX()`、`MIN()`",
                    "⚠️ `WHERE` 在分组**前**筛行，`HAVING` 在分组**后**筛组 —— 用聚合结果做条件必须用 HAVING",
                    "`GROUP BY 省份` 后，SELECT 里只能出现分组列和聚合结果，写别的列是错的",
                    "连表：`SELECT * FROM a JOIN b ON a.id = b.id;`（INNER 内连接 / LEFT 左连接保留左表全部）",
                ],
                "src": "零基础补充 · 出图前的数据聚合",
            },
            {
                "t": "用户与权限（赛题常考）",
                "plain": "root 是超级管理员；比赛常要求新建用户、改密码、开远程登录。",
                "points": [
                    "建用户：`CREATE USER 'eduadmin'@'%' IDENTIFIED BY '******';` —— `@'%'` 表示允许从任意主机连",
                    "授权：`GRANT ALL PRIVILEGES ON education.* TO 'eduadmin'@'%';` 然后 **`FLUSH PRIVILEGES;`**",
                    "改密（5.7）：`ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';`",
                    "允许远程：改 `mysql.user` 表把 host 改成 `%`，再 `FLUSH PRIVILEGES;`",
                    "⚠️ 授权后不 FLUSH，权限不会生效 —— 这是「明明授权了还是连不上」的头号原因",
                ],
                "src": "ZZ052 第 01/07 套 · 模块一",
            },
            {
                "t": "备份与导入导出",
                "plain": "mysqldump 导出成 .sql，mysql 命令导回去；比赛也可能要求你把结果导成 CSV。",
                "points": [
                    "导出：`mysqldump -uroot -p education > education.sql`",
                    "导入：`mysql -uroot -p education < education.sql`",
                    "导出 CSV：`SELECT ... INTO OUTFILE '/tmp/r.csv' FIELDS TERMINATED BY ',';`",
                    "⚠️ `INTO OUTFILE` 受 `secure_file_priv` 限制，报权限错就换目录或改配置",
                    "本机 Hive 元数据库：`hive` 库，账号 hive / 口令见安装记录",
                ],
                "src": "本机环境 · Hive 元数据在 MySQL",
            },
        ],
        "anims": [],
    },
]
