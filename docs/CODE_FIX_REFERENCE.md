# Code Fix Reference - UI Hanging Resolution

**File**: `src/ui/app.py`
**Lines**: 405-410
**Change Type**: Parameter removal (bug fix)
**Status**: ✅ Applied

---

## The Exact Change

### ❌ BEFORE (INCORRECT - Causes Hanging)

```python
# Lines 402-411 in src/ui/app.py

                    # Log interaction to database
                    logger.info(f"[UI-DEBUG] About to log interaction to database")
                    source_names = [s.source for s in response.sources] if response.sources else []
                    interaction = feedback_service.log_interaction(
                        query=prompt,
                        response=response.answer,
                        sources=source_names,
                        processing_time_ms=int(response.processing_time_ms),
                        conversation_id=st.session_state.current_conversation_id,    # ❌ INVALID
                        turn_number=st.session_state.turn_number,                     # ❌ INVALID
                    )
                    logger.info(f"[UI-DEBUG] Interaction logged with id: {interaction.id}")
```

**Problem**:
- Passes `conversation_id` parameter ❌ (not in method signature)
- Passes `turn_number` parameter ❌ (not in method signature)
- Results in `TypeError: unexpected keyword argument`
- Causes UI to hang because error occurs after response display

---

### ✅ AFTER (CORRECT - Works)

```python
# Lines 402-411 in src/ui/app.py

                    # Log interaction to database
                    logger.info(f"[UI-DEBUG] About to log interaction to database")
                    source_names = [s.source for s in response.sources] if response.sources else []
                    interaction = feedback_service.log_interaction(
                        query=prompt,
                        response=response.answer,
                        sources=source_names,
                        processing_time_ms=int(response.processing_time_ms),
                    )
                    logger.info(f"[UI-DEBUG] Interaction logged with id: {interaction.id}")
```

**Solution**:
- ✅ Removed invalid `conversation_id` parameter
- ✅ Removed invalid `turn_number` parameter
- ✅ Kept all 4 valid parameters
- ✅ No TypeError, database logging works correctly

---

## Why This Matters

### The Method Signature

**File**: `src/services/feedback.py` (lines 36-42)

```python
def log_interaction(
    self,
    query: str,
    response: str,
    sources: list[str],
    processing_time_ms: int,
) -> Interaction:
    """Log a chat interaction to the database."""
```

**The method ONLY accepts these 4 parameters:**
1. ✅ `query` — user's question
2. ✅ `response` — assistant's answer
3. ✅ `sources` — list of source document names
4. ✅ `processing_time_ms` — time to generate response

**It DOES NOT accept:**
- ❌ `conversation_id`
- ❌ `turn_number`

---

## What Parameters Are Being Passed

### ✅ Valid Parameters (All 4 Present)

| Parameter | Value | Source |
|-----------|-------|--------|
| `query` | `prompt` | User's input query |
| `response` | `response.answer` | AI assistant's response |
| `sources` | `source_names` | List of document source names |
| `processing_time_ms` | `int(response.processing_time_ms)` | API processing time in milliseconds |

All valid parameters are still being passed. Nothing important is lost.

---

## Impact of the Fix

### Before Fix (Broken)
```
User Query
  ↓
Service generates response ✅
  ↓
UI displays response ✅
  ↓
Log interaction to database ❌ FAILS
  └─ TypeError: unexpected keyword argument 'conversation_id'
  └─ TypeError: unexpected keyword argument 'turn_number'
  └─ Script stalls, UI appears frozen/hanging
```

### After Fix (Working)
```
User Query
  ↓
Service generates response ✅
  ↓
UI displays response ✅
  ↓
Log interaction to database ✅ SUCCEEDS
  └─ All 4 valid parameters passed
  └─ Interaction recorded in database
  └─ Feedback buttons render normally
  └─ UI responsive and ready for next query
```

---

## Verification

### How to Verify the Fix is Applied

1. **Open the file**:
   ```bash
   src/ui/app.py
   ```

2. **Navigate to lines 405-410**

3. **Check the method call**:
   ```python
   interaction = feedback_service.log_interaction(
       query=prompt,
       response=response.answer,
       sources=source_names,
       processing_time_ms=int(response.processing_time_ms),
   )
   ```

4. **Verify**:
   - ✅ No `conversation_id=...` parameter
   - ✅ No `turn_number=...` parameter
   - ✅ Exactly 4 parameters passed
   - ✅ All parameters have correct names and values

### Expected Result
If the fix is properly applied, the call should have **exactly 4 parameters** and the UI should respond normally to queries.

---

## Related Code

### Where conversation_id and turn_number are Used Correctly

These variables are still tracked in the UI but used for different purposes:

**In the main flow** (src/ui/app.py):
```python
# Lines 362-367: Auto-create conversation
if st.session_state.current_conversation_id is None:
    new_conv = conversation_service.start_conversation()
    st.session_state.current_conversation_id = new_conv.id
    st.session_state.turn_number = 1
    logger.info(f"Created new conversation: {new_conv.id}")

# Lines 369-376: Pass conversation context to service
request = ChatRequest(
    query=prompt,
    k=settings.search_k,
    include_sources=True,
    conversation_id=st.session_state.current_conversation_id,      # ✅ CORRECT usage
    turn_number=st.session_state.turn_number,                      # ✅ CORRECT usage
)

# Line 381: Service receives conversation context
response = service.chat(request)
```

These parameters are correctly passed to **ChatService**, not to FeedbackService. The bug was trying to pass them to FeedbackService where they don't belong.

---

## Lines Changed

| Line | Type | Before | After | Status |
|------|------|--------|-------|--------|
| 405 | Opening | `interaction = feedback_service.log_interaction(` | `interaction = feedback_service.log_interaction(` | Same |
| 406 | Parameter | `query=prompt,` | `query=prompt,` | Same |
| 407 | Parameter | `response=response.answer,` | `response=response.answer,` | Same |
| 408 | Parameter | `sources=source_names,` | `sources=source_names,` | Same |
| 409 | Parameter | `processing_time_ms=int(response.processing_time_ms),` | `processing_time_ms=int(response.processing_time_ms),` | Same |
| 410 | Parameter | `conversation_id=...,` | *(removed)* | ✅ REMOVED |
| 411 | Parameter | `turn_number=...,` | *(removed)* | ✅ REMOVED |
| 412 | Closing | `)` | `)` | Same |

**Summary**: 2 lines removed (lines 410-411 in the old version)

---

## Testing the Fix

### Quick Test

```bash
# Start Streamlit
poetry run streamlit run src/ui/app.py

# In the UI, type and submit: high in the chart
# Expected: Response appears, feedback buttons render, no hanging
```

### Comprehensive Test

```bash
# Run the service directly to test
poetry run python scripts/test_chat_service_directly.py

# Test API endpoint
poetry run python scripts/debug_ui_hanging.py
```

Both should work without TypeError.

---

## File Locations

| Item | Location |
|------|----------|
| Main Fix | `src/ui/app.py` lines 405-410 |
| Method Definition | `src/services/feedback.py` lines 36-42 |
| ChatRequest Handler | `src/services/chat.py` |
| ChatService | `src/api/routes/chat.py` |

---

## Conclusion

This is a **minimal but critical fix**:
- ✅ Only 2 lines removed
- ✅ Eliminates the hanging issue completely
- ✅ No functionality lost
- ✅ No side effects
- ✅ Fully backward compatible

The fix corrects a parameter passing error where invalid parameters were being sent to a method that doesn't accept them.

---

**Date**: 2026-02-12
**Version**: 1.0
**Status**: Applied and Verified ✅
