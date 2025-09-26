# Video Optimization Guide for Mobile Safari

## Current Issues
- Safari mobile has stricter video loading policies than desktop
- Large videos may not autoplay on mobile due to data saving features
- GitHub Pages doesn't provide video streaming headers

## Solutions Implemented

### 1. Video Element Optimizations
```html
<video autoplay muted loop playsinline preload="auto" poster="assets/media/01.jpg">
  <source src="assets/media/background-video.mp4" type="video/mp4" />
</video>
```

**Key attributes:**
- `preload="auto"` - Encourages Safari to load video early
- `poster="assets/media/01.jpg"` - Shows image while video loads
- `playsinline` - Required for iOS autoplay
- `muted` - Required for autoplay on mobile

### 2. Loading Animation
- Shows spinner while video loads
- Hides automatically when video is ready
- Fallback timeout prevents stuck loader

### 3. Service Worker Caching
- Caches video on first visit
- Subsequent visits load instantly from cache
- Reduces bandwidth usage

## Video Optimization Commands

### For Mobile-Optimized Video:
```bash
# Reduce file size and optimize for mobile
ffmpeg -i background-video.mp4 \
  -vf "scale=1280:-1" \
  -b:v 1500k \
  -c:v libx264 \
  -c:a aac \
  -movflags faststart \
  background-video-mobile.mp4
```

### For Different Quality Versions:
```bash
# High quality (desktop)
ffmpeg -i input.mp4 -b:v 3000k -movflags faststart background-video-hd.mp4

# Medium quality (tablet)  
ffmpeg -i input.mp4 -b:v 2000k -movflags faststart background-video-md.mp4

# Low quality (mobile)
ffmpeg -i input.mp4 -b:v 1000k -movflags faststart background-video-mobile.mp4
```

## Serving Different Videos by Device

### Option 1: JavaScript Detection
```javascript
const video = document.getElementById('video-background');
const isMobile = window.innerWidth <= 768;

if (isMobile) {
  video.src = 'assets/media/background-video-mobile.mp4';
} else {
  video.src = 'assets/media/background-video.mp4';
}
```

### Option 2: HTML Media Queries
```html
<video autoplay muted loop playsinline preload="auto">
  <source src="assets/media/background-video-mobile.mp4" type="video/mp4" media="(max-width: 768px)">
  <source src="assets/media/background-video.mp4" type="video/mp4">
</video>
```

## Testing Checklist

### Mobile Safari Testing:
- [ ] Video loads on first visit
- [ ] Video autoplays without user interaction
- [ ] Poster image shows while loading
- [ ] Loading animation appears/disappears correctly
- [ ] Video works after switching to desktop mode and back

### Performance Testing:
- [ ] Video file size < 5MB for mobile
- [ ] First frame loads within 2 seconds
- [ ] Service worker caches video properly
- [ ] Subsequent visits load faster

## Troubleshooting

### Video Doesn't Autoplay:
1. Ensure `muted` attribute is present
2. Add `playsinline` for iOS
3. Check if Low Power Mode is enabled
4. Test with smaller video file

### Video Appears Stuck Loading:
1. Add `preload="auto"`
2. Implement loading timeout
3. Provide poster image fallback
4. Optimize video with `movflags faststart`

### Service Worker Issues:
1. Ensure HTTPS (GitHub Pages provides this)
2. Check browser developer tools for SW registration
3. Clear cache and test again
4. Verify video caching in Network tab

## Best Practices

1. **Keep videos short** (< 30 seconds loop)
2. **Optimize file size** (aim for < 5MB on mobile)
3. **Use H.264 codec** (best Safari compatibility)
4. **Provide poster images** (instant visual feedback)
5. **Implement graceful fallbacks** (image backup)
6. **Test on real devices** (not just browser dev tools)