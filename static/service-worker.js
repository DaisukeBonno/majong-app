self.addEventListener("install", e => {
  e.waitUntil(
    caches.open("mahjong").then(cache => cache.addAll(["/"]))
  );
});