import streamlit as st
import requests
import sys
import os

# =====================================================
# CONNECT BACKEND
# =====================================================

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "backend"
        )
    )
)

from database import save_history, get_history

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RepoDoc AI",
    layout="wide"
)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("🚀 RepoDoc AI")

# =====================================================
# SIDEBAR HISTORY
# =====================================================

st.sidebar.title("📜 Previous History")

history = get_history()

# =====================================================
# SHOW HISTORY BUTTONS
# =====================================================

for index, item in enumerate(history):

    repo_name = item["repo_name"]

    summary = item["summary"]

    if st.sidebar.button(
        repo_name,
        key=f"history_{index}"
    ):

        st.session_state[
            "selected_history"
        ] = summary

# =====================================================
# DISPLAY SELECTED HISTORY
# =====================================================

if "selected_history" in st.session_state:

    st.subheader("📄 Retrieved History")

    st.markdown(
        st.session_state["selected_history"]
    )

# =====================================================
# GET USER FROM URL
# =====================================================

query_params = st.query_params

username = query_params.get("user")

# =====================================================
# USER NOT LOGGED IN
# =====================================================

if not username:

    github_login_url = (
        "http://localhost:8000/login/github"
    )

    st.link_button(
        "Login with GitHub",
        github_login_url
    )

# =====================================================
# USER LOGGED IN
# =====================================================

else:

    st.success(
        f"Logged in as {username}"
    )

    # =================================================
    # FETCH REPOSITORIES
    # =================================================

    response = requests.get(
        f"http://localhost:8000/get-repositories/{username}"
    )

    data = response.json()

    # =================================================
    # SESSION EXPIRED
    # =================================================

    if "repositories" not in data:

        st.error(
            "Session expired. Please login again."
        )

        st.stop()

    # =================================================
    # REPOSITORY LIST
    # =================================================

    repo_names = []

    for repo in data["repositories"]:

        repo_names.append(
            repo["full_name"]
        )

    # =================================================
    # REPOSITORY DROPDOWN
    # =================================================

    selected_repo = st.selectbox(
        "Select Repository",
        repo_names
    )

    st.write(
        f"Selected Repo: {selected_repo}"
    )

    # =================================================
    # GENERATE BUTTON
    # =================================================

    generate_button = st.button(
        "Generate Documentation"
    )

    # =================================================
    # BUTTON CLICKED
    # =================================================

    if generate_button:

        st.info(
            "Processing Repository..."
        )

        # =============================================
        # SPLIT OWNER + REPO NAME
        # =============================================

        owner, repo_name = selected_repo.split("/", 1)

        # =============================================
        # CALL BACKEND
        # =============================================

        response = requests.get(

            f"http://localhost:8000/select-repo/"
            f"{username}/{owner}/{repo_name}"

        )

        data = response.json()

        # =============================================
        # SUCCESS
        # =============================================

        st.success(
            "Repository Processed Successfully!"
        )

        # =============================================
        # SHOW DOCUMENTATION
        # =============================================

        st.markdown(
            data["documentation"]
        )

        # =============================================
        # SAVE HISTORY
        # =============================================

        save_history(
            selected_repo,
            data["documentation"]
        )

        # =============================================
        # DOWNLOAD BUTTON
        # =============================================

        st.download_button(

            label="Download README.md",

            data=data["documentation"],

            file_name="README.md",

            mime="text/markdown"

        )

# =====================================================
# DEBUG
# =====================================================

print(get_history())