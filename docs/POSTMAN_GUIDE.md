# Postman Collection Guide

## Overview

A single, complete Postman collection for testing the YouTube Description Service API.

## Single File - Easy Import

**File:** `YouTube_Description_Service_Complete.postman_collection.json`

This single file includes:
- ✅ All API endpoints
- ✅ Built-in variables
- ✅ Auto-save job_id
- ✅ Example requests
- ✅ Comprehensive documentation

## How to Import

### Simple 3-Step Setup

1. **Open Postman**
2. **Import** → Drag and drop `YouTube_Description_Service_Complete.postman_collection.json`
3. **Done!** Start testing immediately

## Switch Between Environments

To switch between local and production:

1. Click on the collection name: **YouTube Description Service - Complete**
2. Go to **Variables** tab
3. Change `base_url`:
   - **Local:** `http://localhost:8082`
   - **Production:** `https://description-service.sevalla.app`
4. Click **Save**

## Collection Structure

### 🏥 Health Check
- **Get Service Health** - Verify service is running (no auth required)

### 📝 Description Generation
1. **Generate Descriptions** - Start generation job
2. **Generate Descriptions (Force)** - Regenerate all descriptions
3. **Get Job Status** - Check progress (uses auto-saved job_id)
4. **List All Descriptions** - See all generated descriptions
5. **Preview Specific Description** - View full description content

### ⚙️ Admin - Prompt Management
- **List All Prompts** - View all AI prompts
- **Get Prompt - What to Expect** - View specific prompt
- **Get Prompt - SEO Tags** - View specific prompt
- **Update Prompt - What to Expect** - Edit prompt text
- **Update Prompt - SEO Tags** - Edit prompt text

## Collection Variables

Edit these in the **Variables** tab of the collection:

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `base_url` | `http://localhost:8082` | Change to production URL as needed |
| `api_token` | `M44483403m` | Authentication token |
| `job_id` | _(auto-saved)_ | Automatically captured from generate response |
| `novel_name` | `Farming at Hogwarts` | Novel name for testing |
| `video_name` | `Chapter-1` | Video name for preview |

## Quick Start Workflow

### 1. Health Check ✅
```
GET /health
```
**No authentication required**

Expected response:
```json
{
  "status": "healthy",
  "service": "description-service",
  "version": "1.0.0"
}
```

### 2. Generate Descriptions 🚀

1. Open **"1. Generate Descriptions"** request
2. Review request body (already filled with example)
3. Click **Send**
4. **job_id automatically saved** via test script ✨

Response:
```json
{
  "success": true,
  "job_id": "abc-123-def-456",
  "status": "processing",
  "message": "Description generation started"
}
```

### 3. Monitor Progress 📊

1. Open **"2. Get Job Status"** request
2. Click **Send** (uses auto-saved job_id)
3. Keep clicking until status is "completed"

Response (in progress):
```json
{
  "status": "processing",
  "progress": {
    "descriptions_generated": 5,
    "total_videos": 10,
    "percent_complete": 50
  }
}
```

### 4. Preview Results 👀

**List all descriptions:**
```
GET /descriptions/{{novel_name}}
```

**Preview specific description:**
```
GET /descriptions/{{novel_name}}/{{video_name}}
```

### 5. Manage Prompts ⚙️

**View prompts:**
```
GET /admin/prompts
```

**Update a prompt:**
```
PATCH /admin/prompts/what_to_expect
```

## Features

### 🎯 Auto Job ID Capture

The "Generate Descriptions" requests include a test script that automatically saves the `job_id`:

```javascript
// Automatically runs after successful request
if (jsonData.job_id) {
    pm.collectionVariables.set("job_id", jsonData.job_id);
    console.log("✅ Job ID saved: " + jsonData.job_id);
}
```

This means:
- ✅ No manual copying of job_id
- ✅ "Get Job Status" works immediately
- ✅ Saved in collection variables for all requests

### 🔐 Collection-Level Authentication

Bearer token is configured at the collection level:
- ✅ All requests (except /health) automatically authenticated
- ✅ No need to add auth to each request
- ✅ Easy to change token in one place

### 📝 Rich Documentation

Every request includes:
- ✅ Description of what it does
- ✅ Request parameters explained
- ✅ Example responses
- ✅ Tips and best practices

