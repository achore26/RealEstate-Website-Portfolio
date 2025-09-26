// Service Worker for Visual House - Advanced Video Caching
const CACHE_NAME = 'visualhouse-cache-v1';
const VIDEO_CACHE_NAME = 'visualhouse-video-cache-v1';

// Critical assets to cache immediately
const CRITICAL_ASSETS = [
  '/',
  '/index.html',
  '/assets/css/styles.css',
  '/assets/js/main.js',
  '/assets/js/mobile-optimizer.js',
  '/assets/media/01.jpg',
  '/assets/media/about-hero.jpg'
];

// Video assets to cache on first request
const VIDEO_ASSETS = [
  '/assets/media/background-video.mp4'
];

// Install event - cache critical assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Caching critical assets');
        return cache.addAll(CRITICAL_ASSETS);
      })
      .then(() => {
        console.log('Critical assets cached successfully');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Failed to cache critical assets:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== VIDEO_CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, cache video on first request
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Handle video files specially
  if (VIDEO_ASSETS.some(asset => url.pathname.endsWith(asset.split('/').pop()))) {
    event.respondWith(
      caches.open(VIDEO_CACHE_NAME)
        .then(cache => {
          return cache.match(event.request)
            .then(response => {
              if (response) {
                console.log('Serving video from cache:', url.pathname);
                return response;
              }
              
              console.log('Fetching and caching video:', url.pathname);
              return fetch(event.request)
                .then(response => {
                  // Only cache successful responses
                  if (response.status === 200) {
                    cache.put(event.request, response.clone());
                  }
                  return response;
                })
                .catch(error => {
                  console.error('Failed to fetch video:', error);
                  throw error;
                });
            });
        })
    );
    return;
  }
  
  // Handle other assets
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version if available
        if (response) {
          console.log('Serving from cache:', url.pathname);
          return response;
        }
        
        // Fetch from network and cache if it's a critical asset
        return fetch(event.request)
          .then(response => {
            // Only cache successful responses for same origin
            if (response.status === 200 && url.origin === location.origin) {
              const responseClone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseClone);
                });
            }
            return response;
          });
      })
      .catch(error => {
        console.error('Fetch failed:', error);
        
        // Return offline fallback for HTML requests
        if (event.request.destination === 'document') {
          return caches.match('/index.html');
        }
        
        throw error;
      })
  );
});

// Message handling for cache management
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_VIDEO') {
    // Preemptively cache video
    caches.open(VIDEO_CACHE_NAME)
      .then(cache => {
        return cache.addAll(VIDEO_ASSETS);
      })
      .then(() => {
        event.ports[0].postMessage({ success: true });
      })
      .catch(error => {
        console.error('Failed to cache video:', error);
        event.ports[0].postMessage({ success: false, error: error.message });
      });
  }
});