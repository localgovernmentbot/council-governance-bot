# Scheduler Freshness Window Fix - Deployment Guide

## Summary of Changes

**File Modified:** `src/posting/scheduler.py`

**Changes Made:**
- `FRESH_MINUTES_LAST_DAYS`: 7 → 14 days (past minutes window)
- `FRESH_AGENDAS_LAST_DAYS`: 7 → 14 days (past agendas window)
- `FRESH_AGENDAS_NEXT_DAYS`: 10 → 14 days (future agendas window)

**Rationale:**
Victorian councils typically meet fortnightly or monthly. The 7-day window was too restrictive and filtered out recent documents that should be posted. The new 14-day window aligns with actual council meeting schedules.

## Testing

### Option 1: Automated Test Script
```bash
chmod +x test_fix.sh
./test_fix.sh
```

### Option 2: Manual Test
```bash
python3 test_scheduler_fix.py
```

### Option 3: Direct Scheduler Test
```bash
python3 scripts/run_scheduler.py --results fresh_results.json
```

**Expected Result:** Should now show 9 documents in the schedule (from fresh_results.json) instead of 0.

## Deployment

### Option 1: Automated Deployment
```bash
chmod +x deploy_fix.sh
./deploy_fix.sh
```
This will:
1. Show the changes
2. Ask for confirmation
3. Commit with a detailed message
4. Push to GitHub

### Option 2: Manual Deployment
```bash
# Review changes
git diff src/posting/scheduler.py

# Stage changes
git add src/posting/scheduler.py test_scheduler_fix.py

# Commit
git commit -m "Fix: Increase scheduler freshness window from 7 to 14 days"

# Push
git push
```

## Verification

After deployment, verify the fix is working:

1. **Check the documents are now picked up:**
   ```bash
   python3 scripts/run_scheduler.py --results fresh_results.json
   ```
   Should show 9 documents in the preview schedule.

2. **Test with a small live run (optional):**
   ```bash
   python3 scripts/run_scheduler.py --results fresh_results.json --live --max-posts 1
   ```
   This will post 1 document to BlueSky as a test.

3. **Monitor the GitHub Actions workflow:**
   - The automated posting workflow should now pick up and post these documents
   - Check `.github/workflows/all_councils.yml`

## Environment Variable Override

If you need to adjust the freshness window without changing code:

```bash
# Set environment variables before running
export FRESH_MINUTES_LAST_DAYS=21
export FRESH_AGENDAS_LAST_DAYS=21
export FRESH_AGENDAS_NEXT_DAYS=21

# Then run scheduler
python3 scripts/run_scheduler.py --results fresh_results.json
```

## Rollback Plan

If issues arise, rollback is simple:

```bash
# Revert the commit
git revert HEAD

# Or manually change back in scheduler.py
# Change the values from 14 back to 7 (and 10 for NEXT_DAYS)
```

## Files Changed

- `src/posting/scheduler.py` - Core fix
- `test_scheduler_fix.py` - Test script (new)
- `deploy_fix.sh` - Deployment script (new)
- `test_fix.sh` - Quick test script (new)
- `DEPLOYMENT_GUIDE.md` - This file (new)

## Expected Impact

**Before Fix:**
- Documents 7-14 days old: Filtered out ❌
- Posting queue: Empty or minimal
- Bot activity: Low or none

**After Fix:**
- Documents 7-14 days old: Included ✅
- Posting queue: 9 documents from 5 councils
- Bot activity: Regular posts from recent council meetings

## Next Steps

1. Test the fix locally
2. Deploy to GitHub
3. Monitor the next automated run
4. Confirm posts appear on BlueSky
5. Adjust windows further if needed (via environment variables)

---

**Date:** 2025-10-01
**Fixed by:** Claude & Jonathon
**Issue:** Documents outside 7-day window weren't being posted despite being recent
**Solution:** Increased freshness window to 14 days to match council meeting schedules
