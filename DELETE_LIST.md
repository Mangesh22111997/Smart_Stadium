# 🗑️ CLEANUP - QUICK DELETE LIST

**Use this for quick reference when deleting files**

---

## 🔴 **IMMEDIATE DELETIONS** (Safe to delete right now)

### Critical - Fixes blocking issue
```
❌ DELETE: app/routes/gates_routes.py
   Reason: Route prefix conflict with gate_routes.py
   Impact: Backend routing broken without this deletion
   
✏️ EDIT: app/main.py
   Remove line: from app.routes import gates_routes
   Remove line: app.include_router(gates_routes.router)
```

### High Priority - Orphaned code
```
❌ DELETE: api_utils.py
   Reason: Zero imports found, replaced by streamlit_app/utils/api_client.py
   
❌ DELETE: hello.py
   Reason: Trivial 1-line test file, no functional value
   
❌ DELETE: train_gate_compact.py
   Reason: Duplicate of app/ml/train_gate_model.py (better version exists)
   
❌ DELETE: QUICK_REFERENCE.txt
   Reason: Duplicate of QUICK_REFERENCE.md (markdown version kept)
```

---

## ❓ **CONDITIONAL DELETIONS** (Review first)

### Only delete if NOT used
```
⚠️  DELETE IF UNUSED: auth_utils.py
    Reason: Only used by frontend.py and frontend_redesigned.py
    Check: Are you using either of the root-level frontend files?
    If NO: Delete
    If YES: Keep
    
⚠️  DELETE IF UNUSED: frontend.py
    Reason: ~500 lines, not imported by active code
    Check: Is this the active frontend?
    If NO (using streamlit_app/app.py instead): Delete
    If YES: Keep
    
⚠️  DELETE IF UNUSED: frontend_redesigned.py
    Reason: ~550 lines, not imported by active code
    Check: Is this the active frontend?
    If NO (using streamlit_app/app.py instead): Delete
    If YES: Keep
```

---

## 📦 **MOVE TO FOLDERS** (Not deletion, just relocation)

### Move to `tests/` folder
```
MOVE: test_firebase_complete.py → tests/
MOVE: test_firebase_integration.py → tests/
MOVE: test_firebase_rtdb.py → tests/
MOVE: test_api_endpoints.py → tests/
MOVE: test_ml_integration.py → tests/
MOVE: test_orchestration.py → tests/
```

### Move to `docs/examples/` folder
```
MOVE: app/config/FIREBASE_SETUP_GUIDE.py → docs/examples/
MOVE: app/services/MIGRATION_EXAMPLES.py → docs/examples/
MOVE: app/config/firebase_test.py → docs/examples/
```

---

## 📚 **RENAME FOR ARCHIVAL** (Not deletion, just rename with _ARCHIVED suffix)

### Old Firebase documentation (keep active ones)
```
RENAME: FIREBASE_INTEGRATION_GUIDE.md → FIREBASE_INTEGRATION_GUIDE_ARCHIVED.md
RENAME: FIREBASE_FIRESTORE_INTEGRATION.md → FIREBASE_FIRESTORE_INTEGRATION_ARCHIVED.md
RENAME: FIREBASE_IMPLEMENTATION_CHECKLIST.md → FIREBASE_IMPLEMENTATION_CHECKLIST_ARCHIVED.md

KEEP: FIREBASE_SETUP_COMPLETE.md (active)
KEEP: FIREBASE_RTD_SETUP_COMPLETE.md (active)
```

### Old planning documents (keep master roadmap)
```
RENAME: smart_stadium_master_plan.md → smart_stadium_master_plan_ARCHIVED.md
RENAME: IMPLEMENTATION_ROADMAP.md → IMPLEMENTATION_ROADMAP_ARCHIVED.md
RENAME: plan.md → plan_ARCHIVED.md

KEEP: MASTER_ROADMAP.md (active)
```

### Old completion reports (move to docs/archived/completion_history/)
```
ARCHIVE: IMPLEMENTATION_COMPLETE.md
ARCHIVE: REDESIGN_COMPLETE.md
ARCHIVE: FIREBASE_DELIVERY_SUMMARY.md
ARCHIVE: ML_INTEGRATION_SUMMARY.md
ARCHIVE: DEPRECATION_FIX_REPORT.md
ARCHIVE: TEST_REPORT_ORCHESTRATION.md
ARCHIVE: COMPLETE_DEVELOPMENT_SUMMARY_COPILOT.md

KEEP: STREAMLIT_BUILD_COMPLETE.md (as reference)
```

### Old frontend guides (keep complete guide)
```
RENAME: FRONTEND_GUIDE.md → FRONTEND_GUIDE_ARCHIVED.md
RENAME: frontend_approach.md → frontend_approach_ARCHIVED.md

KEEP: FRONTEND_COMPLETE_GUIDE.md (active)
```

---

## ✅ **POST-DELETION VERIFICATION**

After deleting/moving files, verify:

```bash
# Check backend still starts
python -m uvicorn app.main:app --reload

# Check frontend still starts
streamlit run streamlit_app/app.py

# Check no import errors in main app
python -m py_compile app/main.py

# Check no import errors in streamlit
python -m py_compile streamlit_app/app.py

# Run a test
python tests/test_firebase_complete.py
```

---

## 📊 **SUMMARY**

| Action | Count | Time |
|--------|-------|------|
| Delete files | 5-8 | 5 min |
| Move files | 9 | 10 min |
| Rename files | 14 | 5 min |
| Verification | All | 10 min |
| **TOTAL** | **32-35** | **30 min** |

---

## 🚀 **QUICK START COMMANDS**

### Windows PowerShell
```powershell
# Delete critical files
Remove-Item app/routes/gates_routes.py
Remove-Item api_utils.py
Remove-Item hello.py
Remove-Item train_gate_compact.py
Remove-Item QUICK_REFERENCE.txt

# Create new folders
mkdir tests
mkdir docs/examples -Force
mkdir docs/archived/completion_history -Force

# Move test files
Move-Item test_firebase_complete.py tests/
Move-Item test_firebase_integration.py tests/
Move-Item test_firebase_rtdb.py tests/
Move-Item test_api_endpoints.py tests/
Move-Item test_ml_integration.py tests/
Move-Item test_orchestration.py tests/

# Move reference docs
Move-Item app/config/FIREBASE_SETUP_GUIDE.py docs/examples/
Move-Item app/services/MIGRATION_EXAMPLES.py docs/examples/
Move-Item app/config/firebase_test.py docs/examples/
```

### Linux/Mac Bash
```bash
# Delete critical files
rm app/routes/gates_routes.py
rm api_utils.py
rm hello.py
rm train_gate_compact.py
rm QUICK_REFERENCE.txt

# Create new folders
mkdir -p tests
mkdir -p docs/examples
mkdir -p docs/archived/completion_history

# Move test files
mv test_firebase_*.py tests/
mv test_api_*.py tests/
mv test_orchestration.py tests/

# Move reference docs
mv app/config/FIREBASE_SETUP_GUIDE.py docs/examples/
mv app/services/MIGRATION_EXAMPLES.py docs/examples/
mv app/config/firebase_test.py docs/examples/
```

---

✅ **Use [CLEANUP_CHECKLIST.md](CLEANUP_CHECKLIST.md) for step-by-step verification**
