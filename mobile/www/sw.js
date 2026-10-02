/* 离线缓存：核心资源预缓存，其余访问过就缓存（cache-first）
   只在 https 下由 index.html 注册；局域网 http 不支持 Service Worker，会静默跳过。 */
const CACHE = 'bdstudy-v3';

const CORE = [
  './', './index.html',
  './assets/app.js', './assets/style.css',
  './data/env.js', './data/exam.js', './data/knowledge.js', './data/configs.js',
  './data/quiz.js', './data/skills.js', './data/concepts.js', './data/demo.js', './data/gate.js',
  './manifest.webmanifest',
  './icons/icon-192.png', './icons/icon-512.png',
  './icons/favicon-32.png', './icons/apple-touch-icon.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(CORE.map((u) => c.add(u).catch(() => null))))  // 单个失败不影响整体
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }).catch(() => caches.match('./index.html')))
  );
});
