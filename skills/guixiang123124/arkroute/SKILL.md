---
name: arkroute
description: Generate images and videos using the best visual AI models (Seedream, Nano Banana, Seedance). One API for Chinese and American AI models.
homepage: https://ark-route.com
metadata:
  openclaw:
    emoji: "🎨"
---

# ArkRoute — Visual AI Model Router

Generate images and videos using the best AI models from around the world. ArkRoute provides a unified API for accessing premium visual AI models from Chinese and American providers.

## Available Models

### Image Generation
- `nano-banana-2` — Google Gemini 2.5 Flash, fast and cheap ($0.02/image)
- `nano-banana-basic` — Google Gemini 2.5 Flash, basic mode
- `seedream-4.5` — ByteDance, highest quality Chinese image model
- `seedream-5.0-lite` — ByteDance, fast and affordable
- `gemini-flash-image` — Google Gemini Flash optimized for images
- `gemini-3-pro-image` — Google Gemini 3 Pro with enhanced image quality

### Video Generation  
- `seedance-1.5-pro` — ByteDance, best video generation AI available
- `seedance-1.0-fast` — ByteDance, fast video generation for quick results

## Quick Start

### Generate Image
```bash
curl -X POST https://api.ark-route.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "prompt": "A serene Japanese garden with cherry blossoms",
    "size": "2K"
  }'
```

### Generate Video
```bash
curl -X POST https://api.ark-route.com/v1/videos/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "seedance-1.5-pro",
    "prompt": "A time-lapse of clouds moving over mountains",
    "duration": 5,
    "aspect_ratio": "16:9"
  }'
```

### Check Video Status
```bash
curl -X GET https://api.ark-route.com/v1/videos/TASK_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## OpenClaw Integration

This skill can be accessed through OpenClaw using the MCP (Model Context Protocol) server:

### As MCP Tool
```python
# The MCP server exposes these tools:
# - generate_image(prompt, model="nano-banana-2", size="2K", reference_image=None)
# - generate_video(prompt, model="seedance-1.5-pro", duration=5, aspect_ratio="16:9")
# - check_video_status(task_id)
# - list_models()

# Start the MCP server
python3 /path/to/arkroute/mcp_server.py
```

### Direct API Usage from OpenClaw
```python
import requests

# Generate an image
response = requests.post(
    "https://api.ark-route.com/v1/images/generations",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "model": "nano-banana-2",
        "prompt": "A futuristic cityscape at sunset",
        "size": "2K"
    }
)

result = response.json()
print(f"Image URL: {result['data'][0]['url']}")
```

## Model Capabilities

| Model | Type | Provider | Quality | Speed | Cost |
|-------|------|----------|---------|-------|------|
| `nano-banana-2` | Image | Google Gemini | High | Fast | $0.02 |
| `nano-banana-basic` | Image | Google Gemini | Good | Very Fast | $0.01 |
| `seedream-4.5` | Image | ByteDance | Excellent | Medium | $0.05 |
| `seedream-5.0-lite` | Image | ByteDance | Good | Fast | $0.03 |
| `seedance-1.5-pro` | Video | ByteDance | Excellent | Slow | $0.20 |
| `seedance-1.0-fast` | Video | ByteDance | Good | Fast | $0.10 |

## Size Options

### Image Sizes
- `1K` — 1024x1024 (square)
- `2K` — 2048x2048 (square) — **Recommended**
- `4K` — 4096x4096 (square, premium)
- `square` — 1:1 aspect ratio
- `portrait` — 3:4 aspect ratio (vertical)
- `landscape` — 4:3 aspect ratio (horizontal)

### Video Aspect Ratios
- `16:9` — Landscape (YouTube, most screens)
- `9:16` — Portrait (TikTok, Instagram Stories)
- `1:1` — Square (Instagram posts)

## Getting an API Key

1. Visit https://ark-route.com
2. Sign up for a free account
3. Get 100 free credits to start generating
4. Upgrade for higher limits and premium models

## Error Handling

### Common Error Codes
- `401` — Invalid API key
- `402` — Insufficient credits
- `429` — Rate limit exceeded
- `500` — Model provider error

### Best Practices
- Always check the response status before processing results
- Implement retry logic for transient errors (429, 500)
- Monitor your credit balance through the dashboard
- Use appropriate timeouts for video generation (can take 30+ seconds)

## Advanced Features

### Image-to-Image Generation
```bash
curl -X POST https://api.ark-route.com/v1/images/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "seedream-4.5",
    "prompt": "Transform this into a cyberpunk scene",
    "reference_image": "https://example.com/input.jpg"
  }'
```

### Image-to-Video Generation
```bash
curl -X POST https://api.ark-route.com/v1/videos/generations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "seedance-1.5-pro",
    "prompt": "Animate this scene with gentle movement",
    "image_url": "https://example.com/scene.jpg",
    "duration": 10
  }'
```

## Support

- **Documentation**: https://docs.ark-route.com
- **API Status**: https://status.ark-route.com
- **Discord Community**: https://discord.gg/arkroute

ArkRoute is designed for developers and creators who need reliable access to the world's best visual AI models through a simple, unified API.