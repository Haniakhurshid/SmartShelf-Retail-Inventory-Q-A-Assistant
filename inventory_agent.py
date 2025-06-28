import streamlit as st
import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline
from database import get_connection
import requests

# === 1. Load Embedder and LLM once ===
embedder = SentenceTransformer("all-MiniLM-L6-v2")
llm = pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=200)

# === 2. Helper: Convert row to readable text ===
def row_to_text(row):
    return f"Brand: {row['Brand']}, Product: {row['Product']}, Package: {row['Package_Size']}, Price: {row['Price_per_Pack']}, Stock: {row['In_Stock']}, Shelf: {row['Shelf']}"

# === 3. Helper: Build FAISS index ===
def build_faiss_index(df):
    row_texts = df.apply(row_to_text, axis=1).tolist()
    embeddings = embedder.encode(row_texts, convert_to_tensor=False)
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index, row_texts

# === 4. Semantic Search ===
def retrieve_context(query, top_k=5):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    query_lower = query.lower()
    matched_rows = df.copy()

    if "shelf" in query_lower:
        for shelf in df["Shelf"].unique():
            if shelf.lower() in query_lower:
                matched_rows = df[df["Shelf"].str.lower() == shelf.lower()]
                break

    rows_to_use = matched_rows.apply(row_to_text, axis=1).tolist()
    new_embeddings = embedder.encode(rows_to_use, convert_to_tensor=False)

    local_index = faiss.IndexFlatL2(new_embeddings[0].shape[0])
    local_index.add(np.array(new_embeddings))

    query_embedding = embedder.encode([query])[0]
    distances, indices = local_index.search(np.array([query_embedding]), top_k)

    return [rows_to_use[i] for i in indices[0]]

# === 5. Setup Streamlit ===
st.set_page_config(page_title="SmartShelf: Retail Inventory Q&A Assistant", layout="wide")
st.markdown("""
    <style>
    /* Increase sidebar width to avoid text wrapping */
    [data-testid="stSidebar"] {
        min-width: 250px;
        max-width: 250px;
    }

    /* Make radio buttons fit better in one line */
    section[data-testid="stSidebar"] label {
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)


st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["Inventory", "Purchase", "Admin Panel"])

st.title("🛒 SmartShelf: Retail Inventory Q&A Assistant")

# === 6. Ask Inventory Page ===
if page == "Inventory":
    st.subheader("🧠 Ask Anything About Inventory")
    question = st.text_input("What would you like to know?")
    if "QA_history" not in st.session_state:
        st.session_state.QA_history = []

    if question:
        try:
            context_passages = retrieve_context(question, top_k=8)
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

    with st.expander("📜 History"):
        for qa in st.session_state.QA_history:
            st.info(f"**Q:** {qa['Question']}\n\n**A:** {qa['Answer']}")

# === 7. Simulate Purchase Page ===
elif page == "Purchase":
    st.subheader("🛍️ Simulate a Customer Purchase")

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    product_list = df["Product"].unique().tolist()
    selected_product = st.selectbox("Select product to purchase:", product_list)
    purchase_qty = st.number_input("Quantity to purchase:", min_value=1, step=1)

    if st.button("Buy Now"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/purchase",
                json={"product_name": selected_product, "quantity": purchase_qty}
            )
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(f"❌ {response.json()['detail']}")
        except Exception as e:
            st.error(f"⚠ Failed to reach the purchase API: {e}")

# === 8. Admin Panel Page ===
elif page == "Admin Panel":
    st.subheader("🛠️ Admin Panel: Update Product Stock")

    conn = get_connection()
    product_data = pd.read_sql_query("SELECT Brand, Product, In_Stock FROM products", conn)
    conn.close()

    product_options = product_data["Product"].tolist()
    selected_product = st.selectbox("Select a product to update", product_options)

    current_stock = int(product_data[product_data["Product"] == selected_product]["In_Stock"].values[0])
    st.info(f"📦 Current stock for '{selected_product}': *{current_stock}* units.")
    new_stock = st.number_input("Enter new stock value", min_value=0, step=1, value=current_stock)

    if st.button("Update Stock"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET In_Stock = ? WHERE Product = ?",
                (new_stock, selected_product)
            )
            conn.commit()
            conn.close()
            st.success(f"✅ Stock for '{selected_product}' updated to {new_stock} units.")
        except Exception as e:
            st.error(f"❌ Error updating stock: {e}")

