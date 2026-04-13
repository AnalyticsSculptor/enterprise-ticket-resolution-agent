import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

def build_vector_db(csv_path="data/tickets.csv"):
    print("📥 Loading IT Support Dataset...")
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("❌ Error: Could not find 'tickets.csv'.")
        return

    # ==========================================
    # 🔍 NEW: DATA SANITY CHECK
    # ==========================================
    print("\n📊 DATASET SANITY CHECK:")
    print(f"Columns found: {df.columns.tolist()}")
    print("\nFirst 5 rows of data:")
    print(df.head())
    print("-" * 50 + "\n")
    # ==========================================

    # Clean the data
    # Drop rows only if they are missing the essential columns we need
    df = df.dropna(subset=['Description', 'Cause']) 
    df = df.head(500) # Limit to 500 for testing speed

    print("🔧 Engineering Features...")
    df['Full_Context'] = df['Problem Statement'].astype(str) + " | " + df['Description'].astype(str)

    content_column_name = "Full_Context" 

    print("📄 Structuring Documents...")
    loader = DataFrameLoader(df, page_content_column=content_column_name)
    docs = loader.load()

    print("🧠 Generating Embeddings (Downloading model if first run)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("💾 Saving to ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=embeddings, 
        persist_directory="./chroma_db"
    )
    print("✅ Vector Database built successfully! The 'Brain' is ready.")

if __name__ == "__main__":
    build_vector_db()