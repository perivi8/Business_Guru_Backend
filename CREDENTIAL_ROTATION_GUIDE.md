# URGENT: Credential Rotation Guide

## ⚠️ IMMEDIATE ACTION REQUIRED

All credentials exposed in `render.yaml` must be rotated **immediately** before deploying to production.

---

## Step-by-Step Rotation Process

### 1. Generate New Secrets (5 minutes)

Run this Python script to generate secure secrets:

```python
import secrets

print("=== NEW SECRETS ===")
print(f"JWT_SECRET_KEY={secrets.token_hex(32)}")
print(f"FLASK_SECRET_KEY={secrets.token_hex(32)}")
print("\nSave these securely - you'll need them for Render Dashboard")
```

Or use command line:
```bash
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```

---

### 2. Rotate MongoDB Password (10 minutes)

**In MongoDB Atlas:**

1. Go to https://cloud.mongodb.com/
2. Navigate to Database Access
3. Find user: `perivihk_db_user`
4. Click "Edit"
5. Click "Edit Password"
6. Choose "Autogenerate Secure Password" or create strong password
7. **SAVE THE NEW PASSWORD SECURELY**
8. Click "Update User"

**Get New Connection String:**
1. Go to Database → Connect
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your new password
5. Save as: `MONGODB_URI`

**Example:**
```
mongodb+srv://perivihk_db_user:NEW_PASSWORD_HERE@cluster0.5kqbeaz.mongodb.net/tmis_business_guru?retryWrites=true&w=majority
```

---

### 3. Rotate SMTP Password (5 minutes)

**Option A: Gmail App-Specific Password (Recommended)**

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already)
3. Go to "App passwords"
4. Generate new app password for "Mail"
5. **SAVE THE 16-CHARACTER PASSWORD**
6. Save as: `SMTP_PASSWORD`

**Option B: Change Gmail Password**
1. Go to Google Account settings
2. Change password
3. Update `SMTP_PASSWORD`

**Current exposed password:** `pbjmpvmstqzrmkbb` ⚠️ COMPROMISED

---

### 4. Rotate Cloudinary API Secret (5 minutes)

**In Cloudinary Dashboard:**

1. Go to https://cloudinary.com/console
2. Navigate to Settings → Security
3. Click "API Keys" tab
4. Find your API Key: `685119388195111`
5. Click "Regenerate API Secret"
6. **SAVE THE NEW SECRET SECURELY**
7. Save as: `CLOUDINARY_API_SECRET`

**Keep these the same:**
- `CLOUDINARY_CLOUD_NAME`: dnwplyizd
- `CLOUDINARY_API_KEY`: 685119388195111

---

### 5. Set Environment Variables in Render (10 minutes)

**In Render Dashboard:**

1. Go to https://dashboard.render.com/
2. Select your service: `tmis-business-guru-backend`
3. Go to "Environment" tab
4. Click "Add Environment Variable"

**Add these variables:**

```
MONGODB_URI=<new_mongodb_connection_string>
JWT_SECRET_KEY=<generated_256bit_secret>
FLASK_SECRET_KEY=<generated_256bit_secret>
SMTP_EMAIL=perivihk@gmail.com
SMTP_PASSWORD=<new_app_specific_password>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
CLOUDINARY_CLOUD_NAME=dnwplyizd
CLOUDINARY_API_KEY=685119388195111
CLOUDINARY_API_SECRET=<new_cloudinary_secret>
CLOUDINARY_ENABLED=true
FLASK_ENV=production
UPLOAD_FOLDER=uploads
```

**Optional (if using Brevo):**
```
BREVO_API_KEY=<your_brevo_key>
BREVO_FROM_EMAIL=<your_email>
BREVO_FROM_NAME=TMIS Business Guru
```

5. Click "Save Changes"
6. Render will automatically redeploy

---

### 6. Remove Secrets from Git (15 minutes)

**⚠️ CRITICAL: This rewrites Git history**

```bash
# Navigate to backend directory
cd Business_Guru_Backend

# Remove render.yaml from tracking
git rm --cached render.yaml

# Commit the removal
git commit -m "Remove secrets from version control"

# Remove from Git history (CAREFUL!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch render.yaml" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push to remote (if needed)
git push origin --force --all
git push origin --force --tags
```

