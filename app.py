import streamlit as st
import os
import sqlite3
import pandas as pd
import time
import io
import re  # Added for better parsing TextToSQL.py
from google import genai
from google.api_core import exceptions
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# --- 1. Configuration ---
st.set_page_config(page_title="DataTalk Pro 2026", layout="wide", page_icon="🤖")
MODEL_ID = "models/gemini-2.5-flash-lite"
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# --- 2. Database Helpers ---
def get_available_dbs():
    return [f for f in os.listdir('.') if f.endswith('.db')]

def get_db_schema(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        schema = ""
        for table_name, table_sql in cursor.fetchall():
            schema += f"Table: {table_name}\nSchema: {table_sql}\n\n"
        conn.close()
        return schema
    except Exception as e:
        return f"Error reading schema: {e}"

def execute_sql(sql, db_path):
    if not sql: return None, "No SQL query generated."
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

# --- 3. Robust AI Calling Logic ---
@retry(
    retry=retry_if_exception_type(exceptions.ResourceExhausted),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=6)
)
def call_gemini(chat_session, prompt):
    return chat_session.send_message(prompt)

# --- 4. Sidebar & State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🗄️ Database Manager")
    db_list = get_available_dbs()
    selected_db = st.selectbox("Active Database:", db_list if db_list else ["No .db files found"])
    
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if selected_db != "No .db files found":
        st.divider()
        with st.expander("Live Schema"):
            st.code(get_db_schema(selected_db), language="sql")

# --- 5. Main Chat ---
st.title("💬 DataTalk: Text-to-SQL")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "data" in msg:
            st.dataframe(msg["data"], use_container_width=True)

if user_prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        schema_context = get_db_schema(selected_db)
        
        # IMPROVED SYSTEM INSTRUCTION
        sys_instr = f"""You are an expert SQLite Data Analyst.
        DATABASE SCHEMA:
        {schema_context}

        RULES:
        1. Output ONLY the raw SQL query after the prefix 'QUERY: '.
        2. DO NOT use markdown code blocks or backticks.
        3. Provide a natural language summary after the prefix 'REASONING: '.
        4. If you cannot find the table, ask for clarification.
        """

        formatted_history = []
        for m in st.session_state.messages[:-1]:
            api_role = "model" if m["role"] == "assistant" else "user"
            formatted_history.append({"role": api_role, "parts": [{"text": m["content"]}]})

        chat = client.chats.create(model=MODEL_ID, config={'system_instruction': sys_instr}, history=formatted_history)

        with st.status("🔍 Processing...", expanded=True) as status:
            try:
                response = call_gemini(chat, user_prompt)
                raw_text = response.text
                
                # Robust Parsing with Regex
                sql_match = re.search(r"QUERY:(.*?)REASONING:", raw_text, re.DOTALL)
                reasoning_match = re.search(r"REASONING:(.*)", raw_text, re.DOTALL)
                
                sql_query = sql_match.group(1).strip() if sql_match else ""
                reasoning = reasoning_match.group(1).strip() if reasoning_match else raw_text

                # Cleanup potential markdown residue
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

                df, error = execute_sql(sql_query, selected_db)

                # Self-correction loop
                if error and sql_query:
                    st.write(f"⚠️ SQL Error: {error}. Attempting fix...")
                    retry_res = call_gemini(chat, f"Your SQL failed with: {error}. Provide a corrected SQLite query using the QUERY: prefix.")
                    
                    sql_match_retry = re.search(r"QUERY:(.*)", retry_res.text, re.DOTALL)
                    if sql_match_retry:
                        sql_query = sql_match_retry.group(1).strip().replace("```sql", "").replace("```", "")
                        df, error = execute_sql(sql_query, selected_db)

                status.update(label="✅ Analysis Complete!", state="complete")
            except Exception as e:
                st.error(f"Error: {e}")
                error = "Fatal"

        if not error and df is not None:
            st.markdown(reasoning)
            with st.expander("View SQL"):
                st.code(sql_query, language="sql")
            st.dataframe(df, use_container_width=True)
            
            # # Export Logic
            # csv = df.to_csv(index=False).encode('utf-8')
            # st.download_button("📊 Download CSV", csv, "data.csv", "text/csv")
            
            # st.session_state.messages.append({"role": "assistant", "content": reasoning, "data": df})




































































