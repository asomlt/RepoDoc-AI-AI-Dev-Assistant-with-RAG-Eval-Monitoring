# =====================================================
# REPO DOC AI - DEV START SCRIPT
# =====================================================

Write-Host "Starting RepoDoc AI Development Environment..."

# =====================================================
# BACKEND SERVER
# =====================================================

Start-Process powershell -ArgumentList "-NoExit", "uvicorn github_login.login:app --reload"

# =====================================================
# STREAMLIT FRONTEND
# =====================================================

Start-Process powershell -ArgumentList "-NoExit", "cd frontend; streamlit run app.py"

# =====================================================
# OPTIONAL DEBUG TERMINAL
# =====================================================

Start-Process powershell -ArgumentList "-NoExit", "cd backend"