### 🎨 Organized Folders

Requests are grouped by functionality:
- 🏥 Health Check
- 📝 Description Generation (numbered workflow)
- ⚙️ Admin - Prompt Management

## Testing Scenarios

### Scenario 1: First-Time Generation

1. **Health Check** → Verify service
2. **Generate Descriptions** → Start job
3. **Get Job Status** → Wait for completion
4. **List All Descriptions** → Verify count
5. **Preview Description** → Check quality

### Scenario 2: Update Prompts

1. **List All Prompts** → See current prompts
2. **Get Prompt - What to Expect** → View current
3. **Update Prompt - What to Expect** → Edit
4. **Generate Descriptions (Force)** → Regenerate with new prompt
5. **Preview Description** → Verify changes

### Scenario 3: Add New Videos

1. **List All Descriptions** → Check existing
2. **Generate Descriptions** (force=false) → Only creates missing
3. **Get Job Status** → Monitor
4. **List All Descriptions** → Verify new descriptions added

## Tips & Tricks

### 💡 Quick Environment Switch

**Local to Production:**
1. Collection → Variables → `base_url`
2. Change to `https://description-service.sevalla.app`
3. Save

**Production to Local:**
1. Collection → Variables → `base_url`
2. Change to `http://localhost:8082`
3. Save

### 💡 Monitor Console

Check the Postman console (bottom left) to see:
- Auto-saved job_id confirmations
- Request/response details
- Error messages

### 💡 Test Different Novels

1. Collection → Variables
2. Change `novel_name` to your test novel
3. Save and run requests

### 💡 Force Regeneration

Use **"Generate Descriptions (Force)"** when:
- You've updated prompts
- Previous generation failed partway
- You want to update existing descriptions

## Common Errors

### ❌ 401 Unauthorized
```json
{
  "success": false,
  "error": "Invalid API token"
}
```
**Fix:** Check `api_token` in collection variables

### ❌ 404 Job Not Found
```json
{
  "success": false,
  "error": "Job not found"
}
```
**Fix:** 
- Verify `job_id` is set in collection variables
- Generate descriptions first to get a valid job_id

### ❌ 400 Bad Request
```json
{
  "success": false,
  "error": "Missing required field: novel_name"
}
```
**Fix:** Check request body includes all required fields

### ❌ Connection Refused

**Fix:**
- Local: Ensure service is running on port 8082
- Production: Check service is deployed and URL is correct

## Advanced Usage

### Variable Scope

Variables in this collection:
- Stored at **collection level**
- Shared across all requests
- Persisted between sessions

### Test Scripts

The collection includes test scripts that:
- Auto-save job_id
- Log helpful messages to console
- Make testing seamless

### Custom Variables

Add your own variables:
1. Collection → Variables → Add
2. Name: `your_variable`
3. Use: `{{your_variable}}` in requests

## Testing Checklist

Use this checklist when testing:

- [ ] ✅ Health check returns 200
- [ ] 📝 Generate descriptions succeeds
- [ ] 🔄 Job_id auto-saved (check console)
- [ ] 📊 Job status shows progress
- [ ] 🎯 Job completes successfully
- [ ] 📋 List descriptions shows all videos
- [ ] 👁️ Preview shows full description
- [ ] 📚 List prompts shows 2 prompts
- [ ] ✏️ Get prompt returns full text
- [ ] 💾 Update prompt succeeds
- [ ] 🔁 Force regeneration works

## Support

### Debug Steps

If something doesn't work:

1. **Check Health**
   ```
   GET /health
   ```
   Should return 200

2. **Verify Variables**
   - Collection → Variables
   - Ensure `base_url` and `api_token` are correct

3. **Check Console**
   - View → Show Postman Console
   - Look for error messages

4. **Test Authentication**
   - Try any endpoint except /health
   - Should not return 401

## Next Steps

After testing the API:

1. **Frontend Integration**
   - Use the same endpoints
   - Implement polling for job status
   - Add preview UI

2. **Production Testing**
   - Switch to production environment
   - Test with real novels
   - Monitor for errors

3. **Prompt Optimization**
   - Test different prompt variations
   - Use force regeneration to see changes
   - Iterate based on results

---

**Happy Testing! 🚀**

For questions or issues, check the service logs and database state.