# ============================================================================================================================
# ========================================================================================================================

# import streamlit as st
# import os
# import sqlite3
# import pandas as pd
# from google import genai
# from dotenv import load_dotenv
# import io

# load_dotenv()

# # --- 1. Configuration & Client Initialization ---
# st.set_page_config(page_title="DataTalk Pro 2026", layout="wide", page_icon="📊")
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# # --- 2. Database & Utility Functions ---
# def get_available_databases():
#     """Finds all .db files in the current directory."""
#     return [f for f in os.listdir('.') if f.endswith('.db')]

# def get_db_schema(db_path):
#     """Dynamically fetches the schema of the selected database."""
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#         cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
#         schema = "\n".join([row[0] for row in cursor.fetchall() if row[0]])
#         conn.close()
#         return schema
#     except Exception as e:
#         return f"Error fetching schema: {e}"

# def run_sql(sql_query, db_path):
#     """Executes SQL and returns results or the raw error for self-correction."""
#     try:
#         conn = sqlite3.connect(db_path)
#         df = pd.read_sql_query(sql_query, conn)
#         conn.close()
#         return df, None
#     except Exception as e:
#         return None, str(e)

# # --- 3. Persistent State ---
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # --- 4. Sidebar UI ---
# with st.sidebar:
#     st.title("⚙️ Workspace Settings")
    
#     db_list = get_available_databases()
#     selected_db = st.selectbox("Select Database:", db_list if db_list else ["No .db files found"])
    
#     if st.button("🗑️ Reset Conversation"):
#         st.session_state.messages = []
#         st.rerun()
    
#     st.divider()
#     if selected_db != "No .db files found":
#         st.subheader("Database Schema")
#         active_schema = get_db_schema(selected_db)
#         st.code(active_schema, language="sql")

# # --- 5. Main Chat Interface ---
# st.title("💬 DataTalk: Agentic SQL Analyst")
# st.caption(f"Connected to: **{selected_db}**")

# # Display History
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
#         if "data" in msg:
#             st.dataframe(msg["data"], use_container_width=True)

# # User Query
# if user_input := st.chat_input("Ask a question about your data..."):
#     st.session_state.messages.append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         schema_context = get_db_schema(selected_db)
        
#         # System Instruction for the Agent
#         sys_instr = f"""You are a senior SQL Data Analyst.
#         DATABASE SCHEMA:
#         {schema_context}

#         INSTRUCTIONS:
#         1. Analyze the user question and the schema.
#         2. Provide the SQL query following this tag: 'QUERY: <sql>'
#         3. Provide a brief explanation following this tag: 'REASONING: <explanation>'
#         4. If the SQL fails, you will be given the error to self-correct.
#         """

#         # Start/Continue Chat Session
#         chat_session = client.chats.create(
#             model="models/gemini-2.5-flash-lite",
#             config={'system_instruction': sys_instr},
#             history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
#         )

#         with st.status("Thinking...", expanded=True) as status:
#             response = chat_session.send_message(user_input)
#             full_text = response.text
            
#             # --- Initial Attempt ---
#             sql_part = full_text.split("QUERY:")[1].split("REASONING:")[0].strip() if "QUERY:" in full_text else ""
#             reasoning = full_text.split("REASONING:")[1].strip() if "REASONING:" in full_text else "Analyzing data..."
            
#             st.write("Checking query syntax...")
#             df, error = run_sql(sql_part, selected_db)

#             # --- Agentic Self-Correction Loop (One-Shot) ---
#             if error:
#                 st.write(f"⚠️ Error detected: {error}. Attempting to self-correct...")
#                 correction_prompt = f"The previous SQL query failed with this error: {error}. Please fix the SQL and provide the corrected version using the same QUERY: and REASONING: format."
                
#                 correction_res = chat_session.send_message(correction_prompt)
#                 full_text = correction_res.text
#                 sql_part = full_text.split("QUERY:")[1].split("REASONING:")[0].strip()
#                 reasoning = "Fixed: " + full_text.split("REASONING:")[1].strip()
#                 df, error = run_sql(sql_part, selected_db)

