const CACHE_NAME = 'cashpilot-v1';
const urlsToCache = [
  '/',
  '/static/css/bootstrap.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/img/favicon.ico',
  '/static/img/web-app-manifest-192x192.png',
  '/static/img/web-app-manifest-512x512.png',
  '/offline/',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Cache opened');
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request).then(response => {
        return response || caches.match('/offline/');
      });
    })
  );
});
