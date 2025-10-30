# Render Deployment Setup Instructions

## Step 1: Replace render.yaml

**IMPORTANT:** The old `render.yaml` has hardcoded secrets and must be replaced.

```bash
# Backup old file (if needed)
cp render.yaml render.yaml.backup

# Replace with secure version
cp render_secure.yaml render.yaml

# Or delete old and rename
rm render.yaml
mv render_secure.yaml render.yaml
```

---

## Step 2: Set Environment Variables in Render Dashboard

**Go to:** https://dashboard.render.com/ → Your Service → Environment

### Required Variables (Set Manually)

#### 1. Database
```
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/tmis_business_guru?retryWrites=true&w=majority
```
**Get from:** MongoDB Atlas → Connect → Connect your application

#### 2. Security Keys
```
JWT_SECRET_KEY=<generate-new-256bit-secret>
FLASK_SECRET_KEY=<generate-new-256bit-secret>
```

**Generate with:**
```python
import secrets
print(f"JWT_SECRET_KEY={secrets.token_hex(32)}")
print(f"FLASK_SECRET_KEY={secrets.token_hex(32)}")
```

#### 3. Email (SMTP)
```
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=<app-specific-password>
```
**Get app password:** https://myaccount.google.com/apppasswords

#### 4. Cloudinary
```
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```
**Get from:** https://cloudinary.com/console → Settings → Security

### Optional Variables

#### 5. Brevo (if using)
```
BREVO_API_KEY=your-brevo-key
BREVO_FROM_EMAIL=your-email@domain.com
```

#### 6. Green API WhatsApp (if using)
```
GREENAPI_INSTANCE_ID=your-instance-id
GREENAPI_TOKEN=your-token
```

#### 7. Gemini AI (if using)
```
GEMINI_API_KEY=your-gemini-key
```

---

## Step 3: Remove Old render.yaml from Git

```bash
# Remove from Git tracking
git rm --cached render.yaml

# Commit the change
git commit -m "Remove hardcoded secrets from render.yaml"

# Push to remote
git push origin main
```

---

## Step 4: Deploy to Render

1. **Push your code:**
   ```bash
   git add .
   git commit -m "Update to secure render.yaml"
   git push origin main
   ```

2. **Render will automatically deploy** when it detects the push

3. **Check deployment logs** in Render Dashboard

---

## Step 5: Verify Deployment

### Check Health Endpoint
```bash
curl https://your-app.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "security_features": [
    "rate_limiting",
    "account_lockout",
    "input_validation",
    "file_security",
    "csrf_protection",
    "security_headers"
  ]
}
```

### Test Login
```bash
curl -X POST https://your-app.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'
```

---

## Troubleshooting

### Issue: "Configuration validation failed"
**Solution:** Check that all required environment variables are set in Render Dashboard

### Issue: "MongoDB connection failed"
**Solution:** 
1. Check MONGODB_URI is correct
2. Verify IP whitelist in MongoDB Atlas (add 0.0.0.0/0 for Render)
3. Check database user has correct permissions

### Issue: "JWT_SECRET_KEY environment variable is required"
**Solution:** Set JWT_SECRET_KEY in Render Dashboard environment variables

---

## Security Checklist

Before going live:

- [ ] All secrets set in Render Dashboard (not in code)
- [ ] Old render.yaml removed from Git
- [ ] New render.yaml has no hardcoded secrets
- [ ] MongoDB password changed (if old one was exposed)
- [ ] JWT secret is new 256-bit random value
- [ ] SMTP password is app-specific password
- [ ] Cloudinary API secret regenerated (if old one was exposed)
- [ ] Test deployment works
- [ ] Health endpoint returns 200
- [ ] Login works with new credentials

---

## What's Different in Secure render.yaml?

### Before (INSECURE):
```yaml
- key: JWT_SECRET_KEY
  value: tmis-business-guru-secret-key-2024  # ❌ EXPOSED
```

### After (SECURE):
```yaml
- key: JWT_SECRET_KEY
  sync: false  # ✅ Set in Dashboard only
```

**Key Changes:**
- `sync: false` means value must be set manually in Dashboard
- No hardcoded secrets in the file
- Safe to commit to Git
- Each environment can have different values

---

## Quick Reference

### Generate New Secrets
```python
import secrets

# JWT Secret (256-bit)
print(f"JWT_SECRET_KEY={secrets.token_hex(32)}")

# Flask Secret (256-bit)
print(f"FLASK_SECRET_KEY={secrets.token_hex(32)}")
```

### Render Dashboard Path
```
Dashboard → Your Service → Environment → Environment Variables → Add Environment Variable
```

### MongoDB Atlas Connection String Format
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

---

## Support

- **Render Docs:** https://render.com/docs/environment-variables
- **MongoDB Atlas:** https://www.mongodb.com/docs/atlas/
- **Gmail App Passwords:** https://support.google.com/accounts/answer/185833

---

**Status:** ✅ Ready to deploy securely once environment variables are set in Render Dashboard