#             status.update(label="Analysis Complete!", state="complete", expanded=False)

#         # --- Display Results ---
#         if error:
#             st.error(f"Failed to execute query after correction: {error}")
#         else:
#             st.markdown(reasoning)
#             with st.expander("View Generated SQL"):
#                 st.code(sql_part, language="sql")
            
#             if not df.empty:
#                 st.dataframe(df, use_container_width=True)
                
#                 # --- Export Functionality ---
#                 csv = df.to_csv(index=False).encode('utf-8')
#                 st.download_button(
#                     label="📥 Download as CSV",
#                     data=csv,
#                     file_name="query_results.csv",
#                     mime="text/csv",
#                 )
                
#                 # Store message with data
#                 st.session_state.messages.append({
#                     "role": "assistant", 
#                     "content": reasoning,
#                     "data": df
#                 })
#             else:
#                 st.warning("Query returned no results.")
#                 st.session_state.messages.append({"role": "assistant", "content": reasoning})

# ========================================================================================================================
# import streamlit as st
# import os
# import sqlite3
# import pandas as pd
# import time
# import io
# from google import genai
# from google.api_core import exceptions
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # --- 1. Configuration & Client Initialization ---
# st.set_page_config(page_title="DataTalk AI 2026", layout="wide", page_icon="🤖")

# # Use gemini-2.0-flash-lite for higher free-tier limits in 2026
# MODEL_ID = "models/gemini-2.5-flash-lite"
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# # --- 2. Database Helper Functions ---
# def get_available_dbs():
#     """Finds all SQLite .db files in the current folder."""
#     return [f for f in os.listdir('.') if f.endswith('.db')]

# def get_db_schema(db_path):
#     """Dynamically extracts schema info for the AI context."""
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#         cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
#         schema = "\n".join([row[0] for row in cursor.fetchall() if row[0]])
#         conn.close()
#         return schema
#     except Exception as e:
#         return f"Error reading schema: {e}"

# def execute_sql(sql, db_path):
#     """Executes the query and returns a DataFrame or the error string."""
#     try:
#         conn = sqlite3.connect(db_path)
#         df = pd.read_sql_query(sql, conn)
#         conn.close()
#         return df, None
#     except Exception as e:
#         return None, str(e)

# # --- 3. UI and Session State ---
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# with st.sidebar:
#     st.title("🗄️ Database Manager")
#     db_list = get_available_dbs()
#     selected_db = st.selectbox("Active Database:", db_list if db_list else ["No .db files found"])
    
#     if st.button("🗑️ Reset Chat History"):
#         st.session_state.messages = []
#         st.rerun()
    
#     if selected_db != "No .db files found":
#         st.divider()
#         with st.expander("Live Database Schema"):
#             st.code(get_db_schema(selected_db), language="sql")

# # --- 4. Main App Logic ---
# st.title("💬 DataTalk: Agentic Text-to-SQL")
# st.caption(f"Currently querying: **{selected_db}**")

# # Display Conversation History
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
#         if "data" in msg:
#             st.dataframe(msg["data"], use_container_width=True)

# # User Query Input
# if user_prompt := st.chat_input("Ex: 'Show me the top 5 students by grade'"):
#     st.session_state.messages.append({"role": "user", "content": user_prompt})
#     with st.chat_message("user"):
#         st.markdown(user_prompt)

#     with st.chat_message("assistant"):
#         schema_context = get_db_schema(selected_db)
        
#         # Define the AI personality and rules
#         sys_instr = f"""You are an expert Data Analyst. 
#         Database Schema: {schema_context}
        
#         Instructions:
#         1. Write a SQL query based on the user question.
#         2. Format response exactly as:
#            QUERY: <sql_query>
#            REASONING: <short_explanation>
#         """

#         # FIX: Format history for Pydantic/GenAI SDK compatibility
#         formatted_history = []
#         for m in st.session_state.messages[:-1]:
#             formatted_history.append({
#                 "role": m["role"],
#                 "parts": [{"text": m["content"]}] # Required dictionary format for 2026 SDK
#             })

