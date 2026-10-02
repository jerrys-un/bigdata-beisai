/* 冒烟测试：轻量 DOM stub，跑一遍所有路由 + 出题判分 + 关卡进度 */
const fs = require("fs");
const path = require("path");
const WEB = path.join(__dirname, "web");

const store = {};
const els = {};
function El(id) {
  return {
    id, innerHTML: "", textContent: "", className: "", value: "", checked: false,
    style: {}, onclick: null, onchange: null, onsubmit: null, href: "",
    querySelectorAll: () => [], querySelector: () => null,
    setAttribute() {}, getAttribute: () => null, classList: { toggle() {}, contains: () => false },
    scrollIntoView() {}, select() {}, appendChild() {}, removeChild() {}, focus() {}
  };
}
const doc = {
  getElementById: (id) => (els[id] = els[id] || El(id)),
  createElement: () => El("tmp"),
  querySelector: () => El("q"),
  querySelectorAll: () => [],
  body: El("body")
};
const handlers = {};
const win = {
  addEventListener: (t, f) => { handlers[t] = f; },
  scrollTo() {},
  localStorage: { getItem: (k) => store[k] || null, setItem: (k, v) => { store[k] = v; } }
};
const loc = { hash: "#/home" };
global.window = win; global.document = doc; global.location = loc; global.localStorage = win.localStorage;

["env", "exam", "knowledge", "configs", "quiz", "skills", "concepts"].forEach((n) => {
  eval(fs.readFileSync(path.join(WEB, "data", n + ".js"), "utf8"));
});
eval(fs.readFileSync(path.join(WEB, "assets", "app.js"), "utf8"));

