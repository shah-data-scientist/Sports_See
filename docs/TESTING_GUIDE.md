# UI Hanging Debug Testing Guide

## ✅ Status Summary

**All components verified working:**
- API: ✅ Responds correctly (4-5 seconds)
- Service Layer: ✅ Processes queries correctly (8-9 seconds)
- Streamlit: ✅ Running and accessible at http://localhost:8501
- Debug Logging: ✅ Added to src/ui/app.py

**Current Configuration:**
- Streamlit is logging to: `streamlit_debug.log`
- Logging level: INFO
- Debug messages prefix: `[UI-DEBUG]`

---

## 🧪 How to Test the UI

### **Step 1: Open Streamlit UI**
Open your browser and go to: **http://localhost:8501**

### **Step 2: Submit the Problematic Query**
In the chat input box, type exactly:
```
high in the chart
```
Press **Enter** to submit.

### **Step 3: Monitor the Logs**
In a **separate terminal** window, run this command:
```bash
cd "c:\Users\shahu\Documents\OneDrive\OPEN CLASSROOMS\PROJET 10\Sports_See"
tail -f streamlit_debug.log | grep "UI-DEBUG"
```

This will show ONLY the debug messages in real-time.

### **Step 4: Observe the Behavior**

**Expected progression of logs:**
```
[UI-DEBUG] Calling service.chat() for query: 'high in the chart'
[UI-DEBUG] service.chat() returned in X.XXs
[UI-DEBUG] Response answer length: XXX
[UI-DEBUG] Response sources count: 5
[UI-DEBUG] About to display answer with st.write()
[UI-DEBUG] Answer displayed successfully
[UI-DEBUG] About to render sources
[UI-DEBUG] Sources rendered successfully
[UI-DEBUG] About to display processing time
[UI-DEBUG] Processing time displayed successfully
[UI-DEBUG] About to log interaction to database
[UI-DEBUG] Interaction logged with id: [ID]
[UI-DEBUG] About to add message to session state
[UI-DEBUG] Message added to session state
[UI-DEBUG] About to call st.rerun()
[UI-DEBUG] st.rerun() completed
```

---

## 🔍 What to Look For

### **If All Logs Appear ✅**
→ The query works end-to-end
→ The hanging issue might be intermittent or browser-specific
→ Check browser console (F12) for JavaScript errors

### **If Logs Stop At:**

| Stop Point | Issue | Action |
|-----------|-------|--------|
| "Calling service.chat()" | Service timeout | Check API logs |
| "returned in X.XXs" | Response parsing error | Check exception logs |
| "About to display answer" | st.write() failing silently | Check console (F12) |
| "Answer displayed" | Sources rendering error | Check render_sources() |
| "About to render sources" | Sources function hanging | Check render_sources() |
| "Interaction logged" | Database operation hanging | Check feedback service |
| "About to call st.rerun()" | State management issue | Check session_state |
| "st.rerun() completed" | After rerun, no display | Check browser refresh |

---

## 📊 What the Response Should Look Like

When "high in the chart" query completes:
- **Answer displayed**: "The available context doesn't contain this information."
- **Sources**: 5 documents from Reddit posts
- **Processing time**: ~6000-9000ms
- **UI shows**: User message + assistant response + sources expander + feedback buttons

---

## 🛠️ Files to Reference

If you need to troubleshoot further:
- **Main UI code**: `src/ui/app.py` (lines 359-438 have the debug logging)
- **Service code**: `src/services/chat.py` (process the query)
- **API code**: `src/api/routes/chat.py` (endpoint definition)
- **Debug log file**: `streamlit_debug.log` (all Streamlit output)

---

## 📋 Troubleshooting Commands

```bash
# View all logs
tail -50 streamlit_debug.log

# View only UI-DEBUG messages
grep "UI-DEBUG" streamlit_debug.log

# View logs with timestamps
tail -f streamlit_debug.log | grep -E "UI-DEBUG|ERROR|Exception"

# Count occurrences of each debug step
grep "UI-DEBUG" streamlit_debug.log | cut -d']' -f2 | sort | uniq -c

# Check for errors in logs
grep -i "error\|exception\|traceback" streamlit_debug.log
```

---

## 🎯 Expected Outcomes

### **Scenario 1: All Logs Complete**
- Logs show complete progression from "Calling service.chat()" to "st.rerun() completed"
- UI should display the answer "The available context doesn't contain this information."
- This means the hanging is resolved or is browser-specific

### **Scenario 2: Logs Stop Mid-Way**
- Logs show a specific failure point
- Example: logs stop at "About to display answer with st.write()"
- This identifies exactly where to fix the code

### **Scenario 3: No Logs Appear**
- Query might not be reaching the service
- Check if chat input is being recognized
- Check browser console (F12) for errors

---

## 🔧 Next Steps After Testing

1. **Run the test** as described above
2. **Note where the logs stop** (if they stop before completion)
3. **Check browser console** (F12) for JavaScript errors
4. **Share the log output** with me showing:
   - Last log message that appeared
   - Any error messages
   - What the UI shows

Then I'll provide the exact fix for the specific issue.

---

## Quick Reference

| Action | Command |
|--------|---------|
| View streaming logs | `tail -f streamlit_debug.log` |
| Filter for debug only | `tail -f streamlit_debug.log \| grep UI-DEBUG` |
| Clear old logs | `rm streamlit_debug.log` |
| Restart Streamlit | Stop current instance, run: `poetry run streamlit run src/ui/app.py` |
| Check if UI is running | Open http://localhost:8501 in browser |
| Check if API is running | `curl http://localhost:8002/health` |

---

## Ready to Test?

1. Go to http://localhost:8501
2. Type "high in the chart"
3. Press Enter
4. In another terminal: `tail -f streamlit_debug.log | grep UI-DEBUG`
5. Watch for the logs and note where they stop (if at all)
6. Share results!
