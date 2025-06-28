# 🛒 SmartShelf: Retail Inventory Q&A Assistant

An intelligent retail inventory management tool powered by **Streamlit**, **FAISS**, **Sentence Transformers**, and **LLMs** (Flan-T5), designed to help store managers and staff easily track, update, and query inventory information.

---

## 💡 Features

- 📦 **Ask Anything About Inventory**  
  Use natural language to ask about stock levels, shelf locations, brand details, and more.

- 🛍️ **Simulate Customer Purchases**  
  Easily simulate stock reduction by "purchasing" products through an intuitive interface.

- 🔧 **Admin Panel**  
  Update and manage product stock directly without manual database edits.

- ⚡ **RAG-powered Q&A**  
  Combines embeddings (FAISS + Sentence Transformers) with a generative model to provide accurate, context-rich answers.

---

## 🚀 Tech Stack

- **Python**
- **Streamlit** (Web UI)
- **SQLite** (Local inventory database)
- **FAISS** (Vector similarity search)
- **Sentence Transformers** (Embeddings)
- **Transformers (Flan-T5)** (Language model for answering)
- **FastAPI** (Backend API for simulated purchases)

 ---
 ## 🌟 Screenshots

 > 🔧 **Admin Panel Page**  
  ![Screenshot 2025-06-27 150454](https://github.com/user-attachments/assets/b33afe67-82c0-4e7f-b37d-24bd8a052a07)
>
> 🛍️ **Simulate Purchase Page**  
![Screenshot 2025-06-27 150209](https://github.com/user-attachments/assets/37f7fb91-68f7-41ad-825c-31295b310285)
>
>💬 **Ask Inventory Page**  
> ![Screenshot 2025-06-27 150136](https://github.com/user-attachments/assets/8e8299f1-4ee0-4a6e-bc9a-273c60300725)
>
>  ---
>
> ## 💼 Example Use Cases

- 🛒 **Retail Managers:** Monitor and query stock levels on the fly without spreadsheets or manual checks.
- 💬 **Customer Support Bots:** Instantly answer product availability and shelf location questions.
- 🤖 **Automated Replenishment:** Connect to future smart shelf or POS sensors to keep inventory real-time.
- 🏬 **Employee Training:** Help new staff understand stock flow and shelf mapping using conversational queries.

-  ---

## ⚠️ Limitations

-  No live integration with real-time sensors or POS systems yet.
-  Purchases and inventory updates still require UI button clicks or API triggers (not fully automated).
-  Not optimized for very large-scale deployments out of the box.

---

