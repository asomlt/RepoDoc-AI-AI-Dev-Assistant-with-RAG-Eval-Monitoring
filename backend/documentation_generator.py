# =====================================================
# documentation_generator.py
# =====================================================

import google.generativeai as genai
from dotenv import load_dotenv
import os

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# =====================================================
# CONFIGURE GEMINI
# =====================================================

genai.configure(
    api_key=GEMINI_API_KEY
)

# =====================================================
# LOAD MODEL
# =====================================================

model = genai.GenerativeModel(
    "models/gemini-3.1-flash-lite"
)

# =====================================================
# GENERATE DOCUMENTATION
# =====================================================

def generate_project_documentation(summaries):

    # =============================================
    # COMBINE ALL AI SUMMARIES
    # =============================================

    combined_summary = "\n\n".join([

        f"""
        FILE NAME:
        {summary['file_name']}

        AI SUMMARY:
        {summary['summary']}
        """

        for summary in summaries

    ])

    # =============================================
    # FINAL DOCUMENTATION PROMPT
    # =============================================

    prompt = f"""
    You are an expert software architect.

    Below are AI-generated summaries
    from a real GitHub repository.

    Use ONLY the provided summaries.

    DO NOT generate generic documentation.

    PROJECT SUMMARIES:
    {combined_summary}

    Generate professional README documentation.

    Include:

    1. Project Purpose
    2. What Problem It Solves
    3. Main Features
    4. Architecture
    5. Core Modules
    6. Technical Flow
    7. Technologies Used
    8. Setup Instructions
    9. Future Improvements

    Return detailed markdown documentation.
    """

    # =============================================
    # GENERATE FINAL DOCS
    # =============================================

    response = model.generate_content(
        prompt
    )

    # =============================================
    # RETURN FINAL DOCUMENTATION
    # =============================================

    return response.text