# 🚀 LLM-Powered Text-to-SQL System

A Natural Language Interface for Relational Databases powered by Large Language Models (LLMs).

This project enables users to interact with SQLite databases using plain English queries.  
The system automatically extracts database schema, converts natural language into optimized SQL queries using an LLM, executes them safely, and displays results dynamically.

---

## 🚀 Features

- Natural Language to SQL conversion using LLM  
- Automatic schema extraction from selected database  
- Dynamic detection of local SQLite databases  
- Multi-database support via dropdown selection  
- Query execution with real-time results display  
- Chat history maintenance for contextual understanding  
- Automatic sample database generation for testing  

---

## 🏗️ System Architecture

1. User selects a SQLite database (.db file)  
2. Application extracts schema metadata dynamically  
3. Natural language query is sent to LLM with schema context  
4. LLM generates syntactically correct SQL  
5. Query is executed safely on the selected database  
6. Results are displayed in tabular format  

This architecture ensures:

- Schema-aware query generation  
- Context-driven SQL accuracy  
- Flexible database integration  

---

## 🛠️ Tech Stack

- Python  
- Streamlit  
- Google Gemini API  
- SQLite  
- Pandas  
- LangChain / LangGraph  

---

## 📂 Project Structure

```
llm-text-to-sql/
│
├── app.py                  # Main Streamlit application
├── create_sample_dbs.py    # Script to generate test databases
├── requirements.txt
├── .gitignore
└── .env.example
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/RajhansJain/llm-text-to-sql.git
cd llm-text-to-sql
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure API Key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

---

## 🗄️ Database Usage

This application automatically detects all `.db` (SQLite) files  
present in the project root directory.

To use your own database:

1. Place your `.db` file in the same folder as `app.py`  
2. Launch the application  
3. Select the database from dropdown  
4. Ask natural language questions  

---

## 🧪 Generate Sample Databases

If you do not have a database available, generate sample databases using:

```bash
python create_sample_dbs.py
```

This will create multiple example databases such as:

- student.db  
- bank.db  
- ecommerce.db  
- hospital.db  
- library.db  

The application will automatically detect them.

---

## ▶️ Run Application

```bash
streamlit run app.py
```

---

## 🔐 Security Note

- API keys are stored securely using environment variables  
- No hardcoded credentials  
- Designed for local database interaction  

---

## 📈 Future Improvements

- Support for PostgreSQL / MySQL  
- Query validation & guardrails  
- Role-based access control  
- Cloud deployment  
- Docker containerization  
- Query performance optimization  

---

## 💡 Why This Project Matters

Traditional databases require SQL knowledge.  
This system democratizes database interaction by enabling non-technical users to query structured data using natural language.

It demonstrates:

- LLM integration with structured systems  
- Schema-aware prompt engineering  
- Real-time query execution pipelines  
- End-to-end AI application design  

---

## 👤 Author

**Rajhans Jain**  
B.Tech | AI/ML & Data Engineering Enthusiast  
