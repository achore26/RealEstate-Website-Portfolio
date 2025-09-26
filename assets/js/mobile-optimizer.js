// Mobile Optimization Configuration
// This file handles advanced mobile optimizations for Visual House

class MobileOptimizer {
  constructor() {
    this.init();
  }

  init() {
    this.detectDevice();
    this.optimizeForMobile();
    this.handleOrientationChange();
    this.preloadCriticalImages();
  }

  detectDevice() {
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    
    document.documentElement.classList.toggle('mobile', isMobile);
    document.documentElement.classList.toggle('ios', isIOS);

    // Store device info
    this.device = {
      isMobile,
      isIOS,
      supportsWebP: this.supportsWebP()
    };
  }

  supportsWebP() {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('webp') !== -1;
  }

  optimizeForMobile() {
    if (!this.device.isMobile) return;

    // Disable hover effects on mobile
    document.documentElement.classList.add('no-hover');

    // Optimize video loading on mobile
    const videos = document.querySelectorAll('video');
    videos.forEach(video => {
      if (this.device.isMobile) {
        video.preload = 'metadata'; // Load only metadata on mobile
        video.muted = true; // Required for autoplay on mobile
      }
    });

    // Add mobile-specific event listeners
    this.addMobileEventListeners();
  }

  addMobileEventListeners() {
    // Handle viewport changes (address bar showing/hiding)
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);

    window.addEventListener('resize', () => {
      vh = window.innerHeight * 0.01;
      document.documentElement.style.setProperty('--vh', `${vh}px`);
    });

    // Prevent zoom on double tap
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function (event) {
      const now = (new Date()).getTime();
      if (now - lastTouchEnd <= 300) {
        event.preventDefault();
      }
      lastTouchEnd = now;
    }, false);
  }

  handleOrientationChange() {
    window.addEventListener('orientationchange', () => {
      // Force layout recalculation after orientation change
      setTimeout(() => {
        window.scrollTo(0, window.pageYOffset);
      }, 100);
    });
  }

  preloadCriticalImages() {
    const criticalImages = [
      'assets/media/01.jpg',
      'assets/media/about-hero.jpg'
    ];

    criticalImages.forEach(src => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
    });
  }

  // Intersection Observer for advanced lazy loading
  setupAdvancedLazyLoading() {
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            imageObserver.unobserve(img);
          }
        });
      });

      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new MobileOptimizer();
});

// Export for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MobileOptimizer;
}