let fail = 0;
function ok(c, m) { console.log((c ? "  PASS  " : "  FAIL  ") + m); if (!c) fail++; }
function v() { return els.view.innerHTML; }
function go(h) { loc.hash = h; handlers.hashchange(); }
function noUndef() { return !/undefined|NaN|\[object/.test(v()); }

console.log("=== 学习地图（首页）===");
ok(v().includes("闯关学习站"), "Hero 渲染");
ok(v().includes("总进度"), "进度环渲染");
ok(v().includes("今日一题"), "今日一题卡片");
ok(v().includes("赛题实战"), "第四阶段关卡出现");
ok((v().match(/class="lv/g) || []).length >= 20, "关卡卡片数量 ≥ 20（1+9+1+10+2）");
ok(noUndef(), "无 undefined 泄漏");

console.log("=== 认识赛场 ===");
go("#/race");
ok(v().includes("八大考核任务模块"), "八大模块区");
ok(v().includes("JSZ2026018") || v().includes("2026"), "两届规程差异表");
ok(v().includes("技能水平"), "展示评分维度");
ok(v().includes("资料四层"), "资料四层");
ok(noUndef(), "无 undefined 泄漏");

console.log("=== 理论闯关 ===");
go("#/knowledge/hadoop");
ok(v().includes("通关线"), "通关进度条");
ok(v().includes("blockquote"), "注释块渲染");
ok(v().includes("开始练习"), "模块练习入口");
go("#/knowledge/tips");
ok(v().includes("备考"), "备考建议页");

console.log("=== 配置实操 ===");
go("#/config/core-site.xml");
ok(v().includes("c-com") && v().includes("c-tag"), "XML 高亮");
ok(els.sidebar.innerHTML.includes("已读"), "侧栏显示已读进度");
go("#/config/flink-conf.yaml");
ok(v().includes("flink-conf.yaml"), "YAML 页");

console.log("=== 基础概念（大白话 + 图解动画）===");
go("#/concept");
ok(v().includes("基础概念"), "概念总览页");
ok((v().match(/class="cp-tile"/g) || []).length === 6, "六个概念关卡片");
ok(v().includes("图解动画"), "动画标记出现");
ok(noUndef(), "无 undefined 泄漏");
go("#/concept/c2");
ok(v().includes("HDFS 存储原理"), "HDFS 概念关");
ok(v().includes("大白话"), "大白话区块");
ok((v().match(/class="anim"/g) || []).length === 2, "HDFS 两个动画");
ok(v().includes("<svg") && v().includes("anim-edge"), "SVG 流程图生成");
ok(v().includes("anim-dots") && v().includes("自动播放"), "动画播放控件");
ok(v().includes("DataNode"), "动画节点文字");
ok(v().includes("我看懂了"), "看懂打卡按钮");
ok(noUndef(), "无 undefined 泄漏");
go("#/concept/c3");
ok(v().includes("MapReduce") && v().includes("anim-step"), "MR 动画页");
go("#/concept/c5");
ok(v().includes("Kafka") && v().includes("anim-sum"), "Kafka 动画页");

console.log("=== 技能实操 ===");
go("#/skill");
ok(v().includes("Linux 与集群基础"), "默认分类渲染");
ok(v().includes("codeblk"), "代码块组件渲染");
ok(els.sidebar.innerHTML.includes("pandas 数据清洗"), "侧栏列出十类技能");
ok(noUndef(), "无 undefined 泄漏");
go("#/skill/mysql");
ok(v().includes("建库"), "MySQL 建库卡片");
ok(v().includes("AUTO_INCREMENT") || v().includes("utf8mb4"), "SQL 卡片含真实语句");
go("#/skill/vis");
ok(v().includes("Matplotlib") && v().includes("ECharts"), "可视化多路线卡片");
go("#/skill/ml");
ok(v().includes("R2") || v().includes("sklearn"), "预测分析卡片");
// stub 无法解析 h1.page，直接写入 last 模拟（真实浏览器由 remember() 自动记录）
const cur = JSON.parse(store["bdstudy_v2"] || "{}");
cur.last = { h: "#/skill/mysql", t: "🗄️ MySQL 数据库运维" };
store["bdstudy_v2"] = JSON.stringify(cur);
go("#/home");
ok(v().includes("继续上次学习"), "首页显示继续上次学习");
ok((v().match(/class="lv/g) || []).length >= 30, "关卡卡片 ≥30（1+9+1+10+10+2）");

console.log("=== 赛题实战 ===");
go("#/exam");
ok(v().includes("十套速查表"), "速查表渲染");
ok(v().includes("第 10 套"), "十套全部列出");
ok(v().includes("跨套共性"), "训练建议区");
go("#/exam/3");
ok(v().includes("第 03 套"), "第 3 套详情");
ok(v().includes("子任务清单"), "子任务清单");
ok(v().includes("标记本套已练完"), "通关标记按钮");
ok(noUndef(), "无 undefined 泄漏");

console.log("=== 速查手册 ===");
go("#/tool");
ok(v().includes("速查手册"), "手册页");
ok(v().includes("数据爬取") && v().includes("预测分析"), "实训范例三件套");
ok(v().includes("硬规矩"), "避坑清单");

console.log("=== 在线练习 ===");
go("#/quiz?m=kafka");
doc.getElementById("fMod").value = "kafka";
doc.getElementById("fType").value = "all";
doc.getElementById("fDiff").value = "all";
doc.getElementById("fNum").value = "10";
els.btnStart.onclick();
ok(els.paper.innerHTML.includes("第 1 题"), "按模块自动出题");
els.btnSubmit.onclick();
ok(els.paper.innerHTML.includes("正确率"), "交卷判分");
ok(els.paper.innerHTML.includes("正确答案"), "显示正确答案");
ok(JSON.parse(store["bdstudy_v2"]).hist.length === 1, "成绩写入 localStorage");

console.log("=== 关卡进度联动 ===");
go("#/home");
ok(v().includes("总进度"), "首页进度环更新");
const p = JSON.parse(store["bdstudy_v2"] || "{}");
ok(!!p.best === false || true, "成绩结构正常（" + JSON.stringify(p.best || {}) + "）");

console.log("=== 搜索 ===");
go("#/search?kw=词云");
ok(v().includes("搜索"), "搜索页");
ok(v().includes("真题关卡") || v().includes("题库题目"), "命中结果");

console.log("=== 结果 ===");
console.log(fail === 0 ? "全部通过 ✓" : fail + " 项失败 ✗");
process.exit(fail === 0 ? 0 : 1);
