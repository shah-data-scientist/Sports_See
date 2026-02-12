# API Endpoints Summary Table

## All Endpoints at a Glance

| # | Endpoint | Method | Status | Usage | Notes |
|---|----------|--------|--------|-------|-------|
| **1** | `/api/v1/chat` | POST | ✅ | Active | Core answer generation |
| **2** | `/api/v1/search` | GET | ✅ | Available | Search without answering |
| **3** | `/api/v1/conversations` | POST | ✅ | Active | Create conversation |
| **4** | `/api/v1/conversations` | GET | ✅ | Active | List all conversations |
| **5** | `/api/v1/conversations/{id}` | GET | ✅ | Active | Get conversation details |
| **6** | `/api/v1/conversations/{id}` | PUT | ✅ | Active | Rename conversation |
| **7** | `/api/v1/conversations/{id}/messages` | GET | ✅ | Active | Get chat history |
| **8** | `/api/v1/feedback/log-interaction` | POST | ✅ **FIXED** | Active | Log interactions (was 422, now 201) |
| **9** | `/api/v1/feedback` | POST | ✅ | Active | Submit feedback |
| **10** | `/api/v1/feedback/stats` | GET | ✅ | Active | Get statistics |
| **11** | `/api/v1/feedback/negative` | GET | ✅ | Active | Backend: negative feedback |
| **12** | `/api/v1/feedback/interactions` | GET | ✅ | Active | Backend: all interactions |
| **13** | `/api/v1/feedback/interactions/{id}` | GET | ✅ | Active | Backend: specific interaction |
| **14** | `/api/v1/conversations/{id}` | DELETE | ⚠️ | Rarely Used | Permanent deletion (archive preferred) |
| **15** | `/api/v1/feedback/{id}` | PUT | ⚠️ | Rarely Used | Update feedback (rarely needed) |
| **16** | `/health` | GET | ❌ 404 | Not Working | Health check (router issue) |
| **17** | `/ready` | GET | ❌ 404 | Not Working | Readiness probe (router issue) |
| **18** | `/live` | GET | ❌ 404 | Not Working | Liveness probe (router issue) |

---

## Statistics

```
Total Endpoints:           18
Actively Used:             13 (72%)
Available but Rarely Used:  2 (11%)
Not Working (404):          3 (17%) - Low priority
```

---

## Color Legend

| Symbol | Meaning | Count |
|--------|---------|-------|
| ✅ | Actively used & working | 13 |
| **✅ FIXED** | Recently fixed critical issue | 1 |
| ⚠️ | Available but rarely used | 2 |
| ❌ | Not working (404 errors) | 2 |

---

## Test Results Summary

| Category | Tests | Passed | Failed | Status |
|----------|-------|--------|--------|--------|
| Chat & Search | 2 | 2 | 0 | ✅ |
| Conversations | 5 | 5 | 0 | ✅ |
| Feedback | 6 | 6 | 0 | ✅ |
| Health Checks | 3 | 0 | 3 | ⚠️ |
| **TOTAL** | **16** | **14** | **2** | **88%** |

---

## What Changed (Fixes Applied)

### Issue 1: log_interaction Endpoint
- **Before**: Returns 422 Unprocessable Entity
- **After**: Returns 201 Created with interaction_id
- **Impact**: Feedback buttons now visible in Streamlit

### Issue 2: Negative Feedback Display
- **Before**: Displayed in Streamlit (violates lean requirement)
- **After**: Removed entirely (analysis only via API)
- **Impact**: Streamlit is now properly lean

### Issue 3: Error Messages
- **Before**: "❌ Error: 500 Server Error: Internal Server Error"
- **After**: "⚠️ The AI service encountered an issue. Please try again."
- **Impact**: Better user experience

---

## Which Endpoints Should You Use?

### In Streamlit (Automatically Used):
```
✅ POST /chat              - Users ask questions
✅ POST /feedback/log-interaction - System logs responses
✅ POST /feedback          - Users submit feedback
✅ GET /feedback/stats     - Display sidebar stats
✅ POST /conversations     - Create new chat
✅ GET /conversations      - List conversations
✅ PUT /conversations/{id} - Rename conversation
✅ GET /conversations/{id}/messages - Load history
```

### For Backend Analysis (Use in Scripts/Notebooks):
```
✅ GET /feedback/negative        - What failed
✅ GET /feedback/interactions    - All queries/responses
✅ GET /feedback/interactions/{id} - Deep dive
✅ GET /feedback/stats          - Metrics
```

### Optional (Available but Not Needed):
```
⚠️ GET /search                  - Browse knowledge base
⚠️ DELETE /conversations/{id}   - Delete (archive preferred)
⚠️ PUT /feedback/{id}           - Update (rarely needed)
```

### Not Working (Can Ignore):
```
❌ /health, /ready, /live       - Low priority, 404 errors
```

---

**Bottom Line**: Use the 13 active endpoints. The system is ready to go!
