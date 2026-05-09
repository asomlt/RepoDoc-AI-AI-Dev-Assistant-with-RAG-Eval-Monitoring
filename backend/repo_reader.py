import requests
import base64

# =====================================================
# READ COMPLETE REPOSITORY CODE
# =====================================================

def read_repository_code(
    owner,
    repo_name,
    default_branch,
    github_access_token
):

    github_headers = {
        "Authorization": f"Bearer {github_access_token}"
    }

    # =================================================
    # GET REPOSITORY TREE
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
    print("\nTREE RESPONSE:\n")
    print(tree_response)
    # =================================================
    # IMPORTANT FILE TYPES
    # =================================================

    important_extensions = (
    ".py",
    ".js",
    ".ts",
    ".java",
    ".md",
    ".json",
    ".dart",
    ".yaml",
    ".yml",
    ".html",
    ".css",
    ".xml",
    ".properties"
)

    # =================================================
    # IGNORE USELESS FOLDERS
    # =================================================

    ignored_folders = (
        "node_modules",
        ".git",
        "dist",
        "build",
        "__pycache__",
        ".next"
    )

    repository_code = []

    # =================================================
    # LOOP THROUGH FILES
    # =================================================

    for item in tree_response.get("tree", []):

        path = item.get("path", "")

        # =============================================
        # IGNORE LARGE USELESS FOLDERS
        # =============================================

        if any(folder in path for folder in ignored_folders):
            continue

        # =============================================
        # IMPORTANT FILES ONLY
        # =============================================

        if path.endswith(important_extensions):

            # =========================================
            # GET FILE CONTENT
            # =========================================

            file_url = (
                f"https://api.github.com/repos/"
                f"{owner}/{repo_name}/contents/{path}"
            )

            file_response = requests.get(
                file_url,
                headers=github_headers
            ).json()

            encoded_content = file_response.get("content")

            if not encoded_content:
                continue

            # =========================================
            # DECODE BASE64 CONTENT
            # =========================================

            try:

                decoded_content = base64.b64decode(
                    encoded_content
                ).decode(
                    "utf-8",
                    errors="ignore"
                )

            except Exception:

                continue

            # =========================================
            # STORE FILE DATA
            # =========================================
            print(path)
            repository_code.append({

                "file_name": path,

                "content": decoded_content,

                "size": file_response.get("size")

            })

    # =================================================
    # FINAL OUTPUT
    # =================================================

    return {
        "repository": f"{owner}/{repo_name}",
        "branch": default_branch,
        "total_files_read": len(repository_code),
        "files": repository_code
    }