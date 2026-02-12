# UI Hanging Debugging Toolkit - Complete Reference

## Overview

You have a complete debugging toolkit to diagnose why the UI hangs on query "high in the chart" while the API works correctly.

**Key Finding**: The API processes the query correctly in ~2.46 seconds, so the issue is in the Streamlit UI layer.

---

## Scripts Available

### 1. `scripts/debug_ui_hanging.py` - API Layer Testing
**What it does**: Tests the API directly to verify it works correctly

```bash
poetry run python scripts/debug_ui_hanging.py
```

**Tests**:
- ✅ API health check
- ✅ Streamlit UI accessibility
- ✅ Direct API calls with "high in the chart" query
- ✅ 5 query variations to identify patterns
- ✅ Timing information for each request
- ✅ Comprehensive error logging

**Expected Output**:
- API health: OK
- UI accessibility: OK
- All queries succeed in 2-5 seconds
- Detailed logs in `debug_ui_hanging.log`

**Use this when**: You want to verify the API is working

### 2. `scripts/monitor_streamlit_logs.py` - Streamlit Diagnostics
**What it does**: Provides debugging guidance and code suggestions

```bash
poetry run python scripts/monitor_streamlit_logs.py
```

**Provides**:
- ✅ Step-by-step debugging instructions
- ✅ Browser developer tools guidance
- ✅ Code modifications for detailed logging
- ✅ Common hanging causes and fixes
- ✅ Streamlit-specific debugging tips

**Use this when**: You need guidance on debugging Streamlit issues

### 3. `scripts/test_chat_service_directly.py` - Service Layer Testing
**What it does**: Tests the ChatService class (what Streamlit actually uses)

```bash
poetry run python scripts/test_chat_service_directly.py
```

**Tests**:
- ✅ ChatService initialization
- ✅ Direct service.chat() calls
- ✅ Response validation
- ✅ Timing breakdown (service time vs overhead)
- ✅ Detailed step-by-step execution

**Expected Output**:
- Service initializes OK
- service.chat() responds in 2-5 seconds
- Response structure is valid
- Overhead timing information

**Use this when**: You want to test Streamlit's chat service directly

---

## Quick Diagnostic Path

### Path 1: Is the API working? (1 minute)
```bash
poetry run python scripts/debug_ui_hanging.py
```
→ If API queries succeed, issue is in UI layer
→ If API queries fail/timeout, issue is in API layer

### Path 2: Does the service layer work? (1-2 minutes)
```bash
poetry run python scripts/test_chat_service_directly.py
```
→ If service.chat() succeeds, issue is in Streamlit rendering
→ If service.chat() hangs, issue is in service layer

### Path 3: Browser-level debugging (5 minutes)
1. Open http://localhost:8501
2. Press F12 (Developer Tools)
3. Go to "Network" tab
4. Submit "high in the chart" query
5. Look for POST request to `/api/v1/chat`
6. Check response (should be 200 with message)

### Path 4: Streamlit-level debugging (5-10 minutes)
1. Check browser Console tab (F12) for JavaScript errors
2. Check Streamlit terminal for Python exceptions
3. Add logging to `src/ui/app.py` (see monitor_streamlit_logs.py for code)
4. Re-run Streamlit and submit query again
5. Check logs to see where it hangs

---

## Documentation Files

### `DEBUG_UI_HANGING_GUIDE.md`
Comprehensive guide with:
- What to look for in logs
- Common causes and fixes
- Debugging workflow
- FAQ and troubleshooting
- Expected results and timings

### `DEBUG_SUMMARY.md`
Executive summary with:
- What was created
- Current findings
- How to use the debug tools
- Key files to monitor

### `DEBUGGING_TOOLKIT.md` (This file)
Complete reference with:
- All scripts and their usage
- Diagnostic paths
- Expected outputs
- Troubleshooting tips

---

## What to Look For

### If API Tests Pass ✅
API is working correctly. Issue is in one of these areas:
1. Streamlit rendering (UI not displaying response)
2. Streamlit state management (widget state not updating)
3. Browser-level issue (JavaScript error)
4. Network/latency (slow communication between UI and API)

### If Service Tests Pass ✅
Service layer is working. Issue is:
1. Streamlit rendering (UI not displaying response)
2. Streamlit state management (session state)
3. Specific to the "high in the chart" query handling

### If Both Pass ✅
Issue is definitely in Streamlit UI:
1. Check browser console (F12) for JavaScript errors
2. Check Streamlit terminal for Python exceptions
3. Check browser Network tab to see API response
4. Add logging to see execution flow

---

## Most Likely Causes (In Order)

1. **Streamlit State Management Issue** (40% probability)
   - `st.session_state` not updating correctly
   - Widget state conflict
   - Rerun loop issue

2. **Response Display Issue** (30% probability)
   - Response message component not rendering
   - Sources not displaying
   - Feedback buttons causing error

3. **Error Not Being Caught** (20% probability)
   - Exception in post-processing
   - Database logging failing
   - Conversation update failing

4. **Query-Specific Handling** (10% probability)
   - "high in the chart" needs special classification
   - Vector search response format issue
   - LLM returning unexpected format

---

## Step-by-Step Debugging Process

### Step 1: Verify API (2 min)
```bash
poetry run python scripts/debug_ui_hanging.py
```
✓ Confirms API works
✓ Gets baseline timing
✓ Identifies if issue is API or UI

