# YouTube Description Service

> AI-powered YouTube description generation using Azure OpenAI

[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/r/mathiasschnack/description-service)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

Microservice that generates SEO-optimized YouTube descriptions for audiobook videos using Azure OpenAI. Features novel-level AI generation for cost efficiency and database-stored prompts for easy customization.

## Key Features

- **✨ Single API Call** - Generates all 3 sections (About, What to Expect, Tags) in one call
- **🎯 Novel-Level Generation** - One AI generation per novel, reused for all videos (88% cost savings)
- **⚡ Non-Blocking Database** - Short-lived transactions won't interfere with other services
- **🎨 Editable Prompts** - System and user prompts stored in database, edit via API
- **📊 Real-Time Progress** - Job status tracking with percentage complete
- **🔄 Smart Incremental** - Only generates missing descriptions
- **👁️ Preview Endpoints** - View descriptions before publishing

## Architecture

```
description-service/
├── src/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── utils/              # Helpers
├── migrations/             # Database migrations
├── docs/                   # Documentation
├── Dockerfile              # Linux/AMD64 ready
└── requirements.txt        # Dependencies
```

## Quick Start

### Using Docker (Recommended)

```bash
docker pull mathiasschnack/description-service:latest
docker run -p 8080:8080 --env-file .env mathiasschnack/description-service:latest
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
psql -f migrations/008_add_description_state.sql
psql -f migrations/009_add_system_prompts.sql

# Start service
python src/app.py
```

## API Endpoints

### Description Generation

**Start Generation:**
```bash
POST /generate-descriptions
{
  "novel_name": "Your Novel",
  "novel_context": "Brief description for AI",
  "playlist_url": "https://youtube.com/playlist?list=...",
  "subscribe_text": "Your subscribe message",
  "force": false
}
```

**Check Progress:**
```bash
GET /jobs/{job_id}
```

**Preview Description:**
```bash
GET /descriptions/{novel_name}/{video_name}
```

### Admin - Prompt Management

**List All Prompts:**
```bash
GET /admin/prompts
```

**Edit System Prompt (Output Format):**
```bash
PATCH /admin/prompts/description_system
{
  "prompt_text": "New format instructions..."
}
```

**Edit User Prompt (Content):**
```bash
PATCH /admin/prompts/full_description
{
  "prompt_text": "New content requirements..."
}
```

## How It Works

### Efficient Novel-Level Generation

```
1 Novel with 8 Videos
    ↓
1 OpenAI API Call (~3 seconds, ~$0.02)
    ↓
Generates:
  - About (8-13 lines)
  - What to Expect (3-6 sentences)
  - Tags (500 chars max)
    ↓
REUSED for all 8 videos
    ↓
Only timestamps change per video
    ↓
Total: ~6 seconds, ~$0.02 per novel
```

**vs. Video-Level:** 8 calls × 3 sec × $0.02 = 24 sec, $0.16 ❌

**Savings:** 77% faster, 88% cheaper ✅

### Database System Prompts

**System Prompt** (`description_system`):
- Controls output format structure
- Tells AI: "Use ABOUT:, WHAT_TO_EXPECT:, TAGS: headers"

**User Prompt** (`full_description`):
- Defines content requirements
- Specifies lengths, tone, style

**Both editable via API - changes apply immediately!**

## Configuration

See `.env.example` for all options.

**Required:**
- Azure OpenAI endpoint and API key
- PostgreSQL connection
- S3/R2 storage credentials
- API authentication token

## Testing

### Postman Collection

Import `YouTube_Description_Service_Complete.postman_collection.json`:
- All endpoints with examples
- Auto-saves job_id
- Built-in variables for local/production

See `docs/POSTMAN_GUIDE.md`

### Example Test

```bash
# Health check
curl http://localhost:8080/health

# Generate descriptions
curl -X POST http://localhost:8080/generate-descriptions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Deployment

**Docker Image:**
```
mathiasschnack/description-service:latest
```

**Platform:** linux/amd64  
**Port:** 8080  
**Instance:** S2 (1 CPU / 2GB RAM)

See `docs/DEPLOYMENT.md` for Sevalla deployment guide.

## Documentation

- `docs/QUICK_START.md` - 5-minute deployment guide
- `docs/DEPLOYMENT.md` - Detailed Sevalla setup
- `docs/POSTMAN_GUIDE.md` - API testing guide
- `docs/IMPLEMENTATION_SUMMARY.md` - Technical details
- `docs/FINAL_STATUS.md` - Complete feature list

## Database Migrations

1. `008_add_description_state.sql` - Core tables
2. `009_add_system_prompts.sql` - System prompts
3. `010_cleanup_legacy_prompts.sql` - Remove unused prompts (optional)

## Performance

- **API Response Time:** < 100ms (immediate job_id return)
- **Generation Time:** ~25 seconds for 8 videos
- **Database Locks:** < 100ms per transaction (non-blocking)
- **Cost:** ~$0.02 per novel regardless of video count

## Security

- Bearer token authentication on all endpoints (except /health)
- Configurable CORS origins
- Environment-based configuration
- No secrets in codebase

## Tech Stack

- **Framework:** Flask 3.0.0
- **Database:** PostgreSQL with SQLAlchemy
- **Storage:** S3/R2 (Cloudflare)
- **AI:** Azure OpenAI (gpt-5-nano)
- **Deployment:** Docker on Sevalla

## License

MIT

## Support

For issues or questions, check:
- `docs/` folder for comprehensive guides
- Service logs for debugging
- Database state for job status

---

**Status:** ✅ Production Ready  
**Docker:** `mathiasschnack/description-service:latest`  
**Platform:** linux/amd64
