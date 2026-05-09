import google.generativeai as genai
from dotenv import load_dotenv
from database import save_history
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
# PROCESS CHUNKS
# =====================================================

def process_code_chunks(chunks):

    summaries = []

    # =================================================
    # LOOP THROUGH CHUNKS
    # =================================================

    for chunk in chunks:

        file_name = chunk["file_name"]

        content = chunk["content"]

        # =============================================
        # PROMPT
        # =============================================

        prompt = f"""
        You are an expert software engineer.

        Analyze this repository code chunk.

        FILE NAME:
        {file_name}

        SOURCE CODE:
        {content}

        Explain clearly:

        1. What this file does
        2. Main functionality
        3. Architecture role
        4. Important logic
        5. Technologies/frameworks used

        Return detailed technical explanation.
        """

        # =============================================
        # GEMINI RESPONSE
        # =============================================

        response = model.generate_content(
            prompt
        )

        # =============================================
        # STORE SUMMARY
        # =============================================

        summaries.append({

            "file_name": file_name,

            "chunk_number": chunk["chunk_number"],

            "summary": response.text

        })
        save_history(file_name,  response.text )
   
    # =================================================
    # DEBUG
    # =================================================
    
    print("\nTOTAL SUMMARIES GENERATED:")
    print(len(summaries))

    # =================================================
    # RETURN FINAL SUMMARIES
    # =================================================

    return summaries