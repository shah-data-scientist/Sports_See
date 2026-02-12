# UI Hanging Debug Guide

**Problem**: UI hangs on query "high in the chart" (but API responds correctly in ~2.68s when called directly)

**Status**: Narrowed down to Streamlit/UI layer issue, NOT API issue

---

## Quick Start

### Option 1: Test API Directly
```bash
poetry run python scripts/debug_ui_hanging.py
```

This will:
- ✅ Check API health
- ✅ Check Streamlit UI accessibility
- ✅ Test problematic query against API directly
- ✅ Log timing information
- ✅ Save detailed logs to `debug_ui_hanging.log`

**Expected Output**:
- "high in the chart" should succeed in ~2-3 seconds
- If it does, the issue is in the UI layer
- If it fails/times out, the issue is in the API

### Option 2: Monitor Streamlit Session
```bash
poetry run python scripts/monitor_streamlit_logs.py
```

This will:
- ✅ Test API endpoints directly
- ✅ Provide interactive debugging instructions
- ✅ Suggest code modifications for detailed logging

---

## What to Look For

### If API Tests Pass ✅
**Conclusion**: Issue is in Streamlit/UI layer

**Next Steps**:
1. Open browser dev tools (F12) while at http://localhost:8501
2. Go to "Network" tab
3. Submit "high in the chart" query
4. Watch the requests:
   - Should see POST to `/api/v1/chat`
   - API should respond with status 200
   - Response should contain the message

5. If API responds but UI still hangs:
   - Go to "Console" tab
   - Check for JavaScript errors (red ones)
   - Check browser console for any error messages

6. Check Streamlit terminal for Python errors:
   ```
   Exception in callback
   Error in async function
   Unhandled exception
   ```

### If API Tests Fail ❌
**Conclusion**: Issue is in API layer

**Next Steps**:
1. Check API logs for error details
2. Verify all services are running
3. Check if query classification is failing
4. Look for SQL/Vector search errors

---

## Common Hanging Causes

### 1. Infinite Rerun Loop
**Symptom**: UI refreshes over and over, query never completes
**Fix**: Check `src/ui/app.py` for widgets that trigger `st.rerun()` unexpectedly

### 2. Missing Error Handling
**Symptom**: API responds but Streamlit doesn't display result
**Fix**: Add try/except around API calls in `app.py`

### 3. Widget State Not Updating
**Symptom**: Input appears stuck or response doesn't display
**Fix**: Check `st.session_state` management in the chat section

### 4. Query Classification Issue
**Symptom**: "high in the chart" specifically causes problems
**Fix**: This query might need special handling - check:
   - Is it classified as SQL/VECTOR/HYBRID correctly?
   - Does it need fallback logic?

### 5. Response Display Issue
**Symptom**: API responds but message doesn't display in UI
**Fix**: Check Streamlit message component rendering in `app.py`

---

## How to Add Detailed Logging

Edit `src/ui/app.py` in the chat input section and add:

```python
import time

if user_query := st.chat_input("Ask about NBA..."):
    # Log submission
    logger.info(f"[UI] Query submitted: '{user_query}' at {time.time()}")

    with st.chat_message("user"):
        st.write(user_query)

    # Log API call
    api_start = time.time()
    logger.info(f"[UI] Sending to API at {api_start}")

    try:
        response = requests.post(
            "http://localhost:8002/api/v1/chat",
            json={
                "message": user_query,
                "conversation_id": None,
                "chat_type": "both"
            },
            timeout=30
        )

        api_elapsed = time.time() - api_start
        logger.info(f"[UI] API responded in {api_elapsed:.2f}s with status {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"[UI] Got message of length {len(data.get('message', ''))}")

            with st.chat_message("assistant"):
                st.write(data.get("message", "No response"))

    except requests.exceptions.Timeout:
        logger.error("[UI] API request TIMED OUT")
        st.error("Request timed out")
    except Exception as e:
        logger.error(f"[UI] ERROR: {e}", exc_info=True)
        st.error(f"Error: {e}")
```

