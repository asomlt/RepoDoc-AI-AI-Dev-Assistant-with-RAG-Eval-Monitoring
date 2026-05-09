# =====================================================
# llm_engine.py
# =====================================================
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =====================================================
# CREATE CHUNKS
# =====================================================

def create_code_chunks(repository_data):

    # =============================================
    # SPLITTER
    # =============================================

    text_splitter = RecursiveCharacterTextSplitter(

        chunk_size=2000,
        chunk_overlap=200

    )

    all_chunks = []

    # =============================================
    # LOOP THROUGH FILES
    # =============================================

    for file in repository_data["files"]:

        file_name = file["file_name"]

        content = file["content"]

        # =========================================
        # SPLIT FILE INTO CHUNKS
        # =========================================

        chunks = text_splitter.split_text(content)

        # =========================================
        # STORE CHUNKS
        # =========================================

        for index, chunk in enumerate(chunks):

            all_chunks.append({

                "file_name": file_name,

                "chunk_number": index + 1,

                "content": chunk

            })

    # =============================================
    # FINAL OUTPUT
    # =============================================

    return all_chunks