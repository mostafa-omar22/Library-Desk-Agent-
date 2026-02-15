# 📚 Library Desk Agent

An AI-powered library management system built with **Streamlit**, **LangChain**, and **SQLite**. This agent manages inventory, processes orders, registers new customers, and tracks conversation history with automated session summaries.

---

## 🚀 Features

* **Intelligent Agent**: Uses LangChain and GPT-4o-mini to chain multiple tools (e.g., creating a customer and placing an order in one step).
* **Database Guardrails**: SQLite with `CHECK` constraints ensures stock never goes below zero.
* **Session Management**: A sidebar that allows you to create new chats or load previous ones with AI-generated titles.
* **Audit Trail**: Logs every message and tool call (including JSON arguments and results) to a permanent database.
* **Advanced Inventory**: Automated "low stock" reporting and real-time inventory adjustments with book title resolution.

---

## 📂 Project Structure

```text
library/
├── app/
│   └── main.py          # Streamlit frontend & session logic
├── server/
│   ├── tools.py         # 7 LangChain tools (DB operations)
│   └── __init__.py      # Package indicator
├── db/
│   ├── schema.sql       # Advanced DB schema with constraints
│   ├── seed.sql         # 10 books, 6 customers, and 4 orders
│   └── library.db       # The SQLite database file (generated)
├── prompts/
│   └── system_prompt.txt # Agent personality and guardrails
├── init_db.py           # Script to reset/rebuild the database
├── requirements.txt     # Python dependencies
└── .env                 # API Keys (Excluded from Git)