### Step 2: Verify Service (2 min)
```bash
poetry run python scripts/test_chat_service_directly.py
```
✓ Tests service layer directly
✓ Identifies service issues
✓ Separates service from UI issues

### Step 3: Browser Developer Tools (5 min)
1. Open UI
2. Press F12
3. Go to Network tab
4. Submit "high in the chart"
5. Check if API request completes
6. Check response body

### Step 4: Add Logging (5 min)
Edit `src/ui/app.py` around line 334 (chat input section):
```python
if prompt := st.chat_input(f"Ask about {settings.app_name}..."):
    logger.info(f"[UI] Query submitted: '{prompt}'")
    # ... rest of code ...

    start_time = time.time()
    response = service.chat(request)
    elapsed = time.time() - start_time
    logger.info(f"[UI] service.chat() returned in {elapsed:.3f}s")
    logger.info(f"[UI] Response: {response.answer[:50]}...")
```

### Step 5: Reproduce and Check Logs
1. Restart Streamlit
2. Submit "high in the chart" query
3. Check Streamlit terminal for `[UI]` logs
4. See exactly where it hangs

---

## Debugging Checklist

- [ ] Run `debug_ui_hanging.py` - confirm API works
- [ ] Run `test_chat_service_directly.py` - confirm service works
- [ ] Check browser Network tab - confirm API returns 200
- [ ] Check browser Console tab - look for JavaScript errors
- [ ] Check Streamlit terminal - look for Python exceptions
- [ ] Add logging to app.py - trace execution flow
- [ ] Reproduce issue with logging - identify exact failure point
- [ ] Check response structure - is it valid JSON?
- [ ] Compare with working query - identify differences
- [ ] Check if it's query-specific or all queries hang

---

## Expected Timings

| Operation | Time | Status |
|-----------|------|--------|
| API health check | <100ms | Should be instant |
| Service initialization | 1-3s | Loads vectors |
| API chat call | 2-5s | Includes LLM call |
| Service.chat() call | 2-5s | Same as API |
| Streamlit rendering | <500ms | Should be fast |
| Database logging | <100ms | Should be instant |
| **Total UI response** | **3-6s** | Expected |

If actual time > 10s, something is hanging.

---

## Common Hanging Patterns

### Pattern 1: Infinite Rerun Loop
**Symptom**: UI constantly refreshes
**Fix**: Check for `st.rerun()` being called unexpectedly
**Location**: Check all `st.rerun()` calls in app.py

### Pattern 2: Missing Error Handling
**Symptom**: UI doesn't display error or response
**Fix**: Add try/except around API calls
**Location**: Line 377 in app.py (`service.chat()`)

### Pattern 3: Unhandled Exception
**Symptom**: No error shown, UI just hangs
**Fix**: Check browser console and Streamlit terminal
**Location**: Look for red errors

### Pattern 4: Response Format Issue
**Symptom**: API returns response but UI hangs
**Fix**: Check if response object is valid
**Location**: Check response structure validation

### Pattern 5: Database Blocking
**Symptom**: API works but service.chat() hangs
**Fix**: Add timeout to database operations
**Location**: Feedback service or conversation service

---

## Files to Check

| File | Purpose | What to Look For |
|------|---------|------------------|
| `src/ui/app.py` | Main UI | Chat input handling (line 334+) |
| `src/services/chat.py` | Chat service | service.chat() method |
| `src/api/routes/chat.py` | API endpoint | Response generation |
| `.streamlit/config.toml` | Streamlit config | Threading, file watching |
| Browser console (F12) | JavaScript errors | Error messages |
| Streamlit terminal | Python errors | Exception tracebacks |

---

## Success Indicators

You've fixed the issue when:
- ✅ Submit "high in the chart" query
- ✅ User message appears immediately
- ✅ "Searching..." spinner appears
- ✅ Response displays after 2-3 seconds
- ✅ No JavaScript errors in console
- ✅ No Python errors in terminal
- ✅ Feedback buttons appear
- ✅ Can submit feedback

---

## Getting Help

1. **Run all diagnostics**:
   ```bash
   poetry run python scripts/debug_ui_hanging.py
   poetry run python scripts/test_chat_service_directly.py
   ```

2. **Collect logs**:
   - `debug_ui_hanging.log` from script
   - Browser console errors (F12)
   - Streamlit terminal output

3. **Provide information**:
   - Are all diagnostics passing?
   - Which tests fail?
   - What errors appear?
   - Where does it hang?

4. **Share findings**:
   - Script output
   - Log files
   - Error messages
   - Expected vs actual behavior

---

## Summary

| Script | Time | What It Tests |
|--------|------|---------------|
| debug_ui_hanging.py | 2 min | API layer |
| test_chat_service_directly.py | 2 min | Service layer |
| Browser Network tab | 5 min | Network communication |
| Browser Console tab | 2 min | JavaScript errors |
| Streamlit terminal | 2 min | Python errors |
| **Total diagnosis** | **13 min** | Complete picture |

Once you've run these diagnostics, you'll know exactly where the issue is and what to fix.

---

## Key Points

✅ **API is working** (confirmed from logs)
❌ **UI is hanging** (but not crashing)
🔧 **Issue is in Streamlit layer** (rendering, state, or error handling)
📝 **Use diagnostics to find exact location** (then fix is easy)
⏱️ **Should take 13 minutes to diagnose** (then fix in 5-15 minutes)
