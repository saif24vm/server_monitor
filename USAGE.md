
# Usage Guide

This document explains how to run the **Server Monitor** application locally and inside a Docker container.  
It also provides basic operational guidelines for container management and logging.

---

## Prerequisites

### Local Execution
- Python **3.12+**
- Google Chrome or Chromium installed
- Virtual environment support
- Properly configured `.env` file

### Docker Execution
- Docker Engine **20.10+**
- `.env` file present in project root  
  (Docker `.env` rules apply: no quotes, no inline comments)

---

## Environment Variables

All configuration is provided via a `.env` file.

**Important rules for Docker `.env`:**
- Use only `KEY=value`
- No quotes
- No inline comments

### Example `.env`

```bash
BASE_URL=https://vmedd-portal.de

EMAIL_PAUSE=1
MISMATCH_THRESHOLD=10
RECOVERY_THRESHOLD=10

EMAIL_SENDER=alerts@example.com
EMAIL_PASSWORD=secret
EMAIL_RECIPIENTS=ops@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=465 
```

```bash
docker rm -f server-monitor || true
docker rmi server-monitor || true
docker build --no-cache -t server-monitor .
docker run -d \
  --name server-monitor \
  --restart unless-stopped \
  --env-file .env \
  server-monitor

docker logs -f server-monitor

```