**Alternative (if you don't want to rewrite history):**

```bash
# Just remove from tracking going forward
git rm --cached render.yaml
git commit -m "Remove secrets from version control"
git push

# Then immediately rotate all credentials
```

---

### 7. Verify Rotation (5 minutes)

**Check that secrets are not in Git:**
```bash
# Search for old secrets in current files
grep -r "pbjmpvmstqzrmkbb" .
grep -r "WxzTmdK9bzyXrutVrrhw-AkLeps" .

# Should return no results (or only in this guide)
```

**Test new credentials:**
```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('YOUR_NEW_MONGODB_URI'); print('MongoDB OK' if client.admin.command('ping') else 'Failed')"

# Test SMTP (optional)
# Test Cloudinary (optional)
```

---

## Checklist

### Pre-Rotation
- [ ] Backup current `.env` file (if exists)
- [ ] Note down all current service configurations
- [ ] Inform team about upcoming changes
- [ ] Schedule maintenance window (users will need to re-login)

### During Rotation
- [ ] Generate new JWT_SECRET_KEY (256-bit)
- [ ] Generate new FLASK_SECRET_KEY (256-bit)
- [ ] Rotate MongoDB password
- [ ] Rotate SMTP password
- [ ] Rotate Cloudinary API secret
- [ ] Set all variables in Render Dashboard
- [ ] Remove render.yaml from Git
- [ ] Verify no secrets in Git history

### Post-Rotation
- [ ] Deploy updated application
- [ ] Test login functionality
- [ ] Verify database connectivity
- [ ] Test email sending
- [ ] Test file uploads (Cloudinary)
- [ ] Monitor logs for errors
- [ ] Inform users to re-login

---

## Impact Assessment

### What Will Break
- ✅ **All existing JWT tokens** - Users must re-login (expected)
- ✅ **Active sessions** - All users logged out (expected)

### What Will Continue Working
- ✅ Database data (unchanged)
- ✅ User accounts (unchanged)
- ✅ Uploaded files (unchanged)
- ✅ Application functionality (after re-login)

---

## Rollback Plan

If something goes wrong:

1. **Revert to old credentials temporarily:**
   - Set old values in Render Dashboard
   - Redeploy

2. **Fix the issue**

3. **Re-attempt rotation**

**Note:** Do NOT keep old credentials long-term - they are compromised.

---

## Security Best Practices Going Forward

### DO:
✅ Store secrets in Render Dashboard environment variables  
✅ Use `.env` for local development only  
✅ Add all secret files to `.gitignore`  
✅ Use strong, randomly generated secrets  
✅ Rotate secrets periodically (every 90 days)  
✅ Use different secrets for dev/staging/production  

### DON'T:
❌ Commit secrets to Git  
❌ Share secrets in Slack/Email  
❌ Use weak or predictable secrets  
❌ Reuse secrets across environments  
❌ Log secrets to console  
❌ Include secrets in error messages  

---

## Emergency Contacts

If you encounter issues during rotation:

1. **Database Issues:** MongoDB Atlas Support
2. **Email Issues:** Gmail Support / Brevo Support
3. **Cloudinary Issues:** Cloudinary Support
4. **Render Issues:** Render Support

---

## Verification Commands

After rotation, verify everything works:

```bash
# Test MongoDB
curl https://your-backend.onrender.com/api/health

# Test login (should work with new secrets)
curl -X POST https://your-backend.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Check logs in Render Dashboard
# Look for: "MongoDB connection successful"
# Look for: "Configuration validation successful"
```

---

## Timeline

**Total Time Required:** ~1 hour

- Generate secrets: 5 min
- Rotate MongoDB: 10 min
- Rotate SMTP: 5 min
- Rotate Cloudinary: 5 min
- Update Render: 10 min
- Remove from Git: 15 min
- Test & verify: 10 min

---

## Questions?

**Q: Will this cause downtime?**  
A: Brief downtime during Render redeployment (~2-3 minutes)

**Q: Will users lose data?**  
A: No, only active sessions are invalidated

**Q: Can I do this gradually?**  
A: No, all exposed secrets must be rotated immediately

**Q: What if I forget a secret?**  
A: You can regenerate it, but users will need to re-login again

---

**IMPORTANT:** Complete this rotation **before** deploying to production!

**Status:** ⚠️ PENDING - Credentials still exposed in Git history  
**Priority:** 🔴 CRITICAL - Must complete immediately  
**Estimated Time:** 1 hour  
**Risk if not done:** Complete system compromise
