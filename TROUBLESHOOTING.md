# Troubleshooting Guide

## CORS 307 Redirect Error on Submissions Detail

**Date:** 2026-08-13
**Author:** Frolov Artem (f84271284)

### Problem

When clicking "View" on a submission in the Submissions page, the modal showed:
- `Submission #undefined — undefined`
- `Invalid Date`
- Console error: `Failed to load module script: Expected a JavaScript-or-Wasm module script but the server responded with a MIME type of "text/html"`

The network tab showed:
1. `GET /api/submissions/2/` → **307 Temporary Redirect**
2. `GET /api/v1/submissions/2` → **200 OK** (but wrong URL!)

### Root Cause

Two issues combined:

1. **Trailing slash in frontend API call**: The frontend was calling `/api/submissions/2/` (with trailing slash), but FastAPI expects `/api/submissions/2` (without trailing slash). FastAPI responded with a **307 Redirect** to the correct URL.

2. **Lost port in redirect URL**: Nginx was using `proxy_set_header Host $host;` which strips the port. FastAPI used this to build the redirect URL, resulting in `http://localhost/api/v1/submissions/2` (missing port 3001). The browser then tried to fetch from port 80, which served HTML instead of JSON.

### Solution

**1. Remove trailing slash in frontend** (`frontend/src/api/workflows.ts`):

```typescript
// BEFORE
submissionApi.get<SubmissionDetail>(`${id}/`),

// AFTER
submissionApi.get<SubmissionDetail>(`${id}`),
```

**2. Fix nginx Host header** (`frontend/nginx.conf`):

```nginx
# Workflow Service - Submissions
location /api/submissions/ {
    proxy_pass http://workflow-service:8000/api/v1/submissions/;
    proxy_redirect default;
    
    # BEFORE: proxy_set_header Host $host;
    # AFTER:
    proxy_set_header Host $http_host;
    
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $http_host;
    proxy_set_header X-Forwarded-Port $server_port;
    
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, PATCH, DELETE' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    if ($request_method = 'OPTIONS') { return 204; }
}
```

### Key Differences

| Header | `$host` | `$http_host` |
|--------|---------|--------------|
| Input: `Host: localhost:3001` | `localhost` | `localhost:3001` |
| Result | Port is lost | Port is preserved |

### Build & Deploy Steps

Due to PowerShell execution policy restrictions, use `cmd /c` for npm commands:

```powershell
# 1. Build frontend
cmd /c "npm run build"

# 2. Rebuild Docker image
cmd /c "docker compose -f docker-compose.yml build frontend"

# 3. Restart container
cmd /c "docker compose -f docker-compose.yml up -d frontend"
```

### Verification

After fix, the network tab should show:
- `GET /api/submissions/2` → **200 OK** (no redirect!)

The modal should display:
- Correct submission ID and title
- Valid dates (not "Invalid Date")
- All fields populated correctly

### Related Files

- `frontend/src/api/workflows.ts` — API client
- `frontend/nginx.conf` — Nginx proxy configuration
- `services/workflow-service/app/main.py` — FastAPI application
