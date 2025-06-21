import streamlit as st
import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline

# === 1. Connect to SQLite Database ===
DB_FILE = "inventory.db"
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query("SELECT * FROM products", conn)

# === 2. Convert Row to Text for RAG Embedding ===
def row_to_text(row):
    return f"Brand: {row['Brand']}, Product: {row['Product']}, Package: {row['Package_Size']}, Price: {row['Price_per_Pack']}, Stock: {row['In_Stock']}, Shelf: {row['Shelf']}"

row_texts = df.apply(row_to_text, axis=1).tolist()

# === 3. Embed Rows Using SentenceTransformer ===
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Small & fast
embeddings = embedder.encode(row_texts, convert_to_tensor=False)

# === 4. Build FAISS Index ===
dimension = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# === 5. Load Flan-T5 Model ===
llm = pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=200)

# === 6. Streamlit App UI ===
st.set_page_config(page_title="SmartShelf: Retail Inventory Q&A Assistant", page_icon="🛒", layout="wide")
st.title("🛒 SmartShelf: Retail Inventory Q&A Assistant")

question = st.text_input("Ask me anything about the inventory:")

if "QA_history" not in st.session_state:
    st.session_state.QA_history = []

# === 7. Semantic Search using FAISS ===
def retrieve_context(query, top_k=5):
    # Lowercase version of the query for easier matching
    query_lower = query.lower()

    # Try structured keyword filtering for "shelf"
    matched_rows = df.copy()
    matched = False

    if "shelf" in query_lower:
        for shelf in df["Shelf"].unique():
            if shelf.lower() in query_lower:
                matched_rows = df[df["Shelf"].str.lower() == shelf.lower()]
                matched = True
                break  # Stop after first match

    # If a shelf was matched, only use that subset for semantic retrieval
    rows_to_use = matched_rows.apply(row_to_text, axis=1).tolist()
    new_embeddings = embedder.encode(rows_to_use, convert_to_tensor=False)

    local_index = faiss.IndexFlatL2(new_embeddings[0].shape[0])
    local_index.add(np.array(new_embeddings))

    query_embedding = embedder.encode([query])[0]
    distances, indices = local_index.search(np.array([query_embedding]), top_k)

    return [rows_to_use[i] for i in indices[0]]


# === 8. RAG + LLM ===
if question:
    try:
        context_passages = retrieve_context(question, top_k=8)  # 🔁 Top_k increased to 8
        context = "\n".join(context_passages)

        prompt = f"""You are an inventory assistant. Use the following inventory entries to answer the user's question accurately.

Inventory Data:
{context}

Question: {question}
Answer:"""

        response = llm(prompt)[0]['generated_text'].strip()
        st.write(response)

        st.session_state.QA_history.insert(0, {"Question": question, "Answer": response})

    except Exception as e:
        st.error(f"❌ Error: {e}")

# === 9. Show History ===
with st.expander("📜 History"):
    for qa in st.session_state.QA_history:
        st.info(f"**Q:** {qa['Question']}\n\n**A:** {qa['Answer']}")