#         # Initialize Chat Session
#         chat = client.chats.create(
#             model=MODEL_ID,
#             config={'system_instruction': sys_instr},
#             history=formatted_history
#         )

#         with st.status("🔍 Analyzing and Generating SQL...", expanded=True) as status:
#             try:
#                 # 1. Generate Query
#                 response = chat.send_message(user_prompt)
#                 raw_text = response.text
                
#                 # Parsing logic
#                 sql_query = raw_text.split("QUERY:")[1].split("REASONING:")[0].strip() if "QUERY:" in raw_text else ""
#                 reasoning = raw_text.split("REASONING:")[1].strip() if "REASONING:" in raw_text else "Fetched data based on your request."

#                 st.write("Executing Query...")
#                 df, error = execute_sql(sql_query, selected_db)

#                 # 2. Self-Correction Loop (The "Agentic" part)
#                 if error:
#                     st.write(f"⚠️ Initial SQL failed: {error}. Retrying...")
#                     correction_prompt = f"The query failed with error: {error}. Please fix the SQL and provide it using the 'QUERY:' tag."
#                     retry_res = chat.send_message(correction_prompt)
                    
#                     if "QUERY:" in retry_res.text:
#                         sql_query = retry_res.text.split("QUERY:")[1].split("REASONING:")[0].strip()
#                         df, error = execute_sql(sql_query, selected_db)
#                         reasoning = "Fixed: " + reasoning

#                 status.update(label="✅ Success!", state="complete")
#             except exceptions.ResourceExhausted:
#                 st.error("Quota exceeded. Please wait a moment before trying again.")
#                 status.update(label="❌ Quota Error", state="error")
#                 error = "Quota Error"

#         # 3. Output Results to UI
#         if not error and df is not None:
#             st.markdown(reasoning)
#             with st.expander("View SQL Statement"):
#                 st.code(sql_query, language="sql")
            
#             st.dataframe(df, use_container_width=True)

#             # Export Features
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.download_button("📊 Download CSV", df.to_csv(index=False), "data.csv", "text/csv")
#             with col2:
#                 buffer = io.BytesIO()
#                 with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#                     df.to_excel(writer, index=False)
#                 st.download_button("📁 Download Excel", buffer, "data.xlsx")

#             # Save to History
#             st.session_state.messages.append({"role": "assistant", "content": reasoning, "data": df})
#         elif error != "Quota Error":
#             st.error(f"Execution Error: {error}")
# ======================================================================================================================



# import streamlit as st
# import os
# import sqlite3
# import pandas as pd
# import time
# import io
# from google import genai
# from google.api_core import exceptions
# from dotenv import load_dotenv

# load_dotenv()

# # --- 1. Configuration ---
# st.set_page_config(page_title="DataTalk Pro 2026", layout="wide", page_icon="🤖")
# # Gemini 2.5 Flash-Lite: Best for free tier (15 RPM / 1000 RPD)
# MODEL_NAME = "models/gemini-2.5-flash-lite" 
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# # --- 2. Database Logic ---
# def get_available_dbs():
#     return [f for f in os.listdir('.') if f.endswith('.db')]

# def get_schema(db_path):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
#     schema = "\n".join([row[0] for row in cursor.fetchall() if row[0]])
#     conn.close()
#     return schema

# def run_query(sql, db_path):
#     try:
#         conn = sqlite3.connect(db_path)
#         df = pd.read_sql_query(sql, conn)
#         conn.close()
#         return df, None
#     except Exception as e:
#         return None, str(e)

# # --- 3. Agentic Logic with Retry ---
# def call_gemini_with_retry(chat_session, prompt):
#     """Retries the call if quota is hit (Exponential Backoff)."""
#     for attempt in range(3): # Try 3 times
#         try:
#             return chat_session.send_message(prompt)
#         except exceptions.ResourceExhausted:
#             wait_time = (attempt + 1) * 5
#             st.warning(f"Quota busy. Retrying in {wait_time}s...")
#             time.sleep(wait_time)
#     return None

# # --- 4. Sidebar & State ---
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# with st.sidebar:
#     st.title("⚙️ Workspace")
#     db_list = get_available_dbs()
#     selected_db = st.selectbox("Active Database", db_list if db_list else ["None Found"])
    