Then run:
```bash
poetry run streamlit run src/ui/app.py
```

Watch the terminal for `[UI]` prefixed logs while submitting "high in the chart".

---

## Debugging Workflow

### Step 1: Verify API Works
```bash
# Terminal 1: Run diagnostics
poetry run python scripts/debug_ui_hanging.py
```

**Expected Result**: All queries complete successfully in ~2-3 seconds

### Step 2: Monitor Streamlit
```bash
# Terminal 2: Run Streamlit monitor
poetry run python scripts/monitor_streamlit_logs.py
```

**Expected Result**: Suggestions for debugging Streamlit issues

### Step 3: Add Detailed Logging
- Modify `src/ui/app.py` with the logging code above
- Restart Streamlit

### Step 4: Reproduce the Issue
- Submit "high in the chart" query
- Watch terminal logs to see exactly where it hangs

### Step 5: Analyze Logs
Check `debug_ui_hanging.log` and Streamlit terminal output to identify the exact point of failure.

---

## Key Files to Check

| File | Purpose | What to Look For |
|------|---------|------------------|
| `src/ui/app.py` | Streamlit UI | Chat input handling, message display, error handling |
| `src/services/chat.py` | Chat service | Query processing, error handling |
| `src/api/main.py` | API routes | Chat endpoint implementation |
| `src/tools/sql_tool.py` | SQL query tool | Query classification, SQL generation |
| `.streamlit/config.toml` | Streamlit config | File watcher, threading settings |

---

## What the Debug Scripts Do

### `debug_ui_hanging.py`
- Tests API health
- Tests UI accessibility
- Runs 5 variations of the problematic query
- Tests timing directly against API
- Logs everything to `debug_ui_hanging.log`

**Use when**: You want to verify if API is working correctly

### `monitor_streamlit_logs.py`
- Tests API endpoints
- Provides interactive debugging instructions
- Suggests code modifications
- Explains Streamlit-specific issues

**Use when**: You want guidance on Streamlit debugging

---

## FAQ

**Q: API works fine but UI still hangs?**
A: The issue is in Streamlit's rendering or state management. Check browser console for errors.

**Q: What if only "high in the chart" hangs, other queries work?**
A: This query might need special classification or error handling. Compare code paths for working vs non-working queries.

**Q: How long should the query take?**
A: API should respond in 2-5 seconds. If UI hangs longer than 10 seconds, something is wrong in the UI layer.

**Q: What if all queries hang?**
A: API might be down, or there's a network issue between UI and API. Start with `poetry run python scripts/debug_ui_hanging.py` to check.

---

## Commands to Run

```bash
# Check API directly
poetry run python scripts/debug_ui_hanging.py

# Monitor Streamlit
poetry run python scripts/monitor_streamlit_logs.py

# Start API
poetry run uvicorn src.api.main:app --reload --port 8002

# Start UI
poetry run streamlit run src/ui/app.py

# Check logs while running
tail -f debug_ui_hanging.log
```

---

## Expected Results

### Successful API Test
```
→ POST http://localhost:8002/api/v1/chat
← POST http://localhost:8002/api/v1/chat | Status: 200 | Time: 2.345s
✅ Query succeeded in 2.345s
   Response type: vector
   Message length: 256
   Has sources: True
```

### UI Should Display
- User message appears immediately
- "Assistant is thinking..." spinner shows
- Response appears after API responds
- Sources and feedback buttons appear

---

## Still Having Issues?

1. Run the debug scripts and share the output
2. Share the `debug_ui_hanging.log` file
3. Check browser console (F12) for errors
4. Check Streamlit terminal for Python exceptions
5. Provide the exact query that's hanging
6. Describe what happens (hangs? shows error? etc.)

**Remember**: The issue is most likely in the UI layer since the API responds correctly.
