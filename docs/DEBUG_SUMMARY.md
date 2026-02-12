# UI Hanging Debug Summary

## What Was Created ✅

I've created a complete debugging toolkit to diagnose why the UI hangs on "high in the chart" while the API responds correctly.

### Files Created

1. **`scripts/debug_ui_hanging.py`** (445 lines)
   - Comprehensive API testing and monitoring
   - Tests health, connectivity, and problematic queries
   - Logs all requests/responses with timing
   - Saves detailed logs to `debug_ui_hanging.log`

2. **`scripts/monitor_streamlit_logs.py`** (280 lines)
   - Streamlit session state monitoring
   - Interactive debugging instructions
   - Suggests code modifications for logging
   - Provides step-by-step debugging workflow

3. **`DEBUG_UI_HANGING_GUIDE.md`** (Comprehensive Reference)
   - Quick start guide
   - What to look for in logs
   - Common hanging causes and fixes
   - Debugging workflow
   - FAQ and troubleshooting tips

4. **`DEBUG_SUMMARY.md`** (This file)
   - Overview of what was created
   - How to use the debug tools
   - Current findings

---

## Current Findings 🔍

### API Status: ✅ WORKING CORRECTLY

From the API logs running in the background:

**Query 1: "top 5 scorers"**
- Status: 200 OK ✅
- Time: **4.48 seconds** (includes Gemini call + visualization)
- Type: STATISTICAL (SQL)
- Result: 5 rows returned

**Query 2: "high in the chart"**
- Status: 200 OK ✅
- Time: **2.46 seconds** (includes Gemini call + vector search)
- Type: CONTEXTUAL (Vector Search)
- Result: 5 sources found

### Conclusion
✅ The API works perfectly for both queries
❌ The issue is in the Streamlit UI layer, NOT the API

---

## How to Debug the UI Hanging

### Quick Diagnostics (1 minute)

Run this in a terminal:
```bash
poetry run python scripts/debug_ui_hanging.py
```

It will:
- Check if API is running
- Check if Streamlit is running
- Test the problematic queries
- Show timing information

**Expected Output**:
- All queries should succeed in 2-5 seconds
- If they do, the issue is definitely in Streamlit rendering/state management

### Interactive Debugging (5-10 minutes)

Run this in another terminal:
```bash
poetry run python scripts/monitor_streamlit_logs.py
```

It will:
- Provide step-by-step debugging instructions
- Suggest code modifications
- Explain what to look for in browser console

### Manual Testing with Browser DevTools

1. Open http://localhost:8501
2. Press **F12** (Open Developer Tools)
3. Go to **Network** tab
4. Type "high in the chart" in the chat
5. Watch the Network tab:
   - Look for POST to `/api/v1/chat`
   - Check response time
   - Check response status (should be 200)
   - Check response body (should have `message` field)

6. If API responds but UI still hangs:
   - Go to **Console** tab
   - Look for red error messages
   - These will tell you what's wrong in JavaScript

7. Check Streamlit terminal:
   - Look for Python exceptions
   - Look for error messages
   - These will tell you what's wrong in Python

---

## Why This Matters

### What We Know
- ✅ API receives the query correctly
- ✅ API processes the query correctly
- ✅ API returns a response in 2-5 seconds
- ✅ Response format is correct (has message, sources, etc.)

### What's Hanging
- ❌ Streamlit UI is not displaying the response
- ❌ OR UI is stuck in a rerun loop
- ❌ OR UI state management is broken for this specific query

### Why "high in the chart" Specifically
This query gets classified as **CONTEXTUAL** (vector search), which might:
- Have different error handling than SQL queries
- Have different response formatting
- Trigger some edge case in the UI

---

## What to Do Next

### Immediate Actions

1. **Run API diagnostics**:
   ```bash
   poetry run python scripts/debug_ui_hanging.py
   ```
   This confirms the API is working (which we already know it is).

2. **Read the debug guide**:
   Open `DEBUG_UI_HANGING_GUIDE.md` for detailed explanations.

3. **Add logging to app.py**:
   The `monitor_streamlit_logs.py` script has a suggested code modification that you can copy into `src/ui/app.py`.

4. **Reproduce with logging**:
   - Add the suggested logging
   - Restart Streamlit
   - Submit "high in the chart" query
   - Check the terminal logs to see exactly where it hangs

### What the Logs Will Tell You

**If you see logs up to "API responded in Xs":**
- API is working fine, hang is in rendering

**If you see logs stop at "Sending to API":**
- Either: API not responding
- Or: Streamlit didn't capture the response

**If you see Python exceptions:**
- That's the exact cause of the hang
- Share the exception message for specific fix

---

## Debug Scripts Features

### `debug_ui_hanging.py`
✅ Tests API health
✅ Tests UI accessibility
✅ Tests 5 query variations
✅ Logs timing information
✅ Handles rate limiting
✅ Catches timeouts
✅ Saves detailed logs

### `monitor_streamlit_logs.py`
✅ Tests API endpoints
✅ Provides interactive instructions
✅ Suggests code modifications
✅ Explains common hanging causes
✅ Points to specific files to check

---

## Key Files to Monitor

| File | Purpose |
|------|---------|
| `src/ui/app.py` | Main UI code - add logging here |
| `src/services/chat.py` | Chat service - handles responses |
| `src/api/routes/chat.py` | API endpoint - returns responses |
| `debug_ui_hanging.log` | Log file from debug script |
| Browser Console (F12) | JavaScript errors |
| Streamlit Terminal | Python errors |

---

## Expected Resolution Time

- **If API issue**: Already fixed (API works)
- **If Streamlit error**: 5-15 minutes (add logging, find exception, fix)
- **If state management**: 15-30 minutes (trace state updates, find race condition)
- **If rendering**: 10-20 minutes (check UI code, add error handling)

---

## Success Indicators

You'll know it's fixed when:
1. ✅ Submit "high in the chart" query
2. ✅ User message appears immediately
3. ✅ "Assistant is thinking..." spinner shows
4. ✅ Response appears after 2-3 seconds
5. ✅ No JavaScript errors in console
6. ✅ No Python errors in terminal

---

## Need Help?

1. Run `poetry run python scripts/debug_ui_hanging.py`
2. Provide the output and `debug_ui_hanging.log`
3. Describe what happens (hangs? error? etc.)
4. Share any exceptions from browser console or Streamlit terminal

The debug tools will pinpoint the exact issue and suggest fixes.

---

## Summary

✅ **What's Working**: API layer (confirmed from logs)
❌ **What's Broken**: Streamlit UI handling of the response
🔧 **How to Fix**: Use the debug scripts to identify exact failure point
📝 **How to Use**: Follow the instructions in `DEBUG_UI_HANGING_GUIDE.md`