#     if st.button("🗑️ Clear History"):
#         st.session_state.messages = []
#         st.rerun()
    
#     if selected_db != "None Found":
#         st.divider()
#         st.caption("Active Schema Structure:")
#         st.code(get_schema(selected_db), language="sql")

# # --- 5. Main Chat UI ---
# st.title("📊 DataTalk AI Analyst")
# st.info(f"Using Model: {MODEL_NAME} (High Quota Free Tier)")

# # Display Chat History
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
#         if "data" in msg:
#             st.dataframe(msg["data"], use_container_width=True)

# # User Input
# if user_input := st.chat_input("Ask: 'What is our total revenue for January?'"):
#     st.session_state.messages.append({"role": "user", "content": user_input})
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.chat_message("assistant"):
#         schema = get_schema(selected_db)
#         sys_instr = f"You are a SQL expert. Schema: {schema}. Return 'QUERY: <sql>' and 'EXPLANATION: <text>'."
        
#         chat = client.chats.create(
#             model=MODEL_NAME,
#             config={'system_instruction': sys_instr},
#             history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
#         )

#         with st.spinner("Analyzing..."):
#             response = call_gemini_with_retry(chat, user_input)
            
#             if response:
#                 full_text = response.text
#                 sql_part = full_text.split("QUERY:")[1].split("EXPLANATION:")[0].strip() if "QUERY:" in full_text else ""
#                 explanation = full_text.split("EXPLANATION:")[1].strip() if "EXPLANATION:" in full_text else "Here is the data."

#                 # Initial Query Execution
#                 df, error = run_query(sql_part, selected_db)

#                 # Agentic Self-Correction Loop
#                 if error:
#                     st.caption("🔄 Error found, attempting to self-fix...")
#                     retry_res = call_gemini_with_retry(chat, f"Fix this SQL error: {error}. Return only the new SQL under QUERY: tag.")
#                     if retry_res:
#                         sql_part = retry_res.text.split("QUERY:")[1].split("EXPLANATION:")[0].strip() if "QUERY:" in retry_res.text else sql_part
#                         df, error = run_query(sql_part, selected_db)

#                 if not error and df is not None:
#                     st.markdown(explanation)
#                     st.dataframe(df)
                    
#                     # UI: Export Options
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.download_button("📥 Download CSV", df.to_csv(index=False), "results.csv", "text/csv")
#                     with col2:
#                         buffer = io.BytesIO()
#                         with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#                             df.to_excel(writer, index=False)
#                         st.download_button("📂 Download Excel", buffer, "results.xlsx")

#                     st.session_state.messages.append({"role": "assistant", "content": explanation, "data": df})
#                 else:
#                     st.error(f"Could not resolve query: {error}")
#             else:
#                 st.error("Model unavailable. Please try again in 1 minute.")


















































# # streamlit run TextToSQL.py
# import streamlit as st
# import os
# import sqlite3
# import pandas as pd
# from google import genai
# from dotenv import load_dotenv

# load_dotenv()

# # --- 1. Configuration & Client Initialization ---
# st.set_page_config(page_title="DataTalk AI 2026", layout="wide")
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# DB_NAME = "business.db"

# # --- 2. Database Helper Functions ---
# def get_db_schema():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
#     schema = "\n".join([row[0] for row in cursor.fetchall()])
#     conn.close()
#     return schema

# def run_sql(sql_query):
#     try:
#         conn = sqlite3.connect(DB_NAME)
#         df = pd.read_sql_query(sql_query, conn)
#         conn.close()
#         return df, None
#     except Exception as e:
#         return None, str(e)

# # --- 3. Persistent Chat State ---
# # We store the conversation history in Streamlit's session_state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # --- 4. Sidebar & UI Elements ---
# with st.sidebar:
#     st.title("⚙️ Database Settings")
#     if st.button("Reset Chat"):
#         st.session_state.messages = []
#         st.rerun()
#     st.info("Current DB: business.db")
#     with st.expander("View Schema"):
#         st.code(get_db_schema(), language="sql")

# # --- 5. Chat Interface ---
# st.title("💬 DataTalk: Chat with your SQL DB")

