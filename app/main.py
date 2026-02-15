import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import uuid
import os
import sqlite3
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.callbacks import StreamlitCallbackHandler
from server.tools import tools


# Load variables from .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
db_path = os.getenv("DB_PATH")


def generate_session_title(user_input):
    """Asks the LLM to create a 3-word title for the sidebar."""
    summary_prompt = f"Summarize this request in 3 words or less for a sidebar title: '{user_input}'"
    response = llm.invoke(summary_prompt)
    return response.content.strip().replace('"', '')


def create_new_session(session_id, first_query):
    """Initializes the session in the DB with a summarized title."""
    title = generate_session_title(first_query)
    with sqlite3.connect("db/library.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (id, title) VALUES (?, ?)", (session_id, title))
        conn.commit()


def get_all_sessions():
    """Fetches unique session IDs from the database."""
    with sqlite3.connect("db/library.db") as conn:
        cursor = conn.cursor()
        # Get unique session IDs ordered by the most recent message
        cursor.execute("SELECT DISTINCT session_id FROM messages ORDER BY id DESC")
        return [row[0] for row in cursor.fetchall()]


def load_chat_history(session_id):
    """Loads all messages for a specific session ID."""
    with sqlite3.connect("db/library.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        # Return as a list of dictionaries for Streamlit session_state
        return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]


def log_message_to_db(session_id, role, content):
    """Saves a single chat message to the DB"""
    with sqlite3.connect("db/library.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()


def log_tool_calls_to_db(session_id, intermediate_steps):
    """Saves tool execution details to the DB """
    with sqlite3.connect("db/library.db") as conn:
        cursor = conn.cursor()
        for action, observation in intermediate_steps:
            # action is the tool call, observation is the result
            tool_id = str(uuid.uuid4())  # Generate a unique ID for the log
            cursor.execute(
                "INSERT INTO tool_calls (id, session_id, name, args_json, result_json) VALUES (?, ?, ?, ?, ?)",
                (tool_id, session_id, action.tool, json.dumps(action.tool_input), json.dumps(observation))
            )
        conn.commit()


#Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_created" not in st.session_state:
    st.session_state.session_created = False

# 1. Page Configuration
st.set_page_config(page_title="Library Desk Agent", layout="wide")

# 2. Sidebar: Session Selector
with st.sidebar:
    st.title("📂 Session Manager")

    # Button to start a new chat session
    if st.button("➕ New Chat Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.session_created = False
        st.rerun()

    sessions_data = []
    with sqlite3.connect("db/library.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM sessions ORDER BY created_at DESC")
        sessions_data = cursor.fetchall()

    if sessions_data:
        # Create a dictionary for the selectbox: { "Title (ID)": "ID" }
        session_options = {f"{row[1]} ({row[0][:8]})": row[0] for row in sessions_data}
        selected_label = st.selectbox("Load History", options=list(session_options.keys()), index=None)

        if selected_label:
            selected_id = session_options[selected_label]
            if st.session_state.get("session_id") != selected_id:
                st.session_state.session_id = selected_id
                st.session_state.messages = load_chat_history(selected_id)
                st.session_state.session_created = True
                st.rerun()



# 3. Agent Initialization Logic
# Note: Ensure your OPENAI_API_KEY is in your .env or environment variables
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

with open("C:/Users/mosta/Desktop/library/prompts/system_prompts.txt", "r") as f:
    system_instructions = f.read()

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instructions),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

# 4. Main Chat Interface
st.title("📚 Library Desk Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. User Interaction
if user_query := st.chat_input("How can I help you?"):
    if not st.session_state.get("session_created", False):
        create_new_session(st.session_state.session_id, user_query)
        st.session_state.session_created = True

    st.session_state.messages.append({"role": "user", "content": user_query})
    log_message_to_db(st.session_state.session_id, "user", user_query)
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        # This shows the tool-calling process in real-time
        st_callback = StreamlitCallbackHandler(st.container())

        response = agent_executor.invoke(
            {"input": user_query, "chat_history": st.session_state.messages},
            {"callbacks": [st_callback]}
        )

        output = response["output"]
        steps = response.get("intermediate_steps", [])  # Capture tool steps
        log_message_to_db(st.session_state.session_id, "assistant", output)  # Log Assistant Message
        log_tool_calls_to_db(st.session_state.session_id, steps)  # Log Tool Calls
        st.write(output)
        st.session_state.messages.append({"role": "assistant", "content": output})
