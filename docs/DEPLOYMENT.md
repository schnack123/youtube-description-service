# Deployment Guide - YouTube Description Service

## Overview

The Description Service is ready for deployment to Sevalla. The Docker image has been built and pushed to Docker Hub.

## Docker Image

```
mathiasschnack/description-service:latest
```

**Platform:** linux/amd64
**Digest:** sha256:408530bfe04a6a522d9e36687e999e1397a9c57e53d6fcf3ce61e377ceaca38c

## Prerequisites

1. Database migration completed:
   - Migration `008_add_description_state.sql` has been run
   - Tables `workflow_description_state` and `ai_prompts` exist
   - AI prompts initialized with default values

2. Environment variables configured (see `.env` file)

## Sevalla Deployment Steps

### 1. Create Application

1. Log into Sevalla dashboard
2. Create new application: **description-service**
3. Select Docker deployment method
4. Instance type: **S2** (1 CPU / 2GB RAM)
5. Port: **8080**

### 2. Configure Docker Image

```
Image: mathiasschnack/description-service:latest
Port: 8080
```

### 3. Set Environment Variables

Required environment variables (from `.env`):

```bash
API_TOKEN=M44483403m
PORT=8080
HOST=0.0.0.0
CORS_ORIGINS=https://manager.novelaudioforge.com,https://audiobook-manager-v8wkm.sevalla.app,http://localhost:3000

# PostgreSQL Database
POSTGRES_HOST=europe-west3-002.proxy.kinsta.app
POSTGRES_PORT=30374
POSTGRES_DB=novels-meta
POSTGRES_USER=admin
POSTGRES_PASSWORD=M44483403m

# S3/R2 Storage
S3_ENDPOINT=https://f6d1d15e6f0b37b4b8fcad3c41a7922d.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=c87874529434b017cdf180b8e5eb1604
S3_SECRET_ACCESS_KEY=5bfcbc491f008c359fcb5a2eaedf1e75b270a105d48f93462ffbee3cdd75b80d
S3_BUCKET_NAME=audio-novels-7x1e4
S3_REGION=auto

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://flugger-ai-sverige.openai.azure.com/openai/v1/
AZURE_OPENAI_DEPLOYMENT=gpt-5-nano
USE_AZURE_OPENAI=true
OPENAI_API_KEY=4b822d3db0854bfd93c682629b921741

# Model Configuration
OPENAI_MODEL=gpt-4o-mini

# Logging
LOG_LEVEL=INFO
```

### 4. Deploy

1. Click "Deploy"
2. Wait for deployment to complete
3. Note the application URL (e.g., `https://description-service.sevalla.app`)

### 5. Verify Deployment

Test the health endpoint:

```bash
curl https://description-service.sevalla.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "description-service",
  "version": "1.0.0"
}
```

### 6. Test API Endpoints

#### List AI Prompts

```bash
curl -H "Authorization: Bearer M44483403m" \
  https://description-service.sevalla.app/admin/prompts
```

#### Get Specific Prompt

```bash
curl -H "Authorization: Bearer M44483403m" \
  https://description-service.sevalla.app/admin/prompts/what_to_expect
```

## API Endpoints Reference

### Description Generation

- `POST /generate-descriptions` - Generate descriptions for a novel
- `GET /jobs/{job_id}` - Check generation job status
- `GET /descriptions/{novel_name}` - List all descriptions for a novel
- `GET /descriptions/{novel_name}/{video_name}` - Preview specific description

### Admin - Prompt Management

- `GET /admin/prompts` - List all AI prompts
- `GET /admin/prompts/{prompt_name}` - Get specific prompt
- `PATCH /admin/prompts/{prompt_name}` - Update prompt content

### Health

- `GET /health` - Service health check

## Authentication

All endpoints except `/health` require Bearer token authentication:

```
Authorization: Bearer M44483403m
```

## Testing the Service

### Generate Descriptions for a Novel

```bash
curl -X POST https://description-service.sevalla.app/generate-descriptions \
  -H "Authorization: Bearer M44483403m" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_name": "Farming at Hogwarts",
    "novel_context": "Epic farming system story in Westeros",
    "playlist_url": "https://youtube.com/playlist?list=TEST123",
    "subscribe_text": "Subscribe for more Game of Thrones fanfiction audiobooks!",
    "force": false
  }'
```

### Check Job Status

```bash
curl -H "Authorization: Bearer M44483403m" \
  https://description-service.sevalla.app/jobs/{job_id}
```

### Preview Description

```bash
curl -H "Authorization: Bearer M44483403m" \
  https://description-service.sevalla.app/descriptions/Farming%20at%20Hogwarts/Chapter-1
```

## Monitoring

Monitor the following:

1. **Health Check**: `/health` endpoint should return 200
2. **Database Connection**: Check if service can connect to PostgreSQL
3. **S3 Access**: Verify service can read timestamps and write descriptions
4. **Azure OpenAI**: Check if API calls are successful
5. **Logs**: Monitor Sevalla application logs for errors

## Troubleshooting

### Service Won't Start

- Check environment variables are correctly set
- Verify database connection details
- Check Docker image is accessible

### Database Errors

- Verify migration was run successfully
- Check PostgreSQL credentials
- Ensure tables exist: `workflow_description_state`, `ai_prompts`

### S3 Errors

- Verify S3 credentials
- Check bucket name and endpoint
- Ensure bucket has required folders: `{novel}/Timestamps/`, `{novel}/Youtube/`

### OpenAI Errors

- Verify Azure OpenAI endpoint and API key
- Check deployment name matches configuration
- Monitor API quota usage

## Next Steps

After deployment:

1. Test with "Farming at Hogwarts" novel
2. Verify descriptions are generated correctly
3. Test regeneration with `force=true`
4. Test prompt editing via admin endpoints
5. Update frontend to integrate with new service

## Rollback Plan

If issues occur:

1. Stop the service in Sevalla
2. Check logs for errors
3. Fix configuration issues
4. Redeploy

## Support

For issues, check:
- Sevalla application logs
- Database connection status
- S3 bucket contents
- Azure OpenAI API status

