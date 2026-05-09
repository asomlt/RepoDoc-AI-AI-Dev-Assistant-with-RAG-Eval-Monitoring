from dotenv import load_dotenv
import os

from repo_reader import read_repository_code
from llm_engine import create_code_chunks
from ai_processor import process_code_chunks
from documentation_generator import (
    generate_project_documentation
)

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

github_access_token = os.getenv(
    "GITHUB_ACCESS_TOKEN"
)

# =====================================================
# TEST REPOSITORY
# =====================================================

owner = "asomlt"

repo_name = "chat_app"

default_branch = "main"

# =====================================================
# STEP 1
# READ REPOSITORY CODE
# =====================================================

repository_data = read_repository_code(

    owner,
    repo_name,
    default_branch,
    github_access_token

)
print("\nREPOSITORY DATA:\n")

print(repository_data)

# =====================================================
# STEP 2
# CREATE CHUNKS
# =====================================================

chunks = create_code_chunks(
    repository_data
)

print("\nCHUNKS:\n")

print(chunks)
# =====================================================
# STEP 3
# PROCESS CHUNKS WITH GEMINI
# =====================================================

summaries = process_code_chunks(
    chunks
)

# =====================================================
# STEP 4
# GENERATE FINAL DOCUMENTATION
# =====================================================

documentation = generate_project_documentation(
    summaries
)

# =====================================================
# STEP 5
# FINAL OUTPUT
# =====================================================

print("\n=====================================\n")

print(documentation)