from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import requests
import os

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI()
# =====================================================
# TEMP SESSION STORAGE
# =====================================================

user_sessions = {}
# =====================================================
# TEMP TOKEN STORAGE
# MVP PURPOSE ONLY
# =====================================================

github_access_token = None

# =====================================================
# HOME ROUTE
# =====================================================

@app.get("/")
def home():

    return {
        "message": "RepoDoc AI Backend Running"
    }

# =====================================================
# STEP 1
# LOGIN WITH GITHUB
# =====================================================

@app.get("/login/github")
def github_login():

    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        "&scope=repo"
    )

    return RedirectResponse(github_auth_url)

# =====================================================
# STEP 2
# GITHUB CALLBACK
# =====================================================

@app.get("/auth/github/callback")
def github_callback(code: str):

    global github_access_token

    token_url = "https://github.com/login/oauth/access_token"

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }

    headers = {
        "Accept": "application/json"
    }

    # =================================================
    # EXCHANGE CODE FOR ACCESS TOKEN
    # =================================================

    response = requests.post(
        token_url,
        data=payload,
        headers=headers
    )

    token_data = response.json()

    access_token = token_data.get("access_token")

    # =================================================
    # AUTH FAILED
    # =================================================

    if not access_token:

        return {
            "error": "GitHub authentication failed"
        }

    # =================================================
    # SAVE TOKEN
    # =================================================

    github_access_token = access_token

    github_headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # =================================================
    # GET USER INFO
    # =================================================

    user_data = requests.get(
        "https://api.github.com/user",
        headers=github_headers
    ).json()

    # =================================================
    # GET USER REPOSITORIES
    # =================================================

    repos_response = requests.get(
        "https://api.github.com/user/repos",
        headers=github_headers
    )

    repos = repos_response.json()

    repo_list = []

    # =================================================
    # STORE REPO DATA
    # =================================================

    for repo in repos:

        repo_list.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "private": repo["private"],
            "default_branch": repo["default_branch"]
        })

    # =================================================
    # FINAL RESPONSE
    # =================================================

    return {
    "access_token": access_token,
    "github_user": user_data["login"],
    "repositories": repo_list[:10]
}

# =====================================================
# STEP 3
# USER SELECTS REPOSITORY
# =====================================================

@app.get("/select-repo/{owner}/{repo_name}")
def select_repository(owner: str, repo_name: str):

    global github_access_token

    if not github_access_token:

        return {
            "error": "User not authenticated"
        }

    github_headers = {
        "Authorization": f"Bearer {github_access_token}"
    }

    # =================================================
    # GET REPO DETAILS
    # =================================================

    repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"

    repo_data = requests.get(
        repo_url,
        headers=github_headers
    ).json()

    # =================================================
    # DYNAMIC DEFAULT BRANCH
    # =================================================

    default_branch = repo_data.get("default_branch", "main")

    # =================================================
    # GET COMPLETE FILE TREE
    # =================================================

    tree_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo_name}/git/trees/"
        f"{default_branch}?recursive=1"
    )

    tree_response = requests.get(
        tree_url,
        headers=github_headers
    ).json()

    # =================================================
    # IMPORTANT FILE TYPES
    # =================================================

    important_extensions = (
        ".py",
        ".js",
        ".ts",
        ".java",
        ".md",
        ".json"
    )

    ignored_folders = (
        "node_modules",
        ".git",
        "dist",
        "build",
        "__pycache__"
    )

    files_data = []

    # =================================================
    # READ IMPORTANT FILES
    # =================================================

    for item in tree_response.get("tree", []):

        path = item.get("path", "")

        # =============================================
        # IGNORE USELESS FOLDERS
        # =============================================

        if any(folder in path for folder in ignored_folders):
            continue

        # =============================================
        # IMPORTANT FILES ONLY
        # =============================================

        if path.endswith(important_extensions):

            file_url = (
                f"https://api.github.com/repos/"
                f"{owner}/{repo_name}/contents/{path}"
            )

            file_response = requests.get(
                file_url,
                headers=github_headers
            ).json()

            files_data.append({
                "file_name": path,
                "download_url": file_response.get("download_url"),
                "size": file_response.get("size")
            })

    # =================================================
    # FINAL RESPONSE
    # =================================================

    # return {
    #     "repository": f"{owner}/{repo_name}",
    #     "branch": default_branch,
    #     "important_files_found": files_data[:20]
    # }
        # =====================================================
    # =====================================================
    # STORE USER SESSION
    # =====================================================

    username = user_data["login"]

    user_sessions[username] = {

        "access_token": access_token,

        "repositories": repo_list

    }

    # =====================================================
    # REDIRECT TO STREAMLIT
    # =====================================================

    redirect_url = (
        f"http://localhost:8501"
        f"?user={username}"
    )

    return RedirectResponse(
        redirect_url
    )