# # Display previous messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#         if "data" in message:
#             st.dataframe(message["data"])

# # User Input
# if prompt := st.chat_input("Ex: 'Who are our top 3 customers?'"):
#     # Add user message to state
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # --- 6. The Agentic Reasoning Loop ---
#     with st.chat_message("assistant"):
#         schema = get_db_schema()
        
#         # We use Gemini 2.0 Flash for its speed in multi-turn chat
#         # System instruction ensures it only focuses on SQL generation
#         sys_instr = f"""You are a SQL expert. Use this schema: {schema}.
#         1. When asked a question, provide the SQL query.
#         2. Format your response exactly like this:
#            QUERY: <your_sql_here>
#            EXPLANATION: <briefly explain what you found>
#         """
        
#         # Create a stateful chat session using history
#         chat = client.chats.create(
#             model="models/gemini-flash-latest",
#             config={'system_instruction': sys_instr},
#             history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
#         )
        
#         response = chat.send_message(prompt)
#         full_text = response.text
        
#         # Parse the SQL out of the response
#         if "QUERY:" in full_text:
#             parts = full_text.split("EXPLANATION:")
#             sql_part = parts[0].replace("QUERY:", "").strip()
#             explanation = parts[1].strip() if len(parts) > 1 else ""
            
#             # Execute the query
#             df, error = run_sql(sql_part)
            
#             if error:
#                 st.error(f"SQL Error: {error}")
#                 st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I had trouble: {error}"})
#             else:
#                 st.markdown(explanation)
#                 st.dataframe(df)
#                 # Store the successful interaction
#                 st.session_state.messages.append({
#                     "role": "assistant", 
#                     "content": explanation,
#                     "data": df
#                 })
#         else:
#             st.markdown(full_text)
#             st.session_state.messages.append({"role": "assistant", "content": full_text})













# import streamlit as st
# import os
# from google import genai
# from dotenv import load_dotenv
# import sqlite3
# import pandas as pd

# load_dotenv()

# # Initialize the new 2026 Client
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# print(client)
# DB_NAME = "business.db"

# def get_db_schema():
#     """Dynamically fetches schema so the AI always knows the table structure."""
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
#     schema = "\n".join([row[1] for row in cursor.fetchall()])
#     conn.close()
#     return schema

# def execute_query(sql):
#     """Executes SQL and returns a DataFrame or an Error Message."""
#     try:
#         conn = sqlite3.connect(DB_NAME)
#         df = pd.read_sql_query(sql, conn)
#         conn.close()
#         return df, None
#     except Exception as e:
#         return None, str(e)

# # --- UI Setup ---
# st.set_page_config(page_title="DataSense AI 2026", layout="wide")
# st.title("🚀 DataSense: Agentic Text-to-SQL")

# user_query = st.text_input("Ask a question about your business data:")

# if st.button("Analyze"):
#     schema = get_db_schema()
    
#     # System Prompt for the Agent
#     sys_instruction = f"""
#     You are a SQL Expert. Given the following database schema, write a SQL query to answer the user request.
#     Schema:
#     {schema}
    
#     Rules:
#     - Output ONLY the raw SQL. No markdown blocks, no backticks, no 'sql' prefix.
#     - If the user asks for a chart, still output the SQL needed to get that data.
#     """

#     # Generate SQL
#     response = client.models.generate_content(
#         model="models/gemini-flash-latest",
#         config={'system_instruction': sys_instruction},
#         contents=user_query
        
#     )
    
#     generated_sql = response.text.strip()
    
#     with st.expander("View Generated SQL"):
#         st.code(generated_sql, language="sql")

#     # Execute and handle potential errors (Agentic Self-Correction)
#     results, error = execute_query(generated_sql)
    
#     if error:
#         st.error(f"First attempt failed: {error}. Retrying with correction...")
#         # Optional: Feed the error back to Gemini to fix the SQL
#     else:
#         st.subheader("Results")
#         st.dataframe(results, use_container_width=True)
        
#         # UI/UX: Automatic Visualization
#         if not results.empty and len(results.columns) >= 2:
#             st.bar_chart(results.set_index(results.columns[0]))