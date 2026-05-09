import streamlit as st
import requests

# =====================================================
# PAGE TITLE
# =====================================================

st.title("RepoDoc AI")

# =====================================================
# GET USER FROM URL
# =====================================================

query_params = st.query_params

username = query_params.get("user")

# =====================================================
# IF USER NOT LOGGED IN
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
    # GENERATE DOCUMENTATION BUTTON
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
        st.write(username)
        st.write(owner)
        st.write(repo_name)
        response = requests.get(

            f"http://localhost:8000/select-repo/"
            f"{username}/{owner}/{repo_name}"

        )

        data = response.json()

        # =============================================
        # SHOW RESPONSE
        # =============================================

        st.success(
            "Repository Processed Successfully!"
        )

        st.markdown(
            data["documentation"]
        )
        st.download_button(

        label="Download README.md",

        data=data["documentation"],

        file_name="README.md",

        mime="text/markdown"

        )   