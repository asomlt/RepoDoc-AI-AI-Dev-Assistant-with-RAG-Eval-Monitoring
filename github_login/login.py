import base64
import requests
import os
import sys

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

# =====================================================
# BACKEND PATH
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND_PATH = os.path.join(
    BASE_DIR,
    "backend"
)

sys.path.append(BACKEND_PATH)

# =====================================================
# AI IMPORTS
# =====================================================

from llm_engine import create_code_chunks

from ai_processor import process_code_chunks

from documentation_generator import (
    generate_project_documentation
)

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
# HOME ROUTE
# =====================================================

@app.get("/")
def home():

    return {

        "message": (
            "RepoDoc AI Backend Running"
        )

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

    return RedirectResponse(
        url=github_auth_url
    )

# =====================================================
# STEP 2
# GITHUB CALLBACK
# =====================================================

@app.get("/auth/github/callback")
def github_callback(code: str):

    token_url = (
        "https://github.com/login/oauth/access_token"
    )

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

    access_token = token_data.get(
        "access_token"
    )

    # =================================================
    # AUTH FAILED
    # =================================================

    if not access_token:

        return {

            "error": (
                "GitHub authentication failed"
            )

        }

    github_headers = {

        "Authorization": (
            f"token {access_token}"
        )

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
    # STORE REPOSITORY DATA
    # =================================================

    for repo in repos:

        repo_list.append({

            "name": repo["name"],

            "full_name": repo["full_name"],

            "private": repo["private"],

            "default_branch": repo[
                "default_branch"
            ]

        })

    # =================================================
    # STORE SESSION
    # =================================================

    username = user_data["login"]

    user_sessions[username] = {

        "access_token": access_token,

        "repositories": repo_list

    }

    # =================================================
    # REDIRECT TO STREAMLIT
    # =================================================

    redirect_url = (
        f"http://localhost:8501"
        f"?user={username}"
    )

    return RedirectResponse(
        redirect_url
    )

# =====================================================
# STEP 3
# GET USER REPOSITORIES
# =====================================================

@app.get("/get-repositories/{username}")
def get_repositories(username: str):

    user_data = user_sessions.get(
        username
    )

    if not user_data:

        return {

            "error": (
                "User session not found"
            )

        }

    return {

        "repositories": (
            user_data["repositories"]
        )

    }

# =====================================================
# STEP 4
# USER SELECTS REPOSITORY
# =====================================================

@app.get("/select-repo/{username}/{owner}/{repo_name}")
def select_repository(

    username: str,
    owner: str,
    repo_name: str

):

    # =================================================
    # GET USER SESSION
    # =================================================

    user_data = user_sessions.get(
        username
    )

    if not user_data:

        return {

            "error": (
                "User not authenticated"
            )

        }

    access_token = user_data[
        "access_token"
    ]

    github_headers = {

        "Authorization": (
            f"token {access_token}"
        )

    }

    # =================================================
    # GET REPOSITORY DETAILS
    # =================================================

    repo_url = (

        f"https://api.github.com/repos/"
        f"{owner}/{repo_name}"

    )

    repo_data = requests.get(

        repo_url,

        headers=github_headers

    ).json()

    # =================================================
    # DEFAULT BRANCH
    # =================================================

    default_branch = repo_data.get(

        "default_branch",

        "main"

    )

    # =================================================
    # GET COMPLETE REPOSITORY TREE
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
        ".jsx",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".md",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
        ".properties",
        ".html",
        ".css"

    )

    # =================================================
    # IGNORED FOLDERS
    # =================================================

    ignored_folders = (

        "node_modules",
        ".git",
        "dist",
        "build",
        "__pycache__",
        ".next",
        "venv"

    )

    files_data = []

    # =================================================
    # READ IMPORTANT FILES
    # =================================================

    for item in tree_response.get(
        "tree",
        []
    ):

        path = item.get(
            "path",
            ""
        )

        # =============================================
        # IGNORE USELESS FOLDERS
        # =============================================

        if any(

            folder in path

            for folder in ignored_folders

        ):

            continue

        # =============================================
        # IMPORTANT FILES ONLY
        # =============================================

        if path.endswith(
            important_extensions
        ):

            file_url = (

                f"https://api.github.com/repos/"
                f"{owner}/{repo_name}/contents/{path}"

            )

            file_response = requests.get(

                file_url,

                headers=github_headers

            ).json()

            encoded_content = file_response.get(
                "content"
            )

            if not encoded_content:

                continue

            try:

                decoded_content = (
                    base64.b64decode(

                        encoded_content

                    ).decode(

                        "utf-8",

                        errors="ignore"

                    )
                )

            except Exception:

                continue

            files_data.append({

                "file_name": path,

                "content": decoded_content,

                "size": file_response.get(
                    "size"
                )

            })

    # =================================================
    # CREATE REPOSITORY DATA
    # =================================================

    repository_data = {

        "repository": (
            f"{owner}/{repo_name}"
        ),

        "branch": default_branch,

        "files": files_data

    }

    # =================================================
    # CREATE CHUNKS
    # =================================================

    chunks = create_code_chunks(
        repository_data
    )

    # =================================================
    # PROCESS WITH GEMINI
    # =================================================

    summaries = process_code_chunks(
        chunks[:5]
    )

    # =================================================
    # GENERATE FINAL DOCUMENTATION
    # =================================================

    documentation = (
        generate_project_documentation(
            summaries
        )
    )

    # =================================================
    # FINAL RESPONSE
    # =================================================

    return {

        "repository": (
            f"{owner}/{repo_name}"
        ),

        "total_files": len(files_data),

        "total_chunks": len(chunks),

        "documentation": documentation

    }